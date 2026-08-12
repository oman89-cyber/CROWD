"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { UserNavbar } from "@/components/layout/UserNavbar";
import { PageHeader } from "@/components/layout/PageHeader";
import { Input } from "@/components/ui/Input";
import { Alert } from "@/components/ui/Alert";
import { DestinationCard } from "@/components/user/DestinationCard";
import { RouteCard } from "@/components/user/RouteCard";
import { ALL_MOCK_DESTINATIONS, INITIAL_USER_ROUTE } from "@/mock/routes";
import { getCrowdAwareRoute } from "@/lib/api";
import { getSession, getSessionId, isSessionValid } from "@/lib/session";
import { UserRoute } from "@/types/route";
import { Search, MapPin, AlertCircle } from "lucide-react";

export default function DestinationPage() {
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [selectedId, setSelectedId] = useState<string>("seat_c124");
  const [currentRoute, setCurrentRoute] = useState<UserRoute | null>(null);
  const [isLoadingRoute, setIsLoadingRoute] = useState<boolean>(false);
  const [routeError, setRouteError] = useState<string>("");
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Check for valid session on mount
  useEffect(() => {
    const session = getSession();
    if (!session) {
      // No session, redirect to ticket verification
      router.push("/verify-ticket");
      return;
    }
    setSessionId(session.sessionId);

    // Set default destination based on user's seat
    if (session.user.destinationZoneId) {
      setSelectedId(session.user.destinationZoneId);
    }
  }, [router]);

  // Fetch route when destination changes
  useEffect(() => {
    if (!sessionId || !selectedId) return;

    const fetchRoute = async () => {
      setIsLoadingRoute(true);
      setRouteError("");
      try {
        const route = await getCrowdAwareRoute(sessionId, selectedId.toUpperCase());
        setCurrentRoute(route);
      } catch (error) {
        console.error("Failed to fetch route:", error);
        setRouteError(error instanceof Error ? error.message : "Failed to fetch route");
        // Fallback to mock route on error
        setCurrentRoute(INITIAL_USER_ROUTE);
      } finally {
        setIsLoadingRoute(false);
      }
    };

    fetchRoute();
  }, [sessionId, selectedId]);

  const filteredDestinations = ALL_MOCK_DESTINATIONS.filter(
    (d) =>
      d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.subtitle.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const activeDestination = ALL_MOCK_DESTINATIONS.find((d) => d.id === selectedId) || ALL_MOCK_DESTINATIONS[0];

  const handleStartNavigation = () => {
    if (currentRoute) {
      // Store the current route in sessionStorage for the navigation page
      try {
        sessionStorage.setItem("current_route", JSON.stringify(currentRoute));
      } catch (error) {
        console.error("Failed to save route:", error);
      }
    }
    router.push("/navigation");
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#080b11]">
      <UserNavbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <PageHeader
          title="Select Destination"
          subtitle="Choose your target stage, facility, or exit corridor for optimized crowd guidance."
        />

        {!sessionId && (
          <Alert variant="error" title="Session Required">
            Please verify your ticket first to use routing features.
          </Alert>
        )}

        {routeError && (
          <Alert variant="warning" title="Route Calculation Issue">
            {routeError}. Showing fallback route.
          </Alert>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left: Search & Destination List */}
          <div className="lg:col-span-7 space-y-4">
            <Input
              placeholder="Search stages, food court, restrooms, exits..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search className="w-4 h-4" />}
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {filteredDestinations.map((dest) => (
                <DestinationCard
                  key={dest.id}
                  id={dest.id}
                  name={dest.name}
                  subtitle={dest.subtitle}
                  distance={dest.distance}
                  time={dest.time}
                  risk={dest.risk}
                  isSelected={selectedId === dest.id}
                  onSelect={setSelectedId}
                />
              ))}
            </div>
          </div>

          {/* Right: Route Details Preview */}
          <div className="lg:col-span-5 space-y-4">
            <h3 className="font-bold font-mono text-sm text-slate-300 uppercase tracking-wider">
              Generated Route Details
            </h3>
            {isLoadingRoute ? (
              <div className="p-8 text-center text-slate-400">
                <div className="animate-spin w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full mx-auto mb-3"></div>
                <p className="text-sm font-mono">Calculating optimal route...</p>
              </div>
            ) : currentRoute ? (
              <RouteCard
                route={currentRoute}
                onStartNavigation={handleStartNavigation}
              />
            ) : (
              <div className="p-8 text-center text-slate-400">
                <AlertCircle className="w-12 h-12 mx-auto mb-3 text-slate-600" />
                <p className="text-sm font-mono">Select a destination to view route</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
