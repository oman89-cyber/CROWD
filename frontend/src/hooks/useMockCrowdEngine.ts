"use client";

import { useEffect, useState, useCallback } from "react";
import { MOCK_VENUE } from "@/mock/venue";
import { INITIAL_USER_ROUTE, UPDATED_SAFER_ROUTE } from "@/mock/routes";
import { VenueZone } from "@/types/venue";
import { UserRoute } from "@/types/route";
import { BottleneckPrediction } from "@/types/prediction";

export type DemoStage = "INITIAL" | "BUILDING_DENSITY" | "CRITICAL_BOTTLENECK" | "REROUTED" | "RESOLVED";

export function useMockCrowdEngine(autoStart: boolean = true) {
  const [zones, setZones] = useState<VenueZone[]>(MOCK_VENUE.zones);
  const [userRoute, setUserRoute] = useState<UserRoute>(INITIAL_USER_ROUTE);
  const [bottleneckAlert, setBottleneckAlert] = useState<BottleneckPrediction | null>(null);
  const [isRerouted, setIsRerouted] = useState<boolean>(false);
  const [reroutedCount, setReroutedCount] = useState<number>(0);
  const [demoStage, setDemoStage] = useState<DemoStage>("INITIAL");
  const [statusMessage, setStatusMessage] = useState<string>("Normal crowd flow across all zones.");
  const [timeRemaining, setTimeRemaining] = useState<number>(74);

  // Helper to update density of a specific zone
  const updateZoneDensity = useCallback((zoneId: string, newDensity: number) => {
    setZones((prev) =>
      prev.map((z) => {
        if (z.id === zoneId) {
          const occ = Math.round(z.capacity * newDensity);
          let risk: VenueZone["risk"] = "LOW";
          if (newDensity >= 0.85) risk = "CRITICAL";
          else if (newDensity >= 0.70) risk = "HIGH";
          else if (newDensity >= 0.50) risk = "MEDIUM";

          return { ...z, density: newDensity, occupancy: occ, risk };
        }
        return z;
      })
    );
  }, []);

  const triggerBottleneckSequence = useCallback(() => {
    setDemoStage("BUILDING_DENSITY");
    setStatusMessage("Crowd building near Gate C / Corridor C...");

    // Step 1: 3s -> Zone C to 72%
    setTimeout(() => {
      updateZoneDensity("corridor-c", 0.72);
      setStatusMessage("Zone C density rising to 72% (HIGH)");
    }, 3000);

    // Step 2: 7s -> Zone C to 84%
    setTimeout(() => {
      updateZoneDensity("corridor-c", 0.84);
      setStatusMessage("Zone C approaching threshold (84%)");
    }, 7000);

    // Step 3: 11s -> Zone C to 91% (CRITICAL) & Bottleneck Alert
    setTimeout(() => {
      updateZoneDensity("corridor-c", 0.91);
      setDemoStage("CRITICAL_BOTTLENECK");
      setBottleneckAlert({
        zoneId: "corridor-c",
        zoneName: "Corridor C",
        currentDensity: 91,
        predictedDensity: 98,
        timeToCritical: 74,
        severity: "CRITICAL",
        recommendedAction: "Reroute heading attendees to Corridor B immediately.",
      });
      setStatusMessage("🚨 BOTTLENECK ALERT: Corridor C critical (91%). Hugging Face Model predicting blockage.");
    }, 11000);

    // Step 4: 15s -> Trigger Route Update for users & Reroute 34 attendees
    setTimeout(() => {
      setDemoStage("REROUTED");
      setIsRerouted(true);
      setUserRoute(UPDATED_SAFER_ROUTE);
      setReroutedCount(34);
      setStatusMessage("⚡ OPTIMIZATION COMPLETE: 34 attendees re-routed via Corridor B.");
    }, 15000);

    // Step 5: 22s -> Crowd redistributes, Zone C drops to 78%, then 64%
    setTimeout(() => {
      updateZoneDensity("corridor-c", 0.78);
      updateZoneDensity("corridor-b", 0.62);
      setStatusMessage("Flow redistributing... Zone C density dropping (78%)");
    }, 22000);

    setTimeout(() => {
      updateZoneDensity("corridor-c", 0.64);
      updateZoneDensity("corridor-b", 0.55);
      setDemoStage("RESOLVED");
      setBottleneckAlert(null);
      setStatusMessage("🟢 CONGESTION RESOLVED: Corridor C normalized at 64%.");
    }, 27000);
  }, [updateZoneDensity]);

  const resetDemo = useCallback(() => {
    setZones(MOCK_VENUE.zones);
    setUserRoute(INITIAL_USER_ROUTE);
    setBottleneckAlert(null);
    setIsRerouted(false);
    setReroutedCount(0);
    setDemoStage("INITIAL");
    setStatusMessage("Normal crowd flow across all zones.");
    setTimeRemaining(74);
  }, []);

  useEffect(() => {
    if (!autoStart) return;
    const timer = setTimeout(() => {
      triggerBottleneckSequence();
    }, 5000);

    return () => clearTimeout(timer);
  }, [autoStart, triggerBottleneckSequence]);

  return {
    zones,
    userRoute,
    bottleneckAlert,
    isRerouted,
    reroutedCount,
    demoStage,
    statusMessage,
    timeRemaining,
    triggerBottleneckSequence,
    resetDemo,
    updateZoneDensity,
  };
}
