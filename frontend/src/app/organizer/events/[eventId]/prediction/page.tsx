"use client";

import React, { use } from "react";
import { OrganizerSidebar } from "@/components/layout/OrganizerSidebar";
import { PageHeader } from "@/components/layout/PageHeader";
import { PredictionPanel } from "@/components/organizer/PredictionPanel";
import { useMockCrowdEngine } from "@/hooks/useMockCrowdEngine";
import { MOCK_BOTTLENECK_PREDICTION } from "@/mock/predictions";

export default function PredictionPage({ params }: { params: Promise<{ eventId: string }> }) {
  const { eventId } = use(params);

  const {
    bottleneckAlert,
    isRerouted,
    triggerBottleneckSequence,
  } = useMockCrowdEngine(true);

  return (
    <div className="min-h-screen flex bg-[#080b11]">
      <OrganizerSidebar eventId={eventId} />

      <main className="flex-1 p-6 space-y-6 max-w-5xl mx-auto">
        <PageHeader
          title="Hugging Face AI Bottleneck Forecasting"
          subtitle="Deep learning predictive time-series models evaluating corridor throughput and surge risks."
        />

        <PredictionPanel
          prediction={bottleneckAlert || MOCK_BOTTLENECK_PREDICTION}
          onRerouteTrigger={triggerBottleneckSequence}
          isRerouted={isRerouted}
        />
      </main>
    </div>
  );
}
