import React from "react";
import { Card } from "./Card";
import { clsx } from "clsx";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  trend?: {
    value: string;
    isPositive?: boolean;
    isNegative?: boolean;
  };
  glowColor?: "cyan" | "red" | "yellow" | "green";
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  glowColor,
  className,
}) => {
  return (
    <Card glow={!!glowColor} glowColor={glowColor} className={clsx("p-4 sm:p-5 relative", className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs font-mono font-medium text-slate-400 tracking-wider uppercase">{title}</p>
          <h4 className="text-2xl sm:text-3xl font-bold font-mono text-white tracking-tight">{value}</h4>
        </div>
        {icon && (
          <div className="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-cyan-400 shrink-0">
            {icon}
          </div>
        )}
      </div>

      {(subtitle || trend) && (
        <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs">
          {subtitle && <span className="text-slate-400">{subtitle}</span>}
          {trend && (
            <span
              className={clsx(
                "font-mono font-semibold px-1.5 py-0.5 rounded",
                trend.isPositive && "text-emerald-400 bg-emerald-500/10",
                trend.isNegative && "text-red-400 bg-red-500/10",
                !trend.isPositive && !trend.isNegative && "text-slate-400"
              )}
            >
              {trend.value}
            </span>
          )}
        </div>
      )}
    </Card>
  );
};
