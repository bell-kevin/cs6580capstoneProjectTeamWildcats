"use client";
import { useSpaceStatus } from "@/hooks/use-space-status";
import { cn } from "@/lib/utils";

const STATUS_CONFIG = {
  online:  { dot: "bg-green-500",  label: "Model ready" },
  warming: { dot: "bg-yellow-500 animate-pulse", label: "Model warming up..." },
  offline: { dot: "bg-red-500",    label: "Model offline" },
  unknown: { dot: "bg-gray-400",   label: "" },
};

export function SpaceStatus() {
  const { status } = useSpaceStatus();
  const config = STATUS_CONFIG[status];
  if (status === "unknown") return null;
  return (
    <div className="flex items-center gap-1.5">
      <div className={cn("h-2 w-2 rounded-full", config.dot)} />
      {config.label && (
        <span className="text-xs text-muted-foreground hidden sm:block">{config.label}</span>
      )}
    </div>
  );
}
