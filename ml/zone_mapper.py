"""CrowdShield AI — Camera-to-Venue Zone Mapper.

Maps pixel-space track positions to logical venue zone IDs using
configurable rectangular regions.  Each camera can define its own
region-to-zone mapping; later a proper camera calibration layer
can replace the rectangles with homography transforms.

The zone IDs intentionally match the venue graph from ``data/venue.json``
to avoid duplicating the venue topology.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ZoneRegion:
    """A rectangular pixel region mapped to a logical venue zone."""

    zone_id: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    def contains(self, x: float, y: float) -> bool:
        """Return True if (x, y) falls inside this region."""
        return self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max


class ZoneMapper:
    """Map pixel coordinates to venue zone IDs.

    Parameters
    ----------
    regions : list[ZoneRegion]
        Ordered list of rectangular regions.  The *first* matching region
        wins when regions overlap.
    default_zone : str
        Returned when a point falls outside all defined regions.
    """

    def __init__(
        self,
        regions: list[ZoneRegion] | None = None,
        default_zone: str = "UNKNOWN",
    ) -> None:
        self.regions: list[ZoneRegion] = regions or []
        self.default_zone = default_zone

    def add_region(self, region: ZoneRegion) -> None:
        """Append a region to the mapper."""
        self.regions.append(region)

    def get_zone(self, x: float, y: float) -> str:
        """Return the zone ID for pixel coordinate (x, y).

        Returns ``default_zone`` if no region contains the point.
        """
        for region in self.regions:
            if region.contains(x, y):
                return region.zone_id
        return self.default_zone


# ---------------------------------------------------------------------------
# Default zone layouts for demo cameras
# ---------------------------------------------------------------------------

def create_demo_zone_mapper(
    frame_width: int = 640,
    frame_height: int = 480,
) -> ZoneMapper:
    """Create a zone mapper with a default layout suitable for demo videos.

    Divides the frame into logical venue zones:

    - Left third   → GATE_C    (entry area)
    - Center third → CORRIDOR_C (main walkway)
    - Right third  → BLOCK_C    (seating area)
    - Top strip    → FOOD_B     (overhead signage / food area)
    - Bottom strip → WASHROOM_C (lower area)

    These map to the existing venue graph zone IDs so the crowd
    pipeline can flow directly into the simulation/routing layers.
    """
    w = frame_width
    h = frame_height

    mapper = ZoneMapper()

    # Top strip — food court area (above crowd)
    mapper.add_region(ZoneRegion(
        zone_id="FOOD_B",
        x_min=0, y_min=0,
        x_max=w, y_max=h * 0.15,
    ))

    # Bottom strip — washroom area
    mapper.add_region(ZoneRegion(
        zone_id="WASHROOM_C",
        x_min=0, y_min=h * 0.85,
        x_max=w, y_max=h,
    ))

    # Left third — gate area
    mapper.add_region(ZoneRegion(
        zone_id="GATE_C",
        x_min=0, y_min=h * 0.15,
        x_max=w * 0.33, y_max=h * 0.85,
    ))

    # Center third — corridor
    mapper.add_region(ZoneRegion(
        zone_id="CORRIDOR_C",
        x_min=w * 0.33, y_min=h * 0.15,
        x_max=w * 0.66, y_max=h * 0.85,
    ))

    # Right third — seating block
    mapper.add_region(ZoneRegion(
        zone_id="BLOCK_C",
        x_min=w * 0.66, y_min=h * 0.15,
        x_max=w, y_max=h * 0.85,
    ))

    return mapper
