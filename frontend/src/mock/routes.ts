import { UserRoute } from "@/types/route";

export const INITIAL_USER_ROUTE: UserRoute = {
  crowdId: "CS-8A41F",
  sourceZone: "corridor-c",
  destinationZone: "main-stage",
  path: ["corridor-c", "corridor-d", "main-stage"],
  points: [
    { x: 685, y: 235, zoneId: "corridor-c" },
    { x: 665, y: 485, zoneId: "corridor-d" },
    { x: 400, y: 425, zoneId: "main-stage" },
  ],
  distance: 145,
  estimatedTime: 3,
  risk: "LOW",
  reason: "Direct path via Corridor C",
};

export const UPDATED_SAFER_ROUTE: UserRoute = {
  crowdId: "CS-8A41F",
  sourceZone: "corridor-c",
  destinationZone: "main-stage",
  path: ["corridor-c", "corridor-b", "main-stage"],
  points: [
    { x: 685, y: 235, zoneId: "corridor-c" },
    { x: 400, y: 235, zoneId: "corridor-b" },
    { x: 400, y: 425, zoneId: "main-stage" },
  ],
  distance: 165,
  estimatedTime: 3.5,
  risk: "LOW",
  reason: "Rerouted via Corridor B to avoid predicted bottleneck in Corridor C (Saves ~2 mins queue time)",
  isAlternative: true,
};

export const ALL_MOCK_DESTINATIONS = [
  { id: "main-stage", name: "Main Stage", subtitle: "Primary Performance Arena", distance: "145 m", time: "3 min", risk: "LOW" as const },
  { id: "food-court", name: "Food Court", subtitle: "Refreshments & Dining Zone", distance: "310 m", time: "5 min", risk: "LOW" as const },
  { id: "restrooms", name: "Restrooms", subtitle: "East Wing Restroom Block", distance: "65 m", time: "1 min", risk: "LOW" as const },
  { id: "exit-a", name: "Exit A", subtitle: "North Gate Evacuation Way", distance: "420 m", time: "7 min", risk: "LOW" as const },
  { id: "exit-b", name: "Exit B", subtitle: "South Gate Exit Way", distance: "180 m", time: "3 min", risk: "LOW" as const },
  { id: "emergency-exit", name: "Emergency Exit", subtitle: "Central Evacuation Corridor", distance: "240 m", time: "4 min", risk: "LOW" as const },
];
