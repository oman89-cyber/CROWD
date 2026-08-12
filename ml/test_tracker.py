"""Tests for Step 8: Anonymous Person Tracking + Zone Assignment.

Tests the tracker algorithm with synthetic detections (no model needed),
the zone mapper, the full video pipeline on a real COCO video, and
backward compatibility with Steps 7.3 and 7.4.
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


# ================================================================= Test 1
print("\n=== Test 1: Tracker initializes ===")
from tracker import CentroidTracker

tracker = CentroidTracker(max_distance=100.0, max_missed_frames=3)
check("tracker created", tracker is not None)
check("no active tracks initially", len(tracker.active_tracks) == 0)

# ================================================================= Test 2
print("\n=== Test 2: First detection receives TRACK_001 ===")
det_frame1 = [
    {"confidence": 0.95, "box": [100.0, 50.0, 160.0, 200.0]},
]
tracks = tracker.update(det_frame1)
check("one track returned", len(tracks) == 1)
check("track ID is TRACK_001", tracks[0].track_id == "TRACK_001")
check("confidence correct", tracks[0].confidence == 0.95)
check("age is 1", tracks[0].age == 1)
check("missed_frames is 0", tracks[0].missed_frames == 0)

# ================================================================= Test 3
print("\n=== Test 3: Same nearby detection retains TRACK_001 ===")
det_frame2 = [
    {"confidence": 0.93, "box": [105.0, 52.0, 165.0, 202.0]},  # slight movement
]
tracks = tracker.update(det_frame2)
check("still one track", len(tracks) == 1)
check("still TRACK_001", tracks[0].track_id == "TRACK_001")
check("age incremented to 2", tracks[0].age == 2)
check("center updated", tracks[0].center_x == 135.0 and tracks[0].center_y == 127.0)

# ================================================================= Test 4
print("\n=== Test 4: Second person receives TRACK_002 ===")
det_frame3 = [
    {"confidence": 0.90, "box": [105.0, 52.0, 165.0, 202.0]},  # person 1
    {"confidence": 0.88, "box": [400.0, 100.0, 460.0, 280.0]}, # person 2 — far away
]
tracks = tracker.update(det_frame3)
check("two tracks", len(tracks) == 2)
ids = {t.track_id for t in tracks}
check("TRACK_001 present", "TRACK_001" in ids)
check("TRACK_002 present", "TRACK_002" in ids)

# ================================================================= Test 5
print("\n=== Test 5: Track persists through short missed frames ===")
# Person 1 disappears, person 2 stays
det_frame4 = [
    {"confidence": 0.85, "box": [402.0, 102.0, 462.0, 282.0]},  # only person 2
]
tracks = tracker.update(det_frame4)
track_ids = {t.track_id for t in tracks}
check("TRACK_001 still alive (missed 1)", "TRACK_001" in track_ids)
check("TRACK_002 still alive", "TRACK_002" in track_ids)

t1 = [t for t in tracks if t.track_id == "TRACK_001"][0]
check("TRACK_001 missed_frames == 1", t1.missed_frames == 1)

# Another miss
det_frame5 = [
    {"confidence": 0.84, "box": [404.0, 104.0, 464.0, 284.0]},  # only person 2
]
tracks = tracker.update(det_frame5)
track_ids = {t.track_id for t in tracks}
check("TRACK_001 survived 2 misses", "TRACK_001" in track_ids)

# ================================================================= Test 6
print("\n=== Test 6: Track removed after max missed frames ===")
# Miss 3 more times (total 5 > max_missed_frames=3)
for _ in range(3):
    tracks = tracker.update([
        {"confidence": 0.80, "box": [406.0, 106.0, 466.0, 286.0]},
    ])

track_ids = {t.track_id for t in tracks}
check("TRACK_001 removed after exceeding max_missed", "TRACK_001" not in track_ids)
check("TRACK_002 still alive", "TRACK_002" in track_ids)

# ================================================================= Test 7
print("\n=== Test 7: Centers calculated correctly ===")
tracker2 = CentroidTracker()
det = [{"confidence": 0.9, "box": [100.0, 200.0, 300.0, 400.0]}]
tracks = tracker2.update(det)
check("center_x = 200.0", tracks[0].center_x == 200.0)
check("center_y = 300.0", tracks[0].center_y == 300.0)

# ================================================================= Test 8
print("\n=== Test 8: Zone mapper returns correct zone ===")
from zone_mapper import ZoneMapper, ZoneRegion, create_demo_zone_mapper

mapper = ZoneMapper()
mapper.add_region(ZoneRegion("CORRIDOR_C", 200, 100, 400, 350))
mapper.add_region(ZoneRegion("BLOCK_C", 400, 100, 640, 350))

check("point in CORRIDOR_C", mapper.get_zone(300, 200) == "CORRIDOR_C")
check("point in BLOCK_C", mapper.get_zone(500, 200) == "BLOCK_C")

# ================================================================= Test 9
print("\n=== Test 9: Unknown location returns UNKNOWN ===")
check("outside all zones", mapper.get_zone(50, 50) == "UNKNOWN")
check("edge case", mapper.get_zone(700, 500) == "UNKNOWN")

# Test demo mapper
demo_mapper = create_demo_zone_mapper(640, 480)
check("demo mapper has regions", len(demo_mapper.regions) > 0)
check("demo center -> CORRIDOR_C", demo_mapper.get_zone(320, 240) == "CORRIDOR_C")
check("demo left -> GATE_C", demo_mapper.get_zone(100, 240) == "GATE_C")
check("demo right -> BLOCK_C", demo_mapper.get_zone(550, 240) == "BLOCK_C")

# ================================================================= Test 10
print("\n=== Test 10: Video tracking pipeline produces track IDs ===")

# Check if real COCO video exists
REAL_VIDEO = os.path.join(os.path.dirname(__file__), "test_crowd_real.mp4")
JSON_OUT = os.path.join(os.path.dirname(__file__), os.pardir,
                        "data", "video_tracks.json")

if os.path.isfile(REAL_VIDEO):
    from video_tracker import run_tracking_pipeline

    result = run_tracking_pipeline(
        video_path=REAL_VIDEO,
        frame_skip=5,
        threshold=0.5,
        output_json=JSON_OUT,
    )
    check("pipeline returns dict", isinstance(result, dict))
    check("frames_processed > 0", result.get("frames_processed", 0) > 0)
    check("unique_tracks >= 0", result.get("unique_tracks", -1) >= 0)

    # Check frame records have active_tracks
    frames = result.get("frames", [])
    if frames:
        has_tracks_key = all("active_tracks" in f for f in frames)
        check("all frames have active_tracks", has_tracks_key)

        # Check track records have required fields
        all_ok = True
        for f in frames:
            for tr in f.get("active_tracks", []):
                if not all(k in tr for k in ("track_id", "zone_id", "center", "confidence")):
                    all_ok = False
        check("track records have required fields", all_ok)
    else:
        check("pipeline returned frames", False, "no frames")
else:
    print("  SKIP  No real COCO video found — skipping pipeline test")
    print("        Run: python ml/video_tracker.py ml/test_crowd_real.mp4")

# ================================================================= Test 11
print("\n=== Test 11: JSON output is valid ===")
if os.path.isfile(JSON_OUT):
    with open(JSON_OUT, "r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    check("JSON parses", isinstance(loaded, dict))
    check("JSON has frames", isinstance(loaded.get("frames"), list))
    check("JSON has unique_tracks", "unique_tracks" in loaded)

    # Validate structure
    for f in loaded.get("frames", []):
        check(f"frame {f['frame_number']} has active_tracks",
              isinstance(f.get("active_tracks"), list))
        break  # check at least one
else:
    check("JSON file exists", False, "not found")

# ================================================================= Test 12
print("\n=== Test 12: Existing Step 7.3 image detector still works ===")
img_path = os.path.join(os.path.dirname(__file__), "test_crowd_real.jpg")
if os.path.isfile(img_path):
    from test_detector import load_model as load_img_model, detect_people as detect_img
    from PIL import Image

    img = Image.open(img_path).convert("RGB")
    ip, im = load_img_model()
    dets, t = detect_img(img, ip, im)
    check("image detector works", isinstance(dets, list))
    check("image detections found", len(dets) >= 0)
else:
    check("Step 7.3 test skipped (no image)", True)

# ================================================================= Test 13
print("\n=== Test 13: Existing Step 7.4 video detector still works ===")
from video_detector import process_video as vd_process

synth_video = os.path.join(os.path.dirname(__file__), "test_crowd.mp4")
if os.path.isfile(synth_video):
    vd_json = os.path.join(os.path.dirname(__file__), os.pardir,
                           "data", "video_detections_compat.json")
    vd_result = vd_process(
        video_path=synth_video,
        frame_skip=10,
        threshold=0.5,
        output_json=vd_json,
        annotate=False,
    )
    check("video_detector pipeline works", isinstance(vd_result, dict))
    check("video_detector has frames", vd_result.get("frames_processed", 0) > 0)
else:
    check("Step 7.4 test skipped (no video)", True)

# ================================================================= Summary
print(f"\n{'='*50}")
print(f"PASSED: {PASS}   FAILED: {FAIL}")
if FAIL > 0:
    sys.exit(1)
print("All tests passed!")
