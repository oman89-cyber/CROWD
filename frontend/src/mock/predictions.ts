import { BottleneckPrediction, DensityTrendPoint } from "@/types/prediction";

export const MOCK_BOTTLENECK_PREDICTION: BottleneckPrediction = {
  zoneId: "corridor-c",
  zoneName: "Corridor C",
  currentDensity: 72,
  predictedDensity: 91,
  timeToCritical: 74,
  severity: "CRITICAL",
  recommendedAction: "Activate automated dynamic rerouting to Corridor B for 34 heading users.",
};

export const MOCK_DENSITY_TRENDS: DensityTrendPoint[] = [
  { time: "-2 min", "Corridor C": 45, "Corridor B": 40, "Main Stage": 60, threshold: 85 },
  { time: "-90s", "Corridor C": 52, "Corridor B": 42, "Main Stage": 63, threshold: 85 },
  { time: "-60s", "Corridor C": 61, "Corridor B": 46, "Main Stage": 66, threshold: 85 },
  { time: "-30s", "Corridor C": 72, "Corridor B": 48, "Main Stage": 68, threshold: 85 },
  { time: "Now", "Corridor C": 84, "Corridor B": 50, "Main Stage": 71, threshold: 85 },
  { time: "+30s (Pred)", "Corridor C": 89, "Corridor B": 53, "Main Stage": 73, threshold: 85 },
  { time: "+60s (Pred)", "Corridor C": 94, "Corridor B": 57, "Main Stage": 75, threshold: 85 },
  { time: "+90s (Pred)", "Corridor C": 97, "Corridor B": 60, "Main Stage": 78, threshold: 85 },
  { time: "+2 min (Pred)", "Corridor C": 99, "Corridor B": 62, "Main Stage": 80, threshold: 85 },
];
