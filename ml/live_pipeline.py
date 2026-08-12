"""CrowdShield AI — Live Video → Crowd Intelligence Pipeline.

Real-time video processing pipeline that connects:
VIDEO → YOLOS Detection → Tracking → Zone Assignment → Crowd Intelligence → Backend API

Usage:
    python -m ml.live_pipeline
    python -m ml.live_pipeline --video path/to/video.mp4
    python -m ml.live_pipeline --fps 2
    python -m ml.live_pipeline --display

The pipeline runs independently from the FastAPI server and updates
the backend intelligence state via HTTP POST requests.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import requests
from PIL import Image

# Import existing components
from ml.video_detector import load_model, detect_people_in_frame, MODEL_NAME
from ml.tracker import CentroidTracker
from ml.zone_mapper import create_demo_zone_mapper

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_VIDEO = Path(__file__).parent / "12208078_1080_1920_60fps.mp4"
DEFAULT_PROCESSING_FPS = 2
DEFAULT_THRESHOLD = 0.5
DEFAULT_BACKEND_URL = "http://localhost:8000"

# ---------------------------------------------------------------------------
# Live Pipeline
# ---------------------------------------------------------------------------

class LiveCrowdPipeline:
    """Real-time crowd intelligence pipeline."""

    def __init__(
        self,
        video_path: str,
        processing_fps: float = DEFAULT_PROCESSING_FPS,
        threshold: float = DEFAULT_THRESHOLD,
        backend_url: str = DEFAULT_BACKEND_URL,
        display: bool = False,
    ):
        self.video_path = video_path
        self.processing_fps = processing_fps
        self.threshold = threshold
        self.backend_url = backend_url
        self.display = display

        # Statistics
        self.frames_processed = 0
        self.total_detections = 0
        self.max_tracks = 0
        self.inference_times = []

        # Components (initialized in run())
        self.cap = None
        self.processor = None
        self.model = None
        self.tracker = None
        self.zone_mapper = None
        self.source_fps = 0
        self.frame_width = 0
        self.frame_height = 0

    def initialize(self) -> bool:
        """Initialize video capture and ML models."""
        # Open video
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print(f"ERROR: Cannot open video: {self.video_path}")
            return False

        # Get video properties
        self.source_fps = self.cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / self.source_fps if self.source_fps > 0 else 0

        print("=" * 70)
        print("CROWDSHIELD AI — LIVE CROWD INTELLIGENCE PIPELINE")
        print("=" * 70)
        print(f"Video: {Path(self.video_path).name}")
        print(f"Resolution: {self.frame_width}x{self.frame_height}")
        print(f"Source FPS: {self.source_fps:.1f}")
        print(f"Total Frames: {total_frames}")
        print(f"Duration: {duration:.1f}s")
        print(f"Processing FPS: {self.processing_fps}")
        print(f"Confidence Threshold: {self.threshold}")
        print(f"Backend API: {self.backend_url}")
        print(f"Display Mode: {'ON' if self.display else 'OFF'}")
        print("=" * 70)
        print()

        # Load YOLOS model
        print(f"Loading {MODEL_NAME}...")
        self.processor, self.model = load_model()
        print()

        # Initialize tracker
        self.tracker = CentroidTracker(max_distance=120.0, max_missed_frames=5)

        # Initialize zone mapper
        self.zone_mapper = create_demo_zone_mapper(
            frame_width=self.frame_width,
            frame_height=self.frame_height,
        )

        print("✓ Pipeline initialized successfully")
        print()

        return True

    def process_frame(self, frame: np.ndarray, frame_number: int, timestamp: float) -> dict:
        """Process a single frame through the pipeline."""
        t0 = time.perf_counter()

        # 1. Detect people
        detections = detect_people_in_frame(frame, self.processor, self.model, self.threshold)
        self.total_detections += len(detections)

        # 2. Update tracker
        tracks = self.tracker.update(detections)
        self.max_tracks = max(self.max_tracks, len(tracks))

        # 3. Assign zones to tracks
        track_observations = []
        zone_counts = {}

        for track in tracks:
            zone_id = self.zone_mapper.get_zone(track.center_x, track.center_y)
            track_observations.append({
                "track_id": track.track_id,
                "zone_id": zone_id,
                "timestamp": timestamp,
                "center_x": track.center_x,
                "center_y": track.center_y,
                "confidence": track.confidence,
            })
            zone_counts[zone_id] = zone_counts.get(zone_id, 0) + 1

        inference_time = time.perf_counter() - t0
        self.inference_times.append(inference_time)

        return {
            "frame_number": frame_number,
            "timestamp": timestamp,
            "detections": len(detections),
            "tracks": tracks,
            "track_observations": track_observations,
            "zone_counts": zone_counts,
            "inference_time": inference_time,
        }

    def update_backend(self, track_observations: list[dict]) -> bool:
        """Send track observations to backend intelligence API."""
        if not track_observations:
            return True  # No data to send

        try:
            # Format tracks for backend API (only needs track_id, zone_id, timestamp)
            payload = {
                "tracks": [
                    {
                        "track_id": t["track_id"],
                        "zone_id": t["zone_id"],
                        "timestamp": t["timestamp"],
                    }
                    for t in track_observations
                ]
            }

            response = requests.post(
                f"{self.backend_url}/api/intelligence/analyze",
                json=payload,
                timeout=5.0,
            )

            if response.status_code == 200:
                return True
            else:
                print(f"  ⚠ Backend returned {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"  ⚠ Backend connection error: {e}")
            return False

    def draw_debug_overlay(self, frame: np.ndarray, result: dict) -> np.ndarray:
        """Draw debug overlay on frame for display mode."""
        overlay = frame.copy()

        # Draw bounding boxes and track IDs
        for track in result["tracks"]:
            x1, y1, x2, y2 = [int(v) for v in track.bbox]
            zone_id = None
            for obs in result["track_observations"]:
                if obs["track_id"] == track.track_id:
                    zone_id = obs["zone_id"]
                    break

            # Draw box
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Draw track ID and zone
            label = f"{track.track_id}"
            if zone_id:
                label += f" [{zone_id}]"
            cv2.putText(
                overlay, label, (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
            )

        # Draw statistics overlay
        y_offset = 30
        stats = [
            f"Frame: {result['frame_number']}",
            f"Time: {result['timestamp']:.1f}s",
            f"Detected: {result['detections']}",
            f"Tracks: {len(result['tracks'])}",
            f"Inference: {result['inference_time']*1000:.0f}ms",
        ]

        for i, stat in enumerate(stats):
            cv2.putText(
                overlay, stat, (10, y_offset + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
            )

        # Draw zone counts
        y_offset = 180
        cv2.putText(
            overlay, "Zone Occupancy:", (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2
        )
        for i, (zone_id, count) in enumerate(sorted(result["zone_counts"].items())):
            cv2.putText(
                overlay, f"{zone_id}: {count}", (10, y_offset + 25 + i * 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1
            )

        return overlay

    def print_frame_summary(self, result: dict, intelligence_updated: bool):
        """Print frame processing summary to terminal."""
        print(f"[{result['timestamp']:6.1f}s] Frame {result['frame_number']:5d}")
        print(f"  Detected: {result['detections']:2d}  |  Active tracks: {len(result['tracks']):2d}  |  Inference: {result['inference_time']*1000:4.0f}ms")

        if result["zone_counts"]:
            zone_str = "  Zones: " + "  ".join(
                f"{zone}={count}" for zone, count in sorted(result["zone_counts"].items())
            )
            print(zone_str)

        backend_status = "✓ Backend updated" if intelligence_updated else "⚠ Backend update failed"
        print(f"  {backend_status}")
        print()

    def run(self) -> dict:
        """Run the live pipeline."""
        if not self.initialize():
            return {"success": False, "error": "Initialization failed"}

        # Calculate frame skip based on processing FPS
        if self.source_fps > 0 and self.processing_fps > 0:
            frame_skip = max(1, int(self.source_fps / self.processing_fps))
        else:
            frame_skip = 1

        print(f"Starting pipeline (processing every {frame_skip} frames)...")
        print("=" * 70)
        print()

        frame_idx = 0
        start_time = time.perf_counter()

        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break

                # Process frame according to sampling rate
                if frame_idx % frame_skip == 0:
                    timestamp = frame_idx / self.source_fps if self.source_fps > 0 else 0.0

                    # Process frame through pipeline
                    result = self.process_frame(frame, frame_idx, timestamp)
                    self.frames_processed += 1

                    # Update backend
                    intelligence_updated = self.update_backend(result["track_observations"])

                    # Print summary
                    self.print_frame_summary(result, intelligence_updated)

                    # Display mode
                    if self.display:
                        overlay = self.draw_debug_overlay(frame, result)
                        cv2.imshow("CrowdShield Live Pipeline", overlay)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            print("\nUser requested stop (pressed 'q')")
                            break

                frame_idx += 1

        except KeyboardInterrupt:
            print("\n\nPipeline stopped by user (Ctrl+C)")

        finally:
            # Cleanup
            total_time = time.perf_counter() - start_time
            self.cap.release()
            if self.display:
                cv2.destroyAllWindows()

            # Print final statistics
            self.print_statistics(total_time)

            return {
                "success": True,
                "frames_processed": self.frames_processed,
                "total_time": total_time,
                "max_tracks": self.max_tracks,
            }

    def print_statistics(self, total_time: float):
        """Print final pipeline statistics."""
        print()
        print("=" * 70)
        print("PIPELINE STATISTICS")
        print("=" * 70)
        print(f"Source FPS: {self.source_fps:.1f}")
        print(f"Processing FPS Target: {self.processing_fps:.1f}")
        print(f"Frames Processed: {self.frames_processed}")
        print(f"Total Processing Time: {total_time:.2f}s")
        print(f"Average Processing FPS: {self.frames_processed / total_time:.2f}")
        print()
        print(f"Total Detections: {self.total_detections}")
        print(f"Average Detections per Frame: {self.total_detections / max(self.frames_processed, 1):.1f}")
        print(f"Maximum Active Tracks: {self.max_tracks}")
        print()
        if self.inference_times:
            avg_inference = sum(self.inference_times) / len(self.inference_times)
            max_inference = max(self.inference_times)
            min_inference = min(self.inference_times)
            print(f"Average Inference Time: {avg_inference*1000:.1f}ms")
            print(f"Min Inference Time: {min_inference*1000:.1f}ms")
            print(f"Max Inference Time: {max_inference*1000:.1f}ms")
        print("=" * 70)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CrowdShield AI — Live Crowd Intelligence Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--video",
        type=str,
        default=str(DEFAULT_VIDEO),
        help=f"Path to video file (default: {DEFAULT_VIDEO.name})",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=DEFAULT_PROCESSING_FPS,
        help=f"Processing FPS (default: {DEFAULT_PROCESSING_FPS})",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Detection confidence threshold (default: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--backend",
        type=str,
        default=DEFAULT_BACKEND_URL,
        help=f"Backend API URL (default: {DEFAULT_BACKEND_URL})",
    )
    parser.add_argument(
        "--display",
        action="store_true",
        help="Show video with debug overlay (press 'q' to quit)",
    )

    args = parser.parse_args()

    # Create and run pipeline
    pipeline = LiveCrowdPipeline(
        video_path=args.video,
        processing_fps=args.fps,
        threshold=args.threshold,
        backend_url=args.backend,
        display=args.display,
    )

    result = pipeline.run()

    if result["success"]:
        print("\n✓ Pipeline completed successfully")
        sys.exit(0)
    else:
        print(f"\n✗ Pipeline failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
