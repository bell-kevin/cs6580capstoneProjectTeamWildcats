"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check, Pencil, RefreshCw, Volume2, VolumeX, Snowflake, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import { MapDisplay, parsePlacesFromContent, cleanMapDataFromContent } from "./map-display";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export interface MessageMeta {
  model?: string;   // "random-forest" | "lstm"
  sources?: string[]; // ["UDOT", "UTA", "ML"]
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt?: Date | string;
  meta?: MessageMeta;
}

interface ChatMessagesProps {
  messages: Message[];
  isLoading?: boolean;
  streamingContent?: string;
  onEditMessage?: (messageId: string, newContent: string) => void;
  onResendMessage?: (content: string) => void;
  onRetry?: () => void;
  onSuggest?: (msg: string) => void;
}

// --- Follow-up suggestion helper ---
function getFollowUps(content: string): string[] {
  const lower = content.toLowerCase();
  const suggestions: string[] = [];
  if (lower.includes("vehicle") || lower.includes("traffic") || lower.includes("forecast")) {
    suggestions.push("Check SR-167 road conditions");
    suggestions.push("Compare weekend vs weekday traffic");
  }
  if (lower.includes("sr-167") || lower.includes("road condition") || lower.includes("udot")) {
    suggestions.push("Predict traffic for tomorrow morning");
    suggestions.push("Are chains required on SR-210?");
  }
  if (lower.includes("bus") || lower.includes("uta") || lower.includes("transit")) {
    suggestions.push("How busy will Snowbasin be today?");
    suggestions.push("What are SR-167 conditions?");
  }
  if (suggestions.length === 0) {
    suggestions.push("Predict traffic this Saturday at 9am");
    suggestions.push("SR-167 road conditions");
  }
  return suggestions.slice(0, 3);
}

