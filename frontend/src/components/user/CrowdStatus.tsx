import React from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { VenueZone } from "@/types/venue";
import { AlertTriangle, ShieldCheck } from "lucide-react";

interface CrowdStatusProps {
  zone: VenueZone;
  isCongested?: boolean;
}

export const CrowdStatus: React.FC<CrowdStatusProps> = ({ zone, isCongested = false }) => {
  const densityPct = Math.round(zone.density * 100);

  return (
    <Card
      glow={isCongested}
      glowColor={isCongested ? "red" : "cyan"}
      className="p-5 space-y-4"
    >
      <div className="flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono font-semibold text-slate-400 uppercase tracking-widest block">
            Current Location
          </span>
          <h3 className="text-xl font-bold font-mono text-white tracking-tight">{zone.name}</h3>
        </div>
        <Badge risk={zone.risk} pulse={isCongested}>
          {zone.risk} DENSITY
        </Badge>
      </div>

      <div className="space-y-2">
        <ProgressBar value={densityPct} label="Zone Occupancy Rate" risk={zone.risk} size="md" />
        <div className="flex justify-between text-xs font-mono text-slate-400">
          <span>Capacity: {zone.capacity}</span>
          <span>Occupancy: {zone.occupancy}</span>
        </div>
      </div>

      {isCongested ? (
        <div className="p-3 rounded-lg bg-red-950/40 border border-red-500/40 flex items-start gap-2 text-xs text-red-200">
          <AlertTriangle className="w-4 h-4 shrink-0 text-red-400 mt-0.5" />
          <span>Your current route is experiencing increased congestion. Alternative route available.</span>
        </div>
      ) : (
        <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-500/30 flex items-start gap-2 text-xs text-emerald-200">
          <ShieldCheck className="w-4 h-4 shrink-0 text-emerald-400 mt-0.5" />
          <span>Zone flow is steady. Safe to proceed towards destination.</span>
        </div>
      )}
    </Card>
  );
};
