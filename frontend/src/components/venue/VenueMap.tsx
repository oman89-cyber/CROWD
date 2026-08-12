"use client";

import React, { useState } from "react";
import { Venue, VenueZone as TVenueZone } from "@/types/venue";
import { CrowdAgent } from "@/types/crowd";
import { UserRoute } from "@/types/route";
import { Camera } from "@/types/camera";
import { VenueZone } from "./VenueZone";
import { VenuePath } from "./VenuePath";
import { CameraMarker } from "./CameraMarker";
import { GateMarker } from "./GateMarker";
import { ExitMarker } from "./ExitMarker";
import { RouteLayer } from "./RouteLayer";
import { UserMarker } from "./UserMarker";
import { CrowdAgentLayer } from "./CrowdAgentLayer";

export type VenueMapMode = "user" | "organizer" | "simulation" | "editor";

interface VenueMapProps {
  venue: Venue;
  agents?: CrowdAgent[];
  userRoute?: UserRoute | null;
  selectedZoneId?: string | null;
  onZoneSelect?: (zone: TVenueZone) => void;
  cameras?: Camera[];
  mode?: VenueMapMode;
  showCrowdLayer?: boolean;
  showCameras?: boolean;
  showHeatmap?: boolean;
  onAddPoint?: (x: number, y: number) => void;
}

export const VenueMap: React.FC<VenueMapProps> = ({
  venue,
  agents = [],
  userRoute = null,
  selectedZoneId = null,
  onZoneSelect,
  cameras = [],
  mode = "organizer",
  showCrowdLayer = true,
  showCameras = true,
  onAddPoint,
}) => {
  const [hoveredZone, setHoveredZone] = useState<TVenueZone | null>(null);

  const handleSvgClick = (e: React.MouseEvent<SVGSVGElement>) => {
    if (mode === "editor" && onAddPoint) {
      const rect = e.currentTarget.getBoundingClientRect();
      const x = Math.round(((e.clientX - rect.left) / rect.width) * venue.width);
      const y = Math.round(((e.clientY - rect.top) / rect.height) * venue.height);
      onAddPoint(x, y);
    }
  };

  return (
    <div className="relative w-full aspect-[4/3] max-h-[650px] bg-[#070a10] rounded-2xl border border-slate-800/90 overflow-hidden shadow-2xl group">
      {/* Background Grid Pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:2rem_2rem] opacity-20 pointer-events-none" />

      {/* Mode Tag */}
      <div className="absolute top-3 left-3 z-20 flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/80 border border-slate-800 backdrop-blur-md text-[11px] font-mono text-slate-300">
        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
        <span className="uppercase font-bold tracking-wider">{mode} MAP VIEW</span>
      </div>

      {/* Heatmap Legend */}
      <div className="absolute bottom-3 right-3 z-20 hidden sm:flex items-center gap-3 px-3 py-1.5 rounded-lg bg-slate-950/90 border border-slate-800 backdrop-blur-md text-[10px] font-mono text-slate-300">
        <span className="text-slate-400 font-bold uppercase">Density:</span>
        <div className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
          <span>Low</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
          <span>Med</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-orange-500" />
          <span>High</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />
          <span>Critical</span>
        </div>
      </div>

      {/* Interactive SVG Layer */}
      <svg
        viewBox={`0 0 ${venue.width} ${venue.height}`}
        className="w-full h-full relative z-0 select-none"
        onClick={handleSvgClick}
      >
        {/* Render Paths connecting zones */}
        {venue.paths.map((p) => (
          <VenuePath key={p.id} path={p} zones={venue.zones} />
        ))}

        {/* Render Zones */}
        {venue.zones.map((zone) => (
          <VenueZone
            key={zone.id}
            zone={zone}
            isSelected={selectedZoneId === zone.id}
            isHighlighted={hoveredZone?.id === zone.id}
            onClick={() => onZoneSelect && onZoneSelect(zone)}
            showDetails={mode !== "user" || selectedZoneId === zone.id || zone.id === "corridor-c"}
          />
        ))}

        {/* Render User Route Navigation Line */}
        {userRoute && <RouteLayer route={userRoute} isAlternative={userRoute.isAlternative} />}

        {/* Render User Animated Position Marker */}
        {userRoute && userRoute.points && userRoute.points.length >= 2 && (
          <UserMarker points={userRoute.points} isNavigating={true} />
        )}

        {/* Render Gates */}
        {venue.gates?.map((g) => (
          <GateMarker key={g.id} gate={g} />
        ))}

        {/* Render Exits */}
        {venue.exits?.map((e) => (
          <ExitMarker key={e.id} exit={e} />
        ))}

        {/* Render Cameras if toggled */}
        {showCameras &&
          cameras.map((cam) => (
            <CameraMarker key={cam.id} camera={cam} />
          ))}
      </svg>

      {/* HTML Canvas Layer for 60fps Crowd Agents & Glowing User Dot */}
      {showCrowdLayer && (
        <CrowdAgentLayer
          agents={agents}
          width={venue.width}
          height={venue.height}
          showUserOnly={mode === "user" && false}
        />
      )}
    </div>
  );
};
