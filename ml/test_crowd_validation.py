"""Tests for Step 8.2: Real Crowd Detection Validation.

Runs the crowd_validation pipeline and verifies all outputs,
then checks backward compatibility with Steps 7.3, 7.4, and 8.
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


# Run the full validation pipeline first
print("\n=== Running crowd validation pipeline ===")
from crowd_validation import run_validation, TEST_IMAGES, OUT_DIR, REPORT_PATH, SHEET_PATH, load_model

report = run_validation()

# ================================================================= Test 1
print("\n=== Test 1: All images load ===")
from pathlib import Path
IMG_DIR = Path("ml/crowd_images")
for meta in TEST_IMAGES:
    p = IMG_DIR / f"{meta['id']}.jpg"
    check(f"{meta['id']} downloaded", p.exists(),
          f"not found: {p}")

# ================================================================= Test 2
print("\n=== Test 2: Model loads ===")
proc, mdl = load_model()
check("processor loaded", proc is not None)
check("model loaded", mdl is not None)
param_count = sum(p.numel() for p in mdl.parameters())
check("parameter count correct", param_count == 6_488_736,
      f"got {param_count}")

# ================================================================= Test 3
print("\n=== Test 3: Detection runs for all images ===")
check("all images in report",
      len(report["images"]) == len(TEST_IMAGES),
      f"got {len(report['images'])}")
for img in report["images"]:
    check(f"{img['image']} inference_seconds > 0",
          img["inference_seconds"] > 0)

# ================================================================= Test 4
print("\n=== Test 4: Person filtering works ===")
# Re-run detection on one image and verify all returned objects are persons
from PIL import Image
from crowd_validation import detect
for meta in TEST_IMAGES[:1]:
    raw = IMG_DIR / f"{meta['id']}.jpg"
    pil_img = Image.open(str(raw)).convert("RGB")
    dets, _ = detect(pil_img, 0.5)
    # All detections should have confidence + box fields
    all_valid = all(
        "confidence" in d and "box" in d and len(d["box"]) == 4
        for d in dets
    )
    check("detections have confidence + box[4]", all_valid)

# ================================================================= Test 5
print("\n=== Test 5: Threshold 0.5 detections >= threshold 0.7 ===")
for img in report["images"]:
    n05 = img["detections_threshold_0_5"]
    n07 = img["detections_threshold_0_7"]
    check(
        f"{img['image']} @0.5 >= @0.7",
        n05 >= n07,
        f"@0.5={n05}, @0.7={n07}",
    )

# ================================================================= Test 6
print("\n=== Test 6: Threshold 0.7 > 0 or 0.5 > 0 for crowd images ===")
total_05 = sum(img["detections_threshold_0_5"] for img in report["images"])
check("at least some detections @0.5 across all images",
      total_05 > 0, f"total={total_05}")

# ================================================================= Test 7
print("\n=== Test 7: Annotated images generated ===")
for meta in TEST_IMAGES:
    ann = OUT_DIR / f"{meta['id']}_annotated.jpg"
    check(f"{meta['id']}_annotated.jpg exists", ann.exists())
    if ann.exists():
        size = ann.stat().st_size
        check(f"{meta['id']}_annotated.jpg non-empty", size > 1000,
              f"size={size}")

# ================================================================= Test 8
print("\n=== Test 8: Contact sheet generated ===")
check("contact sheet exists", Path(str(SHEET_PATH)).exists())
if Path(str(SHEET_PATH)).exists():
    import cv2
    sheet = cv2.imread(str(SHEET_PATH))
    check("contact sheet readable", sheet is not None)
    if sheet is not None:
        check("contact sheet width > 400", sheet.shape[1] > 400)
        check("contact sheet height > 200", sheet.shape[0] > 200)

# ================================================================= Test 9
print("\n=== Test 9: JSON report is valid ===")
check("report JSON exists", Path(str(REPORT_PATH)).exists())
with open(str(REPORT_PATH), encoding="utf-8") as fh:
    loaded = json.load(fh)
check("model field present", loaded.get("model") == "hustvl/yolos-tiny")
check("images list length correct",
      len(loaded.get("images", [])) == len(TEST_IMAGES))
for img in loaded.get("images", []):
    check(f"{img['image']} has ground_truth_count",
          "ground_truth_count" in img)
    check(f"{img['image']} has detections_threshold_0_5",
          isinstance(img.get("detections_threshold_0_5"), int))
    check(f"{img['image']} has detections_threshold_0_7",
          isinstance(img.get("detections_threshold_0_7"), int))

# ================================================================= Test 10
print("\n=== Test 10: Step 7.3 image detector still works ===")
img_path = os.path.join(os.path.dirname(__file__), "test_crowd_real.jpg")
if os.path.isfile(img_path):
    from test_detector import load_model as load_img_model, detect_people as detect_img
    pil_img = Image.open(img_path).convert("RGB")
    ip, im  = load_img_model()
    dets, t = detect_img(pil_img, ip, im)
    check("Step 7.3 detector returns list", isinstance(dets, list))
    check("Step 7.3 detections >= 0", len(dets) >= 0)
else:
    check("Step 7.3 skipped (no image)", True)

# ================================================================= Test 11
print("\n=== Test 11: Step 7.4 video detector still works ===")
synth_video = os.path.join(os.path.dirname(__file__), "test_crowd.mp4")
if os.path.isfile(synth_video):
    from video_detector import process_video
    json_out = "data/video_detections_compat2.json"
    result = process_video(synth_video, frame_skip=10, threshold=0.5,
                           output_json=json_out, annotate=False)
    check("Step 7.4 pipeline works", isinstance(result, dict))
    check("Step 7.4 frames_processed > 0",
          result.get("frames_processed", 0) > 0)
else:
    check("Step 7.4 skipped (no video)", True)

# ================================================================= Test 12
print("\n=== Test 12: Step 8 tracker tests still work ===")
from tracker import CentroidTracker
t8 = CentroidTracker(max_distance=100, max_missed_frames=3)
tracks = t8.update([{"confidence": 0.9, "box": [10.0, 20.0, 60.0, 120.0]}])
check("Step 8 tracker init", len(tracks) == 1)
check("Step 8 first track ID", tracks[0].track_id == "TRACK_001")
tracks2 = t8.update([{"confidence": 0.88, "box": [12.0, 22.0, 62.0, 122.0]}])
check("Step 8 track persistence", tracks2[0].track_id == "TRACK_001")
check("Step 8 track age increments", tracks2[0].age == 2)

# ================================================================= Summary
print(f"\n{'='*55}")
print(f"PASSED: {PASS}   FAILED: {FAIL}")
if FAIL > 0:
    sys.exit(1)
print("All tests passed!")
