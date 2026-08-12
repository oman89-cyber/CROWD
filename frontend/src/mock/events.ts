import { EventInfo } from "@/types/event";

export const MOCK_EVENT: EventInfo = {
  id: "event-tf2026",
  name: "TechFest 2026 Global Summit",
  date: "August 15, 2026",
  startTime: "09:00 AM PST",
  expectedCrowd: 5000,
  venueName: "Metropolis Arena & Expo Center",
  status: "LIVE",
  gates: ["Gate A (North)", "Gate B (Central)", "Gate C (East)"],
  exits: ["Exit A", "Exit B", "Emergency Exit"],
  facilities: [
    { id: "f1", name: "Main Stage Arena", type: "stage", zoneId: "main-stage", status: "OPERATIONAL" },
    { id: "f2", name: "Gourmet Food Court", type: "food", zoneId: "food-court", status: "OPERATIONAL" },
    { id: "f3", name: "East Wing Restrooms", type: "restroom", zoneId: "restrooms", status: "BUSY" },
    { id: "f4", name: "Medical Station Alpha", type: "medical", zoneId: "corridor-a", status: "OPERATIONAL" },
    { id: "f5", name: "Help Desk Gate A", type: "info", zoneId: "gate-a", status: "OPERATIONAL" },
  ],
  schedule: [
    { id: "s1", time: "10:00 AM", title: "Opening Keynote: Smart City Sensing", stageName: "Main Stage", description: "Exploring real-time crowd dynamics and AI routing." },
    { id: "s2", time: "11:30 AM", title: "Panel: Next-Gen Event Operations", stageName: "Main Stage", description: "Stadium operators discuss computer vision & ML." },
    { id: "s3", time: "01:30 PM", title: "Hugging Face ML Architecture Showcase", stageName: "Main Stage", description: "Real-time edge detection and density heatmaps." },
    { id: "s4", time: "03:00 PM", title: "Live Simulation & Safety Rerouting", stageName: "Main Stage", description: "Interactive crowd flow control demo." },
  ],
  instructions: [
    "Follow dynamic crowd navigation prompts on your smartphone for faster access.",
    "Report congested corridors or emergency issues immediately to nearest event steward.",
    "Keep QR codes ready for swift re-entry verification at all gates.",
    "In case of emergency evacuation alarms, follow highlighted green path indicators to Exit A/B.",
  ],
};
