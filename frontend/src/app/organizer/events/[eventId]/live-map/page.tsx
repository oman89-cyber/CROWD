"use client";

import React, { useState, use } from "react";
import { OrganizerSidebar } from "@/components/layout/OrganizerSidebar";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { BottleneckAlert } from "@/components/organizer/BottleneckAlert";
import { VenueMap } from "@/components/venue/VenueMap";
import { useMockCrowdEngine } from "@/hooks/useMockCrowdEngine";
import { MOCK_VENUE } from "@/mock/venue";
import { MOCK_CAMERAS } from "@/mock/cameras";
import { generateInitialAgents } from "@/mock/crowd";
import { Activity, Camera, Layers, Eye, RefreshCw, ShieldAlert } from "lucide-react";

export default function LiveMapPage({ params }: { params: Promise<{ eventId: string }> }) {
  const { eventId } = use(params);

  const {
    zones,
    bottleneckAlert,
    reroutedCount,
    statusMessage,
    triggerBottleneckSequence,
    resetDemo,
  } = useMockCrowdEngine(true);

  const [showCrowd, setShowCrowd] = useState<boolean>(true);
  const [showCameras, setShowCameras] = useState<boolean>(true);

  const agents = generateInitialAgents(120);
  const currentVenue = { ...MOCK_VENUE, zones };

  return (
    <div className="min-h-screen flex bg-[#080b11]">
      <OrganizerSidebar eventId={eventId} />

      <main className="flex-1 p-6 space-y-6 max-w-[1600px] mx-auto flex flex-col justify-between">
        <div className="space-y-6">
          <PageHeader
            title="FULL-SCREEN COMMAND CENTER — LIVE CROWD GRAPH"
            subtitle="Anonymous Track ID Telemetry, Heatmaps & Hugging Face Automated Load Balancing"
            badge={<Badge risk="LOW" pulse font-mono>120 TRACKED AGENTS</Badge>}
            actions={
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant={showCrowd ? "cyan" : "secondary"}
                  onClick={() => setShowCrowd(!showCrowd)}
                  leftIcon={<Eye className="w-3.5 h-3.5" />}
                >
                  Agents Layer
                </Button>

                <Button
                  size="sm"
                  variant={showCameras ? "cyan" : "secondary"}
                  onClick={() => setShowCameras(!showCameras)}
                  leftIcon={<Camera className="w-3.5 h-3.5" />}
                >
                  Cameras Layer
                </Button>

                <Button
                  size="sm"
                  variant="outline"
                  onClick={triggerBottleneckSequence}
                  leftIcon={<RefreshCw className="w-3.5 h-3.5 text-cyan-400" />}
                >
                  Trigger Surge
                </Button>
              </div>
            }
          />

          {bottleneckAlert && (
            <BottleneckAlert
              prediction={bottleneckAlert}
              reroutedCount={reroutedCount}
              onTriggerReroute={triggerBottleneckSequence}
            />
          )}

          {/* Full Screen Interactive Venue Map */}
          <Card glow glowColor="cyan" className="p-4 relative">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-2">
              <div className="flex items-center gap-2 font-mono text-xs text-white">
                <Activity className="w-4 h-4 text-emerald-400 animate-pulse" />
                <span>RTSP VISION STREAM & ANONYMOUS TRACKING ACTIVE</span>
              </div>
              <span className="text-xs font-mono text-cyan-400">{statusMessage}</span>
            </div>

            <VenueMap
              venue={currentVenue}
              agents={agents}
              cameras={MOCK_CAMERAS}
              mode="organizer"
              showCrowdLayer={showCrowd}
              showCameras={showCameras}
            />
          </Card>
        </div>

        {/* Bottom Track ID Legend & Privacy Status Bar */}
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 font-mono text-xs flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4 text-slate-300">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" />
              <span>User Track (Alex Sharma CS-8A41F)</span>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-slate-400" />
              <span>Anonymous Track IDs (Track 17, 22, 41)</span>
            </span>
          </div>

          <div className="text-slate-400 text-[11px]">
            <span>Privacy Standard: </span>
            <strong className="text-emerald-400">Zero Facial Metadata Saved</strong>
          </div>
        </div>
      </main>
    </div>
  );
}
