"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { UserNavbar } from "@/components/layout/UserNavbar";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Alert } from "@/components/ui/Alert";
import { verifyTicket } from "@/lib/api";
import { saveSession } from "@/lib/session";
import { Ticket, QrCode, CheckCircle2, ArrowRight, ShieldCheck } from "lucide-react";

export default function VerifyTicketPage() {
  const router = useRouter();
  const [ticketId, setTicketId] = useState<string>("T0004");
  const [eventCode, setEventCode] = useState<string>("TF-2026");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isVerified, setIsVerified] = useState<boolean>(false);
  const [verificationData, setVerificationData] = useState<any>(null);
  const [error, setError] = useState<string>("");

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    try {
      const res = await verifyTicket(ticketId, eventCode);
      if (res.success) {
        setIsVerified(true);
        setVerificationData(res);
        // Save session for use in other pages
        saveSession(res.user);
      }
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Failed to verify ticket");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#080b11]">
      <UserNavbar />

      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md space-y-6">
          <div className="text-center space-y-2">
            <div className="mx-auto w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 flex items-center justify-center">
              <Ticket className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold font-mono text-white">Event Ticket Verification</h1>
            <p className="text-xs text-slate-400 font-sans">
              Enter your event credential or ticket code to unlock personalized crowd navigation.
            </p>
          </div>

          <Card glow glowColor={isVerified ? "green" : "cyan"} className="p-6 space-y-6">
            {!isVerified ? (
              <form onSubmit={handleVerify} className="space-y-4">
                {error && (
                  <Alert variant="error" title="Verification Failed">
                    {error}
                  </Alert>
                )}

                <Input
                  label="Ticket ID"
                  value={ticketId}
                  onChange={(e) => setTicketId(e.target.value)}
                  placeholder="e.g. T0004"
                  required
                />

                <Input
                  label="Event Access Code"
                  value={eventCode}
                  onChange={(e) => setEventCode(e.target.value)}
                  placeholder="e.g. TF-2026"
                  required
                />

                <Button
                  type="submit"
                  variant="cyan"
                  className="w-full"
                  isLoading={isLoading}
                  leftIcon={<ShieldCheck className="w-4 h-4" />}
                >
                  Verify Ticket
                </Button>

                <div className="relative py-2 flex items-center justify-center">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-slate-800" />
                  </div>
                  <span className="relative px-2 bg-slate-900 text-[10px] font-mono text-slate-500 uppercase">
                    OR
                  </span>
                </div>

                <Link href="/scan" className="block w-full">
                  <Button variant="outline" className="w-full" leftIcon={<QrCode className="w-4 h-4 text-cyan-400" />}>
                    Scan Ticket QR Code
                  </Button>
                </Link>
              </form>
            ) : (
              <div className="space-y-6 text-center">
                <Alert variant="success" title="Ticket Verified Successfully">
                  {verificationData?.message || "Your ticket has been authenticated."}
                </Alert>

                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-left font-mono text-xs space-y-2">
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">SESSION ID:</span>
                    <span className="font-bold text-white">{verificationData?.user?.crowdId || "N/A"}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">TICKET ID:</span>
                    <span className="text-slate-200">{verificationData?.user?.ticketId || ticketId}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">GATE:</span>
                    <span className="font-bold text-emerald-400">{verificationData?.user?.gateAssigned || "N/A"}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">PARKING:</span>
                    <span className="text-cyan-400">{verificationData?.user?.currentZoneId?.toUpperCase() || "N/A"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">SEAT:</span>
                    <span className="font-bold text-purple-400">{verificationData?.user?.destinationZoneId?.toUpperCase() || "N/A"}</span>
                  </div>
                </div>

                <Button
                  variant="cyan"
                  className="w-full"
                  onClick={() => router.push("/dashboard")}
                  rightIcon={<ArrowRight className="w-4 h-4" />}
                >
                  Continue to Dashboard
                </Button>
              </div>
            )}
          </Card>
        </div>
      </main>
    </div>
  );
}
