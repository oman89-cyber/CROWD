import { MOCK_VENUE } from "@/mock/venue";
import { INITIAL_CROWD_STATE } from "@/mock/crowd";
import { DEMO_USER } from "@/mock/users";
import { INITIAL_USER_ROUTE, UPDATED_SAFER_ROUTE } from "@/mock/routes";
import { MOCK_BOTTLENECK_PREDICTION } from "@/mock/predictions";
import { MOCK_NOTIFICATIONS } from "@/mock/notifications";
import { MOCK_EVENT } from "@/mock/events";
import { MOCK_CAMERAS } from "@/mock/cameras";
import { Venue } from "@/types/venue";
import { CrowdState } from "@/types/crowd";
import { User } from "@/types/user";
import { UserRoute, CrowdAwareRouteResponse } from "@/types/route";
import { BottleneckPrediction } from "@/types/prediction";
import { AppNotification } from "@/types/notification";
import { EventInfo } from "@/types/event";
import { Camera } from "@/types/camera";
import { RiskLevel } from "@/types/venue";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const IS_MOCK = process.env.NEXT_PUBLIC_MOCK_MODE !== "false";

export async function verifyTicket(ticketId: string, eventCode: string): Promise<{ success: boolean; user: User; message: string }> {
  if (IS_MOCK) {
    await new Promise((res) => setTimeout(res, 600)); // Simulate network latency
    return {
      success: true,
      user: DEMO_USER,
      message: "Ticket verified successfully for TechFest 2026",
    };
  }

  try {
    const res = await fetch(`${API_URL}/api/ticket/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticket_id: ticketId }),
    });

    if (!res.ok) {
      if (res.status === 404) {
        const errorData = await res.json();
        throw new Error(errorData.message || "Ticket not found");
      }
      throw new Error(`Server error: ${res.status}`);
    }

    const data = await res.json();
    
    // Map FastAPI response to frontend User structure
    const user: User = {
      id: `usr-${data.session_id}`,
      crowdId: data.session_id,
      name: "Event Attendee", // Backend doesn't return name yet
      ticketId: ticketId,
      eventId: eventCode || "event-default",
      currentZoneId: data.parking?.toLowerCase() || "parking",
      destinationZoneId: data.seat?.toLowerCase() || undefined,
      gateAssigned: data.gate ? `Gate ${data.gate}` : undefined,
    };

    return {
      success: data.valid,
      user: user,
      message: `Ticket verified successfully. Session: ${data.session_id}`,
    };
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Failed to connect to backend server");
  }
}

export async function checkInUser(ticketId: string): Promise<{ success: boolean; crowdId: string; user: User }> {
  if (IS_MOCK) {
    await new Promise((res) => setTimeout(res, 400));
    return {
      success: true,
      crowdId: DEMO_USER.crowdId,
      user: DEMO_USER,
    };
  }
  const res = await fetch(`${API_URL}/users/check-in`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticketId }),
  });
  return res.json();
}

export async function getEvent(eventId: string): Promise<EventInfo> {
  if (IS_MOCK) return MOCK_EVENT;
  const res = await fetch(`${API_URL}/events/${eventId}`);
  return res.json();
}

export async function getVenue(venueId: string): Promise<Venue> {
  if (IS_MOCK) return MOCK_VENUE;
  const res = await fetch(`${API_URL}/venues/${venueId}`);
  return res.json();
}

export async function getCrowdState(): Promise<CrowdState> {
  if (IS_MOCK) return INITIAL_CROWD_STATE;
  const res = await fetch(`${API_URL}/crowd/state`);
  return res.json();
}

export async function getPredictions(): Promise<BottleneckPrediction[]> {
  if (IS_MOCK) return [MOCK_BOTTLENECK_PREDICTION];
  const res = await fetch(`${API_URL}/crowd/predictions`);
  return res.json();
}

export async function getRoute(crowdId: string, destZoneId: string, reroute: boolean = false): Promise<UserRoute> {
  if (IS_MOCK) {
    return reroute ? UPDATED_SAFER_ROUTE : INITIAL_USER_ROUTE;
  }
  const res = await fetch(`${API_URL}/routes?crowdId=${crowdId}&dest=${destZoneId}`);
  return res.json();
}

export async function getNotifications(): Promise<AppNotification[]> {
  if (IS_MOCK) return MOCK_NOTIFICATIONS;
  const res = await fetch(`${API_URL}/notifications`);
  return res.json();
}

export async function createEvent(data: Partial<EventInfo>): Promise<{ success: boolean; eventId: string }> {
  if (IS_MOCK) {
    await new Promise((res) => setTimeout(res, 500));
    return { success: true, eventId: "event-tf2026" };
  }
  const res = await fetch(`${API_URL}/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function uploadBlueprint(eventId: string, formData: FormData): Promise<{ success: boolean; blueprintUrl: string }> {
  if (IS_MOCK) {
    await new Promise((res) => setTimeout(res, 700));
    return { success: true, blueprintUrl: "/sample-blueprint.svg" };
  }
  const res = await fetch(`${API_URL}/events/${eventId}/blueprint`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

export async function registerCamera(cameraData: Partial<Camera>): Promise<{ success: boolean; camera: Camera }> {
  if (IS_MOCK) {
    return {
      success: true,
      camera: {
        id: cameraData.id || `CAM-0${MOCK_CAMERAS.length + 1}`,
        name: cameraData.name || "New Vision Cam",
        zoneId: cameraData.zoneId || "gate-a",
        status: "ONLINE",
        fps: 30,
        detectedCount: 0,
      },
    };
  }
  const res = await fetch(`${API_URL}/cameras`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cameraData),
  });
  return res.json();
}

export async function uploadTickets(eventId: string, file: File): Promise<{ success: boolean; count: number }> {
  if (IS_MOCK) {
    await new Promise((res) => setTimeout(res, 600));
    return { success: true, count: 5000 };
  }
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/events/${eventId}/tickets`, {
    method: "POST",
    body: formData,
  });
  return res.json();
}

export async function startSimulation(params: { crowdSize: number; entryRate: number; scenario: string }): Promise<{ success: boolean }> {
  if (IS_MOCK) return { success: true };
  const res = await fetch(`${API_URL}/simulation/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return res.json();
}

// Helper to convert risk score (0-1) to risk level
function getRiskLevel(riskScore: number): RiskLevel {
  if (riskScore < 0.30) return "LOW";
  if (riskScore < 0.60) return "MEDIUM";
  if (riskScore < 0.80) return "HIGH";
  return "CRITICAL";
}

// Helper to generate mock route points for visualization
function generateRoutePoints(path: string[]): any[] {
  // Simple mock points generation - in a real app, this would map to actual venue coordinates
  return path.map((zoneId, idx) => ({
    x: 400 + idx * 100,
    y: 300 + idx * 50,
    zoneId: zoneId.toLowerCase(),
  }));
}

// Route re-evaluation API
export async function recalculateRoute(
  sessionId: string,
  destination: string
): Promise<{
  routeChanged: boolean;
  currentRoute: UserRoute;
  previousRoute?: UserRoute;
  reason: string;
  routeVersion: number;
}> {
  if (IS_MOCK) {
    await new Promise((res) => setTimeout(res, 300));
    return {
      routeChanged: Math.random() > 0.7, // 30% chance of reroute in mock
      currentRoute: INITIAL_USER_ROUTE,
      reason: "Mock route evaluation",
      routeVersion: 1,
    };
  }

  try {
    const res = await fetch(`${API_URL}/api/route/recalculate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        destination: destination,
      }),
    });

    if (!res.ok) {
      if (res.status === 404) {
        const errorData = await res.json();
        throw new Error(errorData.message || "Route recalculation failed");
      }
      throw new Error(`Server error: ${res.status}`);
    }

    const data = await res.json();

    // Convert current route to frontend format
    const currentRoute: UserRoute = {
      crowdId: sessionId,
      sourceZone: data.current_route[0]?.toLowerCase() || "start",
      destinationZone: data.current_route[data.current_route.length - 1]?.toLowerCase() || "destination",
      path: data.current_route.map((z: string) => z.toLowerCase()),
      points: generateRoutePoints(data.current_route),
      distance: Math.round(Math.random() * 200 + 100), // Mock distance
      estimatedTime: Math.round(Math.random() * 5 + 3), // Mock time
      risk: getRiskLevel(data.risk_score),
      reason: data.reason,
      isAlternative: data.route_changed,
    };

    let previousRoute: UserRoute | undefined;
    if (data.route_changed && data.previous_route?.length > 0) {
      previousRoute = {
        crowdId: sessionId,
        sourceZone: data.previous_route[0]?.toLowerCase() || "start",
        destinationZone: data.previous_route[data.previous_route.length - 1]?.toLowerCase() || "destination",
        path: data.previous_route.map((z: string) => z.toLowerCase()),
        points: generateRoutePoints(data.previous_route),
        distance: Math.round(Math.random() * 200 + 100), // Mock distance
        estimatedTime: Math.round(Math.random() * 5 + 3), // Mock time
        risk: "HIGH" as RiskLevel, // Assume previous route was high risk
        reason: "Previous route (high risk)",
        isAlternative: false,
      };
    }

    return {
      routeChanged: data.route_changed,
      currentRoute,
      previousRoute,
      reason: data.reason,
      routeVersion: data.route_version,
    };
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Failed to recalculate route");
  }
}

export async function getCrowdAwareRoute(
  sessionId: string,
  destination: string
): Promise<UserRoute> {
  if (IS_MOCK) {
    await new Promise((res) => setTimeout(res, 400));
    return INITIAL_USER_ROUTE;
  }

  try {
    const res = await fetch(`${API_URL}/api/route/crowd-aware`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        destination: destination,
      }),
    });

    if (!res.ok) {
      if (res.status === 404) {
        const errorData = await res.json();
        throw new Error(errorData.message || "Route not found");
      }
      throw new Error(`Server error: ${res.status}`);
    }

    const data: CrowdAwareRouteResponse = await res.json();

    // Convert backend response to frontend UserRoute format
    const routePath = data.rerouted ? data.recommended_route : data.original_route;
    const userRoute: UserRoute = {
      crowdId: sessionId,
      sourceZone: routePath[0]?.toLowerCase() || "start",
      destinationZone: routePath[routePath.length - 1]?.toLowerCase() || "destination",
      path: routePath.map((z) => z.toLowerCase()),
      points: generateRoutePoints(routePath),
      distance: Math.round(data.distance),
      estimatedTime: Math.round(data.estimated_minutes * 10) / 10,
      risk: getRiskLevel(data.risk_score),
      reason: data.reason,
      isAlternative: data.rerouted,
    };

    return userRoute;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Failed to get route from backend");
  }
}

export async function getCrowdAwareRouteComparison(
  sessionId: string,
  destination: string
): Promise<{ original: UserRoute; recommended: UserRoute; rerouted: boolean }> {
  if (IS_MOCK) {
    await new Promise((res) => setTimeout(res, 400));
    return {
      original: INITIAL_USER_ROUTE,
      recommended: UPDATED_SAFER_ROUTE,
      rerouted: false,
    };
  }

  try {
    const res = await fetch(`${API_URL}/api/route/crowd-aware`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        destination: destination,
      }),
    });

    if (!res.ok) {
      if (res.status === 404) {
        const errorData = await res.json();
        throw new Error(errorData.message || "Route not found");
      }
      throw new Error(`Server error: ${res.status}`);
    }

    const data: CrowdAwareRouteResponse = await res.json();

    // Create original route
    const originalRoute: UserRoute = {
      crowdId: sessionId,
      sourceZone: data.original_route[0]?.toLowerCase() || "start",
      destinationZone:
        data.original_route[data.original_route.length - 1]?.toLowerCase() ||
        "destination",
      path: data.original_route.map((z) => z.toLowerCase()),
      points: generateRoutePoints(data.original_route),
      distance: Math.round(data.distance),
      estimatedTime: Math.round(data.estimated_minutes * 10) / 10,
      risk: getRiskLevel(data.risk_score),
      reason: "Original shortest path",
      isAlternative: false,
    };

    // Create recommended route
    const recommendedRoute: UserRoute = {
      crowdId: sessionId,
      sourceZone: data.recommended_route[0]?.toLowerCase() || "start",
      destinationZone:
        data.recommended_route[data.recommended_route.length - 1]?.toLowerCase() ||
        "destination",
      path: data.recommended_route.map((z) => z.toLowerCase()),
      points: generateRoutePoints(data.recommended_route),
      distance: Math.round(data.distance),
      estimatedTime: Math.round(data.estimated_minutes * 10) / 10,
      risk: getRiskLevel(data.risk_score),
      reason: data.reason,
      isAlternative: data.rerouted,
    };

    return {
      original: originalRoute,
      recommended: recommendedRoute,
      rerouted: data.rerouted,
    };
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Failed to get route from backend");
  }
}
