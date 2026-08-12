"use client";

import React, { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Select } from "@/components/ui/Select";
import { Play, Pause, RotateCcw, Sliders, Zap } from "lucide-react";

interface SimulationControlsProps {
  onStart?: () => void;
  onPause?: () => void;
  onReset?: () => void;
  isRunning?: boolean;
}

export const SimulationControls: React.FC<SimulationControlsProps> = ({
  onStart,
  onPause,
  onReset,
  isRunning = false,
}) => {
  const [crowdSize, setCrowdSize] = useState<number>(4820);
  const [entryRate, setEntryRate] = useState<number>(25);
  const [scenario, setScenario] = useState<string>("normal");
  const [simSpeed, setSimSpeed] = useState<string>("1x");

  const scenarioOptions = [
    { value: "normal", label: "Normal Crowd Flow" },
    { value: "gate_a_closed", label: "Scenario: Gate A Closed" },
    { value: "gate_b_closed", label: "Scenario: Gate B Closed" },
    { value: "exit_a_closed", label: "Scenario: Exit A Closed" },
    { value: "event_ending", label: "Scenario: Event Ending (Mass Exit)" },
    { value: "emergency", label: "Scenario: Emergency Evacuation" },
  ];

  const speedOptions = [
    { value: "1x", label: "1x Speed (Realtime)" },
    { value: "2x", label: "2x Fast Forward" },
    { value: "5x", label: "5x Stress Test" },
  ];

  return (
    <Card className="p-5 space-y-5">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
            <Sliders className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold font-mono text-base text-white">Simulation Engine</h3>
            <p className="text-xs text-slate-400">Monte Carlo & Dynamic Agent Flow Parameters</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-xs font-mono text-emerald-400 font-bold uppercase">
            {isRunning ? "Running" : "Standby"}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Crowd Size */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-400 uppercase">Simulated Crowd</span>
            <span className="text-cyan-400 font-bold">{crowdSize.toLocaleString()}</span>
          </div>
          <input
            type="range"
            min={500}
            max={10000}
            step={250}
            value={crowdSize}
            onChange={(e) => setCrowdSize(Number(e.target.value))}
            className="w-full accent-cyan-400 bg-slate-800 rounded-lg cursor-pointer"
          />
        </div>

        {/* Entry Rate */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-400 uppercase">Entry Rate</span>
            <span className="text-cyan-400 font-bold">{entryRate} people/sec</span>
          </div>
          <input
            type="range"
            min={0}
            max={100}
            step={5}
            value={entryRate}
            onChange={(e) => setEntryRate(Number(e.target.value))}
            className="w-full accent-cyan-400 bg-slate-800 rounded-lg cursor-pointer"
          />
        </div>

        {/* Scenario Selection */}
        <Select
          label="Test Scenario"
          options={scenarioOptions}
          value={scenario}
          onChange={(e) => setScenario(e.target.value)}
        />

        {/* Sim Speed */}
        <Select
          label="Execution Speed"
          options={speedOptions}
          value={simSpeed}
          onChange={(e) => setSimSpeed(e.target.value)}
        />
      </div>

      {/* Control Buttons */}
      <div className="pt-2 flex items-center justify-end gap-3 border-t border-slate-800">
        <Button variant="secondary" onClick={onReset} leftIcon={<RotateCcw className="w-4 h-4" />}>
          RESET
        </Button>
        {isRunning ? (
          <Button variant="danger" onClick={onPause} leftIcon={<Pause className="w-4 h-4" />}>
            PAUSE SIMULATION
          </Button>
        ) : (
          <Button variant="cyan" onClick={onStart} leftIcon={<Play className="w-4 h-4" />}>
            START SIMULATION
          </Button>
        )}
      </div>
    </Card>
  );
};
