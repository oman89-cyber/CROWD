"use client";

import React, { useEffect, useState } from "react";
import { RoutePoint } from "@/types/route";

interface UserMarkerProps {
  points: RoutePoint[];
  isNavigating?: boolean;
}

export const UserMarker: React.FC<UserMarkerProps> = ({ points, isNavigating = true }) => {
  const [currentPos, setCurrentPos] = useState<{ x: number; y: number }>({
    x: points[0]?.x || 685,
    y: points[0]?.y || 235,
  });

  useEffect(() => {
    if (!points || points.length < 2 || !isNavigating) return;

    let segmentIndex = 0;
    let progress = 0;
    const speed = 0.008; // Smooth motion speed

    const interval = setInterval(() => {
      progress += speed;
      if (progress >= 1) {
        progress = 0;
        segmentIndex = (segmentIndex + 1) % (points.length - 1);
      }

      const p1 = points[segmentIndex];
      const p2 = points[segmentIndex + 1];

      if (p1 && p2) {
        const x = p1.x + (p2.x - p1.x) * progress;
        const y = p1.y + (p2.y - p1.y) * progress;
        setCurrentPos({ x, y });
      }
    }, 30);

    return () => clearInterval(interval);
  }, [points, isNavigating]);

  return (
    <g transform={`translate(${currentPos.x}, ${currentPos.y})`} className="pointer-events-none z-30">
      {/* Outer Pulse Ring */}
      <circle r={14} fill="rgba(0, 240, 255, 0.2)" className="animate-ping" />
      <circle r={9} fill="rgba(0, 240, 255, 0.4)" />
      {/* Core Glowing Dot */}
      <circle r={5} fill="#00f0ff" stroke="#ffffff" strokeWidth={1.5} />
      {/* Label Badge */}
      <g transform="translate(0, -16)">
        <rect x={-28} y={-10} width={56} height={14} rx={3} fill="rgba(8, 11, 17, 0.9)" stroke="#00f0ff" strokeWidth={0.8} />
        <text x={0} y={-1} textAnchor="middle" fill="#00f0ff" fontSize={8} fontFamily="monospace" fontWeight="bold">
          CS-8A41F
        </text>
      </g>
    </g>
  );
};
