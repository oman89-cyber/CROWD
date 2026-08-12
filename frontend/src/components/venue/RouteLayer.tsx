"use client";

import React from "react";
import { UserRoute } from "@/types/route";

interface RouteLayerProps {
  route: UserRoute;
  isAlternative?: boolean;
}

export const RouteLayer: React.FC<RouteLayerProps> = ({ route, isAlternative = false }) => {
  if (!route.points || route.points.length < 2) return null;

  // Format SVG path string d="M x1 y1 L x2 y2 L x3 y3"
  const d = route.points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
    .join(" ");

  const strokeColor = isAlternative ? "#10b981" : "#00f0ff";
  const glowColor = isAlternative ? "rgba(16, 185, 129, 0.4)" : "rgba(0, 240, 255, 0.4)";

  return (
    <g className="pointer-events-none">
      {/* Outer Glow Path */}
      <path
        d={d}
        fill="none"
        stroke={glowColor}
        strokeWidth={10}
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Main Path Line */}
      <path
        d={d}
        fill="none"
        stroke={strokeColor}
        strokeWidth={4}
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray="8 6"
        className="animate-[dash_1.5s_linear_infinite]"
      />

      {/* Route Direction Waypoints */}
      {route.points.map((pt, idx) => (
        <g key={idx} transform={`translate(${pt.x}, ${pt.y})`}>
          <circle r={6} fill={strokeColor} stroke="#080b11" strokeWidth={2} />
          {idx === 0 && (
            <text y={-12} textAnchor="middle" fill="#00f0ff" fontSize={10} fontFamily="monospace" fontWeight="bold">
              START
            </text>
          )}
          {idx === route.points.length - 1 && (
            <text y={-12} textAnchor="middle" fill="#10b981" fontSize={10} fontFamily="monospace" fontWeight="bold">
              DESTINATION
            </text>
          )}
        </g>
      ))}
    </g>
  );
};
