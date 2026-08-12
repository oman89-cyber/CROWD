"use client";

import React, { useState, use } from "react";
import { useRouter } from "next/navigation";
import { OrganizerSidebar } from "@/components/layout/OrganizerSidebar";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Modal } from "@/components/ui/Modal";
import { Badge } from "@/components/ui/Badge";
import { VenueMap } from "@/components/venue/VenueMap";
import { MOCK_VENUE } from "@/mock/venue";
import { VenueZone } from "@/types/venue";
import {
  MousePointer,
  Square,
  Share2,
  DoorOpen,
  LogOut,
  Camera,
  Save,
  Plus,
  CheckCircle2,
} from "lucide-react";

export type EditorTool = "select" | "zone" | "path" | "gate" | "exit" | "camera";

export default function VenueEditorPage({ params }: { params: Promise<{ eventId: string }> }) {
  const { eventId } = use(params);
  const router = useRouter();

  const [activeTool, setActiveTool] = useState<EditorTool>("select");
  const [zones, setZones] = useState<VenueZone[]>(MOCK_VENUE.zones);
  const [selectedZone, setSelectedZone] = useState<VenueZone | null>(MOCK_VENUE.zones[5]);
  const [isSaved, setIsSaved] = useState<boolean>(false);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // Edit fields
  const [editName, setEditName] = useState<string>("");
  const [editCapacity, setEditCapacity] = useState<number>(300);
  const [editType, setEditType] = useState<string>("corridor");

  const handleZoneSelect = (zone: VenueZone) => {
    setSelectedZone(zone);
    setEditName(zone.name);
    setEditCapacity(zone.capacity);
    setEditType(zone.type || "corridor");
  };

  const handleSaveZoneDetails = () => {
    if (!selectedZone) return;
    setZones((prev) =>
      prev.map((z) =>
        z.id === selectedZone.id
          ? { ...z, name: editName, capacity: editCapacity, type: editType as VenueZone["type"] }
          : z
      )
    );
    setIsModalOpen(false);
  };

  const handleSaveGraph = () => {
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 3000);
  };

  return (
    <div className="min-h-screen flex bg-[#080b11]">
      <OrganizerSidebar eventId={eventId} />

      <main className="flex-1 p-6 space-y-6 max-w-[1600px] mx-auto">
        <PageHeader
          title="Interactive Venue Spatial Graph Editor"
          subtitle="Define polygon zone boundaries, graph connectivity paths, access gates, and vision cameras."
          actions={
            <Button
              variant="cyan"
              onClick={handleSaveGraph}
              leftIcon={<Save className="w-4 h-4" />}
            >
              {isSaved ? "Venue Graph Saved!" : "Save Venue Graph"}
            </Button>
          }
        />

        {/* Top Interactive Toolbar */}
        <Card className="p-3 bg-slate-900/90 border-slate-800 flex items-center justify-between gap-4 font-mono">
          <div className="flex items-center gap-2 overflow-x-auto">
            <Button
              size="sm"
              variant={activeTool === "select" ? "cyan" : "secondary"}
              onClick={() => setActiveTool("select")}
              leftIcon={<MousePointer className="w-4 h-4" />}
            >
              Select
            </Button>

            <Button
              size="sm"
              variant={activeTool === "zone" ? "cyan" : "secondary"}
              onClick={() => setActiveTool("zone")}
              leftIcon={<Square className="w-4 h-4" />}
            >
              + Zone Polygon
            </Button>

            <Button
              size="sm"
              variant={activeTool === "path" ? "cyan" : "secondary"}
              onClick={() => setActiveTool("path")}
              leftIcon={<Share2 className="w-4 h-4" />}
            >
              + Graph Path Edge
            </Button>

            <Button
              size="sm"
              variant={activeTool === "gate" ? "cyan" : "secondary"}
              onClick={() => setActiveTool("gate")}
              leftIcon={<DoorOpen className="w-4 h-4" />}
            >
              + Access Gate
            </Button>

            <Button
              size="sm"
              variant={activeTool === "exit" ? "cyan" : "secondary"}
              onClick={() => setActiveTool("exit")}
              leftIcon={<LogOut className="w-4 h-4" />}
            >
              + Evacuation Exit
            </Button>

            <Button
              size="sm"
              variant={activeTool === "camera" ? "cyan" : "secondary"}
              onClick={() => setActiveTool("camera")}
              leftIcon={<Camera className="w-4 h-4" />}
            >
              + CCTV Camera
            </Button>
          </div>

          <Badge risk="LOW">ACTIVE TOOL: {activeTool.toUpperCase()}</Badge>
        </Card>

        {/* Editor Main Canvas & Property Inspector Drawer */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-8">
            <Card glow glowColor="cyan" className="p-3">
              <VenueMap
                venue={{ ...MOCK_VENUE, zones }}
                selectedZoneId={selectedZone?.id}
                onZoneSelect={handleZoneSelect}
                mode="editor"
                showCrowdLayer={false}
                showCameras={true}
              />
            </Card>
          </div>

          {/* Right Inspector Drawer */}
          <div className="lg:col-span-4 space-y-4">
            <Card className="p-5 space-y-4 border-slate-800 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h4 className="font-bold text-sm text-white">Zone Inspector</h4>
                {selectedZone && <Badge risk={selectedZone.risk}>{selectedZone.id}</Badge>}
              </div>

              {selectedZone ? (
                <div className="space-y-4">
                  <Input
                    label="Zone Name"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                  />

                  <Input
                    label="Max Capacity"
                    type="number"
                    value={editCapacity}
                    onChange={(e) => setEditCapacity(Number(e.target.value))}
                  />

                  <Select
                    label="Zone Type"
                    value={editType}
                    onChange={(e) => setEditType(e.target.value)}
                    options={[
                      { value: "corridor", label: "Corridor / Transit" },
                      { value: "gate", label: "Access Gate" },
                      { value: "stage", label: "Main Stage / Attraction" },
                      { value: "food", label: "Food Court" },
                      { value: "restroom", label: "Restroom" },
                      { value: "exit", label: "Exit Corridor" },
                    ]}
                  />

                  <div className="pt-2 flex gap-2">
                    <Button variant="cyan" className="w-full" onClick={handleSaveZoneDetails}>
                      Apply Zone Changes
                    </Button>
                  </div>
                </div>
              ) : (
                <p className="text-slate-400">Click on any zone polygon in the editor to inspect properties.</p>
              )}
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
