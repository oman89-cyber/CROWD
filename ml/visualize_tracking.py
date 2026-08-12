"""CrowdShield AI — Tracking Visualization.

Reads the source video + existing tracking results (data/video_tracks.json)
and writes an annotated output video with:

  - Bounding boxes per track
  - Track ID + Zone ID labels
  - Center point dots
  - Zone boundary overlays with labels
  - Frame number + active track count HUD

Usage:
    python ml/visualize_tracking.py
    python ml/visualize_tracking.py --video ml/test_crowd_real.mp4
                                    --tracks data/video_tracks.json
                                    --output data/tracking_demo.mp4

If tracks JSON does not exist, runs the full pipeline first.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Colours per track — deterministic palette (BGR)
# ---------------------------------------------------------------------------
_PALETTE = [
    (0,   220,  80),   # green
    (255, 120,   0),   # blue-orange
    (80,   80, 255),   # red
    (255, 220,   0),   # cyan
    (200,   0, 200),   # magenta
    (0,   200, 220),   # yellow
    (120, 255, 120),   # light green
    (255, 180, 100),   # light blue
]


def _track_color(track_id: str) -> tuple[int, int, int]:
    """Return a deterministic BGR colour for a given track ID."""
    idx = int(track_id.split("_")[-1]) - 1
    return _PALETTE[idx % len(_PALETTE)]


# ---------------------------------------------------------------------------
# Zone drawing helpers
# ---------------------------------------------------------------------------

def _draw_zone_overlays(
    frame: np.ndarray,
    zone_regions: list[dict],
    alpha: float = 0.10,
) -> np.ndarray:
    """Draw semi-transparent zone rectangles + labels on the frame."""
    overlay = frame.copy()

    zone_colors: dict[str, tuple[int, int, int]] = {
        "GATE_C":      (200, 140,  60),
        "CORRIDOR_C":  ( 60, 200, 200),
        "BLOCK_C":     ( 60,  60, 220),
        "FOOD_B":      ( 60, 220,  60),
        "WASHROOM_C":  (200,  60, 200),
    }

    for zone in zone_regions:
        x1, y1 = int(zone["x_min"]), int(zone["y_min"])
        x2, y2 = int(zone["x_max"]), int(zone["y_max"])
        color = zone_colors.get(zone["zone_id"], (180, 180, 180))

        # Semi-transparent fill
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)

        # Solid border
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Zone label (top-left of region, offset inward)
        lx = x1 + 6
        ly = y1 + 22
        cv2.putText(frame, zone["zone_id"], (lx, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, color, 2,
                    cv2.LINE_AA)

    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    return frame


def _draw_tracks(frame: np.ndarray, active_tracks: list[dict]) -> np.ndarray:
    """Draw bounding boxes, labels, and center dots for all active tracks."""
    for track in active_tracks:
        tid      = track["track_id"]
        zone_id  = track["zone_id"]
        bbox     = track["bbox"]           # [x1, y1, x2, y2]
        center   = track["center"]         # [cx, cy]
        conf     = track["confidence"]
        color    = _track_color(tid)

        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        cx, cy = int(center[0]), int(center[1])

        # Bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Label background
        label_top = f"{tid}"
        label_bot = f"{zone_id}  {conf:.2f}"
        lw_top, lh = cv2.getTextSize(label_top, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)[0]
        lw_bot, _  = cv2.getTextSize(label_bot, cv2.FONT_HERSHEY_SIMPLEX, 0.44, 1)[0]
        lw = max(lw_top, lw_bot)
        bar_top = max(y1 - 38, 0)
        cv2.rectangle(frame, (x1, bar_top), (x1 + lw + 6, y1), color, -1)
        cv2.putText(frame, label_top, (x1 + 3, bar_top + 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, label_bot, (x1 + 3, bar_top + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 0, 0), 1, cv2.LINE_AA)

        # Center dot
        cv2.circle(frame, (cx, cy), 5, color, -1)
        cv2.circle(frame, (cx, cy), 5, (255, 255, 255), 1)

    return frame


def _draw_hud(
    frame: np.ndarray,
    frame_number: int,
    timestamp: float,
    track_count: int,
) -> np.ndarray:
    """Draw the top-right HUD (frame number, track count)."""
    h, w = frame.shape[:2]
    lines = [
        f"Frame: {frame_number}",
        f"Time:  {timestamp:.2f}s",
        f"Active Tracks: {track_count}",
    ]
    x0 = w - 200
    y0 = 14
    # Dark background bar
    cv2.rectangle(frame, (x0 - 4, 0), (w, y0 + len(lines) * 20 + 4),
                  (20, 20, 20), -1)
    for i, line in enumerate(lines):
        cv2.putText(frame, line, (x0, y0 + i * 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (230, 230, 230), 1,
                    cv2.LINE_AA)
    return frame


# ---------------------------------------------------------------------------
# Zone region definitions (mirror of zone_mapper.py demo layout)
# ---------------------------------------------------------------------------

def _build_zone_regions(w: int, h: int) -> list[dict]:
    return [
        {"zone_id": "FOOD_B",      "x_min": 0,       "y_min": 0,        "x_max": w,       "y_max": h * 0.15},
        {"zone_id": "WASHROOM_C",  "x_min": 0,       "y_min": h * 0.85, "x_max": w,       "y_max": h},
        {"zone_id": "GATE_C",      "x_min": 0,       "y_min": h * 0.15, "x_max": w * 0.33,"y_max": h * 0.85},
        {"zone_id": "CORRIDOR_C",  "x_min": w * 0.33,"y_min": h * 0.15, "x_max": w * 0.66,"y_max": h * 0.85},
        {"zone_id": "BLOCK_C",     "x_min": w * 0.66,"y_min": h * 0.15, "x_max": w,       "y_max": h * 0.85},
    ]


# ---------------------------------------------------------------------------
# Main visualization function
# ---------------------------------------------------------------------------

def visualize(
    video_path: str,
    tracks_json: str,
    output_path: str,
) -> dict:
    """Annotate *video_path* with tracking data from *tracks_json*.

    Returns a summary dict for verification.
    """
    # ---- Load tracking data ----
    with open(tracks_json, "r", encoding="utf-8") as fh:
        track_data = json.load(fh)

    # Build frame-number → track list lookup
    frame_lookup: dict[int, dict] = {
        f["frame_number"]: f for f in track_data.get("frames", [])
    }

    # ---- Open source video ----
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERROR: Cannot open video: {video_path}")
        sys.exit(1)

    fps    = cap.get(cv2.CAP_PROP_FPS)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Source video : {video_path}")
    print(f"Resolution   : {width}x{height}")
    print(f"FPS          : {fps}")
    print(f"Total frames : {total}")

    # ---- Prepare output writer ----
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    if not writer.isOpened():
        print(f"ERROR: Cannot open VideoWriter for: {output_path}")
        sys.exit(1)

    zone_regions = _build_zone_regions(width, height)

    # ---- Annotate frames ----
    frame_idx   = 0
    frames_out  = 0
    track_ids_seen: set[str] = set()

    t0 = time.perf_counter()
    last_tracks: list[dict] = []     # carry last known tracks for un-processed frames

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Refresh tracks if this frame was processed
        if frame_idx in frame_lookup:
            last_tracks = frame_lookup[frame_idx]["active_tracks"]
            timestamp   = frame_lookup[frame_idx]["timestamp"]
        else:
            timestamp   = round(frame_idx / fps, 3) if fps > 0 else 0.0

        for tr in last_tracks:
            track_ids_seen.add(tr["track_id"])

        # Draw zone overlays first (background layer)
        frame = _draw_zone_overlays(frame, zone_regions)

        # Draw tracks on top
        frame = _draw_tracks(frame, last_tracks)

        # HUD
        frame = _draw_hud(frame, frame_idx, timestamp, len(last_tracks))

        writer.write(frame)
        frames_out += 1
        frame_idx  += 1

    elapsed = time.perf_counter() - t0
    cap.release()
    writer.release()

    return {
        "output": output_path,
        "width": width,
        "height": height,
        "fps": fps,
        "frames_written": frames_out,
        "track_ids_visualized": sorted(track_ids_seen),
        "elapsed_seconds": round(elapsed, 2),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    HERE = os.path.dirname(os.path.abspath(__file__))
    ROOT = os.path.join(HERE, os.pardir)

    parser = argparse.ArgumentParser(
        description="CrowdShield AI — Tracking Visualization",
    )
    parser.add_argument(
        "--video", default=os.path.join(HERE, "test_crowd_real.mp4"),
        help="Source video (default: ml/test_crowd_real.mp4)",
    )
    parser.add_argument(
        "--tracks", default=os.path.join(ROOT, "data", "video_tracks.json"),
        help="Tracking JSON (default: data/video_tracks.json)",
    )
    parser.add_argument(
        "--output", default=os.path.join(ROOT, "data", "tracking_demo.mp4"),
        help="Annotated output video (default: data/tracking_demo.mp4)",
    )
    args = parser.parse_args()

    # Run pipeline first if tracks JSON is missing
    if not os.path.isfile(args.tracks):
        print(f"Tracking JSON not found: {args.tracks}")
        print("Running video tracking pipeline first ...")
        sys.path.insert(0, HERE)
        from video_tracker import run_tracking_pipeline
        run_tracking_pipeline(
            video_path=args.video,
            output_json=args.tracks,
        )

    if not os.path.isfile(args.video):
        print(f"ERROR: Source video not found: {args.video}")
        sys.exit(1)

    print("=" * 60)
    print("CrowdShield AI — Tracking Visualization")
    print("=" * 60)
    print()

    result = visualize(args.video, args.tracks, args.output)

    print()
    print("=" * 60)
    print(f"Output video : {result['output']}")
    print(f"Frame count  : {result['frames_written']}")
    print(f"FPS          : {result['fps']}")
    print(f"Resolution   : {result['width']}x{result['height']}")
    print(f"Track IDs    : {result['track_ids_visualized']}")
    print(f"Render time  : {result['elapsed_seconds']}s")
    print("Done.")


if __name__ == "__main__":
    main()
