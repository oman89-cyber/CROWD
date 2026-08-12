"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MapPin,
  Camera,
  Ticket,
  TrendingUp,
  Sliders,
  PlusCircle,
  Upload,
  Edit3,
  Activity,
  ArrowLeft,
  ShieldAlert,
} from "lucide-react";
import { Badge } from "@/components/ui/Badge";

interface OrganizerSidebarProps {
  eventId?: string;
}

export const OrganizerSidebar: React.FC<OrganizerSidebarProps> = ({
  eventId = "event-tf2026",
}) => {
  const pathname = usePathname();

  const mainLinks = [
    { href: "/organizer", label: "Overview", icon: LayoutDashboard },
    { href: "/organizer/events/create", label: "Create Event", icon: PlusCircle },
  ];

  const eventLinks = [
    { href: `/organizer/events/${eventId}/live-map`, label: "Live Command Map", icon: Activity, badge: "LIVE" },
    { href: `/organizer/events/${eventId}/blueprint`, label: "Blueprint Upload", icon: Upload },
    { href: `/organizer/events/${eventId}/venue-editor`, label: "Venue Graph Editor", icon: Edit3 },
    { href: `/organizer/events/${eventId}/cameras`, label: "Camera Vision", icon: Camera },
    { href: `/organizer/events/${eventId}/tickets`, label: "Ticket Registry", icon: Ticket },
    { href: `/organizer/events/${eventId}/prediction`, label: "AI Predictions", icon: TrendingUp },
    { href: `/organizer/events/${eventId}/simulation`, label: "Flow Simulation", icon: Sliders },
  ];

  return (
    <aside className="w-64 border-r border-slate-800/80 bg-slate-950/90 backdrop-blur-xl flex flex-col justify-between shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="p-4 space-y-6">
        {/* Brand */}
        <div className="px-2 pt-1 flex items-center justify-between border-b border-slate-800/80 pb-4">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-cyan-500/20 border border-cyan-500/40 text-cyan-400">
              <ShieldAlert className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h2 className="font-bold text-sm text-white font-mono tracking-wider">CROWDSENSE</h2>
              <p className="text-[10px] text-cyan-400 font-mono tracking-widest uppercase">Ops Center v2.4</p>
            </div>
          </div>
        </div>

        {/* Global Navigation */}
        <div className="space-y-1">
          <p className="px-2 text-[10px] font-mono font-semibold text-slate-500 uppercase tracking-widest">
            Platform Operations
          </p>
          {mainLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-mono transition ${
                  isActive
                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-semibold"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </div>

        {/* Current Event Context */}
        <div className="space-y-1 pt-2">
          <div className="px-2 flex items-center justify-between">
            <p className="text-[10px] font-mono font-semibold text-slate-500 uppercase tracking-widest">
              TechFest 2026
            </p>
            <Badge risk="LOW" pulse>ACTIVE</Badge>
          </div>

          <div className="mt-2 space-y-1">
            {eventLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs font-mono transition ${
                    isActive
                      ? "bg-slate-800 text-cyan-400 border border-slate-700 font-semibold shadow-inner"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4" />
                    <span>{link.label}</span>
                  </div>
                  {link.badge && (
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                      {link.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        </div>
      </div>

      {/* Footer / Switch back to User View */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-900/40">
        <Link
          href="/dashboard"
          className="flex items-center justify-center gap-2 w-full px-3 py-2 rounded-lg border border-slate-800 text-xs font-mono text-slate-400 hover:text-cyan-400 hover:border-slate-700 transition"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Exit Ops to User App</span>
        </Link>
      </div>
    </aside>
  );
};
