export interface EventFacility {
  id: string;
  name: string;
  type: "restroom" | "food" | "medical" | "info" | "exit" | "stage";
  zoneId: string;
  status: "OPERATIONAL" | "BUSY" | "CLOSED";
}

export interface EventScheduleItem {
  id: string;
  time: string;
  title: string;
  stageName: string;
  description: string;
}

export interface EventInfo {
  id: string;
  name: string;
  date: string;
  startTime: string;
  expectedCrowd: number;
  venueName: string;
  status: "UPCOMING" | "LIVE" | "ENDED";
  gates: string[];
  exits: string[];
  facilities: EventFacility[];
  schedule: EventScheduleItem[];
  instructions: string[];
}
