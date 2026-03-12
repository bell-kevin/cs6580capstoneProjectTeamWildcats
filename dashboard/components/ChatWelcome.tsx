"use client";

import { Mountain, AlertTriangle, Thermometer, Brain, TreePine, Activity } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ModelType } from "@/components/chat-input";

interface ChatWelcomeProps {
  selectedModel: ModelType;
  onModelChange: (model: ModelType) => void;
  isGuest?: boolean;
}

export function ChatWelcome({ selectedModel, onModelChange, isGuest }: ChatWelcomeProps) {
  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="text-center space-y-1">
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
          Snowbasin Traffic Assistant
        </h1>
        <p className="text-sm text-muted-foreground">
          ML-powered traffic predictions · Live UDOT road conditions · UTA transit
        </p>
        {isGuest && (
          <div className="inline-flex items-center gap-1.5 mt-1 px-3 py-1 rounded-full bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800">
            <span className="text-xs text-amber-700 dark:text-amber-400 font-medium">
              👤 Guest Mode — chats are not saved
            </span>
          </div>
        )}
      </div>

      {/* Model Selector Cards */}
      <div className="grid grid-cols-2 gap-3">
        <button
          type="button"
          onClick={() => onModelChange("random-forest")}
          className={cn(
            "group rounded-xl border p-4 text-left transition-all duration-200",
            selectedModel === "random-forest"
              ? "border-blue-500 bg-blue-50 dark:bg-blue-950/30 shadow-sm"
              : "border-border hover:border-blue-300 hover:bg-muted/50"
          )}
        >
          <div className="flex items-center gap-2 mb-2">
            <div className={cn(
              "flex h-8 w-8 items-center justify-center rounded-lg text-base transition-colors",
              selectedModel === "random-forest"
                ? "bg-blue-500 text-white"
                : "bg-muted text-muted-foreground group-hover:bg-blue-100 group-hover:text-blue-600"
            )}>
              🌲
            </div>
            <div>
              <p className="text-xs font-semibold">Random Forest</p>
              {selectedModel === "random-forest" && (
                <span className="text-xs text-blue-600 dark:text-blue-400 font-medium">Active</span>
              )}
            </div>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Fast & reliable. Best for general traffic forecasts using weather and time features.
          </p>
          <div className="mt-2 flex items-center gap-1">
            <Activity className="h-3 w-3 text-green-500" />
            <span className="text-xs text-green-600 dark:text-green-400 font-medium">Deployed</span>
          </div>
        </button>

        <button
          type="button"
          onClick={() => onModelChange("lstm")}
          className={cn(
            "group rounded-xl border p-4 text-left transition-all duration-200",
            selectedModel === "lstm"
              ? "border-green-500 bg-green-50 dark:bg-green-950/30 shadow-sm"
              : "border-border hover:border-green-300 hover:bg-muted/50"
          )}
        >
          <div className="flex items-center gap-2 mb-2">
            <div className={cn(
              "flex h-8 w-8 items-center justify-center rounded-lg text-base transition-colors",
              selectedModel === "lstm"
                ? "bg-green-500 text-white"
                : "bg-muted text-muted-foreground group-hover:bg-green-100 group-hover:text-green-600"
            )}>
              🧠
            </div>
            <div>
              <p className="text-xs font-semibold">LSTM</p>
              {selectedModel === "lstm" && (
                <span className="text-xs text-green-600 dark:text-green-400 font-medium">Active</span>
              )}
            </div>
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            Advanced time-series analysis. Learns sequential traffic patterns over time.
          </p>
          <div className="mt-2 flex items-center gap-1">
            <Brain className="h-3 w-3 text-green-500" />
            <span className="text-xs text-green-600 dark:text-green-400 font-medium">Available</span>
          </div>
        </button>
      </div>

      {/* Capability Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="rounded-xl border bg-card p-4 space-y-2">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-500/10 text-blue-600">
              <TreePine className="h-4 w-4" />
            </div>
            <h3 className="text-xs font-semibold">Traffic Prediction</h3>
          </div>
          <p className="text-xs text-muted-foreground">
            ML-powered forecasts using time, weather, and seasonal data.
          </p>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground font-medium">Try:</p>
            <p className="text-xs text-muted-foreground italic">"Predict traffic Saturday at 8am"</p>
            <p className="text-xs text-muted-foreground italic">"How busy on a holiday weekend?"</p>
          </div>
        </div>

        <div className="rounded-xl border bg-card p-4 space-y-2">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-600">
              <Mountain className="h-4 w-4" />
            </div>
            <h3 className="text-xs font-semibold">Road Conditions</h3>
          </div>
          <p className="text-xs text-muted-foreground">
            Live UDOT data: passes, closures, plows, traction laws.
          </p>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground font-medium">Try:</p>
            <p className="text-xs text-muted-foreground italic">"SR-39 conditions to Snowbasin?"</p>
            <p className="text-xs text-muted-foreground italic">"Are chains required on SR-210?"</p>
          </div>
        </div>

        <div className="rounded-xl border bg-card p-4 space-y-2">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-orange-500/10 text-orange-600">
              <Thermometer className="h-4 w-4" />
            </div>
            <h3 className="text-xs font-semibold">Weather & Alerts</h3>
          </div>
          <p className="text-xs text-muted-foreground">
            Live weather stations, surface temps, wind, and alerts.
          </p>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground font-medium">Try:</p>
            <p className="text-xs text-muted-foreground italic">"Surface temp at Parley's Canyon"</p>
            <p className="text-xs text-muted-foreground italic">"Any closures on I-80?"</p>
          </div>
        </div>
      </div>

      {/* Prediction parameters info */}
      <div className="rounded-xl border bg-muted/30 p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-4 w-4 text-amber-500 mt-0.5 shrink-0" />
          <div className="space-y-1">
            <p className="text-xs font-semibold">For Traffic Predictions</p>
            <p className="text-xs text-muted-foreground">
              Tell me the <span className="font-medium text-foreground">day, time, and weather conditions</span> (or say "use typical winter conditions") and I'll run the {selectedModel === "random-forest" ? "🌲 Random Forest" : "🧠 LSTM"} model and explain the results.
            </p>
            <p className="text-xs text-muted-foreground italic mt-1">
              "Predict traffic for Saturday 8am with 18 inches of snow and 28°F"
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
