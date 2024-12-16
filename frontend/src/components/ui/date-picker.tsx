import { format } from "date-fns";
import { Calendar as CalendarIcon } from "lucide-react";
import { DayPicker } from "react-day-picker";
import { cn } from "@/lib/utils";

interface DatePickerProps {
  date?: Date;
  onChange: (date?: Date) => void;
  className?: string;
}

export function DatePicker({ date, onChange, className }: DatePickerProps) {
  return (
    <div className={cn("grid gap-2", className)}>
      <div className="flex items-center gap-2 rounded-md border p-2">
        <CalendarIcon className="h-4 w-4" />
        <span className="text-sm">
          {date ? format(date, "PPP") : "Pick a date"}
        </span>
      </div>
      <div className="absolute mt-2 bg-white p-3 rounded-md shadow-md border">
        <DayPicker
          mode="single"
          selected={date}
          onSelect={onChange}
          className="border-none"
        />
      </div>
    </div>
  );
}