import React from "react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { PredictionChart } from "@/components/charts/PredictionChart";
import { BottleneckPrediction } from "@/types/prediction";
import { TrendingUp, Cpu, RefreshCw, AlertTriangle, ShieldCheck } from "lucide-react";

interface PredictionPanelProps {
  prediction?: BottleneckPrediction;
  onRerouteTrigger?: () => void;
  isRerouted?: boolean;
}

export const PredictionPanel: React.FC<PredictionPanelProps> = ({
  prediction,
  onRerouteTrigger,
  isRerouted = false,
}) => {
  return (
    <div className="space-y-4">
      <Card glow glowColor="cyan" className="p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold font-mono text-base text-white">Density Forecasting Engine</h3>
              <p className="text-xs text-slate-400">Hugging Face Time-Series Transformer & Network Flow ML</p>
            </div>
          </div>

          <Badge risk={prediction?.severity || "HIGH"}>ML MODEL ACTIVE</Badge>
        </div>

        {/* Prediction Chart */}
        <PredictionChart />

        {/* Prediction Card details */}
        {prediction && (
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3 font-mono">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400 uppercase">Target Zone:</span>
              <span className="font-bold text-white text-sm">{prediction.zoneName}</span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-center text-xs">
              <div className="p-2 bg-slate-900 rounded border border-slate-800">
                <span className="text-slate-400 block text-[10px]">CURRENT DENSITY</span>
                <span className="font-bold text-amber-400 text-sm">{prediction.currentDensity}%</span>
              </div>
              <div className="p-2 bg-slate-900 rounded border border-slate-800">
                <span className="text-slate-400 block text-[10px]">PREDICTED (+90s)</span>
                <span className="font-bold text-red-400 text-sm">{prediction.predictedDensity}%</span>
              </div>
            </div>

            <p className="text-xs text-amber-300 flex items-center gap-2 pt-1">
              <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
              <span>Zone C predicted to reach critical density in approximately {prediction.timeToCritical} seconds.</span>
            </p>

            {onRerouteTrigger && (
              <div className="pt-2 flex justify-end">
                {isRerouted ? (
                  <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 bg-emerald-950/40 p-2.5 rounded-lg border border-emerald-500/40 w-full justify-center">
                    <ShieldCheck className="w-4 h-4" />
                    <span>34 Users Rerouted to Corridor B</span>
                  </div>
                ) : (
                  <Button
                    variant="cyan"
                    className="w-full"
                    onClick={onRerouteTrigger}
                    leftIcon={<RefreshCw className="w-4 h-4" />}
                  >
                    Execute Automatic Rerouting (Corridor B)
                  </Button>
                )}
              </div>
            )}
          </div>
        )}

        {/* Backend Hugging Face Payload Schema Box */}
        <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] font-mono space-y-1">
          <div className="flex items-center gap-1.5 text-slate-400 mb-1">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span>Hugging Face Model Payload Schema (Live JSON stream)</span>
          </div>
          <pre className="text-cyan-300 bg-slate-900 p-2 rounded overflow-x-auto text-[10px]">
{`{
  "zoneId": "corridor-c",
  "occupancy": 183,
  "capacity": 300,
  "density": 0.91,
  "risk": "CRITICAL",
  "predictedTimeToCritical": 74
}`}
          </pre>
        </div>
      </Card>
    </div>
  );
};
