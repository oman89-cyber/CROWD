"use client";

import React from "react";
import Link from "next/link";
import { OrganizerSidebar } from "@/components/layout/OrganizerSidebar";
import { PageHeader } from "@/components/layout/PageHeader";
import { CrowdOverview } from "@/components/organizer/CrowdOverview";
import { BottleneckAlert } from "@/components/organizer/BottleneckAlert";
import { VenueMap } from "@/components/venue/VenueMap";
import { DensityChart } from "@/components/charts/DensityChart";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useMockCrowdEngine } from "@/hooks/useMockCrowdEngine";
import { MOCK_VENUE } from "@/mock/venue";
import { generateInitialAgents } from "@/mock/crowd";
import { Activity, ShieldAlert, RefreshCw, Layers, ArrowRight } from "lucide-react";

export default function OrganizerDashboardPage() {
  const {
    zones,
    bottleneckAlert,
    isRerouted,
    reroutedCount,
    statusMessage,
    triggerBottleneckSequence,
    resetDemo,
  } = useMockCrowdEngine(true);

  const agents = generateInitialAgents(110);
  const currentVenue = { ...MOCK_VENUE, zones };

  return (
    <div className="min-h-screen flex bg-[#080b11]">
      <OrganizerSidebar eventId="event-tf2026" />

      <main className="flex-1 p-6 space-y-6 overflow-y-auto max-w-[1600px] mx-auto">
        <PageHeader
          title="COMMAND CENTER — TECHFEST 2026"
          subtitle="Real-Time Venue Density, Edge Vision Telemetry & Automated Crowd Flow Optimization"
          badge={<Badge risk="LOW" pulse>LIVE OPERATIONAL</Badge>}
          actions={
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={triggerBottleneckSequence}
                leftIcon={<RefreshCw className="w-3.5 h-3.5 text-cyan-400" />}
              >
                Trigger Demo Surge
              </Button>

              <Link href="/organizer/events/event-tf2026/live-map">
                <Button size="sm" variant="cyan" rightIcon={<ArrowRight className="w-4 h-4" />}>
                  Full Screen Live Map
                </Button>
              </Link>
            </div>
          }
        />

        {/* Top 5 Metrics Overview Bar */}
        <CrowdOverview
          totalPeople={4820}
          activeUsers={482}
          avgDensity={64}
          criticalZonesCount={zones.filter((z) => z.risk === "CRITICAL").length}
          predictedBottlenecks={bottleneckAlert ? 1 : 0}
        />

        {/* Live Bottleneck Alert Banner */}
        {bottleneckAlert && (
          <BottleneckAlert
            prediction={bottleneckAlert}
            reroutedCount={reroutedCount}
            onTriggerReroute={triggerBottleneckSequence}
          />
        )}

        {/* Center Grid: Main Live Map & Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main Map Canvas */}
          <div className="lg:col-span-8 space-y-4">
            <Card glow glowColor="cyan" className="p-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-2">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
                  <h3 className="font-bold font-mono text-sm text-white">LIVE VENUE CROWD GRAPH</h3>
                </div>
                <span className="text-xs font-mono text-cyan-400">{statusMessage}</span>
              </div>

              <VenueMap
                venue={currentVenue}
                agents={agents}
                mode="organizer"
                showCrowdLayer={true}
                showCameras={true}
              />
            </Card>
          </div>

          {/* Right Sidebar: Density Chart & Quick Actions */}
          <div className="lg:col-span-4 space-y-6">
            <Card className="p-5 space-y-4 border-slate-800">
              <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                <h4 className="font-bold font-mono text-sm text-white">Zone Density Breakdown</h4>
                <Badge risk="LOW">14 ZONES</Badge>
              </div>
              <DensityChart zones={zones} />
            </Card>

            <Card className="p-5 space-y-4 border-slate-800 font-mono text-xs">
              <h4 className="font-bold text-sm text-white border-b border-slate-800 pb-2 uppercase">
                OPS Quick Controls
              </h4>
              <div className="space-y-2">
                <Link href="/organizer/events/event-tf2026/prediction" className="block">
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition flex items-center justify-between text-slate-300">
                    <span>Hugging Face AI Forecast</span>
                    <ArrowRight className="w-4 h-4 text-cyan-400" />
                  </div>
                </Link>
                <Link href="/organizer/events/event-tf2026/simulation" className="block">
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition flex items-center justify-between text-slate-300">
                    <span>Crowd Flow Simulation</span>
                    <ArrowRight className="w-4 h-4 text-cyan-400" />
                  </div>
                </Link>
                <Link href="/organizer/events/event-tf2026/cameras" className="block">
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition flex items-center justify-between text-slate-300">
                    <span>CCTV Camera Vision</span>
                    <ArrowRight className="w-4 h-4 text-cyan-400" />
                  </div>
                </Link>
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
