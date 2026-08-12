import React from "react";
import { clsx } from "clsx";
import { RiskLevel } from "@/types/venue";

interface ProgressBarProps {
  value: number; // 0 to 100 or 0 to 1
  max?: number;
  label?: string;
  showValue?: boolean;
  risk?: RiskLevel;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  label,
  showValue = true,
  risk,
  size = "md",
  className,
}) => {
  // Normalize percentage
  const percentage = Math.min(100, Math.max(0, max === 1 ? value * 100 : (value / max) * 100));

  // Determine risk level color dynamically if not explicitly provided
  let barColor = "bg-emerald-500 shadow-emerald-500/50";
  if (risk === "CRITICAL" || (!risk && percentage >= 85)) {
    barColor = "bg-red-500 shadow-red-500/50";
  } else if (risk === "HIGH" || (!risk && percentage >= 70)) {
    barColor = "bg-orange-500 shadow-orange-500/50";
  } else if (risk === "MEDIUM" || (!risk && percentage >= 50)) {
    barColor = "bg-amber-500 shadow-amber-500/50";
  }

  const heightClasses = {
    sm: "h-1.5",
    md: "h-2.5",
    lg: "h-4",
  };

  return (
    <div className={clsx("w-full space-y-1.5", className)}>
      {(label || showValue) && (
        <div className="flex justify-between items-center text-xs font-mono">
          {label && <span className="text-slate-300">{label}</span>}
          {showValue && <span className="text-slate-400 font-bold">{Math.round(percentage)}%</span>}
        </div>
      )}
      <div className={clsx("w-full rounded-full bg-slate-800/80 overflow-hidden p-0.5 border border-slate-700/50", heightClasses[size])}>
        <div
          className={clsx("h-full rounded-full transition-all duration-500 shadow-sm", barColor)}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
