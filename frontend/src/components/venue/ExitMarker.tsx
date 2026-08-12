import React from "react";
import { Exit } from "@/types/venue";

export const ExitMarker: React.FC<{ exit: Exit }> = ({ exit }) => {
  const isEmergency = exit.isEmergencyOnly;
  return (
    <g transform={`translate(${exit.x}, ${exit.y})`} className="pointer-events-none">
      <rect
        x={-35}
        y={-10}
        width={70}
        height={18}
        rx={4}
        fill={isEmergency ? "rgba(239, 68, 68, 0.85)" : "rgba(16, 185, 129, 0.85)"}
        stroke={isEmergency ? "#f87171" : "#34d399"}
        strokeWidth={1}
      />
      <text x={0} y={2} textAnchor="middle" fill="#ffffff" fontSize={9} fontFamily="monospace" fontWeight="bold">
        {exit.name}
      </text>
    </g>
  );
};
