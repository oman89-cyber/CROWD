"use client";

import React from "react";
import { VenueZone as TVenueZone } from "@/types/venue";

interface VenueZoneProps {
  zone: TVenueZone;
  isSelected?: boolean;
  isHighlighted?: boolean;
  onClick?: () => void;
  showDetails?: boolean;
}

export const VenueZone: React.FC<VenueZoneProps> = ({
  zone,
  isSelected = false,
  isHighlighted = false,
  onClick,
  showDetails = true,
}) => {
  const pointsString = zone.polygon.map((p) => `${p[0]},${p[1]}`).join(" ");

  // Compute centroid for label positioning
  const center = zone.center || [
    zone.polygon.reduce((acc, p) => acc + p[0], 0) / zone.polygon.length,
    zone.polygon.reduce((acc, p) => acc + p[1], 0) / zone.polygon.length,
  ];

  const densityPct = Math.round(zone.density * 100);

  // Dynamic colors based on risk/density
  let fillColor = "rgba(16, 185, 129, 0.15)";
  let strokeColor = "#10b981";
  let textColor = "#34d399";

  if (zone.risk === "CRITICAL" || densityPct >= 85) {
    fillColor = "rgba(239, 68, 68, 0.35)";
    strokeColor = "#ef4444";
    textColor = "#fca5a5";
  } else if (zone.risk === "HIGH" || densityPct >= 70) {
    fillColor = "rgba(249, 115, 22, 0.25)";
    strokeColor = "#f97316";
    textColor = "#fdba74";
  } else if (zone.risk === "MEDIUM" || densityPct >= 50) {
    fillColor = "rgba(234, 179, 8, 0.20)";
    strokeColor = "#eab308";
    textColor = "#fde047";
  }

  if (isSelected) {
    strokeColor = "#00f0ff";
  }

  return (
    <g className="cursor-pointer group transition-all duration-300" onClick={onClick}>
      {/* Zone Polygon */}
      <polygon
        points={pointsString}
        fill={fillColor}
        stroke={strokeColor}
        strokeWidth={isSelected ? 3 : isHighlighted ? 2.5 : 1.5}
        strokeDasharray={zone.risk === "CRITICAL" ? "4 2" : "none"}
        className={`transition-all duration-300 group-hover:fill-opacity-50 ${
          zone.risk === "CRITICAL" ? "animate-pulse" : ""
        }`}
      />

      {/* Center Label Box */}
      {showDetails && (
        <foreignObject
          x={center[0] - 55}
          y={center[1] - 22}
          width={110}
          height={44}
          className="pointer-events-none"
        >
          <div className="flex flex-col items-center justify-center h-full text-center">
            <span className="font-mono text-[11px] font-bold text-white tracking-wider uppercase drop-shadow">
              {zone.name}
            </span>
            <div className="flex items-center gap-1 mt-0.5">
              <span className="font-mono text-[10px] text-slate-300">
                {zone.occupancy}/{zone.capacity}
              </span>
              <span
                className="font-mono text-[10px] font-bold px-1 rounded"
                style={{ color: textColor, backgroundColor: "rgba(0,0,0,0.5)" }}
              >
                {densityPct}%
              </span>
            </div>
          </div>
        </foreignObject>
      )}
    </g>
  );
};
