import React from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { UserRoute } from "@/types/route";
import { Navigation, Clock, ShieldCheck, ArrowRight, RefreshCw } from "lucide-react";

interface RouteCardProps {
  route: UserRoute;
  onStartNavigation?: () => void;
  onAcceptAlternative?: () => void;
}

export const RouteCard: React.FC<RouteCardProps> = ({
  route,
  onStartNavigation,
  onAcceptAlternative,
}) => {
  return (
    <Card glow={route.isAlternative} glowColor={route.isAlternative ? "green" : "cyan"} className="p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Navigation className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] font-mono font-semibold text-slate-400 uppercase tracking-widest block">
              {route.isAlternative ? "RECOMMENDED ALTERNATIVE ROUTE" : "RECOMMENDED ROUTE"}
            </span>
            <h4 className="text-base font-bold font-mono text-white">
              {route.sourceZone.toUpperCase()} → {route.destinationZone.toUpperCase()}
            </h4>
          </div>
        </div>
        <Badge risk={route.risk}>{route.risk} RISK</Badge>
      </div>

      {/* Route Path Steps */}
      <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 font-mono text-xs text-slate-300 flex items-center justify-between gap-1 overflow-x-auto">
        {route.path.map((zoneId, idx) => (
          <React.Fragment key={idx}>
            <span className={`px-2 py-1 rounded ${idx === 0 ? "bg-cyan-500/20 text-cyan-300 font-bold" : idx === route.path.length - 1 ? "bg-emerald-500/20 text-emerald-300 font-bold" : "bg-slate-800"}`}>
              {zoneId.toUpperCase()}
            </span>
            {idx < route.path.length - 1 && <ArrowRight className="w-3.5 h-3.5 text-slate-500 shrink-0" />}
          </React.Fragment>
        ))}
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-3 gap-3 text-center">
        <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
          <span className="text-[10px] font-mono text-slate-400 uppercase block">Distance</span>
          <span className="font-bold font-mono text-white text-sm">{route.distance} m</span>
        </div>
        <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
          <span className="text-[10px] font-mono text-slate-400 uppercase block">Est. Time</span>
          <span className="font-bold font-mono text-cyan-400 text-sm">~{route.estimatedTime} min</span>
        </div>
        <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
          <span className="text-[10px] font-mono text-slate-400 uppercase block">Safety Index</span>
          <span className="font-bold font-mono text-emerald-400 text-sm">98% Safe</span>
        </div>
      </div>

      {route.reason && (
        <p className="text-xs text-slate-400 italic bg-slate-900/40 p-2.5 rounded border border-slate-800/60">
          "{route.reason}"
        </p>
      )}

      <div className="pt-2 flex gap-3">
        {route.isAlternative && onAcceptAlternative ? (
          <Button variant="cyan" className="w-full" onClick={onAcceptAlternative} leftIcon={<RefreshCw className="w-4 h-4" />}>
            Follow New Safer Route
          </Button>
        ) : (
          <Button variant="cyan" className="w-full" onClick={onStartNavigation} rightIcon={<ArrowRight className="w-4 h-4" />}>
            Start Live Navigation
          </Button>
        )}
      </div>
    </Card>
  );
};
