"use client";

import React, { useState, use } from "react";
import { OrganizerSidebar } from "@/components/layout/OrganizerSidebar";
import { PageHeader } from "@/components/layout/PageHeader";
import { StatCard } from "@/components/ui/StatCard";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Ticket, Upload, CheckCircle2, FileSpreadsheet } from "lucide-react";

export default function TicketsPage({ params }: { params: Promise<{ eventId: string }> }) {
  const { eventId } = use(params);
  const [uploaded, setUploaded] = useState<boolean>(true);

  const mockTicketList = [
    { ticketId: "TKT-2026-1042", name: "Alex Sharma", crowdId: "CS-8A41F", gate: "Gate A", status: "VERIFIED" },
    { ticketId: "TKT-2026-1043", name: "Priya Patel", crowdId: "CS-8A420", gate: "Gate B", status: "VERIFIED" },
    { ticketId: "TKT-2026-1044", name: "Rohan Verma", crowdId: "CS-8A421", gate: "Gate A", status: "CHECKED-IN" },
    { ticketId: "TKT-2026-1045", name: "Sarah Jenkins", crowdId: "CS-8A422", gate: "Gate C", status: "VERIFIED" },
    { ticketId: "TKT-2026-1046", name: "Michael Chen", crowdId: "CS-8A423", gate: "Gate B", status: "CHECKED-IN" },
  ];

  return (
    <div className="min-h-screen flex bg-[#080b11]">
      <OrganizerSidebar eventId={eventId} />

      <main className="flex-1 p-6 space-y-6 max-w-6xl mx-auto">
        <PageHeader
          title="Ticket Registry & Attendee Batch Import"
          subtitle="Upload event ticketing CSV manifests to bind barcode hashes to anonymized Crowd IDs."
        />

        {/* Top Telemetry Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard title="Total Tickets Issued" value="5,000" icon={<Ticket className="w-5 h-5 text-cyan-400" />} />
          <StatCard title="Verified Credentials" value="4,820" icon={<CheckCircle2 className="w-5 h-5 text-emerald-400" />} />
          <StatCard title="Active In-Venue" value="4,100" icon={<Ticket className="w-5 h-5 text-purple-400" />} />
        </div>

        {/* CSV Upload Container */}
        <Card className="p-6 space-y-4 border-slate-800">
          <div className="border-2 border-dashed border-cyan-500/40 p-6 rounded-xl bg-slate-950 text-center space-y-2">
            <FileSpreadsheet className="w-10 h-10 text-cyan-400 mx-auto" />
            <h4 className="font-bold text-sm text-white font-mono">Upload Ticketing Manifest (CSV)</h4>
            <p className="text-xs text-slate-400">Schema: ticketId, attendeeName, assignedGate, eventCode</p>
            <Button size="sm" variant="cyan" leftIcon={<Upload className="w-4 h-4" />}>
              Select CSV Manifest File
            </Button>
          </div>

          {/* Registry Table */}
          <div className="space-y-3 pt-2 font-mono text-xs">
            <h4 className="font-bold text-white uppercase tracking-wider">Active Ticket Manifest Preview</h4>
            <div className="overflow-x-auto rounded-lg border border-slate-800 bg-slate-950">
              <table className="w-full text-left">
                <thead className="bg-slate-900 border-b border-slate-800 text-slate-400 text-[10px] uppercase">
                  <tr>
                    <th className="p-3">Ticket ID</th>
                    <th className="p-3">Attendee Name</th>
                    <th className="p-3">Crowd ID</th>
                    <th className="p-3">Gate</th>
                    <th className="p-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {mockTicketList.map((row) => (
                    <tr key={row.ticketId} className="hover:bg-slate-900/50">
                      <td className="p-3 text-cyan-400 font-bold">{row.ticketId}</td>
                      <td className="p-3 text-white">{row.name}</td>
                      <td className="p-3 text-slate-300">{row.crowdId}</td>
                      <td className="p-3 text-slate-400">{row.gate}</td>
                      <td className="p-3">
                        <Badge risk="LOW">{row.status}</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
}
