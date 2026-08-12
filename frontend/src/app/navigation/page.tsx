"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import { UserNavbar } from "@/components/layout/UserNavbar";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { VenueMap } from "@/components/venue/VenueMap";
import { useMockCrowdEngine } from "@/hooks/useMockCrowdEngine";
import { MOCK_VENUE } from "@/mock/venue";
import { generateInitialAgents } from "@/mock/crowd";
import { getSession } from "@/lib/session";
import { recalculateRoute } from "@/lib/api";
import { UserRoute } from "@/types/route";
import {
  Navigation,
  ArrowRight,
  ShieldAlert,
  Clock,
  Compass,
  RefreshCcw,
  CheckCircle2,
  AlertTriangle,
  Zap,
} from "lucide-react";

// Route polling interval from environment (default 5 seconds)
const ROUTE_RECHECK_INTERVAL = parseInt(
  process.env.NEXT_PUBLIC_ROUTE_RECHECK_INTERVAL_MS || "5000"
);

export default function NavigationPage() {
  // Mock engine for visualization
  const {
    zones,
    userRoute: mockRoute,
    bottleneckAlert,
    isRerouted: mockIsRerouted,
    triggerBottleneckSequence,
    resetDemo,
  } = useMockCrowdEngine(true);

  // Live route state
  const [currentRoute, setCurrentRoute] = useState<UserRoute>(mockRoute);
  const [previousRoute, setPreviousRoute] = useState<UserRoute | null>(null);
  const [routeChanged, setRouteChanged] = useState<boolean>(false);
  const [routeUpdateReason, setRouteUpdateReason] = useState<string>("");
  const [routeVersion, setRouteVersion] = useState<number>(1);
  const [isPolling, setIsPolling] = useState<boolean>(false);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const [pollingError, setPollingError] = useState<string>("");

  // Navigation state
  const [isNavigating, setIsNavigating] = useState<boolean>(true);
  const [distanceRemaining, setDistanceRemaining] = useState<number>(145);

  // Refs for cleanup
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const distanceIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Get session data
  const session = getSession();
  const sessionId = session?.sessionId || "CS-1021";
  const destination = session?.user?.destinationZoneId?.toUpperCase() || "SEAT_C124";

  // Route polling function
  const checkRouteUpdate = useCallback(async () => {
    if (!sessionId || !destination) return;

    try {
      setPollingError("");
      const result = await recalculateRoute(sessionId, destination);
      
      setRouteVersion(result.routeVersion);
      setLastUpdate(new Date().toLocaleTimeString());

      if (result.routeChanged) {
        // Route has changed - show update
        if (result.previousRoute) {
          setPreviousRoute(result.previousRoute);
        }
        setCurrentRoute(result.currentRoute);
        setRouteChanged(true);
        setRouteUpdateReason(result.reason);
        
        console.log("Route updated:", {
          reason: result.reason,
          version: result.routeVersion,
          newRoute: result.currentRoute.path,
        });
      } else {
        // Route unchanged - update current route in case of risk score changes
        setCurrentRoute(result.currentRoute);
        setRouteUpdateReason(result.reason);
      }
    } catch (error) {
      console.error("Route polling error:", error);
      setPollingError(error instanceof Error ? error.message : "Route update failed");
    }
  }, [sessionId, destination]);

  // Start route polling
  useEffect(() => {
    if (!isPolling) return;

    // Initial check
    checkRouteUpdate();

    // Set up polling interval
    pollingIntervalRef.current = setInterval(checkRouteUpdate, ROUTE_RECHECK_INTERVAL);

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [isPolling, checkRouteUpdate]);

  // Distance countdown animation
  useEffect(() => {
    if (!isNavigating) return;

    distanceIntervalRef.current = setInterval(() => {
      setDistanceRemaining((prev) => (prev > 10 ? prev - 5 : 145));
    }, 1500);

    return () => {
      if (distanceIntervalRef.current) {
        clearInterval(distanceIntervalRef.current);
      }
    };
  }, [isNavigating]);

  // Start polling on mount
  useEffect(() => {
    setIsPolling(true);
    return () => {
      setIsPolling(false);
    };
  }, []);

  // Manual route refresh
  const handleManualRefresh = useCallback(() => {
    checkRouteUpdate();
  }, [checkRouteUpdate]);

  // Acknowledge route update
  const acknowledgeRouteUpdate = useCallback(() => {
    setRouteChanged(false);
    setPreviousRoute(null);
    setRouteUpdateReason("");
  }, []);

  // Use live route or fall back to mock
  const displayRoute = currentRoute;
  const agents = generateInitialAgents(70);
  const currentVenue = { ...MOCK_VENUE, zones };

  return (
    <div className="min-h-screen flex flex-col bg-[#080b11]">
      <UserNavbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Navigation Header Banner */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              <Navigation className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-white uppercase">
                  LIVE ROUTE MONITORING
                </span>
                <Badge risk={displayRoute.risk}>{displayRoute.risk} RISK</Badge>
                <span className="text-xs font-mono text-slate-400">
                  v{routeVersion}
                </span>
              </div>
              <p className="text-sm font-bold font-mono text-cyan-400">
                {displayRoute.sourceZone.toUpperCase()} → {displayRoute.destinationZone.toUpperCase()}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button
              size="sm"
              variant="cyan"
              onClick={handleManualRefresh}
              leftIcon={<RefreshCcw className="w-3.5 h-3.5" />}
            >
              Check Route
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={triggerBottleneckSequence}
            >
              Demo Surge
            </Button>
          </div>
        </div>

        {/* Route Update Alert */}
        {routeChanged && (
          <Alert
            variant="warning"
            title="⚡ ROUTE UPDATED"
            className="border-amber-500/30 bg-amber-500/5"
          >
            <div className="flex flex-col gap-3">
              <p className="text-amber-200">
                {routeUpdateReason}
              </p>
              
              {previousRoute && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
                  <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-3 h-3 rounded-full bg-red-500"></div>
                      <span className="text-red-400 font-bold">PREVIOUS ROUTE</span>
                    </div>
                    <div className="text-slate-300">
                      {previousRoute.path.map(p => p.toUpperCase()).join(" → ")}
                    </div>
                    <div className="text-red-400 mt-1">Risk: {previousRoute.risk}</div>
                  </div>
                  
                  <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                      <span className="text-emerald-400 font-bold">NEW ROUTE</span>
                    </div>
                    <div className="text-slate-300">
                      {displayRoute.path.map(p => p.toUpperCase()).join(" → ")}
                    </div>
                    <div className="text-emerald-400 mt-1">Risk: {displayRoute.risk}</div>
                  </div>
                </div>
              )}
              
              <Button
                size="sm"
                variant="ghost"
                onClick={acknowledgeRouteUpdate}
                className="self-start"
              >
                Got it, continue with new route
              </Button>
            </div>
          </Alert>
        )}

        {/* Polling Status */}
        {pollingError && (
          <Alert variant="error" title="Route Monitoring Error">
            {pollingError}
          </Alert>
        )}

        {/* Bottleneck Alert (from mock engine for demo) */}
        {bottleneckAlert && !routeChanged && (
          <Alert variant="CRITICAL" title="⚠ CONGESTION ALERT AHEAD">
            {bottleneckAlert.name} is reaching critical density ({bottleneckAlert.currentDensity}%). 
            Live crowd monitoring is calculating alternative route...
          </Alert>
        )}

        {/* Interactive Map */}
        <Card glow glowColor={routeChanged ? "green" : "cyan"} className="p-3">
          <VenueMap
            venue={currentVenue}
            agents={agents}
            userRoute={displayRoute}
            selectedZoneId="corridor-c"
            mode="user"
            showCrowdLayer={true}
            showCameras={false}
          />
        </Card>

        {/* Navigation Content */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          {/* Turn-by-Turn Instructions */}
          <Card className="md:col-span-8 p-5 space-y-4 border-slate-800">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Compass className={`w-5 h-5 text-cyan-400 ${isNavigating ? 'animate-spin' : ''}`} />
                <h4 className="font-bold font-mono text-sm text-white">LIVE NAVIGATION</h4>
              </div>
              <span className="text-xs font-mono text-cyan-400 font-bold">
                {distanceRemaining} m remaining (~{displayRoute.estimatedTime} min)
              </span>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="flex items-center gap-3 p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-200">
                <div className="w-8 h-8 rounded-full bg-cyan-500 text-slate-950 flex items-center justify-center font-bold text-sm shrink-0">
                  ↑
                </div>
                <div>
                  <h5 className="font-bold text-sm text-white">
                    Continue straight through {displayRoute.path[1]?.toUpperCase() || "next zone"}
                  </h5>
                  <p className="text-slate-300">{distanceRemaining} meters to next turn</p>
                </div>
              </div>

              {routeChanged ? (
                <div className="flex items-center gap-3 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-200">
                  <div className="w-8 h-8 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center font-bold text-sm shrink-0">
                    <Zap className="w-4 h-4" />
                  </div>
                  <div>
                    <h5 className="font-bold text-sm text-white">Following updated safer route</h5>
                    <p className="text-slate-300 font-sans">Avoiding high-risk areas detected by live crowd monitoring</p>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-900 border border-slate-800 text-slate-400">
                  <div className="w-8 h-8 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center font-bold text-sm shrink-0">
                    →
                  </div>
                  <div>
                    <h5 className="font-bold text-sm text-slate-200">
                      Turn right at {displayRoute.path[2]?.toUpperCase() || "intersection"}
                    </h5>
                    <p className="text-slate-400 font-sans">Continue to destination</p>
                  </div>
                </div>
              )}
            </div>
          </Card>

          {/* Route Status Panel */}
          <Card className="md:col-span-4 p-5 space-y-4 border-slate-800 flex flex-col justify-between">
            <div className="space-y-3">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest block">
                Route Status
              </span>
              <div className="space-y-2 font-mono text-xs">
                <div className="flex justify-between border-b border-slate-800 pb-1.5">
                  <span className="text-slate-400">STATUS:</span>
                  <span className={`font-bold ${isNavigating ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {isNavigating ? 'NAVIGATING' : 'PAUSED'}
                  </span>
                </div>
                <div className="flex justify-between border-b border-slate-800 pb-1.5">
                  <span className="text-slate-400">MONITORING:</span>
                  <span className={`font-bold ${isPolling ? 'text-cyan-400' : 'text-red-400'}`}>
                    {isPolling ? 'ACTIVE' : 'OFFLINE'}
                  </span>
                </div>
                <div className="flex justify-between border-b border-slate-800 pb-1.5">
                  <span className="text-slate-400">LAST UPDATE:</span>
                  <span className="text-slate-200">{lastUpdate || 'Never'}</span>
                </div>
                <div className="flex justify-between border-b border-slate-800 pb-1.5">
                  <span className="text-slate-400">DISTANCE:</span>
                  <span className="text-slate-200">{displayRoute.distance} m</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">CROWD SAFETY:</span>
                  <span className={`font-bold ${
                    displayRoute.risk === 'LOW' ? 'text-emerald-400' :
                    displayRoute.risk === 'MEDIUM' ? 'text-amber-400' : 'text-red-400'
                  }`}>
                    {displayRoute.risk}
                  </span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Button
                variant="cyan"
                className="w-full"
                onClick={() => setIsNavigating(!isNavigating)}
              >
                {isNavigating ? "Pause Navigation" : "Resume Navigation"}
              </Button>
              
              <div className="text-xs text-slate-400 text-center">
                Route auto-updates every {ROUTE_RECHECK_INTERVAL/1000}s
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
}
