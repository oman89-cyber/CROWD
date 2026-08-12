import { VenueZone } from "./venue";

export interface CrowdState {
  totalPeople: number;
  activeTrackedPeople: number;
  zones: VenueZone[];
  timestamp: string;
}

export interface CrowdAgent {
  id: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  currentZoneId: string;
  targetZoneId: string;
  isUser?: boolean;
  color?: string;
  speed?: number;
}
