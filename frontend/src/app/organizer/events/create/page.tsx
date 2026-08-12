"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { OrganizerSidebar } from "@/components/layout/OrganizerSidebar";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { createEvent } from "@/lib/api";
import { PlusCircle, Calendar, Users, MapPin, ArrowRight } from "lucide-react";

export default function CreateEventPage() {
  const router = useRouter();
  const [name, setName] = useState<string>("TechFest 2026 Summit");
  const [date, setDate] = useState<string>("2026-08-15");
  const [startTime, setStartTime] = useState<string>("09:00");
  const [expectedCrowd, setExpectedCrowd] = useState<number>(5000);
  const [venueName, setVenueName] = useState<string>("Metropolis Arena & Expo Center");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await createEvent({ name, date, startTime, expectedCrowd, venueName });
      if (res.success) {
        router.push(`/organizer/events/${res.eventId}/blueprint`);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-[#080b11]">
      <OrganizerSidebar />

      <main className="flex-1 p-6 max-w-4xl mx-auto space-y-6">
        <PageHeader
          title="Create New Event"
          subtitle="Provision a crowd monitoring instance, register gates, and generate spatial venue graph."
        />

        <Card glow glowColor="cyan" className="p-6 space-y-6">
          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              label="Event Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. TechFest 2026 Summit"
              required
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Event Date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                required
              />

              <Input
                label="Start Time"
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Expected Crowd Size"
                type="number"
                value={expectedCrowd}
                onChange={(e) => setExpectedCrowd(Number(e.target.value))}
                placeholder="5000"
                required
              />

              <Input
                label="Venue Name"
                value={venueName}
                onChange={(e) => setVenueName(e.target.value)}
                placeholder="e.g. Metropolis Arena"
                required
              />
            </div>

            <div className="pt-4 flex justify-end">
              <Button
                type="submit"
                variant="cyan"
                size="lg"
                isLoading={isLoading}
                rightIcon={<ArrowRight className="w-5 h-5" />}
              >
                Create Event & Upload Blueprint
              </Button>
            </div>
          </form>
        </Card>
      </main>
    </div>
  );
}
