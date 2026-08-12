import React from "react";
import { Gate } from "@/types/venue";

export const GateMarker: React.FC<{ gate: Gate }> = ({ gate }) => {
  return (
    <g transform={`translate(${gate.x}, ${gate.y - 20})`} className="pointer-events-none">
      <rect x={-25} y={-10} width={50} height={18} rx={4} fill="#0284c7" fillOpacity={0.8} stroke="#38bdf8" strokeWidth={1} />
      <text x={0} y={2} textAnchor="middle" fill="#ffffff" fontSize={9} fontFamily="monospace" fontWeight="bold">
        {gate.name}
      </text>
    </g>
  );
};
