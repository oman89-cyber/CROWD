"use client";

import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

const MOCK_FLOW_DATA = [
  { time: "10:00", gateA: 45, gateB: 62, gateC: 38 },
  { time: "10:15", gateA: 52, gateB: 78, gateC: 42 },
  { time: "10:30", gateA: 68, gateB: 95, gateC: 58 },
  { time: "10:45", gateA: 84, gateB: 110, gateC: 89 },
  { time: "11:00", gateA: 70, gateB: 88, gateC: 92 },
  { time: "11:15", gateA: 55, gateB: 65, gateC: 60 },
];

export const FlowChart: React.FC = () => {
  return (
    <div className="w-full h-52">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={MOCK_FLOW_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <XAxis dataKey="time" stroke="#64748b" fontSize={10} fontFamily="monospace" />
          <YAxis stroke="#64748b" fontSize={10} fontFamily="monospace" />
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
          <Area type="monotone" dataKey="gateA" stackId="1" stroke="#00f0ff" fill="#00f0ff33" name="Gate A Flow" />
          <Area type="monotone" dataKey="gateB" stackId="1" stroke="#eab308" fill="#eab30833" name="Gate B Flow" />
          <Area type="monotone" dataKey="gateC" stackId="1" stroke="#10b981" fill="#10b98133" name="Gate C Flow" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
