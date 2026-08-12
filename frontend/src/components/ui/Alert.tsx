import React from "react";
import { AlertTriangle, Info, CheckCircle2, XCircle, X } from "lucide-react";
import { clsx } from "clsx";
import { RiskLevel } from "@/types/venue";

interface AlertProps {
  title?: string;
  children: React.ReactNode;
  variant?: "info" | "warning" | "error" | "success" | RiskLevel;
  onClose?: () => void;
  action?: React.ReactNode;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  title,
  children,
  variant = "info",
  onClose,
  action,
  className,
}) => {
  const normVariant = variant.toLowerCase();

  const variantStyles = {
    info: "bg-cyan-950/40 border-cyan-500/40 text-cyan-200 icon-cyan",
    low: "bg-emerald-950/40 border-emerald-500/40 text-emerald-200 icon-emerald",
    success: "bg-emerald-950/40 border-emerald-500/40 text-emerald-200 icon-emerald",
    medium: "bg-amber-950/40 border-amber-500/40 text-amber-200 icon-amber",
    warning: "bg-amber-950/40 border-amber-500/40 text-amber-200 icon-amber",
    high: "bg-orange-950/40 border-orange-500/40 text-orange-200 icon-orange",
    critical: "bg-red-950/50 border-red-500/50 text-red-200 icon-red animate-pulse-slow",
    error: "bg-red-950/50 border-red-500/50 text-red-200 icon-red",
  };

  const getIcon = () => {
    switch (normVariant) {
      case "critical":
      case "high":
      case "warning":
      case "medium":
      case "error":
        return <AlertTriangle className="w-5 h-5 shrink-0 text-amber-400" />;
      case "success":
      case "low":
        return <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-400" />;
      default:
        return <Info className="w-5 h-5 shrink-0 text-cyan-400" />;
    }
  };

  const currentStyle = variantStyles[normVariant as keyof typeof variantStyles] || variantStyles.info;

  return (
    <div
      className={clsx(
        "flex items-start justify-between gap-3 p-4 rounded-xl border backdrop-blur-md transition-all",
        currentStyle,
        className
      )}
    >
      <div className="flex items-start gap-3">
        {getIcon()}
        <div className="space-y-1">
          {title && <h5 className="font-semibold text-sm tracking-wide">{title}</h5>}
          <div className="text-xs leading-relaxed opacity-90">{children}</div>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {action}
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 rounded bg-black/20 hover:bg-black/40 text-current transition"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
