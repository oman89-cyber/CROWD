"use client";

import React, { useState, use } from "react";
import { OrganizerSidebar } from "@/components/layout/OrganizerSidebar";
import { PageHeader } from "@/components/layout/PageHeader";
import { SimulationControls } from "@/components/organizer/SimulationControls";
import { VenueMap } from "@/components/venue/VenueMap";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { MOCK_VENUE } from "@/mock/venue";
import { generateInitialAgents } from "@/mock/crowd";

export default function SimulationPage({ params }: { params: Promise<{ eventId: string }> }) {
  const { eventId } = use(params);
  const [isRunning, setIsRunning] = useState<boolean>(true);

  const agents = generateInitialAgents(150);

  return (
    <div className="min-h-screen flex bg-[#080b11]">
      <OrganizerSidebar eventId={eventId} />

      <main className="flex-1 p-6 space-y-6 max-w-[1600px] mx-auto">
        <PageHeader
          title="Crowd Flow Simulation & Scenario Stress Testing"
          subtitle="Run agent-based spatial simulations to evaluate emergency egress times and gate closures."
          badge={<Badge risk="LOW">MONTE CARLO SIMULATOR</Badge>}
        />

        {/* Control Sliders */}
        <SimulationControls
          isRunning={isRunning}
          onStart={() => setIsRunning(true)}
          onPause={() => setIsRunning(false)}
          onReset={() => setIsRunning(false)}
        />

        {/* Live Simulation Interactive Map Canvas */}
        <Card glow glowColor="cyan" className="p-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-2 font-mono text-xs">
            <span className="text-white font-bold">MONTE CARLO SIMULATION CANVAS (150 PARTICLES)</span>
            <span className="text-cyan-400">FPS: 60 • SIMULATION TIME: 00:04:12</span>
          </div>

          <VenueMap
            venue={MOCK_VENUE}
            agents={agents}
            mode="simulation"
            showCrowdLayer={isRunning}
            showCameras={false}
          />
        </Card>
      </main>
    </div>
  );
}
