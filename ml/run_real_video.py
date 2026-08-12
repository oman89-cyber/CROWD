"""CrowdShield AI — Real-World Video Processing Test.

Runs the real 1080x1920 60fps video through the EXISTING pipeline:
  OpenCV -> YOLOS-Tiny -> CentroidTracker -> ZoneMapper

Generates:
  data/real_video_tracks.json       — tracking results
  data/real_video_tracking_demo.mp4 — annotated output video

Usage:
    python ml/run_real_video.py
    python ml/run_real_video.py --frame-skip 10 --threshold 0.65
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForObjectDetection

# Reuse existing modules
sys.path.insert(0, os.path.dirname(__file__))
from tracker import CentroidTracker
from zone_mapper import create_demo_zone_mapper

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MODEL_NAME = "hustvl/yolos-tiny"
PERSON_LABEL = "person"

INPUT_VIDEO  = os.path.join(os.path.dirname(__file__),
                            "12208078_1080_1920_60fps.mp4")
OUTPUT_JSON  = os.path.join(os.path.dirname(__file__), os.pardir,
                            "data", "real_video_tracks.json")
OUTPUT_VIDEO = os.path.join(os.path.dirname(__file__), os.pardir,
                            "data", "real_video_tracking_demo.mp4")


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
def load_model():
    print(f"Loading model: {MODEL_NAME} ...")
    t0 = time.perf_counter()
    processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
    model = AutoModelForObjectDetection.from_pretrained(MODEL_NAME)
    model.eval()
    elapsed = time.perf_counter() - t0
    params = sum(p.numel() for p in model.parameters())
    print(f"Model loaded in {elapsed:.2f}s  ({params:,} params, cpu)")
    return processor, model


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------
def detect_people(frame_bgr, processor, model, threshold):
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
    dets = []
    for score, label, box in zip(
        results["scores"], results["labels"], results["boxes"]
    ):
        if model.config.id2label[label.item()] == PERSON_LABEL:
            dets.append({
                "confidence": round(score.item(), 4),
                "box": [round(v, 1) for v in box.tolist()],
            })
    return dets


# ---------------------------------------------------------------------------
# Annotation drawing
# ---------------------------------------------------------------------------
_PALETTE = [
    (0, 220, 80), (255, 120, 0), (80, 80, 255), (255, 220, 0),
    (200, 0, 200), (0, 200, 220), (120, 255, 120), (255, 180, 100),
    (100, 200, 255), (200, 255, 100), (255, 100, 200), (100, 255, 255),
]


def _color(track_id):
    idx = int(track_id.split("_")[-1]) - 1
    return _PALETTE[idx % len(_PALETTE)]


def _draw_zone_overlay(frame, zones, alpha=0.08):
    overlay = frame.copy()
    zone_colors = {
        "GATE_C": (200, 140, 60), "CORRIDOR_C": (60, 200, 200),
        "BLOCK_C": (60, 60, 220), "FOOD_B": (60, 220, 60),
        "WASHROOM_C": (200, 60, 200),
    }
    for z in zones:
        x1, y1, x2, y2 = int(z["x_min"]), int(z["y_min"]), int(z["x_max"]), int(z["y_max"])
        color = zone_colors.get(z["zone_id"], (180, 180, 180))
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, z["zone_id"], (x1 + 8, y1 + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    return frame


def _draw_tracks(frame, tracks):
    for tr in tracks:
        color = _color(tr["track_id"])
        x1, y1, x2, y2 = [int(v) for v in tr["bbox"]]
        cx, cy = int(tr["center"][0]), int(tr["center"][1])
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        label1 = tr["track_id"]
        label2 = f"{tr['zone_id']} {tr['confidence']:.2f}"
        lw1, _ = cv2.getTextSize(label1, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
        lw2, _ = cv2.getTextSize(label2, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        lw = max(lw1, lw2)
        bar_top = max(y1 - 45, 0)
        cv2.rectangle(frame, (x1, bar_top), (x1 + lw + 8, y1), color, -1)
        cv2.putText(frame, label1, (x1 + 4, bar_top + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(frame, label2, (x1 + 4, bar_top + 36),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.circle(frame, (cx, cy), 6, color, -1)
        cv2.circle(frame, (cx, cy), 6, (255, 255, 255), 1)
    return frame


def _draw_hud(frame, frame_number, timestamp, track_count, det_count):
    h, w = frame.shape[:2]
    lines = [
        f"Frame: {frame_number}",
        f"Time:  {timestamp:.2f}s",
        f"Detected: {det_count}",
        f"Active Tracks: {track_count}",
    ]
    x0 = w - 320
    cv2.rectangle(frame, (x0 - 4, 0), (w, 18 + len(lines) * 28), (20, 20, 20), -1)
    for i, line in enumerate(lines):
        cv2.putText(frame, line, (x0, 22 + i * 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (230, 230, 230), 1, cv2.LINE_AA)
    return frame


# ---------------------------------------------------------------------------
# Zone region builder (mirrors zone_mapper.py demo layout)
# ---------------------------------------------------------------------------
def _build_zone_regions(w, h):
    return [
        {"zone_id": "FOOD_B",     "x_min": 0, "y_min": 0,
         "x_max": w, "y_max": h * 0.15},
        {"zone_id": "WASHROOM_C", "x_min": 0, "y_min": h * 0.85,
         "x_max": w, "y_max": h},
        {"zone_id": "GATE_C",     "x_min": 0, "y_min": h * 0.15,
         "x_max": w * 0.33, "y_max": h * 0.85},
        {"zone_id": "CORRIDOR_C", "x_min": w * 0.33, "y_min": h * 0.15,
         "x_max": w * 0.66, "y_max": h * 0.85},
        {"zone_id": "BLOCK_C",    "x_min": w * 0.66, "y_min": h * 0.15,
         "x_max": w, "y_max": h * 0.85},
    ]


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def run(
    video_path: str = INPUT_VIDEO,
    frame_skip: int = 10,
    threshold: float = 0.65,
    output_json: str = OUTPUT_JSON,
    output_video: str = OUTPUT_VIDEO,
    max_distance: float = 200.0,
    max_missed_frames: int = 8,
):
    # ---- Open video ----
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERROR: Cannot open video: {video_path}")
        sys.exit(1)

    fps    = cap.get(cv2.CAP_PROP_FPS)
    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print("=" * 60)
    print("CrowdShield AI - Real-World Video Processing")
    print("=" * 60)
    print(f"Video      : {video_path}")
    print(f"Resolution : {width}x{height}")
    print(f"FPS        : {fps:.2f}")
    print(f"Frames     : {total}")
    print(f"Duration   : {total / fps:.2f}s")
    print(f"Frame skip : {frame_skip}")
    print(f"Threshold  : {threshold}")
    print(f"Tracker    : max_dist={max_distance}, max_missed={max_missed_frames}")
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
    zone_regions = _build_zone_regions(width, height)

    # ---- Video writer ----
    os.makedirs(os.path.dirname(output_video), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    # ---- Process ----
    frame_results = []
    all_track_ids = set()
    person_counts = []
    track_counts  = []
    inference_times = []
    frame_idx = 0
    last_tracks_for_viz = []
    last_det_count = 0

    t_start = time.perf_counter()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_skip == 0:
            # Detect
            t_inf = time.perf_counter()
            dets = detect_people(frame, processor, model, threshold)
            inf_time = time.perf_counter() - t_inf
            inference_times.append(inf_time)

            # Track
            active_tracks = tracker.update(dets)

            # Zone assignment
            track_records = []
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
                "person_count": len(dets),
                "active_tracks": track_records,
            })

            person_counts.append(len(dets))
            track_counts.append(len(active_tracks))
            last_tracks_for_viz = track_records
            last_det_count = len(dets)

            # Progress
            pct = frame_idx / total * 100
            print(f"\r  Frame {frame_idx:4d}/{total} ({pct:5.1f}%)  "
                  f"det={len(dets):2d}  tracks={len(active_tracks):2d}  "
                  f"inf={inf_time:.2f}s", end="", flush=True)

        # ---- Annotate every frame for smooth video ----
        timestamp_viz = round(frame_idx / fps, 3) if fps > 0 else 0.0
        ann = frame.copy()
        ann = _draw_zone_overlay(ann, zone_regions)
        ann = _draw_tracks(ann, last_tracks_for_viz)
        ann = _draw_hud(ann, frame_idx, timestamp_viz,
                        len(last_tracks_for_viz), last_det_count)
        writer.write(ann)

        frame_idx += 1

    t_total = time.perf_counter() - t_start
    cap.release()
    writer.release()

    # ---- Statistics ----
    max_det   = max(person_counts) if person_counts else 0
    avg_det   = round(sum(person_counts) / len(person_counts), 1) if person_counts else 0
    max_trk   = max(track_counts)  if track_counts  else 0
    avg_trk   = round(sum(track_counts) / len(track_counts), 1) if track_counts else 0
    avg_inf   = round(sum(inference_times) / len(inference_times), 3) if inference_times else 0

    print()
    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total frames           : {total}")
    print(f"Processed frames       : {len(frame_results)}")
    print(f"Frame skip             : {frame_skip}")
    print(f"Processing time        : {t_total:.1f}s")
    print(f"Avg inference/frame    : {avg_inf}s")
    print(f"Max detected people    : {max_det}")
    print(f"Avg detected people    : {avg_det}")
    print(f"Max active tracks      : {max_trk}")
    print(f"Avg active tracks      : {avg_trk}")
    print(f"Unique tracks created  : {len(all_track_ids)}")
    print(f"Output JSON            : {output_json}")
    print(f"Output video           : {output_video}")

    # ---- Save JSON ----
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    result = {
        "video": os.path.basename(video_path),
        "resolution": f"{width}x{height}",
        "fps": round(fps, 2),
        "total_frames": total,
        "frame_skip": frame_skip,
        "confidence_threshold": threshold,
        "frames_processed": len(frame_results),
        "unique_tracks": len(all_track_ids),
        "max_detected_people": max_det,
        "avg_detected_people": avg_det,
        "max_active_tracks": max_trk,
        "avg_active_tracks": avg_trk,
        "avg_inference_seconds": avg_inf,
        "total_processing_seconds": round(t_total, 1),
        "frames": frame_results,
    }
    with open(output_json, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)
    print(f"\nJSON saved: {output_json}")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="CrowdShield AI - Real-World Video Processing",
    )
    parser.add_argument("--video", default=INPUT_VIDEO)
    parser.add_argument("--frame-skip", type=int, default=10)
    parser.add_argument("--threshold", type=float, default=0.65)
    parser.add_argument("--output-json", default=OUTPUT_JSON)
    parser.add_argument("--output-video", default=OUTPUT_VIDEO)
    parser.add_argument("--max-distance", type=float, default=200.0,
                        help="Track association max pixel distance (larger for HD)")
    parser.add_argument("--max-missed", type=int, default=8,
                        help="Max missed frames before track removal")
    args = parser.parse_args()

    run(
        video_path=args.video,
        frame_skip=args.frame_skip,
        threshold=args.threshold,
        output_json=args.output_json,
        output_video=args.output_video,
        max_distance=args.max_distance,
        max_missed_frames=args.max_missed,
    )


if __name__ == "__main__":
    main()
