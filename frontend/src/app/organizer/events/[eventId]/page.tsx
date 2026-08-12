"use client";

import React, { use } from "react";
import Link from "next/link";
import { OrganizerSidebar } from "@/components/layout/OrganizerSidebar";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { MOCK_EVENT } from "@/mock/events";
import { Upload, Edit3, Camera, Ticket, Activity, Sliders, ArrowRight } from "lucide-react";

export default function EventDetailPage({ params }: { params: Promise<{ eventId: string }> }) {
  const { eventId } = use(params);

  return (
    <div className="min-h-screen flex bg-[#080b11]">
      <OrganizerSidebar eventId={eventId} />

      <main className="flex-1 p-6 max-w-5xl mx-auto space-y-6">
        <PageHeader
          title={`Event Management: ${MOCK_EVENT.name}`}
          subtitle={`ID: ${eventId} • Venue: ${MOCK_EVENT.venueName} • Expected: ${MOCK_EVENT.expectedCrowd}`}
          badge={<Badge risk="LOW">LIVE STATUS</Badge>}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="p-5 space-y-4 border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                <Upload className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold font-mono text-base text-white">1. Blueprint Upload</h3>
                <p className="text-xs text-slate-400">Upload PNG/JPG/SVG architectural floorplan</p>
              </div>
            </div>
            <Link href={`/organizer/events/${eventId}/blueprint`}>
              <Button variant="outline" className="w-full" rightIcon={<ArrowRight className="w-4 h-4" />}>
                Open Blueprint Manager
              </Button>
            </Link>
          </Card>

          <Card className="p-5 space-y-4 border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/30">
                <Edit3 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold font-mono text-base text-white">2. Venue Graph Editor</h3>
                <p className="text-xs text-slate-400">Define polygon zones, paths, gates & exits</p>
              </div>
            </div>
            <Link href={`/organizer/events/${eventId}/venue-editor`}>
              <Button variant="outline" className="w-full" rightIcon={<ArrowRight className="w-4 h-4" />}>
                Open Spatial Graph Editor
              </Button>
            </Link>
          </Card>

          <Card className="p-5 space-y-4 border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/30">
                <Camera className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold font-mono text-base text-white">3. Camera Vision Feeds</h3>
                <p className="text-xs text-slate-400">Register RTSP CCTV feeds for object detection</p>
              </div>
            </div>
            <Link href={`/organizer/events/${eventId}/cameras`}>
              <Button variant="outline" className="w-full" rightIcon={<ArrowRight className="w-4 h-4" />}>
                Manage Camera Feeds
              </Button>
            </Link>
          </Card>

          <Card className="p-5 space-y-4 border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                <Activity className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold font-mono text-base text-white">4. Live Command Map</h3>
                <p className="text-xs text-slate-400">Real-time crowd telemetry and bottleneck control</p>
              </div>
            </div>
            <Link href={`/organizer/events/${eventId}/live-map`}>
              <Button variant="cyan" className="w-full" rightIcon={<ArrowRight className="w-4 h-4" />}>
                Launch Live Command Center
              </Button>
            </Link>
          </Card>
        </div>
      </main>
    </div>
  );
}
