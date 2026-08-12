import React from "react";
import { clsx } from "clsx";
import { RiskLevel } from "@/types/venue";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  risk?: RiskLevel;
  variant?: "low" | "medium" | "high" | "critical" | "cyan" | "outline" | "slate";
  pulse?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  risk,
  variant,
  pulse = false,
  className,
  ...props
}) => {
  const effectiveVariant = risk ? risk.toLowerCase() : variant || "cyan";

  const variantStyles = {
    low: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
    medium: "bg-amber-500/10 text-amber-400 border-amber-500/30",
    high: "bg-orange-500/10 text-orange-400 border-orange-500/30",
    critical: "bg-red-500/15 text-red-400 border-red-500/40 font-bold",
    cyan: "bg-cyan-500/10 text-cyan-300 border-cyan-500/30",
    outline: "bg-transparent text-slate-300 border-slate-700",
    slate: "bg-slate-800 text-slate-300 border-slate-700",
  };

  const dotColor = {
    low: "bg-emerald-400",
    medium: "bg-amber-400",
    high: "bg-orange-400",
    critical: "bg-red-400",
    cyan: "bg-cyan-400",
    outline: "bg-slate-400",
    slate: "bg-slate-400",
  };

  const currentVariant = effectiveVariant as keyof typeof variantStyles;

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono border backdrop-blur-sm",
        variantStyles[currentVariant] || variantStyles.cyan,
        className
      )}
      {...props}
    >
      <span
        className={clsx(
          "w-1.5 h-1.5 rounded-full shrink-0",
          dotColor[currentVariant] || "bg-cyan-400",
          pulse && "animate-ping"
        )}
      />
      {children}
    </span>
  );
};
