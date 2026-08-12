"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { UserNavbar } from "@/components/layout/UserNavbar";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { QrCode, CheckCircle2, Shield, ArrowRight, Camera } from "lucide-react";

export default function ScanPage() {
  const router = useRouter();
  const [isScanning, setIsScanning] = useState<boolean>(true);
  const [isSuccess, setIsSuccess] = useState<boolean>(false);

  const handleSimulateScan = () => {
    setIsScanning(false);
    setIsSuccess(true);
  };

  useEffect(() => {
    // Auto simulate scan after 2.5 seconds for smooth hackathon demo
    const timer = setTimeout(() => {
      if (isScanning) {
        handleSimulateScan();
      }
    }, 2500);

    return () => clearTimeout(timer);
  }, [isScanning]);

  return (
    <div className="min-h-screen flex flex-col bg-[#080b11]">
      <UserNavbar />

      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md space-y-6">
          <div className="text-center space-y-2">
            <h1 className="text-2xl font-bold font-mono text-white">Event Gate Check-In</h1>
            <p className="text-xs text-slate-400 font-sans">
              Scan your event QR code at Gate A scanner for anonymous tracking assignment.
            </p>
          </div>

          <Card glow glowColor={isSuccess ? "green" : "cyan"} className="p-6 space-y-6">
            {!isSuccess ? (
              <div className="space-y-6 text-center">
                {/* Simulated Camera Scanner Viewport */}
                <div className="relative aspect-square w-full rounded-2xl bg-slate-950 border-2 border-dashed border-cyan-500/50 flex flex-col items-center justify-center overflow-hidden group">
                  <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:1rem_1rem] opacity-30" />

                  {/* Corner Target Markers */}
                  <div className="absolute top-4 left-4 w-8 h-8 border-t-2 border-l-2 border-cyan-400" />
                  <div className="absolute top-4 right-4 w-8 h-8 border-t-2 border-r-2 border-cyan-400" />
                  <div className="absolute bottom-4 left-4 w-8 h-8 border-b-2 border-l-2 border-cyan-400" />
                  <div className="absolute bottom-4 right-4 w-8 h-8 border-b-2 border-r-2 border-cyan-400" />

                  {/* Scanning Laser Line */}
                  <div className="w-full h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-pulse shadow-[0_0_15px_#00f0ff]" />

                  <QrCode className="w-20 h-20 text-cyan-400/40 my-4 animate-pulse" />

                  <p className="text-xs font-mono text-cyan-300 z-10 font-medium">
                    Align QR code within frame
                  </p>
                </div>

                <Button
                  variant="cyan"
                  className="w-full"
                  onClick={handleSimulateScan}
                  leftIcon={<Camera className="w-4 h-4" />}
                >
                  Simulate Instant Scan
                </Button>
              </div>
            ) : (
              <div className="space-y-6 text-center">
                <Alert variant="success" title="Check-In Successful">
                  Anonymous Crowd Track ID assigned successfully.
                </Alert>

                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-left font-mono text-xs space-y-3">
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">ASSIGNED CROWD ID:</span>
                    <span className="font-bold text-cyan-400 text-sm">CS-8A41F</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">ENTRY GATE:</span>
                    <span className="text-slate-200">Gate A (North Entry)</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">INITIAL ZONE:</span>
                    <span className="text-emerald-400 font-bold">Gate A</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">PRIVACY PROTOCOL:</span>
                    <span className="text-slate-400">Zero PII / Fully Anonymized</span>
                  </div>
                </div>

                <Button
                  variant="cyan"
                  className="w-full"
                  onClick={() => router.push("/dashboard")}
                  rightIcon={<ArrowRight className="w-4 h-4" />}
                >
                  Enter Attendee Dashboard
                </Button>
              </div>
            )}
          </Card>
        </div>
      </main>
    </div>
  );
}
