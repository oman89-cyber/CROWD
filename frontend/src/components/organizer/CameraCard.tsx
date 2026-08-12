import React from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Camera } from "@/types/camera";
import { Video, Activity, Eye, AlertCircle } from "lucide-react";

interface CameraCardProps {
  camera: Camera;
  onSelect?: (camera: Camera) => void;
}

export const CameraCard: React.FC<CameraCardProps> = ({ camera, onSelect }) => {
  const isOnline = camera.status === "ONLINE";

  return (
    <Card
      glow={camera.status === "WARNING"}
      glowColor="yellow"
      className="p-4 space-y-3 hover:border-slate-700 transition cursor-pointer"
      onClick={() => onSelect && onSelect(camera)}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded bg-slate-800 text-cyan-400 border border-slate-700">
            <Video className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-bold text-sm text-white font-mono">{camera.id}</h4>
            <span className="text-[10px] text-slate-400 font-mono">{camera.name}</span>
          </div>
        </div>

        <Badge
          variant={camera.status === "ONLINE" ? "low" : camera.status === "WARNING" ? "medium" : "critical"}
          pulse={isOnline}
        >
          {camera.status}
        </Badge>
      </div>

      {/* Simulated Live Video Feed */}
      <div className="relative aspect-video w-full rounded-lg bg-slate-950 border border-slate-800 overflow-hidden flex items-center justify-center group">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:1rem_1rem] opacity-40" />

        {isOnline ? (
          <>
            {/* Bounding box simulation for Hugging Face person detection */}
            <div className="absolute top-4 left-6 w-12 h-20 border border-cyan-400/80 bg-cyan-400/10 rounded flex items-end p-1">
              <span className="text-[8px] font-mono bg-cyan-500 text-slate-950 px-0.5 font-bold">P1</span>
            </div>
            <div className="absolute top-8 right-12 w-14 h-24 border border-cyan-400/80 bg-cyan-400/10 rounded flex items-end p-1">
              <span className="text-[8px] font-mono bg-cyan-500 text-slate-950 px-0.5 font-bold">P2</span>
            </div>
            <div className="absolute bottom-6 left-20 w-10 h-16 border border-emerald-400/80 bg-emerald-400/10 rounded flex items-end p-1">
              <span className="text-[8px] font-mono bg-emerald-500 text-slate-950 px-0.5 font-bold">P3</span>
            </div>

            {/* Hugging Face AI Tag */}
            <div className="absolute top-2 left-2 z-10 flex items-center gap-1.5 px-2 py-0.5 rounded bg-slate-900/90 border border-slate-700 text-[9px] font-mono text-cyan-300">
              <Eye className="w-3 h-3 text-cyan-400" />
              <span>Hugging Face Detector (YOLOv8)</span>
            </div>

            <div className="absolute bottom-2 right-2 z-10 flex items-center gap-2 px-2 py-0.5 rounded bg-black/80 text-[10px] font-mono text-slate-300">
              <span>{camera.fps} FPS</span>
              <span className="text-emerald-400 font-bold">{camera.detectedCount} Detected</span>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center gap-2 text-slate-500 text-xs font-mono">
            <AlertCircle className="w-6 h-6 text-red-500/60" />
            <span>VIDEO FEED OFFLINE</span>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between text-xs font-mono text-slate-400 pt-1">
        <span>Zone: <strong className="text-slate-200">{camera.zoneId.toUpperCase()}</strong></span>
        <span>RTSP Direct Stream</span>
      </div>
    </Card>
  );
};
