"use client";

import * as React from "react";
import { DayPicker } from "react-day-picker";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

export type CalendarProps = React.ComponentProps<typeof DayPicker>;

function Calendar({ className, showOutsideDays = true, ...props }: CalendarProps) {
  return (
    <DayPicker
      showOutsideDays={showOutsideDays}
      className={cn("p-3", className)}
      classNames={{
        months: "relative flex flex-col",
        month: "space-y-3",
        month_caption: "flex justify-center items-center h-8 px-8",
        caption_label: "text-sm font-semibold",
        nav: "absolute inset-x-0 top-0 flex items-center justify-between h-8 px-1",
        button_previous: cn(
          "inline-flex items-center justify-center rounded-md h-7 w-7 text-foreground",
          "hover:bg-accent hover:text-accent-foreground transition-colors",
          "disabled:opacity-50 disabled:pointer-events-none"
        ),
        button_next: cn(
          "inline-flex items-center justify-center rounded-md h-7 w-7 text-foreground",
          "hover:bg-accent hover:text-accent-foreground transition-colors",
          "disabled:opacity-50 disabled:pointer-events-none"
        ),
        month_grid: "w-full border-collapse mt-1",
        weekdays: "flex",
        weekday: "text-muted-foreground w-9 h-9 flex items-center justify-center text-[0.8rem] font-normal",
        weeks: "flex flex-col gap-1",
        week: "flex",
        day: "relative p-0 flex items-center justify-center",
        day_button: cn(
          "h-9 w-9 text-sm rounded-md font-normal transition-colors",
          "hover:bg-accent hover:text-accent-foreground",
          "focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        ),
        selected: "[&>button]:bg-primary [&>button]:text-primary-foreground [&>button]:hover:bg-primary/90",
        today: "[&>button]:border [&>button]:border-primary [&>button]:font-semibold",
        outside: "[&>button]:text-muted-foreground [&>button]:opacity-40",
        disabled: "[&>button]:opacity-20 [&>button]:pointer-events-none",
        hidden: "invisible",
      }}
      components={{
        Chevron: ({ orientation }) =>
          orientation === "left"
            ? <ChevronLeft className="h-4 w-4" />
            : <ChevronRight className="h-4 w-4" />,
      }}
      {...props}
    />
  );
}

Calendar.displayName = "Calendar";
export { Calendar };
