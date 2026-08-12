import React from "react";
import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { AppNotification } from "@/types/notification";
import { Bell, Navigation, AlertTriangle, ArrowRight } from "lucide-react";

interface NotificationCardProps {
  notification: AppNotification;
  onRead?: (id: string) => void;
}

export const NotificationCard: React.FC<NotificationCardProps> = ({
  notification,
  onRead,
}) => {
  return (
    <Card
      glow={!notification.read && notification.severity === "HIGH"}
      glowColor={notification.severity === "HIGH" ? "red" : "cyan"}
      className={`p-4 space-y-2.5 transition ${notification.read ? "opacity-75" : "opacity-100"}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-slate-800 border border-slate-700 text-cyan-400">
            {notification.type === "route_update" || notification.type === "safer_route" ? (
              <Navigation className="w-4 h-4 text-cyan-400" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            )}
          </div>
          <div>
            <h5 className="font-semibold text-sm text-white font-mono">{notification.title}</h5>
            <span className="text-[10px] text-slate-400 font-mono">{notification.timestamp}</span>
          </div>
        </div>

        <Badge risk={notification.severity}>{notification.severity}</Badge>
      </div>

      <p className="text-xs text-slate-300 leading-relaxed font-sans pl-1">
        {notification.message}
      </p>

      {notification.actionUrl && (
        <div className="pt-2 flex justify-end">
          <Link
            href={notification.actionUrl}
            onClick={() => onRead && onRead(notification.id)}
            className="inline-flex items-center gap-1 text-xs font-mono text-cyan-400 hover:text-cyan-300 font-medium"
          >
            <span>View Details</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}
    </Card>
  );
};
