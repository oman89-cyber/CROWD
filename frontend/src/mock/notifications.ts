import { AppNotification } from "@/types/notification";

export const MOCK_NOTIFICATIONS: AppNotification[] = [
  {
    id: "notif-1",
    title: "Route Update Triggered",
    message: "Corridor C is experiencing heavy congestion (84% capacity). You have been re-routed via Corridor B.",
    type: "route_update",
    timestamp: "1 min ago",
    read: false,
    severity: "HIGH",
    actionUrl: "/navigation",
  },
  {
    id: "notif-2",
    title: "Safer Alternative Route Available",
    message: "An alternative path via Corridor B can save approximately 2 minutes and bypass density.",
    type: "safer_route",
    timestamp: "3 mins ago",
    read: false,
    severity: "MEDIUM",
    actionUrl: "/navigation",
  },
  {
    id: "notif-3",
    title: "Event Update - Main Stage",
    message: "Keynote presentation 'AI in Urban Intelligence' starts in 10 minutes at Main Stage.",
    type: "event_update",
    timestamp: "12 mins ago",
    read: true,
    severity: "LOW",
    actionUrl: "/event",
  },
  {
    id: "notif-4",
    title: "Gate B Flow Normal",
    message: "Gate B queue length has normalized. Processing rate: 45 attendees/min.",
    type: "event_update",
    timestamp: "25 mins ago",
    read: true,
    severity: "LOW",
  },
];
