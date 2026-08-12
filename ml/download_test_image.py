"""Download a sample crowd image for testing the person detector.

Uses the COCO dataset sample from Hugging Face which is always accessible.
"""

import sys
sys.path.insert(0, r"c:\Users\Dell\crowdshield-ai\backend\.venv\Lib\site-packages")

from pathlib import Path
from PIL import Image
import urllib.request
import io

OUT = Path(__file__).parent / "test_crowd_real.jpg"

# Use a known-accessible sample image from the Hugging Face COCO dataset
# This is a standard COCO validation image with people
URL = "http://images.cocodataset.org/val2017/000000039769.jpg"

# Fallback: Hugging Face hosted sample
URLS = [
    "http://images.cocodataset.org/val2017/000000039769.jpg",
    "http://images.cocodataset.org/val2017/000000000139.jpg",
    "http://images.cocodataset.org/val2017/000000397133.jpg",
]

def download():
    for url in URLS:
        try:
            print(f"Trying: {url}")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=15)
            data = resp.read()
            img = Image.open(io.BytesIO(data)).convert("RGB")
            img.save(str(OUT))
            print(f"Saved to: {OUT}  ({img.size[0]}x{img.size[1]})")
            return True
        except Exception as e:
            print(f"  Failed: {e}")
    return False

if __name__ == "__main__":
    if not download():
        print("Could not download any sample image.")
        print("Please manually provide an image to: ml/test_crowd_real.jpg")
        sys.exit(1)
    print("Done")
