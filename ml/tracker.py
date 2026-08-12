"""CrowdShield AI — Lightweight Centroid-Distance Object Tracker.

Converts frame-level person detections into persistent anonymous track IDs
using centroid-distance matching.  Designed to be replaced by ByteTrack or
a more advanced tracker later — the interface is kept minimal and modular.

Algorithm
---------
1. Compute the centroid of each new detection's bounding box.
2. Compute pairwise Euclidean distances between existing track centroids
   and new detection centroids.
3. Greedily match closest pairs under ``max_distance``.
4. Matched tracks: update position, reset ``missed_frames``, increment ``age``.
5. Unmatched detections: create new tracks.
6. Unmatched tracks: increment ``missed_frames``; remove after
   ``max_missed_frames`` consecutive misses.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Track data object
# ---------------------------------------------------------------------------

@dataclass
class Track:
    """A single anonymous person track."""

    track_id: str
    bbox: list[float]           # [x1, y1, x2, y2]
    center_x: float
    center_y: float
    confidence: float
    age: int = 1                # number of frames this track has existed
    missed_frames: int = 0      # consecutive frames without a matching detection

    def to_dict(self) -> dict:
        return {
            "track_id": self.track_id,
            "bbox": [round(v, 1) for v in self.bbox],
            "center": [round(self.center_x, 1), round(self.center_y, 1)],
            "confidence": round(self.confidence, 4),
            "age": self.age,
            "missed_frames": self.missed_frames,
        }


# ---------------------------------------------------------------------------
# Tracker
# ---------------------------------------------------------------------------

class CentroidTracker:
    """Greedy centroid-distance tracker with configurable thresholds.

    Parameters
    ----------
    max_distance : float
        Maximum Euclidean distance (pixels) to consider a detection as
        belonging to an existing track.  Detections farther than this
        always spawn a new track.
    max_missed_frames : int
        Remove a track after this many consecutive frames without a match.
    """

    def __init__(
        self,
        max_distance: float = 120.0,
        max_missed_frames: int = 5,
    ) -> None:
        self.max_distance = max_distance
        self.max_missed_frames = max_missed_frames
        self._next_id: int = 1
        self._tracks: dict[str, Track] = {}   # track_id → Track

    # -- public API ---------------------------------------------------------

    @property
    def active_tracks(self) -> list[Track]:
        """Return currently active tracks (sorted by ID for determinism)."""
        return sorted(self._tracks.values(), key=lambda t: t.track_id)

    def update(self, detections: list[dict]) -> list[Track]:
        """Process a new frame's detections and return active tracks.

        Parameters
        ----------
        detections : list[dict]
            Each dict must contain ``"confidence"`` (float) and
            ``"box"`` (list of 4 floats ``[x1, y1, x2, y2]``).

        Returns
        -------
        list[Track]
            All currently active tracks after this update.
        """
        # Compute centroids for new detections
        det_centroids: list[tuple[float, float]] = []
        for det in detections:
            cx, cy = _bbox_center(det["box"])
            det_centroids.append((cx, cy))

        matched_track_ids: set[str] = set()
        matched_det_indices: set[int] = set()

        if self._tracks and detections:
            # Build distance pairs: (distance, track_id, det_index)
            pairs: list[tuple[float, str, int]] = []
            for tid, track in self._tracks.items():
                for di, (cx, cy) in enumerate(det_centroids):
                    d = _euclidean(track.center_x, track.center_y, cx, cy)
                    pairs.append((d, tid, di))

            # Sort by distance (greedy closest-first matching)
            pairs.sort(key=lambda p: p[0])

            for dist, tid, di in pairs:
                if tid in matched_track_ids or di in matched_det_indices:
                    continue
                if dist > self.max_distance:
                    continue
                # Match found — update existing track
                det = detections[di]
                cx, cy = det_centroids[di]
                track = self._tracks[tid]
                track.bbox = list(det["box"])
                track.center_x = cx
                track.center_y = cy
                track.confidence = det["confidence"]
                track.age += 1
                track.missed_frames = 0

                matched_track_ids.add(tid)
                matched_det_indices.add(di)

        # --- Create new tracks for unmatched detections --------------------
        for di, det in enumerate(detections):
            if di in matched_det_indices:
                continue
            cx, cy = det_centroids[di]
            tid = self._make_id()
            self._tracks[tid] = Track(
                track_id=tid,
                bbox=list(det["box"]),
                center_x=cx,
                center_y=cy,
                confidence=det["confidence"],
                age=1,
                missed_frames=0,
            )

        # --- Age unmatched tracks and remove expired ones ------------------
        to_remove: list[str] = []
        for tid, track in self._tracks.items():
            if tid not in matched_track_ids and tid not in {
                t.track_id for t in self._tracks.values()
                if t.age == 1 and t.missed_frames == 0
            }:
                # Only increment missed for tracks that existed before this frame
                if track.age > 1 or track.missed_frames > 0:
                    track.missed_frames += 1
                    if track.missed_frames > self.max_missed_frames:
                        to_remove.append(tid)

        for tid in to_remove:
            del self._tracks[tid]

        return self.active_tracks

    def reset(self) -> None:
        """Clear all tracks and reset the ID counter."""
        self._tracks.clear()
        self._next_id = 1

    # -- internals ----------------------------------------------------------

    def _make_id(self) -> str:
        tid = f"TRACK_{self._next_id:03d}"
        self._next_id += 1
        return tid


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bbox_center(box: list[float]) -> tuple[float, float]:
    """Return the center (cx, cy) of a bounding box [x1, y1, x2, y2]."""
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def _euclidean(x1: float, y1: float, x2: float, y2: float) -> float:
    """Euclidean distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
