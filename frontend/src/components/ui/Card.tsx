import React from "react";
import { clsx } from "clsx";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glow?: boolean;
  glowColor?: "cyan" | "red" | "yellow" | "green";
  glass?: boolean;
  hoverEffect?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  glow = false,
  glowColor = "cyan",
  glass = true,
  hoverEffect = false,
  ...props
}) => {
  const glowStyles = {
    cyan: "border-cyan-500/30 shadow-[0_0_15px_rgba(0,240,255,0.15)]",
    red: "border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.15)]",
    yellow: "border-yellow-500/30 shadow-[0_0_15px_rgba(234,179,8,0.15)]",
    green: "border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.15)]",
  };

  return (
    <div
      className={clsx(
        "rounded-xl border border-slate-800/80 transition-all duration-200 overflow-hidden",
        glass ? "bg-slate-900/75 backdrop-blur-md" : "bg-slate-900",
        glow && glowStyles[glowColor],
        hoverEffect && "hover:border-slate-700 hover:shadow-lg hover:shadow-cyan-500/5 hover:-translate-y-0.5",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
