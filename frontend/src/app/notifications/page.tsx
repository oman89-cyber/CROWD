"use client";

import React, { useState } from "react";
import { UserNavbar } from "@/components/layout/UserNavbar";
import { PageHeader } from "@/components/layout/PageHeader";
import { NotificationCard } from "@/components/user/NotificationCard";
import { MOCK_NOTIFICATIONS } from "@/mock/notifications";
import { AppNotification } from "@/types/notification";
import { Bell, CheckCheck, Filter } from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<AppNotification[]>(MOCK_NOTIFICATIONS);
  const [filter, setFilter] = useState<string>("all");

  const markAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const markRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const filtered = notifications.filter((n) => {
    if (filter === "unread") return !n.read;
    if (filter === "high") return n.severity === "HIGH" || n.severity === "CRITICAL";
    return true;
  });

  return (
    <div className="min-h-screen flex flex-col bg-[#080b11]">
      <UserNavbar />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <PageHeader
          title="Notifications & Safety Alerts"
          subtitle="Real-time route updates, event schedules, and emergency staff guidance."
          actions={
            <Button size="sm" variant="outline" onClick={markAllRead} leftIcon={<CheckCheck className="w-3.5 h-3.5" />}>
              Mark All as Read
            </Button>
          }
        />

        {/* Filter Pills */}
        <div className="flex items-center gap-2 border-b border-slate-800 pb-4">
          <Filter className="w-4 h-4 text-slate-500" />
          <button
            onClick={() => setFilter("all")}
            className={`px-3 py-1 rounded-full text-xs font-mono transition ${
              filter === "all" ? "bg-cyan-500 text-slate-950 font-bold" : "bg-slate-900 text-slate-400"
            }`}
          >
            All Alerts ({notifications.length})
          </button>
          <button
            onClick={() => setFilter("unread")}
            className={`px-3 py-1 rounded-full text-xs font-mono transition ${
              filter === "unread" ? "bg-cyan-500 text-slate-950 font-bold" : "bg-slate-900 text-slate-400"
            }`}
          >
            Unread ({notifications.filter((n) => !n.read).length})
          </button>
          <button
            onClick={() => setFilter("high")}
            className={`px-3 py-1 rounded-full text-xs font-mono transition ${
              filter === "high" ? "bg-red-500 text-white font-bold" : "bg-slate-900 text-slate-400"
            }`}
          >
            High Priority
          </button>
        </div>

        {/* List of Notifications */}
        <div className="space-y-4">
          {filtered.map((n) => (
            <NotificationCard key={n.id} notification={n} onRead={markRead} />
          ))}
        </div>
      </main>
    </div>
  );
}