export function ChatMessages({
  messages,
  isLoading,
  streamingContent,
  onEditMessage,
  onResendMessage,
  onRetry,
  onSuggest,
}: ChatMessagesProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex h-full flex-col items-center justify-center px-4">
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-linear-to-br from-blue-400 to-cyan-500">
          <Snowflake className="h-8 w-8 text-white" />
        </div>
        <h2 className="mb-2 text-xl sm:text-2xl font-semibold text-center">Welcome to Snowbasin</h2>
        <p className="text-center text-sm sm:text-base text-muted-foreground max-w-md">
          Ask me about Utah snow forecasts, ski conditions, or UTA transit schedules.
        </p>
      </div>
    );
  }

  // Determine which message should receive the onRetry prop:
  // the last message if it is an assistant error and not currently loading.
  const lastMsg = messages.length > 0 ? messages[messages.length - 1] : null;
  const lastMsgIsError =
    lastMsg !== null &&
    lastMsg.role === "assistant" &&
    /^[⏳🔄🔧🔑💥📡]/.test(lastMsg.content);

  // Determine whether to show follow-up suggestions:
  const showSuggestions =
    lastMsg !== null &&
    lastMsg.role === "assistant" &&
    !lastMsgIsError &&
    !isLoading &&
    !!onSuggest;

  return (
    <div className="h-full">
      <div className="mx-auto max-w-3xl px-3 sm:px-4 py-4 sm:py-8">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onEdit={onEditMessage}
            onResend={onResendMessage}
            onRetry={
              message.id === lastMsg?.id && lastMsgIsError && !isLoading
                ? onRetry
                : undefined
            }
          />
        ))}

        {/* Streaming message */}
        {(isLoading || streamingContent) && (
          <MessageBubble
            message={{
              id: "streaming",
              role: "assistant",
              content: streamingContent || "",
            }}
            isStreaming={isLoading && !streamingContent}
            streamingMeta={streamingContent ? undefined : undefined}
          />
        )}

        {/* Follow-up suggestion chips */}
        {showSuggestions && (
          <div className="pb-2">
            <div className="flex flex-wrap gap-2 ml-1">
              {getFollowUps(lastMsg!.content).map((s) => (
                <button
                  key={s}
                  onClick={() => onSuggest!(s)}
                  className="flex items-center gap-1 rounded-full border bg-muted/50 px-3 py-1 text-xs hover:bg-muted hover:border-primary/40 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}

const SOURCE_BADGE: Record<string, { icon: string; label: string; color: string; border: string }> = {
  UDOT:  { icon: "📡", label: "UDOT",  color: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400", border: "border-orange-200 dark:border-orange-800" },
  UTA:   { icon: "🚌", label: "UTA",   color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",   border: "border-green-200 dark:border-green-800" },
  ML:    { icon: "",   label: "",      color: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",        border: "border-blue-200 dark:border-blue-800" },
  Maps:  { icon: "🗺️", label: "Maps",  color: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400", border: "border-purple-200 dark:border-purple-800" },
};

function ModelBadge({ model, sources }: { model?: string; sources?: string[] }) {
  if (!model) return null;
  const modelLabel = model === "lstm" ? "🧠 LSTM" : "🌲 Random Forest";
  const hasPrediction = sources?.includes("ML");
  return (
    <>
      <span className="inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
        {modelLabel}
      </span>
      {hasPrediction && (
        <span className="inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
          {model === "lstm" ? "🧠 LSTM Prediction" : "🌲 RF Prediction"}
        </span>
      )}
      {sources?.filter((s) => s !== "ML").map((src) => {
        const badge = SOURCE_BADGE[src];
        if (!badge) return null;
        return (
          <span
            key={src}
            className={`inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium border ${badge.color} ${badge.border}`}
          >
            {badge.icon} {badge.label}
          </span>
        );
      })}
    </>
  );
}

function CodeBlock({ children, className }: { children?: React.ReactNode; className?: string }) {
  const [codeCopied, setCodeCopied] = useState(false);
  const code = String(children).replace(/\n$/, "");
  const copyCode = async () => {
    await navigator.clipboard.writeText(code);
    setCodeCopied(true);
    setTimeout(() => setCodeCopied(false), 2000);
  };
  return (
    <div className="relative group/code my-2">
      <pre className={cn("rounded-lg bg-muted p-4 overflow-x-auto text-xs", className)}>
        <code>{children}</code>
      </pre>
      <button
        onClick={copyCode}
        className="absolute top-2 right-2 opacity-0 group-hover/code:opacity-100 transition-opacity p-1.5 rounded-md bg-background/80 hover:bg-background border text-xs"
        title="Copy code"
      >
        {codeCopied ? <Check className="h-3 w-3 text-green-500" /> : <Copy className="h-3 w-3" />}
      </button>
    </div>
  );
}


function MessageBubble({
  message,
  isStreaming,
  onEdit,
  onResend,
  onRetry,
}: {
  message: Message;
  isStreaming?: boolean;
  streamingMeta?: MessageMeta;
  onEdit?: (messageId: string, newContent: string) => void;
  onResend?: (content: string) => void;
  onRetry?: () => void;
}) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(message.content);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [showActions, setShowActions] = useState(false);

  // Parse places from assistant messages
  const places = !isUser ? parsePlacesFromContent(message.content) : null;
  const displayContent = places ? cleanMapDataFromContent(message.content) : message.content;
  const isError = !isUser && /^[⏳🔄🔧🔑💥📡]/.test(message.content);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleEdit = () => {
    setIsEditing(true);
    setEditContent(message.content);
  };

  const handleSaveEdit = () => {
    if (editContent.trim() && onEdit) {
      onEdit(message.id, editContent);
    }
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditContent(message.content);
  };

  const handleResend = () => {
    if (onResend) {
      onResend(message.content);
    }
  };

  const handleListen = () => {
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    } else {
      const utterance = new SpeechSynthesisUtterance(displayContent);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
      setIsSpeaking(true);
    }
  };

  // Clean up speech on unmount
  useEffect(() => {
    return () => {
      if (isSpeaking) {
        window.speechSynthesis.cancel();
      }
    };
  }, [isSpeaking]);

  return (
    <div
      className={cn(
        "group mb-4 sm:mb-6 flex flex-col",
        isUser ? "items-end" : "items-start"
      )}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Message Label + inline source badges */}
      <div className={cn("flex items-center gap-1.5 flex-wrap mb-1.5 px-1", isUser ? "justify-end" : "justify-start")}>
        <span className={cn("text-xs font-medium", isUser ? "text-primary" : "text-muted-foreground")}>
          {isUser ? "You" : "Snowbasin"}
        </span>
        {!isUser && !isStreaming && (
          <ModelBadge model={message.meta?.model} sources={message.meta?.sources} />
        )}
        {showActions && (
          <span className="text-[10px] text-muted-foreground/60 ml-auto">
            {message.createdAt
              ? new Date(message.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
              : "just now"}
          </span>
        )}
      </div>

      {/* Message Content */}
      {isEditing ? (
        <div className="w-full max-w-[85%] sm:max-w-[80%]">
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            className="w-full rounded-xl border bg-background p-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary resize-none"
            rows={3}
            autoFocus
          />
          <div className="flex gap-2 mt-2">
            <Button size="sm" onClick={handleSaveEdit}>Save & Resend</Button>
            <Button size="sm" variant="outline" onClick={handleCancelEdit}>Cancel</Button>
          </div>
        </div>
      ) : (
        <div
          className={cn(
            "relative max-w-[85%] sm:max-w-[80%] rounded-2xl px-4 py-3 text-sm sm:text-base",
            isUser
              ? "bg-primary text-primary-foreground"
              : isError
              ? "bg-destructive/5 text-card-foreground shadow-sm border border-destructive/30"
              : "bg-card text-card-foreground shadow-sm border",
            !isUser && isStreaming && "ring-1 ring-primary/20"
          )}
        >
          {isStreaming ? (
            <div className="flex items-center gap-1.5 py-1">
              <div className="h-2 w-2 animate-bounce rounded-full bg-current opacity-60 [animation-delay:-0.3s]" />
              <div className="h-2 w-2 animate-bounce rounded-full bg-current opacity-60 [animation-delay:-0.15s]" />
              <div className="h-2 w-2 animate-bounce rounded-full bg-current opacity-60" />
            </div>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code({ className, children, ...props }) {
                    const isBlock = className?.includes("language-");
                    if (isBlock) {
                      return <CodeBlock className={className}>{children}</CodeBlock>;
                    }
                    return <code className="rounded bg-muted px-1 py-0.5 text-xs font-mono" {...props}>{children}</code>;
                  },
                }}
              >
                {displayContent}
              </ReactMarkdown>
            </div>
          )}
        </div>
      )}

      {/* Retry button for error assistant messages */}
      {isError && onRetry && (
        <button
          onClick={onRetry}
          className="mt-1.5 flex items-center gap-1.5 text-xs text-muted-foreground hover:text-destructive transition-colors px-1"
        >
          <RefreshCw className="h-3 w-3" /> Retry
        </button>
      )}

      {/* Message Actions */}
      {!isStreaming && !isEditing && message.id !== "streaming" && (
        <div
          className={cn(
            "flex items-center gap-1 mt-2 transition-opacity duration-200",
            showActions ? "opacity-100" : "opacity-100 sm:opacity-0 sm:group-hover:opacity-100"
          )}
        >
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                size="icon"
                variant="ghost"
                className="h-7 w-7"
                onClick={handleCopy}
              >
                {copied ? (
                  <Check className="h-3.5 w-3.5 text-green-500" />
                ) : (
                  <Copy className="h-3.5 w-3.5" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>Copy</TooltipContent>
          </Tooltip>

          {isUser && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-7 w-7"
                  onClick={handleEdit}
                >
                  <Pencil className="h-3.5 w-3.5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Edit</TooltipContent>
            </Tooltip>
          )}

          {isUser && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-7 w-7"
                  onClick={handleResend}
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Resend</TooltipContent>
            </Tooltip>
          )}

          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                size="icon"
                variant="ghost"
                className="h-7 w-7"
                onClick={handleListen}
              >
                {isSpeaking ? (
                  <VolumeX className="h-3.5 w-3.5 text-primary" />
                ) : (
                  <Volume2 className="h-3.5 w-3.5" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>{isSpeaking ? "Stop" : "Listen"}</TooltipContent>
          </Tooltip>
        </div>
      )}

      {/* Render map if places are found */}
      {places && places.length > 0 && (
        <div className="mt-3 w-full max-w-[85%] sm:max-w-[80%]">
          <MapDisplay places={places} />
        </div>
      )}
    </div>
  );
}
