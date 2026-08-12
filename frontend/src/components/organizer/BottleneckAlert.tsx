import React from "react";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { BottleneckPrediction } from "@/types/prediction";
import { ShieldAlert, RefreshCcw } from "lucide-react";

interface BottleneckAlertProps {
  prediction: BottleneckPrediction;
  reroutedCount?: number;
  onTriggerReroute?: () => void;
}

export const BottleneckAlert: React.FC<BottleneckAlertProps> = ({
  prediction,
  reroutedCount = 0,
  onTriggerReroute,
}) => {
  return (
    <Alert
      variant={prediction.severity}
      title={`CRITICAL BOTTLENECK PREDICTED: ${prediction.zoneName}`}
      action={
        onTriggerReroute ? (
          <Button
            size="sm"
            variant="cyan"
            onClick={onTriggerReroute}
            leftIcon={<RefreshCcw className="w-3.5 h-3.5 animate-spin" />}
          >
            Auto-Reroute Users
          </Button>
        ) : undefined
      }
    >
      <div className="space-y-1 font-mono">
        <p>
          Density in <span className="font-bold text-white">{prediction.zoneName}</span> is current{" "}
          <span className="text-red-400 font-bold">{prediction.currentDensity}%</span> and predicted to reach{" "}
          <span className="text-red-400 font-bold">{prediction.predictedDensity}%</span> in{" "}
          <span className="underline">{prediction.timeToCritical} seconds</span>.
        </p>

        {reroutedCount > 0 ? (
          <p className="text-emerald-400 font-bold flex items-center gap-1.5 mt-1">
            <ShieldAlert className="w-4 h-4" />
            SUCCESS: {reroutedCount} active heading users have been automatically re-routed via Corridor B.
          </p>
        ) : (
          <p className="text-slate-300">
            Recommended Action: {prediction.recommendedAction || "Re-route incoming attendees via Corridor B."}
          </p>
        )}
      </div>
    </Alert>
  );
};
