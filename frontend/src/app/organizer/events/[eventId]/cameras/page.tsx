"use client";

import React, { useState, use } from "react";
import { OrganizerSidebar } from "@/components/layout/OrganizerSidebar";
import { PageHeader } from "@/components/layout/PageHeader";
import { CameraCard } from "@/components/organizer/CameraCard";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Modal } from "@/components/ui/Modal";
import { MOCK_CAMERAS } from "@/mock/cameras";
import { Camera } from "@/types/camera";
import { Plus, Video, Eye, ShieldCheck } from "lucide-react";

export default function CamerasPage({ params }: { params: Promise<{ eventId: string }> }) {
  const { eventId } = use(params);
  const [cameras, setCameras] = useState<Camera[]>(MOCK_CAMERAS);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // Form state
  const [camId, setCamId] = useState<string>("CAM-07");
  const [camName, setCamName] = useState<string>("Corridor D Entrance");
  const [zoneId, setZoneId] = useState<string>("corridor-d");
  const [videoSource, setVideoSource] = useState<string>("rtsp://camera-07.local/live");

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    const newCam: Camera = {
      id: camId,
      name: camName,
      zoneId,
      status: "ONLINE",
      videoSource,
      fps: 30,
      detectedCount: 22,
    };
    setCameras([...cameras, newCam]);
    setIsModalOpen(false);
  };

  return (
    <div className="min-h-screen flex bg-[#080b11]">
      <OrganizerSidebar eventId={eventId} />

      <main className="flex-1 p-6 space-y-6 max-w-[1600px] mx-auto">
        <PageHeader
          title="Optical Vision Camera Registration"
          subtitle="Provision RTSP camera feeds feeding person-detection bounding boxes into Hugging Face backend."
          actions={
            <Button
              variant="cyan"
              onClick={() => setIsModalOpen(true)}
              leftIcon={<Plus className="w-4 h-4" />}
            >
              Register Camera
            </Button>
          }
        />

        {/* Camera Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cameras.map((cam) => (
            <CameraCard key={cam.id} camera={cam} />
          ))}
        </div>

        {/* Register Camera Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Register New CCTV Vision Camera"
        >
          <form onSubmit={handleRegister} className="space-y-4 font-mono text-xs">
            <Input
              label="Camera ID"
              value={camId}
              onChange={(e) => setCamId(e.target.value)}
              required
            />

            <Input
              label="Camera Name"
              value={camName}
              onChange={(e) => setCamName(e.target.value)}
              required
            />

            <Select
              label="Assigned Venue Zone"
              value={zoneId}
              onChange={(e) => setZoneId(e.target.value)}
              options={[
                { value: "gate-a", label: "Gate A" },
                { value: "gate-b", label: "Gate B" },
                { value: "gate-c", label: "Gate C" },
                { value: "corridor-c", label: "Corridor C" },
                { value: "corridor-d", label: "Corridor D" },
                { value: "main-stage", label: "Main Stage" },
                { value: "food-court", label: "Food Court" },
              ]}
            />

            <Input
              label="RTSP Video Source Stream URL"
              value={videoSource}
              onChange={(e) => setVideoSource(e.target.value)}
              required
            />

            <div className="pt-3 flex justify-end">
              <Button type="submit" variant="cyan" leftIcon={<ShieldCheck className="w-4 h-4" />}>
                Register & Bind Feed
              </Button>
            </div>
          </form>
        </Modal>
      </main>
    </div>
  );
}
