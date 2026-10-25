"""Create a tolerance-aware red-overlay PNG diff for two audit screenshots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops


def padded(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGBA", size, (255, 255, 255, 255))
    canvas.alpha_composite(image.convert("RGBA"), (0, 0))
    return canvas


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("streamlit", type=Path)
    parser.add_argument("nextjs", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--threshold", type=int, default=24)
    args = parser.parse_args()

    with Image.open(args.streamlit) as left_source, Image.open(args.nextjs) as right_source:
        size = (
            max(left_source.width, right_source.width),
            max(left_source.height, right_source.height),
        )
        left = padded(left_source, size)
        right = padded(right_source, size)

    raw = ImageChops.difference(left.convert("RGB"), right.convert("RGB"))
    mask = raw.convert("L").point(lambda value: 255 if value > args.threshold else 0)
    changed = sum(mask.histogram()[1:]) // 255
    total = size[0] * size[1]
    overlay = Image.new("RGBA", size, (220, 38, 38, 0))
    overlay.putalpha(mask)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(args.output, optimize=True)
    print(json.dumps({
        "changed_pixels": changed,
        "total_pixels": total,
        "difference_pct": round(changed / total * 100, 4) if total else 0.0,
        "width": size[0],
        "height": size[1],
    }))


if __name__ == "__main__":
    main()
