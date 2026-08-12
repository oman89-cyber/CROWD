"use client";

import React from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from "recharts";
import { MOCK_DENSITY_TRENDS } from "@/mock/predictions";

interface PredictionChartProps {
  data?: typeof MOCK_DENSITY_TRENDS;
  targetZone?: string;
  threshold?: number;
}

export const PredictionChart: React.FC<PredictionChartProps> = ({
  data = MOCK_DENSITY_TRENDS,
  targetZone = "Corridor C",
  threshold = 85,
}) => {
  return (
    <div className="w-full h-64 sm:h-72">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
          <XAxis
            dataKey="time"
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            fontFamily="monospace"
          />
          <YAxis
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            domain={[0, 100]}
            unit="%"
            fontFamily="monospace"
          />
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
          <ReferenceLine
            y={threshold}
            stroke="#ef4444"
            strokeDasharray="4 4"
            label={{ value: "CRITICAL THRESHOLD (85%)", fill: "#f87171", fontSize: 10, position: "top" }}
          />
          <Line
            type="monotone"
            dataKey={targetZone}
            stroke="#00f0ff"
            strokeWidth={3}
            dot={{ r: 4, fill: "#00f0ff" }}
            activeDot={{ r: 7, fill: "#00f0ff" }}
            name={`${targetZone} Density`}
          />
          <Line
            type="monotone"
            dataKey="Corridor B"
            stroke="#eab308"
            strokeWidth={2}
            strokeDasharray="3 3"
            dot={{ r: 3 }}
            name="Corridor B (Bypass)"
          />
          <Line
            type="monotone"
            dataKey="Main Stage"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            name="Main Stage"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
