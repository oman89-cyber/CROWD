"""CrowdShield AI — Video Person Detection.

Processes a video frame-by-frame using OpenCV + YOLOS-Tiny to detect people.

Usage:
    python ml/video_detector.py <video_path>
    python ml/video_detector.py <video_path> --frame-skip 10
    python ml/video_detector.py <video_path> --threshold 0.6
    python ml/video_detector.py <video_path> --annotate

Options:
    --frame-skip N      Process every N-th frame (default: 5)
    --threshold  F      Confidence threshold (default: 0.5)
    --annotate          Write annotated output video
    --output     PATH   JSON output path (default: data/video_detections.json)
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

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MODEL_NAME = "hustvl/yolos-tiny"
PERSON_LABEL = "person"
DEFAULT_FRAME_SKIP = 5
DEFAULT_THRESHOLD = 0.5
DEFAULT_OUTPUT = os.path.join(
    os.path.dirname(__file__), os.pardir, "data", "video_detections.json"
)
ANNOTATED_OUTPUT = os.path.join(
    os.path.dirname(__file__), os.pardir, "data", "video_detections_annotated.mp4"
)


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------
def load_model() -> tuple:
    """Load YOLOS-Tiny model and processor (cached after first download)."""
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
def detect_people_in_frame(
    frame_bgr: np.ndarray,
    processor,
    model,
    threshold: float = DEFAULT_THRESHOLD,
) -> list[dict]:
    """Run YOLOS-Tiny on a single OpenCV BGR frame.

    Returns a list of dicts with ``confidence`` and ``box`` keys.
    """
    # OpenCV BGR → PIL RGB
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

    detections.sort(key=lambda d: d["confidence"], reverse=True)
    return detections


# ---------------------------------------------------------------------------
# Video processing
# ---------------------------------------------------------------------------
def process_video(
    video_path: str,
    frame_skip: int = DEFAULT_FRAME_SKIP,
    threshold: float = DEFAULT_THRESHOLD,
    output_json: str = DEFAULT_OUTPUT,
    annotate: bool = False,
) -> dict:
    """Process a video and return detection results.

    Parameters
    ----------
    video_path : str
        Path to input video file.
    frame_skip : int
        Process every *frame_skip*-th frame.
    threshold : float
        Minimum confidence for person detections.
    output_json : str
        Where to save the JSON results.
    annotate : bool
        If True, write an annotated output video.

    Returns
    -------
    dict
        Full results structure (also saved to *output_json*).
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
    print(f"FPS: {fps}")
    print(f"Frames: {total_frames}")
    print(f"Resolution: {width}x{height}")
    print(f"Frame sampling: every {frame_skip} frames")
    print(f"Confidence threshold: {threshold}")
    print()

    # ---- Load model ----
    processor, model = load_model()
    print()

    # ---- Optional annotated writer ----
    ann_writer = None
    if annotate:
        ann_path = os.path.normpath(ANNOTATED_OUTPUT)
        os.makedirs(os.path.dirname(ann_path), exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        ann_writer = cv2.VideoWriter(ann_path, fourcc, fps, (width, height))
        print(f"Annotated output: {ann_path}")
        print()

    # ---- Process frames ----
    frame_results: list[dict] = []
    person_counts: list[int] = []
    frame_idx = 0
    t_start = time.perf_counter()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % frame_skip == 0:
            detections = detect_people_in_frame(frame, processor, model, threshold)
            count = len(detections)
            timestamp = round(frame_idx / fps, 3) if fps > 0 else 0.0

            frame_results.append({
                "frame_number": frame_idx,
                "timestamp": timestamp,
                "person_count": count,
                "detections": detections,
            })
            person_counts.append(count)

            print(f"Frame {frame_idx}:")
            print(f"  people: {count}")

            # Draw annotations on frame
            if ann_writer is not None:
                ann_frame = frame.copy()
                for det in detections:
                    x1, y1, x2, y2 = [int(v) for v in det["box"]]
                    conf = det["confidence"]
                    cv2.rectangle(ann_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = f"person {conf:.2f}"
                    cv2.putText(ann_frame, label, (x1, y1 - 8),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # Count overlay
                cv2.putText(ann_frame, f"People: {count}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                            (0, 0, 255), 2)
                ann_writer.write(ann_frame)

        frame_idx += 1

    t_total = time.perf_counter() - t_start
    cap.release()
    if ann_writer is not None:
        ann_writer.release()

    # ---- Summary ----
    max_people = max(person_counts) if person_counts else 0
    avg_people = round(sum(person_counts) / len(person_counts), 1) if person_counts else 0.0

    print()
    print("=" * 50)
    print(f"Frames processed: {len(frame_results)}")
    print(f"Maximum visible people: {max_people}")
    print(f"Average visible people: {avg_people}")
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
        "max_people": max_people,
        "avg_people": avg_people,
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
        description="CrowdShield AI — Video Person Detection",
    )
    parser.add_argument("video", help="Path to input video file")
    parser.add_argument("--frame-skip", type=int, default=DEFAULT_FRAME_SKIP,
                        help=f"Process every N-th frame (default: {DEFAULT_FRAME_SKIP})")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                        help=f"Confidence threshold (default: {DEFAULT_THRESHOLD})")
    parser.add_argument("--output", type=str, default=DEFAULT_OUTPUT,
                        help="JSON output path")
    parser.add_argument("--annotate", action="store_true",
                        help="Write annotated output video")

    args = parser.parse_args()

    if not os.path.isfile(args.video):
        print(f"ERROR: Video file not found: {args.video}")
        sys.exit(1)

    print("=" * 60)
    print("CrowdShield AI — Video Person Detection")
    print("=" * 60)
    print()

    process_video(
        video_path=args.video,
        frame_skip=args.frame_skip,
        threshold=args.threshold,
        output_json=args.output,
        annotate=args.annotate,
    )

    print("=" * 60)
    print("Done.")


if __name__ == "__main__":
    main()
