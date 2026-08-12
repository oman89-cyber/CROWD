"use client";

import React, { useState, use } from "react";
import { useRouter } from "next/navigation";
import { OrganizerSidebar } from "@/components/layout/OrganizerSidebar";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Upload, FileImage, CheckCircle2, ArrowRight } from "lucide-react";

export default function BlueprintPage({ params }: { params: Promise<{ eventId: string }> }) {
  const { eventId } = use(params);
  const router = useRouter();
  const [uploaded, setUploaded] = useState<boolean>(true);
  const [fileName, setFileName] = useState<string>("metropolis-arena-floorplan.svg");

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFileName(e.dataTransfer.files[0].name);
      setUploaded(true);
    }
  };

  return (
    <div className="min-h-screen flex bg-[#080b11]">
      <OrganizerSidebar eventId={eventId} />

      <main className="flex-1 p-6 max-w-4xl mx-auto space-y-6">
        <PageHeader
          title="Upload Venue Architectural Blueprint"
          subtitle="Upload high-resolution PNG, JPG, or SVG blueprint to construct spatial zone mesh."
        />

        <Card glow glowColor="cyan" className="p-6 space-y-6">
          {/* Drag and Drop Zone */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className="border-2 border-dashed border-cyan-500/40 hover:border-cyan-400 bg-slate-950 p-8 rounded-2xl text-center space-y-3 cursor-pointer transition"
          >
            <div className="mx-auto w-14 h-14 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 flex items-center justify-center">
              <Upload className="w-7 h-7" />
            </div>
            <div>
              <h4 className="font-bold text-base font-mono text-white">
                Drag & Drop Architectural CAD / Blueprint File
              </h4>
              <p className="text-xs text-slate-400 mt-1">Supports PNG, JPG, or SVG vector floorplans (Max 50MB)</p>
            </div>
          </div>

          {/* Uploaded File Preview */}
          {uploaded && (
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between font-mono text-xs">
              <div className="flex items-center gap-3">
                <FileImage className="w-5 h-5 text-cyan-400" />
                <div>
                  <span className="font-bold text-white block">{fileName}</span>
                  <span className="text-[10px] text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Ready for spatial zone mapping
                  </span>
                </div>
              </div>

              <Button
                variant="cyan"
                onClick={() => router.push(`/organizer/events/${eventId}/venue-editor`)}
                rightIcon={<ArrowRight className="w-4 h-4" />}
              >
                Open Venue Editor
              </Button>
            </div>
          )}
        </Card>
      </main>
    </div>
  );
}
