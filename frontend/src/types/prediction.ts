import { RiskLevel } from "./venue";

export interface BottleneckPrediction {
  zoneId: string;
  zoneName: string;
  currentDensity: number; // 0 to 100
  predictedDensity: number; // 0 to 100
  timeToCritical: number; // in seconds
  severity: RiskLevel;
  recommendedAction?: string;
}

export interface DensityTrendPoint {
  time: string;
  [zoneId: string]: number | string;
}
