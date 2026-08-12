"use client";

import React from "react";
import { UserNavbar } from "@/components/layout/UserNavbar";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { MOCK_EVENT } from "@/mock/events";
import { Calendar, Clock, MapPin, ShieldAlert, Utensils, Info } from "lucide-react";

export default function EventPage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#080b11]">
      <UserNavbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <PageHeader
          title={MOCK_EVENT.name}
          subtitle={`Date: ${MOCK_EVENT.date} • Venue: ${MOCK_EVENT.venueName}`}
          badge={<Badge risk="LOW">STATUS: {MOCK_EVENT.status}</Badge>}
        />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Schedule & Important Instructions */}
          <div className="lg:col-span-7 space-y-6">
            <Card className="p-5 space-y-4 border-slate-800">
              <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
                <Clock className="w-5 h-5 text-cyan-400" />
                <h3 className="font-bold font-mono text-base text-white">Event Keynote & Panel Schedule</h3>
              </div>

              <div className="space-y-4">
                {MOCK_EVENT.schedule.map((item) => (
                  <div key={item.id} className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-cyan-400 font-bold">{item.time}</span>
                      <span className="text-slate-400">{item.stageName}</span>
                    </div>
                    <h4 className="font-bold text-sm text-white font-sans">{item.title}</h4>
                    <p className="text-xs text-slate-400 font-sans">{item.description}</p>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-5 space-y-4 border-slate-800">
              <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
                <ShieldAlert className="w-5 h-5 text-amber-400" />
                <h3 className="font-bold font-mono text-base text-white">Safety & Crowd Navigation Rules</h3>
              </div>

              <ul className="space-y-2 text-xs font-sans text-slate-300">
                {MOCK_EVENT.instructions.map((inst, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-cyan-400 font-mono font-bold">•</span>
                    <span>{inst}</span>
                  </li>
                ))}
              </ul>
            </Card>
          </div>

          {/* Right Column: Facilities & Gates Overview */}
          <div className="lg:col-span-5 space-y-6">
            <Card className="p-5 space-y-4 border-slate-800">
              <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
                <MapPin className="w-5 h-5 text-emerald-400" />
                <h3 className="font-bold font-mono text-base text-white">Venue Facilities & Status</h3>
              </div>

              <div className="space-y-3">
                {MOCK_EVENT.facilities.map((fac) => (
                  <div key={fac.id} className="flex items-center justify-between p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono">
                    <div>
                      <h5 className="font-bold text-white">{fac.name}</h5>
                      <span className="text-slate-400 text-[10px]">Zone: {fac.zoneId}</span>
                    </div>
                    <Badge variant={fac.status === "OPERATIONAL" ? "low" : "medium"}>
                      {fac.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </Card>

            <Card className="p-5 space-y-3 border-slate-800">
              <h4 className="font-bold font-mono text-sm text-slate-300 uppercase">Access Gates & Exits</h4>
              <div className="space-y-2 text-xs font-mono text-slate-400">
                <div>Gates: <strong className="text-white">{MOCK_EVENT.gates.join(", ")}</strong></div>
                <div>Exits: <strong className="text-white">{MOCK_EVENT.exits.join(", ")}</strong></div>
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
