"use client";

import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";
import { VenueZone } from "@/types/venue";

interface DensityChartProps {
  zones: VenueZone[];
}

export const DensityChart: React.FC<DensityChartProps> = ({ zones }) => {
  const chartData = zones.map((z) => ({
    name: z.name,
    density: Math.round(z.density * 100),
    risk: z.risk,
  }));

  const getColor = (density: number) => {
    if (density >= 85) return "#ef4444";
    if (density >= 70) return "#f97316";
    if (density >= 50) return "#eab308";
    return "#10b981";
  };

  return (
    <div className="w-full h-56">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
          <XAxis
            dataKey="name"
            stroke="#64748b"
            fontSize={10}
            angle={-30}
            textAnchor="end"
            interval={0}
            fontFamily="monospace"
          />
          <YAxis stroke="#64748b" fontSize={10} unit="%" domain={[0, 100]} fontFamily="monospace" />
          <Tooltip
            contentStyle={{
              backgroundColor: "rgba(15, 23, 42, 0.95)",
              borderColor: "#334155",
              borderRadius: "8px",
              fontSize: "12px",
              fontFamily: "monospace",
              color: "#fff",
            }}
          />
          <Bar dataKey="density" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.density)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
