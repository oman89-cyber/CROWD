import React from "react";
import { VenuePath as TVenuePath, VenueZone } from "@/types/venue";

interface VenuePathProps {
  path: TVenuePath;
  zones: VenueZone[];
}

export const VenuePath: React.FC<VenuePathProps> = ({ path, zones }) => {
  const fromZone = zones.find((z) => z.id === path.from);
  const toZone = zones.find((z) => z.id === path.to);

  if (!fromZone || !toZone) return null;

  const fromCenter = fromZone.center || [
    fromZone.polygon.reduce((a, b) => a + b[0], 0) / fromZone.polygon.length,
    fromZone.polygon.reduce((a, b) => a + b[1], 0) / fromZone.polygon.length,
  ];

  const toCenter = toZone.center || [
    toZone.polygon.reduce((a, b) => a + b[0], 0) / toZone.polygon.length,
    toZone.polygon.reduce((a, b) => a + b[1], 0) / toZone.polygon.length,
  ];

  return (
    <line
      x1={fromCenter[0]}
      y1={fromCenter[1]}
      x2={toCenter[0]}
      y2={toCenter[1]}
      stroke="rgba(51, 65, 85, 0.4)"
      strokeWidth={2}
      strokeDasharray="4 4"
      className="pointer-events-none"
    />
  );
};
