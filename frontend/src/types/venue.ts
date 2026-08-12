export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type ZoneType = "gate" | "stage" | "corridor" | "food" | "restroom" | "exit" | "general";

export interface VenueZone {
  id: string;
  name: string;
  capacity: number;
  occupancy: number;
  density: number; // 0.0 to 1.0
  risk: RiskLevel;
  polygon: [number, number][]; // [x, y] coordinates in venue space
  type?: ZoneType;
  center?: [number, number];
}

export interface VenuePath {
  id: string;
  from: string;
  to: string;
  distance: number; // in meters
  capacity: number;
}

export interface Gate {
  id: string;
  name: string;
  zoneId: string;
  x: number;
  y: number;
  status: "OPEN" | "CLOSED" | "CONGESTED";
}

export interface Exit {
  id: string;
  name: string;
  zoneId: string;
  x: number;
  y: number;
  isEmergencyOnly?: boolean;
}

export interface Venue {
  id: string;
  name: string;
  width: number;
  height: number;
  zones: VenueZone[];
  paths: VenuePath[];
  gates?: Gate[];
  exits?: Exit[];
}
