"""CrowdShield AI — Person Detection Test Script.

Proves that a pretrained Hugging Face object-detection model can detect
people on this machine using CPU inference.

Usage:
    python ml/test_detector.py                     # uses a generated test image
    python ml/test_detector.py path/to/image.jpg   # uses a provided image

Model: hustvl/yolos-tiny  (YOLOS-Tiny, COCO-pretrained, ~6.5M params)
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import torch
from PIL import Image, ImageDraw
from transformers import AutoImageProcessor, AutoModelForObjectDetection


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MODEL_NAME = "hustvl/yolos-tiny"
PERSON_LABEL = "person"
CONFIDENCE_THRESHOLD = 0.5


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
def load_model() -> tuple:
    """Download (first run) and load the pretrained YOLOS-Tiny model.

    Returns
    -------
    processor : AutoImageProcessor
    model : AutoModelForObjectDetection
    """
    print(f"Loading model: {MODEL_NAME} ...")
    t0 = time.perf_counter()
    processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
    model = AutoModelForObjectDetection.from_pretrained(MODEL_NAME)
    model.eval()
    elapsed = time.perf_counter() - t0
    print(f"Model loaded in {elapsed:.2f}s")
    print(f"  Parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"  Device: cpu")
    return processor, model


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------
def detect_people(
    image: Image.Image,
    processor,
    model,
    threshold: float = CONFIDENCE_THRESHOLD,
) -> list[dict]:
    """Run inference on *image* and return person detections.

    Returns
    -------
    list[dict]
        Each dict has keys ``confidence`` (float) and ``box`` (list of 4 floats
        [x1, y1, x2, y2]).
    """
    inputs = processor(images=image, return_tensors="pt")

    t0 = time.perf_counter()
    with torch.no_grad():
        outputs = model(**inputs)
    inference_time = time.perf_counter() - t0

    target_sizes = torch.tensor([image.size[::-1]])  # (height, width)
    results = processor.post_process_object_detection(
        outputs, target_sizes=target_sizes, threshold=threshold
    )[0]

    detections: list[dict] = []
    for score, label, box in zip(
        results["scores"], results["labels"], results["boxes"]
    ):
        label_name = model.config.id2label[label.item()]
        if label_name == PERSON_LABEL:
            detections.append({
                "confidence": round(score.item(), 4),
                "box": [round(v, 1) for v in box.tolist()],
            })

    # Sort by confidence descending for readable output
    detections.sort(key=lambda d: d["confidence"], reverse=True)

    return detections, inference_time


# ---------------------------------------------------------------------------
# Synthetic test image
# ---------------------------------------------------------------------------
def create_test_image(save_path: Path) -> Image.Image:
    """Generate a simple synthetic image with person-like silhouettes.

    This is a fallback so the script can run without external images.
    A real photograph will produce far better detection results.
    """
    width, height = 640, 480
    img = Image.new("RGB", (width, height), color=(180, 200, 220))
    draw = ImageDraw.Draw(img)

    # Draw a simple ground / floor
    draw.rectangle([0, 350, 640, 480], fill=(140, 140, 140))

    # Draw several person-like silhouettes (head + body rectangles)
    people = [
        # (head_x, head_y, body_w, body_h, color)
        (100, 180, 30, 120, (60, 60, 120)),
        (200, 160, 35, 140, (120, 50, 50)),
        (320, 170, 32, 130, (50, 100, 60)),
        (420, 190, 28, 110, (100, 80, 40)),
        (530, 175, 33, 125, (70, 70, 100)),
        (150, 200, 26, 100, (80, 60, 90)),
        (460, 185, 30, 115, (90, 70, 50)),
    ]

    for hx, hy, bw, bh, color in people:
        head_r = bw // 3
        # Head (circle approximated as ellipse)
        draw.ellipse(
            [hx - head_r, hy - head_r * 2, hx + head_r, hy],
            fill=color,
        )
        # Body
        draw.rectangle(
            [hx - bw // 2, hy, hx + bw // 2, hy + bh],
            fill=color,
        )
        # Legs
        leg_w = bw // 4
        draw.rectangle(
            [hx - bw // 2, hy + bh, hx - bw // 2 + leg_w, hy + bh + 40],
            fill=color,
        )
        draw.rectangle(
            [hx + bw // 2 - leg_w, hy + bh, hx + bw // 2, hy + bh + 40],
            fill=color,
        )

    img.save(save_path)
    print(f"Synthetic test image saved to: {save_path}")
    return img


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("=" * 60)
    print("CrowdShield AI — Person Detection Test")
    print("=" * 60)

    # ---- Determine image path ----
    if len(sys.argv) > 1:
        image_path = Path(sys.argv[1])
        if not image_path.exists():
            print(f"ERROR: Image not found: {image_path}")
            sys.exit(1)
        print(f"Using provided image: {image_path}")
        image = Image.open(image_path).convert("RGB")
    else:
        image_path = Path(__file__).parent / "test_crowd.png"
        print("No image provided — generating synthetic test image ...")
        image = create_test_image(image_path)

    print(f"Image size: {image.size[0]}x{image.size[1]}")

    # ---- Load model ----
    processor, model = load_model()

    # ---- Run detection ----
    print("\nRunning inference ...")
    detections, inference_time = detect_people(image, processor, model)

    # ---- Print results ----
    print(f"\nInference time: {inference_time:.2f} seconds")
    print(f"Total persons detected: {len(detections)}")
    print()

    for i, det in enumerate(detections, 1):
        print(f"Person {i}")
        print(f"  confidence: {det['confidence']}")
        print(f"  box: {det['box']}")
        print()

    if len(detections) == 0:
        print("NOTE: Zero detections. This is expected with a synthetic image.")
        print("      For real detections, provide an actual photograph:")
        print("        python ml/test_detector.py path/to/crowd_photo.jpg")

    print("=" * 60)
    print("Test complete.")


if __name__ == "__main__":
    main()
