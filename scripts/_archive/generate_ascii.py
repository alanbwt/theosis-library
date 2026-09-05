#!/usr/bin/env python3
"""
generate_ascii.py — Pre-generate high-quality ASCII art from images using PIL.

Uses LANCZOS resampling and histogram normalization for maximum quality.
Outputs JSON with pre-rendered ASCII strings for each image.

Usage:
    python scripts/generate_ascii.py
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "site" / "assets"
OUTPUT_FILE = PROJECT_ROOT / "site" / "data" / "ascii-frames.json"

# Exact density string from scipython
DENSITY = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,"^`\'. '

# Images to process (chronological order)
IMAGES = [
    "gilgamesh-statue.jpg",     # Gilgamesh c. 2100 BCE
    "moses-tablets.jpg",        # Moses with tablets
    "socrates-death.jpg",       # Death of Socrates
    "rembrandt-paul.jpg",       # Rembrandt's Paul
    "christ-bloch.jpg",         # Christ portrait (Bloch)
    "augustine-botticelli.jpg", # Botticelli's Augustine
    "dore-leviathan.png",       # Doré Leviathan
]

# Target ASCII dimensions (characters)
ASCII_WIDTH = 140  # chars wide
ASPECT_CORRECTION = 0.5  # chars are ~2x taller than wide


TARGET_RATIO = 0.55  # rows/cols ratio — produces nearly square visual output (accounting for 0.5 char aspect correction)


def process_image(img_path, width=ASCII_WIDTH):
    """Load image, enhance, and convert to ASCII string."""
    img = Image.open(img_path)

    # Convert to grayscale
    img = img.convert('L')

    # Fixed portrait dimensions — crop image to match, never stretch
    height = int(width * TARGET_RATIO)

    # Crop to target aspect ratio (center crop) BEFORE resizing
    target_aspect = width / (height / ASPECT_CORRECTION)  # undo the 0.5 correction to get pixel aspect
    orig_w, orig_h = img.size
    orig_aspect = orig_w / orig_h

    if orig_aspect > target_aspect:
        # Image is wider — crop sides
        new_w = int(orig_h * target_aspect)
        left = (orig_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, orig_h))
    else:
        # Image is taller — crop top/bottom (center)
        new_h = int(orig_w / target_aspect)
        top = (orig_h - new_h) // 2
        img = img.crop((0, top, orig_w, top + new_h))

    # Resize with LANCZOS (highest quality)
    img = img.resize((width, height), Image.LANCZOS)

    # Histogram normalization: stretch brightness to full 0-255 range
    img = ImageOps.autocontrast(img, cutoff=2)

    # Boost contrast slightly
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)

    # Boost brightness slightly
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.2)

    # Slight sharpen for edge definition
    img = img.filter(ImageFilter.SHARPEN)

    # Convert to numpy array
    arr = np.array(img)
    n = len(DENSITY)

    # Build ASCII lines
    lines = []
    for y in range(height):
        line = ''
        for x in range(width):
            p = arr[y, x]
            k = int(np.floor(p / 256 * n))
            # n-1-k: dark pixel = dense char, bright pixel = sparse char
            char_idx = n - 1 - k
            char_idx = max(0, min(n - 1, char_idx))
            line += DENSITY[char_idx]
        lines.append(line)

    return lines


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    frames = []
    for img_name in IMAGES:
        img_path = ASSETS_DIR / img_name
        if not img_path.exists():
            print(f"  SKIP: {img_name} (not found)")
            continue

        print(f"  Processing: {img_name}")

        # Generate at multiple widths for responsive
        lines_desktop = process_image(img_path, width=140)
        lines_mobile = process_image(img_path, width=90)

        frames.append({
            "name": img_name,
            "desktop": lines_desktop,
            "mobile": lines_mobile,
            "cols_desktop": 140,
            "cols_mobile": 90,
            "rows_desktop": len(lines_desktop),
            "rows_mobile": len(lines_mobile),
        })

        print(f"    Desktop: {140}x{len(lines_desktop)} chars")
        print(f"    Mobile:  {90}x{len(lines_mobile)} chars")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(frames, f, ensure_ascii=False)

    print(f"\nSaved {len(frames)} frames to {OUTPUT_FILE}")
    print(f"File size: {OUTPUT_FILE.stat().st_size // 1024}KB")


if __name__ == "__main__":
    main()
