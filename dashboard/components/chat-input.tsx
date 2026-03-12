"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Square } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export type ModelType = "random-forest" | "lstm";

interface ChatInputProps {
  onSend: (message: string) => void;
  onStop?: () => void;
  isLoading?: boolean;
  disabled?: boolean;
  selectedModel: ModelType;
  onModelChange: (model: ModelType) => void;
}

export function ChatInput({
  onSend,
  onStop,
  isLoading,
  disabled,
  selectedModel,
  onModelChange,
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading && !disabled) {
      onSend(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t bg-background px-2 pt-2 pb-3 sm:px-4 sm:pt-3 sm:pb-4">
      <form onSubmit={handleSubmit} className="mx-auto max-w-3xl space-y-2">

        {/* Model Selector */}
        <div className="flex items-center gap-2 px-1">
          <span className="text-xs text-muted-foreground">Model:</span>
          <div className="flex items-center gap-1 rounded-full border bg-muted/40 p-0.5">
            <button
              type="button"
              onClick={() => onModelChange("random-forest")}
              className={cn(
                "flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium transition-all duration-200",
                selectedModel === "random-forest"
                  ? "bg-background text-blue-600 dark:text-blue-400 shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              🌲 Random Forest
            </button>
            <button
              type="button"
              onClick={() => onModelChange("lstm")}
              className={cn(
                "flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium transition-all duration-200",
                selectedModel === "lstm"
                  ? "bg-background text-green-600 dark:text-green-400 shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              🧠 LSTM
            </button>
          </div>
          <span className="text-xs text-muted-foreground hidden sm:block">
            {selectedModel === "random-forest"
              ? "· Fast & reliable for general forecasts"
              : "· Advanced time-series analysis"}
          </span>
        </div>

        {/* Textarea + Send */}
        <div className="relative flex items-end gap-2 rounded-2xl border bg-muted/50 p-2">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              selectedModel === "random-forest"
                ? "Ask about traffic, road conditions, ski resorts..."
                : "Ask about traffic predictions using LSTM time-series..."
            }
            disabled={disabled}
            rows={1}
            className={cn(
              "max-h-50 min-h-10 sm:min-h-11 flex-1 resize-none bg-transparent px-2 sm:px-3 py-2 text-sm outline-none placeholder:text-muted-foreground",
              disabled && "cursor-not-allowed opacity-50"
            )}
          />

          {isLoading ? (
            <Button
              type="button"
              size="icon"
              variant="destructive"
              onClick={onStop}
              className="h-9 w-9 sm:h-10 sm:w-10 rounded-xl shrink-0"
            >
              <Square className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              type="submit"
              size="icon"
              disabled={!input.trim() || disabled}
              className="h-9 w-9 sm:h-10 sm:w-10 rounded-xl shrink-0"
            >
              <Send className="h-4 w-4" />
            </Button>
          )}
        </div>

        <p className="text-center text-xs text-muted-foreground hidden sm:block">
          Press Enter to send · Shift+Enter for new line
        </p>
      </form>
    </div>
  );
}
