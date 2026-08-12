import React from "react";
import { Camera } from "@/types/camera";

interface CameraMarkerProps {
  camera: Camera;
  onClick?: () => void;
}

export const CameraMarker: React.FC<CameraMarkerProps> = ({ camera, onClick }) => {
  const x = camera.x || 100;
  const y = camera.y || 100;

  const statusColor = {
    ONLINE: "#10b981",
    WARNING: "#eab308",
    OFFLINE: "#ef4444",
  }[camera.status];

  return (
    <g className="cursor-pointer group" onClick={onClick} transform={`translate(${x}, ${y})`}>
      {/* Outer Halo */}
      <circle r={10} fill="rgba(15, 23, 42, 0.8)" stroke="#334155" strokeWidth={1} />
      
      {/* Status indicator dot */}
      <circle r={4} fill={statusColor} className={camera.status === "ONLINE" ? "animate-pulse" : ""} />

      {/* Hover tooltip */}
      <title>{`${camera.name} (${camera.id}) - ${camera.status}`}</title>
    </g>
  );
};
