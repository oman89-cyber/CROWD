"use client";

import React from "react";
import Link from "next/link";
import { UserNavbar } from "@/components/layout/UserNavbar";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { VenueMap } from "@/components/venue/VenueMap";
import { MOCK_VENUE } from "@/mock/venue";
import { generateInitialAgents } from "@/mock/crowd";
import {
  Shield,
  Zap,
  TrendingUp,
  Navigation,
  Lock,
  ArrowRight,
  Activity,
  Cpu,
  Layers,
  Sparkles,
} from "lucide-react";

export default function LandingPage() {
  const agents = generateInitialAgents(80);

  return (
    <div className="min-h-screen flex flex-col bg-[#080b11]">
      <UserNavbar />

      {/* Hero Section */}
      <main className="flex-1">
        <section className="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28 border-b border-slate-800/80">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-cyan-500/10 blur-[120px] rounded-full pointer-events-none" />

          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
              {/* Hero Left Content */}
              <div className="lg:col-span-6 space-y-6 text-center lg:text-left">
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-mono">
                  <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                  <span>NEXT-GEN CROWD INTELLIGENCE ENGINE</span>
                </div>

                <div className="space-y-3">
                  <h1 className="text-4xl sm:text-6xl font-extrabold font-mono tracking-tight text-white leading-tight">
                    CROWD <span className="text-cyan-400">SENSE</span>
                  </h1>
                  <p className="text-xl sm:text-2xl font-semibold font-mono text-cyan-300">
                    "See the crowd. Predict the flow. Move smarter."
                  </p>
                </div>

                <p className="text-slate-400 text-base sm:text-lg max-w-xl font-sans leading-relaxed">
                  Real-time crowd intelligence, Hugging Face AI bottleneck prediction, and personalized safety rerouting for stadium and expo operations.
                </p>

                <div className="pt-2 flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
                  <Link href="/verify-ticket" className="w-full sm:w-auto">
                    <Button variant="cyan" size="lg" className="w-full" rightIcon={<ArrowRight className="w-5 h-5" />}>
                      Explore Event (Attendee)
                    </Button>
                  </Link>

                  <Link href="/organizer" className="w-full sm:w-auto">
                    <Button variant="secondary" size="lg" className="w-full" leftIcon={<Shield className="w-5 h-5 text-cyan-400" />}>
                      Organizer Portal
                    </Button>
                  </Link>
                </div>

                {/* Integration Badges */}
                <div className="pt-4 flex items-center justify-center lg:justify-start gap-6 text-xs font-mono text-slate-400">
                  <div className="flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-cyan-400" />
                    <span>Hugging Face AI</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-emerald-400" />
                    <span>FastAPI WebSocket</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-amber-400" />
                    <span>Graph Rerouting</span>
                  </div>
                </div>
              </div>

              {/* Hero Right Interactive Venue Preview */}
              <div className="lg:col-span-6 relative">
                <Card glow glowColor="cyan" className="p-3 shadow-2xl">
                  <div className="flex items-center justify-between px-3 py-2 border-b border-slate-800 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
                      <span className="text-xs font-mono text-white font-bold">TECHFEST 2026 LIVE MAP</span>
                    </div>
                    <Badge risk="LOW">4,820 ATTENDEES</Badge>
                  </div>

                  <VenueMap
                    venue={MOCK_VENUE}
                    agents={agents}
                    mode="user"
                    showCameras={false}
                    showCrowdLayer={true}
                  />
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Cards Grid Section */}
        <section className="py-16 bg-slate-950/40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
            <div className="text-center max-w-2xl mx-auto space-y-3">
              <span className="text-xs font-mono text-cyan-400 uppercase tracking-widest font-bold">
                SYSTEM CAPABILITIES
              </span>
              <h2 className="text-3xl font-bold font-mono text-white">End-to-End Crowd Telemetry</h2>
              <p className="text-sm text-slate-400 font-sans">
                Connecting optical sensors, ticket registries, and edge ML models into a unified attendee guidance pipeline.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card hoverEffect className="p-6 space-y-3 border-slate-800">
                <div className="p-3 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 w-fit">
                  <Activity className="w-6 h-6" />
                </div>
                <h3 className="font-bold font-mono text-lg text-white">Real-Time Intelligence</h3>
                <p className="text-xs text-slate-400 leading-relaxed font-sans">
                  Sub-second density heatmaps computed from camera feeds and anonymous track IDs.
                </p>
              </Card>

              <Card hoverEffect className="p-6 space-y-3 border-slate-800">
                <div className="p-3 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/30 w-fit">
                  <TrendingUp className="w-6 h-6" />
                </div>
                <h3 className="font-bold font-mono text-lg text-white">Predictive Congestion</h3>
                <p className="text-xs text-slate-400 leading-relaxed font-sans">
                  Hugging Face models forecast bottleneck formation up to 90 seconds before critical thresholds.
                </p>
              </Card>

              <Card hoverEffect className="p-6 space-y-3 border-slate-800">
                <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 w-fit">
                  <Navigation className="w-6 h-6" />
                </div>
                <h3 className="font-bold font-mono text-lg text-white">Personalized Routing</h3>
                <p className="text-xs text-slate-400 leading-relaxed font-sans">
                  Dynamic indoor pathfinding automatically guides users away from congested corridors.
                </p>
              </Card>

              <Card hoverEffect className="p-6 space-y-3 border-slate-800">
                <div className="p-3 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/30 w-fit">
                  <Lock className="w-6 h-6" />
                </div>
                <h3 className="font-bold font-mono text-lg text-white">Safer Event Navigation</h3>
                <p className="text-xs text-slate-400 leading-relaxed font-sans">
                  Automated crowd load balancing prevents dangerous crushes during peak ingress/egress.
                </p>
              </Card>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
