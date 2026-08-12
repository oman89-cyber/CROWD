"""Generate a short synthetic test video with person-like silhouettes.

Creates a ~3-second, 30 FPS video (90 frames) with simple moving figures
so the YOLOS detector pipeline can be exercised end-to-end on CPU without
needing an external crowd video.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np


def create_test_video(out_path: str | Path, n_frames: int = 90, fps: int = 30) -> Path:
    """Write a short synthetic video with moving person-like shapes.

    Parameters
    ----------
    out_path : path
        Destination .mp4 file.
    n_frames : int
        Total frame count (default 90 → 3 s at 30 fps).
    fps : int
        Frames per second.

    Returns
    -------
    Path
        Absolute path to the written video.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    W, H = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(out), fourcc, fps, (W, H))

    if not writer.isOpened():
        raise RuntimeError(f"Cannot open VideoWriter for {out}")

    # Deterministic seed for reproducibility
    rng = np.random.RandomState(42)

    # Define 6 "people" with starting positions and velocities
    people = []
    for i in range(6):
        x = 60 + i * 100
        y = rng.randint(150, 280)
        vx = rng.choice([-2, -1, 1, 2])
        vy = 0
        body_w = rng.randint(28, 42)
        body_h = rng.randint(100, 150)
        color = tuple(int(c) for c in rng.randint(30, 120, size=3))
        skin = (180 + rng.randint(0, 40), 150 + rng.randint(0, 30), 120 + rng.randint(0, 30))
        people.append(dict(x=x, y=y, vx=vx, vy=vy, bw=body_w, bh=body_h,
                           color=color, skin=skin))

    for fi in range(n_frames):
        # Sky-to-ground gradient background
        frame = np.zeros((H, W, 3), dtype=np.uint8)
        for row in range(H):
            t = row / H
            frame[row, :] = (
                int(200 - 80 * t),   # B
                int(210 - 100 * t),  # G
                int(230 - 130 * t),  # R
            )
        # Ground
        frame[380:, :] = (100, 100, 100)

        # Draw each person
        for p in people:
            px, py, bw, bh = int(p["x"]), int(p["y"]), p["bw"], p["bh"]

            # Body rectangle
            cv2.rectangle(frame,
                          (px - bw // 2, py),
                          (px + bw // 2, py + bh),
                          p["color"], -1)

            # Head circle
            head_r = bw // 3
            cv2.circle(frame, (px, py - head_r), head_r, p["skin"], -1)

            # Legs
            leg_w = bw // 5
            cv2.rectangle(frame,
                          (px - bw // 3, py + bh),
                          (px - bw // 3 + leg_w, py + bh + 45),
                          p["color"], -1)
            cv2.rectangle(frame,
                          (px + bw // 3 - leg_w, py + bh),
                          (px + bw // 3, py + bh + 45),
                          p["color"], -1)

            # Move
            p["x"] += p["vx"]
            if p["x"] < 40 or p["x"] > W - 40:
                p["vx"] *= -1

        writer.write(frame)

    writer.release()
    print(f"Test video written: {out}  ({n_frames} frames, {fps} fps, "
          f"{n_frames / fps:.1f}s)")
    return out.resolve()


if __name__ == "__main__":
    dst = sys.argv[1] if len(sys.argv) > 1 else "ml/test_crowd.mp4"
    create_test_video(dst)
