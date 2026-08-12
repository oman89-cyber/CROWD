export interface Camera {
  id: string;
  name: string;
  zoneId: string;
  status: "ONLINE" | "OFFLINE" | "WARNING";
  videoSource?: string;
  fps?: number;
  detectedCount?: number;
  x?: number;
  y?: number;
}
