import { Camera } from "@/types/camera";

export const MOCK_CAMERAS: Camera[] = [
  { id: "CAM-01", name: "Gate A Overhead Vision", zoneId: "gate-a", status: "ONLINE", videoSource: "rtsp://camera-01.local/live", fps: 30, detectedCount: 42, x: 115, y: 90 },
  { id: "CAM-02", name: "Gate B Vision", zoneId: "gate-b", status: "ONLINE", videoSource: "rtsp://camera-02.local/live", fps: 30, detectedCount: 55, x: 400, y: 90 },
  { id: "CAM-03", name: "Corridor C Density Cam", zoneId: "corridor-c", status: "ONLINE", videoSource: "rtsp://camera-03.local/live", fps: 30, detectedCount: 84, x: 685, y: 235 },
  { id: "CAM-04", name: "Main Stage Front Crowd", zoneId: "main-stage", status: "ONLINE", videoSource: "rtsp://camera-04.local/live", fps: 30, detectedCount: 142, x: 400, y: 425 },
  { id: "CAM-05", name: "Food Court Entrance", zoneId: "food-court", status: "WARNING", videoSource: "rtsp://camera-05.local/live", fps: 15, detectedCount: 28, x: 135, y: 415 },
  { id: "CAM-06", name: "Exit B Safety Monitor", zoneId: "exit-b", status: "OFFLINE", videoSource: "rtsp://camera-06.local/live", fps: 0, detectedCount: 0, x: 700, y: 510 },
];
