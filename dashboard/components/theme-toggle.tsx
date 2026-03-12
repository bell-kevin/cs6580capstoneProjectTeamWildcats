"use client";

import { useTheme } from "next-themes";
import { Sun, Moon, Monitor } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex items-center gap-0.5 rounded-lg border bg-muted/40 p-0.5">
      <Button
        type="button"
        size="icon"
        variant="ghost"
        onClick={() => setTheme("light")}
        className={cn(
          "h-7 w-7 rounded-md",
          theme === "light" && "bg-background shadow-sm text-foreground"
        )}
        title="Light"
      >
        <Sun className="h-3.5 w-3.5" />
      </Button>
      <Button
        type="button"
        size="icon"
        variant="ghost"
        onClick={() => setTheme("system")}
        className={cn(
          "h-7 w-7 rounded-md",
          theme === "system" && "bg-background shadow-sm text-foreground"
        )}
        title="System"
      >
        <Monitor className="h-3.5 w-3.5" />
      </Button>
      <Button
        type="button"
        size="icon"
        variant="ghost"
        onClick={() => setTheme("dark")}
        className={cn(
          "h-7 w-7 rounded-md",
          theme === "dark" && "bg-background shadow-sm text-foreground"
        )}
        title="Dark"
      >
        <Moon className="h-3.5 w-3.5" />
      </Button>
    </div>
  );
}
