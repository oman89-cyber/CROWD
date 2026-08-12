import { RiskLevel } from "./venue";

export type NotificationType = "route_update" | "safer_route" | "event_update" | "emergency" | "bottleneck";

export interface AppNotification {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  timestamp: string;
  read: boolean;
  severity: RiskLevel;
  actionUrl?: string;
}
