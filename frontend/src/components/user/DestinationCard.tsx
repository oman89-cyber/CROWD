import React from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { MapPin, Navigation, Clock } from "lucide-react";
import { RiskLevel } from "@/types/venue";

interface DestinationCardProps {
  id: string;
  name: string;
  subtitle: string;
  distance: string;
  time: string;
  risk: RiskLevel;
  isSelected?: boolean;
  onSelect: (id: string) => void;
}

export const DestinationCard: React.FC<DestinationCardProps> = ({
  id,
  name,
  subtitle,
  distance,
  time,
  risk,
  isSelected = false,
  onSelect,
}) => {
  return (
    <Card
      glow={isSelected}
      glowColor="cyan"
      className="p-4 cursor-pointer hover:border-slate-700 transition space-y-3"
      onClick={() => onSelect(id)}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-slate-800 text-cyan-400 border border-slate-700">
            <MapPin className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-base text-white font-mono">{name}</h4>
            <p className="text-xs text-slate-400">{subtitle}</p>
          </div>
        </div>
        <Badge risk={risk}>{risk}</Badge>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs font-mono">
        <div className="flex items-center gap-4 text-slate-400">
          <span className="flex items-center gap-1">
            <Navigation className="w-3.5 h-3.5 text-cyan-400" />
            {distance}
          </span>
          <span className="flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            {time}
          </span>
        </div>

        <Button size="sm" variant={isSelected ? "cyan" : "outline"}>
          {isSelected ? "Selected" : "Select"}
        </Button>
      </div>
    </Card>
  );
};
