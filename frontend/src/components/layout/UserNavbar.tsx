"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, Bell, Navigation, Calendar, Ticket, Compass } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { MOCK_NOTIFICATIONS } from "@/mock/notifications";

export const UserNavbar: React.FC = () => {
  const pathname = usePathname();
  const unreadCount = MOCK_NOTIFICATIONS.filter((n) => !n.read).length;

  const navLinks = [
    { href: "/dashboard", label: "Dashboard", icon: Compass },
    { href: "/destination", label: "Destinations", icon: Navigation },
    { href: "/navigation", label: "Live Route", icon: Navigation },
    { href: "/notifications", label: "Alerts", icon: Bell, badge: unreadCount },
    { href: "/event", label: "Event Info", icon: Calendar },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 group-hover:bg-cyan-500/20 transition">
            <Shield className="w-5 h-5 text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold tracking-wider text-base text-white font-mono">CROWD</span>
              <span className="font-bold tracking-wider text-base text-cyan-400 font-mono">SENSE</span>
            </div>
            <span className="text-[10px] text-slate-400 block tracking-widest font-mono uppercase">User Assistant</span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-mono font-medium transition ${
                  isActive
                    ? "bg-slate-800 text-cyan-400 border border-slate-700 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{link.label}</span>
                {link.badge ? (
                  <span className="ml-1 px-1.5 py-0.2 bg-cyan-500 text-slate-950 rounded-full text-[10px] font-bold">
                    {link.badge}
                  </span>
                ) : null}
              </Link>
            );
          })}
        </nav>

        {/* Action Button & Mode Switch */}
        <div className="flex items-center gap-3">
          <Link
            href="/verify-ticket"
            className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono bg-slate-900 border border-slate-800 text-slate-300 hover:text-cyan-400 hover:border-slate-700 transition"
          >
            <Ticket className="w-3.5 h-3.5 text-cyan-400" />
            <span>TKT-2026-1042</span>
          </Link>

          <Link
            href="/organizer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/20 transition shadow-sm"
          >
            <span>Organizer Portal</span>
          </Link>
        </div>
      </div>

      {/* Mobile Nav Bar bottom */}
      <div className="md:hidden flex items-center justify-around border-t border-slate-800/80 bg-slate-950/90 py-2 px-2">
        {navLinks.map((link) => {
          const Icon = link.icon;
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex flex-col items-center gap-1 px-2 py-1 rounded text-[10px] font-mono ${
                isActive ? "text-cyan-400 font-bold" : "text-slate-400"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{link.label}</span>
            </Link>
          );
        })}
      </div>
    </header>
  );
};
