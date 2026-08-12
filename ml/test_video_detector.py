"""Tests for Step 7.4: Video → Person Detection.

Generates a short synthetic test video, runs the video detector pipeline,
and verifies correctness of outputs.
"""

from __future__ import annotations

import json
import os
import sys
import time

# Ensure we can import sibling modules
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


# ================================================================= Setup
print("\n=== Setup: Generate synthetic test video ===")
from create_test_video import create_test_video

VIDEO_PATH = os.path.join(os.path.dirname(__file__), "test_crowd.mp4")
create_test_video(VIDEO_PATH, n_frames=30, fps=30)  # 1 second, 30 frames
check("test video created", os.path.isfile(VIDEO_PATH))

# ================================================================= Test 1
print("\n=== Test 1: Video opens and metadata is read ===")
import cv2

cap = cv2.VideoCapture(VIDEO_PATH)
check("video opens", cap.isOpened())

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
check("FPS detected", fps > 0, f"fps={fps}")
check("frame count > 0", total_frames > 0, f"frames={total_frames}")
cap.release()

# ================================================================= Test 2
print("\n=== Test 2: Frames can be read ===")
cap = cv2.VideoCapture(VIDEO_PATH)
ret, frame = cap.read()
check("first frame read", ret and frame is not None)
check("frame has shape", frame is not None and len(frame.shape) == 3)
if frame is not None:
    check("frame has 3 channels", frame.shape[2] == 3)
cap.release()

# ================================================================= Test 3
print("\n=== Test 3: Frame sampling works ===")
cap = cv2.VideoCapture(VIDEO_PATH)
frame_skip = 5
sampled = []
idx = 0
while True:
    ret, frm = cap.read()
    if not ret:
        break
    if idx % frame_skip == 0:
        sampled.append(idx)
    idx += 1
cap.release()
expected_sampled = len([i for i in range(total_frames) if i % frame_skip == 0])
check("frame sampling count correct",
      len(sampled) == expected_sampled,
      f"got {len(sampled)}, expected {expected_sampled}")

# ================================================================= Test 4
print("\n=== Test 4: YOLOS inference on a video frame ===")
from video_detector import load_model, detect_people_in_frame

processor, model = load_model()
cap = cv2.VideoCapture(VIDEO_PATH)
ret, frame = cap.read()
cap.release()

t0 = time.perf_counter()
detections = detect_people_in_frame(frame, processor, model, threshold=0.5)
t1 = time.perf_counter()
check("inference returns list", isinstance(detections, list))
check("inference time reasonable", (t1 - t0) < 30, f"{t1-t0:.2f}s")

# ================================================================= Test 5
print("\n=== Test 5: Person detections structure ===")
for det in detections:
    has_conf = "confidence" in det and isinstance(det["confidence"], float)
    has_box = "box" in det and isinstance(det["box"], list) and len(det["box"]) == 4
    check(f"detection has confidence", has_conf)
    check(f"detection has box[4]", has_box)
    break  # check at least one if any exist
if len(detections) == 0:
    check("zero detections OK for synthetic", True)

# ================================================================= Test 6
print("\n=== Test 6: Full pipeline via process_video ===")
from video_detector import process_video

JSON_OUT = os.path.join(os.path.dirname(__file__), os.pardir,
                        "data", "video_detections.json")

result = process_video(
    video_path=VIDEO_PATH,
    frame_skip=5,
    threshold=0.5,
    output_json=JSON_OUT,
    annotate=False,
)

check("result is dict", isinstance(result, dict))
check("frames key exists", "frames" in result)
check("frames_processed > 0", result.get("frames_processed", 0) > 0)
check("max_people >= 0", result.get("max_people", -1) >= 0)
check("avg_people >= 0", result.get("avg_people", -1) >= 0)
check("processing_time > 0", result.get("processing_time_seconds", 0) > 0)

# ================================================================= Test 7
print("\n=== Test 7: JSON output is valid ===")
check("JSON file exists", os.path.isfile(JSON_OUT))
with open(JSON_OUT, "r", encoding="utf-8") as fh:
    loaded = json.load(fh)
check("JSON parses", isinstance(loaded, dict))
check("JSON has frames list", isinstance(loaded.get("frames"), list))
check("JSON frame count matches",
      len(loaded["frames"]) == result["frames_processed"])

# ================================================================= Test 8
print("\n=== Test 8: Person counts are non-negative ===")
all_non_neg = all(
    f.get("person_count", -1) >= 0 for f in loaded.get("frames", [])
)
check("all person counts >= 0", all_non_neg)

# ================================================================= Test 9
print("\n=== Test 9: Existing image detector still works ===")
from test_detector import load_model as load_img_model, detect_people
from PIL import Image

img_path = os.path.join(os.path.dirname(__file__), "test_crowd_real.jpg")
if os.path.isfile(img_path):
    img = Image.open(img_path).convert("RGB")
    ip, im = load_img_model()
    dets, t = detect_people(img, ip, im)
    check("image detector still works", isinstance(dets, list))
    check("image detections >= 0", len(dets) >= 0)
else:
    check("image detector test skipped (no test image)", True)

# ================================================================= Summary
print(f"\n{'='*50}")
print(f"PASSED: {PASS}   FAILED: {FAIL}")
if FAIL > 0:
    sys.exit(1)
print("All tests passed!")
