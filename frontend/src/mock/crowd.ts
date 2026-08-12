import { CrowdAgent, CrowdState } from "@/types/crowd";
import { MOCK_VENUE } from "./venue";

export function generateInitialAgents(count: number = 120): CrowdAgent[] {
  const agents: CrowdAgent[] = [];
  const zones = MOCK_VENUE.zones;

  for (let i = 0; i < count; i++) {
    // Pick a zone randomly weighted by zone capacity
    const zone = zones[i % zones.length];
    const poly = zone.polygon;
    
    // Compute bounds
    const minX = Math.min(...poly.map(p => p[0])) + 5;
    const maxX = Math.max(...poly.map(p => p[0])) - 5;
    const minY = Math.min(...poly.map(p => p[1])) + 5;
    const maxY = Math.max(...poly.map(p => p[1])) - 5;

    const x = minX + Math.random() * (maxX - minX);
    const y = minY + Math.random() * (maxY - minY);
    const angle = Math.random() * Math.PI * 2;
    const speed = 0.3 + Math.random() * 0.7;

    agents.push({
      id: `agent-${i + 1}`,
      x,
      y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      currentZoneId: zone.id,
      targetZoneId: zones[(i + 1) % zones.length].id,
      speed,
    });
  }

  // Add the demo user Alex Sharma as a distinct glowing blue agent
  agents.push({
    id: "agent-alex",
    x: 685, // Corridor C center
    y: 235,
    vx: 0.2,
    vy: 0.3,
    currentZoneId: "corridor-c",
    targetZoneId: "main-stage",
    isUser: true,
    color: "#00f0ff",
    speed: 0.8,
  });

  return agents;
}

export const INITIAL_CROWD_STATE: CrowdState = {
  totalPeople: 4820,
  activeTrackedPeople: 482,
  zones: MOCK_VENUE.zones,
  timestamp: new Date().toISOString(),
};
