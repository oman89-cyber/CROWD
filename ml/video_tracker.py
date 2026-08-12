"""CrowdShield AI — Video Tracking Pipeline.

End-to-end pipeline:  Video → YOLOS-Tiny → Tracker → Zone Assignment → JSON.

Usage:
    python ml/video_tracker.py <video_path>
    python ml/video_tracker.py <video_path> --frame-skip 5 --threshold 0.5

Outputs:
    data/video_tracks.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForObjectDetection

from tracker import CentroidTracker
from zone_mapper import create_demo_zone_mapper

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MODEL_NAME = "hustvl/yolos-tiny"
PERSON_LABEL = "person"
DEFAULT_FRAME_SKIP = 5
DEFAULT_THRESHOLD = 0.5
DEFAULT_OUTPUT = os.path.join(
    os.path.dirname(__file__), os.pardir, "data", "video_tracks.json"
)


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
def load_model() -> tuple:
    """Load YOLOS-Tiny model and processor."""
    print(f"Loading model: {MODEL_NAME} ...")
    t0 = time.perf_counter()
    processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
    model = AutoModelForObjectDetection.from_pretrained(MODEL_NAME)
    model.eval()
    elapsed = time.perf_counter() - t0
    print(f"Model loaded in {elapsed:.2f}s  "
          f"({sum(p.numel() for p in model.parameters()):,} params, cpu)")
    return processor, model


# ---------------------------------------------------------------------------
# Single-frame detection
# ---------------------------------------------------------------------------
def detect_people(
    frame_bgr: np.ndarray,
    processor,
    model,
    threshold: float,
) -> list[dict]:
    """Run YOLOS-Tiny on a BGR frame, return person detections."""
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)

    inputs = processor(images=pil_img, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)

    h, w = frame_bgr.shape[:2]
    target_sizes = torch.tensor([[h, w]])
    results = processor.post_process_object_detection(
        outputs, target_sizes=target_sizes, threshold=threshold
    )[0]

    detections: list[dict] = []
    for score, label, box in zip(
        results["scores"], results["labels"], results["boxes"]
    ):
        if model.config.id2label[label.item()] == PERSON_LABEL:
            detections.append({
                "confidence": round(score.item(), 4),
                "box": [round(v, 1) for v in box.tolist()],
            })

    return detections


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def run_tracking_pipeline(
    video_path: str,
    frame_skip: int = DEFAULT_FRAME_SKIP,
    threshold: float = DEFAULT_THRESHOLD,
    output_json: str = DEFAULT_OUTPUT,
    max_distance: float = 120.0,
    max_missed_frames: int = 5,
) -> dict:
    """Run the full detection → tracking → zone-assignment pipeline.

    Returns the result dict (also saved to *output_json*).
    """
    # ---- Open video ----
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERROR: Cannot open video: {video_path}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Video: {video_path}")
    print(f"FPS: {fps}  Frames: {total_frames}  Resolution: {width}x{height}")
    print(f"Frame sampling: every {frame_skip} frames")
    print(f"Confidence threshold: {threshold}")
    print(f"Tracker: max_distance={max_distance}, max_missed={max_missed_frames}")
    print()

    # ---- Load model ----
    processor, model = load_model()
    print()

    # ---- Initialize tracker and zone mapper ----
    tracker = CentroidTracker(
        max_distance=max_distance,
        max_missed_frames=max_missed_frames,
    )
    zone_mapper = create_demo_zone_mapper(width, height)

    # ---- Process frames ----
    frame_results: list[dict] = []
    all_track_ids: set[str] = set()
    frame_idx = 0
    t_start = time.perf_counter()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_skip == 0:
            # Detect
            detections = detect_people(frame, processor, model, threshold)

            # Track
            active_tracks = tracker.update(detections)

            # Zone assignment
            track_records: list[dict] = []
            for track in active_tracks:
                zone_id = zone_mapper.get_zone(track.center_x, track.center_y)
                all_track_ids.add(track.track_id)
                track_records.append({
                    "track_id": track.track_id,
                    "zone_id": zone_id,
                    "bbox": [round(v, 1) for v in track.bbox],
                    "center": [round(track.center_x, 1), round(track.center_y, 1)],
                    "confidence": round(track.confidence, 4),
                    "age": track.age,
                })

            timestamp = round(frame_idx / fps, 3) if fps > 0 else 0.0

            frame_results.append({
                "frame_number": frame_idx,
                "timestamp": timestamp,
                "person_count": len(detections),
                "active_tracks": track_records,
            })

            print(f"Frame {frame_idx}: "
                  f"detected={len(detections)}  "
                  f"tracks={len(active_tracks)}  "
                  f"zones={[r['zone_id'] for r in track_records]}")

        frame_idx += 1

    t_total = time.perf_counter() - t_start
    cap.release()

    # ---- Summary ----
    print()
    print("=" * 50)
    print(f"Frames processed: {len(frame_results)}")
    print(f"Unique tracks created: {len(all_track_ids)}")
    print(f"Processing time: {t_total:.2f} seconds")

    # ---- Save JSON ----
    output_path = os.path.normpath(output_json)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    result = {
        "video": os.path.basename(video_path),
        "fps": fps,
        "total_frames": total_frames,
        "frame_skip": frame_skip,
        "confidence_threshold": threshold,
        "frames_processed": len(frame_results),
        "unique_tracks": len(all_track_ids),
        "processing_time_seconds": round(t_total, 2),
        "frames": frame_results,
    }

    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
    print(f"Results saved to: {output_path}")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="CrowdShield AI — Video Tracking Pipeline",
    )
    parser.add_argument("video", help="Path to input video file")
    parser.add_argument("--frame-skip", type=int, default=DEFAULT_FRAME_SKIP)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-distance", type=float, default=120.0,
                        help="Max pixel distance for track association")
    parser.add_argument("--max-missed", type=int, default=5,
                        help="Max consecutive missed frames before track removal")

    args = parser.parse_args()

    if not os.path.isfile(args.video):
        print(f"ERROR: Video file not found: {args.video}")
        sys.exit(1)

    print("=" * 60)
    print("CrowdShield AI — Video Tracking Pipeline")
    print("=" * 60)
    print()

    run_tracking_pipeline(
        video_path=args.video,
        frame_skip=args.frame_skip,
        threshold=args.threshold,
        output_json=args.output,
        max_distance=args.max_distance,
        max_missed_frames=args.max_missed,
    )

    print("=" * 60)
    print("Done.")


if __name__ == "__main__":
    main()
