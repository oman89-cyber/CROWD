import { RiskLevel } from "./venue";

export interface RoutePoint {
  x: number;
  y: number;
  zoneId: string;
}

export interface UserRoute {
  crowdId: string;
  sourceZone: string;
  destinationZone: string;
  path: string[]; // zone IDs sequence e.g., ["corridor-c", "corridor-d", "main-stage"]
  points: RoutePoint[]; // [x,y] points for canvas/SVG rendering
  distance: number; // in meters
  estimatedTime: number; // in minutes
  risk: RiskLevel;
  reason?: string;
  isAlternative?: boolean;
}

// Backend crowd-aware route response
export interface CrowdAwareRouteResponse {
  original_route: string[];
  recommended_route: string[];
  distance: number;
  estimated_minutes: number;
  risk_score: number;
  route_mode: string;
  rerouted: boolean;
  reason: string;
}

// Route re-evaluation response
export interface RouteRecalculateResponse {
  session_id: string;
  route_changed: boolean;
  current_route: string[];
  previous_route: string[];
  new_route: string[];
  risk_score: number;
  reason: string;
  route_version: number;
  improvement: number;
}
