import React from "react";
import { StatCard } from "@/components/ui/StatCard";
import { Users, UserCheck, Activity, AlertTriangle, TrendingUp } from "lucide-react";

interface CrowdOverviewProps {
  totalPeople?: number;
  activeUsers?: number;
  avgDensity?: number;
  criticalZonesCount?: number;
  predictedBottlenecks?: number;
}

export const CrowdOverview: React.FC<CrowdOverviewProps> = ({
  totalPeople = 4820,
  activeUsers = 482,
  avgDensity = 64,
  criticalZonesCount = 1,
  predictedBottlenecks = 2,
}) => {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4">
      <StatCard
        title="Total Crowd"
        value={totalPeople.toLocaleString()}
        subtitle="Venue Capacity: 6,500"
        icon={<Users className="w-5 h-5 text-cyan-400" />}
        trend={{ value: "+120/m", isPositive: true }}
      />

      <StatCard
        title="Active Users"
        value={activeUsers.toLocaleString()}
        subtitle="App Tracked ID"
        icon={<UserCheck className="w-5 h-5 text-emerald-400" />}
        trend={{ value: "10% Total", isPositive: true }}
      />

      <StatCard
        title="Avg Density"
        value={`${avgDensity}%`}
        subtitle="Overall Capacity"
        icon={<Activity className="w-5 h-5 text-amber-400" />}
        glowColor={avgDensity > 75 ? "yellow" : undefined}
      />

      <StatCard
        title="Critical Zones"
        value={criticalZonesCount}
        subtitle="Zone C (>85%)"
        icon={<AlertTriangle className="w-5 h-5 text-red-400" />}
        glowColor="red"
        trend={{ value: "Action Req", isNegative: true }}
      />

      <StatCard
        title="Bottlenecks"
        value={predictedBottlenecks}
        subtitle="Predicted in 90s"
        icon={<TrendingUp className="w-5 h-5 text-purple-400" />}
        glowColor="cyan"
      />
    </div>
  );
};
