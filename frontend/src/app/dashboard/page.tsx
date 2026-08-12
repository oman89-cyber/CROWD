"use client";

import React from "react";
import Link from "next/link";
import { UserNavbar } from "@/components/layout/UserNavbar";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { CrowdStatus } from "@/components/user/CrowdStatus";
import { RouteCard } from "@/components/user/RouteCard";
import { VenueMap } from "@/components/venue/VenueMap";
import { useMockCrowdEngine } from "@/hooks/useMockCrowdEngine";
import { DEMO_USER } from "@/mock/users";
import { MOCK_VENUE } from "@/mock/venue";
import { generateInitialAgents } from "@/mock/crowd";
import {
  Navigation,
  MapPin,
  Bell,
  Calendar,
  Shield,
  ArrowRight,
  RefreshCw,
  AlertTriangle,
} from "lucide-react";

export default function UserDashboardPage() {
  const {
    zones,
    userRoute,
    bottleneckAlert,
    isRerouted,
    triggerBottleneckSequence,
    resetDemo,
  } = useMockCrowdEngine(true);

  const agents = generateInitialAgents(60);
  const currentZone = zones.find((z) => z.id === DEMO_USER.currentZoneId) || zones[5];
  const isCongested = currentZone.density >= 0.75 || !!bottleneckAlert;

  const currentVenue = { ...MOCK_VENUE, zones };

  return (
    <div className="min-h-screen flex flex-col bg-[#080b11]">
      <UserNavbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Welcome Header */}
        <PageHeader
          title={`Welcome back, ${DEMO_USER.name}`}
          subtitle={`Event: TechFest 2026 • Crowd ID: ${DEMO_USER.crowdId} • Assigned Gate: ${DEMO_USER.gateAssigned}`}
          badge={<Badge risk={currentZone.risk}>CROWD LEVEL: {currentZone.risk}</Badge>}
          actions={
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={triggerBottleneckSequence}
                leftIcon={<RefreshCw className="w-3.5 h-3.5 text-cyan-400" />}
              >
                Simulate Crowd Surge
              </Button>
              <Link href="/navigation">
                <Button size="sm" variant="cyan" rightIcon={<ArrowRight className="w-4 h-4" />}>
                  Live Navigation
                </Button>
              </Link>
            </div>
          }
        />

        {/* Dynamic Bottleneck Warning Banner */}
        {isCongested && (
          <div className="p-4 rounded-xl bg-red-950/50 border border-red-500/50 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-pulse-slow">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
              <div>
                <h4 className="font-bold font-mono text-sm text-red-200">
                  Corridor C Congestion Warning (84% Density)
                </h4>
                <p className="text-xs text-slate-300">
                  Your current route is experiencing increased density. An optimized safer route via Corridor B is available.
                </p>
              </div>
            </div>

            <Link href="/navigation">
              <Button size="sm" variant="cyan" className="shrink-0">
                View & Accept Reroute
              </Button>
            </Link>
          </div>
        )}

        {/* Quick Action Navigation Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link href="/navigation">
            <Card hoverEffect className="p-4 flex flex-col items-center text-center space-y-2 border-slate-800 group">
              <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 group-hover:scale-110 transition">
                <Navigation className="w-6 h-6" />
              </div>
              <h4 className="font-bold font-mono text-sm text-white">Navigate</h4>
              <p className="text-[11px] text-slate-400 font-sans">Live turn-by-turn guidance</p>
            </Card>
          </Link>

          <Link href="/destination">
            <Card hoverEffect className="p-4 flex flex-col items-center text-center space-y-2 border-slate-800 group">
              <div className="p-3 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/30 group-hover:scale-110 transition">
                <MapPin className="w-6 h-6" />
              </div>
              <h4 className="font-bold font-mono text-sm text-white">Change Destination</h4>
              <p className="text-[11px] text-slate-400 font-sans">Select stages & exits</p>
            </Card>
          </Link>

          <Link href="/notifications">
            <Card hoverEffect className="p-4 flex flex-col items-center text-center space-y-2 border-slate-800 group">
              <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/30 group-hover:scale-110 transition">
                <Bell className="w-6 h-6" />
              </div>
              <h4 className="font-bold font-mono text-sm text-white">Notifications</h4>
              <p className="text-[11px] text-slate-400 font-sans">Route updates & announcements</p>
            </Card>
          </Link>

          <Link href="/event">
            <Card hoverEffect className="p-4 flex flex-col items-center text-center space-y-2 border-slate-800 group">
              <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 group-hover:scale-110 transition">
                <Calendar className="w-6 h-6" />
              </div>
              <h4 className="font-bold font-mono text-sm text-white">Event Info</h4>
              <p className="text-[11px] text-slate-400 font-sans">Schedule, stages & help</p>
            </Card>
          </Link>
        </div>

        {/* Dashboard Grid: Live Map & Status Details */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Main Map View */}
          <div className="lg:col-span-8 space-y-4">
            <Card glow glowColor="cyan" className="p-4">
              <div className="flex items-center justify-between pb-3 mb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
                  <h3 className="font-bold font-mono text-sm text-white">VENUE MAP — LIVE USER TELEMETRY</h3>
                </div>
                <Badge risk="LOW">CS-8A41F (Corridor C)</Badge>
              </div>

              <VenueMap
                venue={currentVenue}
                agents={agents}
                userRoute={userRoute}
                selectedZoneId={currentZone.id}
                mode="user"
                showCrowdLayer={true}
                showCameras={false}
              />
            </Card>
          </div>

          {/* Right Sidebar: Crowd Status & Recommended Route */}
          <div className="lg:col-span-4 space-y-6">
            <CrowdStatus zone={currentZone} isCongested={isCongested} />
            <RouteCard route={userRoute} />
          </div>
        </div>
      </main>
    </div>
  );
}
