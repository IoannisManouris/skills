#!/usr/bin/env python3
"""Normalize RGBA images or pack an explicitly ordered atlas; never upload assets."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import warnings
from PIL import Image, ImageChops

Image.MAX_IMAGE_PIXELS = 32_000_000  # Local helper safety bound, NOT a Roblox limit.
warnings.simplefilter("error", Image.DecompressionBombWarning)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Image.Image:
    with Image.open(path) as im:
        if getattr(im, "n_frames", 1) != 1:
            raise ValueError("Animated image input must be exported to ordered individual frames first")
        im.load()
        return im.convert("RGBA")


def normalize(im: Image.Image, size: int, alpha: str = "preserve", white: bool = False, pixel: bool = False) -> Image.Image:
    if not 1 <= size <= 4096: raise ValueError("Helper output size must be 1..4096 (a local safety bound)")
    im = im.convert("RGBA")
    if alpha == "luminance":
        im.putalpha(ImageChops.multiply(im.convert("RGB").convert("L"), im.getchannel("A")))
    elif alpha != "preserve": raise ValueError("Unknown alpha mode")
    if white:
        a = im.getchannel("A"); im = Image.new("RGBA", im.size, (255, 255, 255, 255)); im.putalpha(a)
    scale = min(size / im.width, size / im.height)
    dims = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
    im = im.resize(dims, Image.Resampling.NEAREST if pixel else Image.Resampling.LANCZOS)
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(im, ((size - im.width) // 2, (size - im.height) // 2))  # No second alpha multiplication.
    return result


def pack(frames: list[Image.Image], columns: int, rows: int, allow_empty: bool = False) -> Image.Image:
    if not frames or columns < 1 or rows < 1: raise ValueError("Supply frames and positive grid dimensions")
    if len(frames) > columns * rows or (len(frames) != columns * rows and not allow_empty):
        raise ValueError("Frame count must equal grid cells, unless --allow-empty is intentional")
    cell = frames[0].size
    if any(f.size != cell for f in frames): raise ValueError("All frames must have identical dimensions")
    if cell[0] * columns * cell[1] * rows > 32_000_000: raise ValueError("Atlas exceeds local pixel budget")
    result = Image.new("RGBA", (cell[0] * columns, cell[1] * rows), (0, 0, 0, 0))
    for i, im in enumerate(frames): result.paste(im.convert("RGBA"), ((i % columns) * cell[0], (i // columns) * cell[1]))
    return result


def save(im: Image.Image, output: Path, metadata: dict):
    record_path = output.with_suffix(output.suffix + ".meta.json")
    if output.suffix.lower() != ".png": raise ValueError("Prepared output must be PNG")
    if output.exists() or record_path.exists(): raise ValueError("Output exists; choose a new filename")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream: im.save(stream, format="PNG")
    metadata.update({"output": str(output), "sha256": digest(output), "size": list(im.size),
                     "alpha_extrema": list(im.getchannel("A").getextrema()),
                     "rights_note": "Processing does not grant or change rights. Link this derivative to the source asset manifest."})
    record_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest="command", required=True)
    n = sub.add_parser("normalize"); n.add_argument("source", type=Path); n.add_argument("output", type=Path)
    n.add_argument("--size", type=int, default=512); n.add_argument("--alpha", choices=["preserve", "luminance"], default="preserve")
    n.add_argument("--white", action="store_true"); n.add_argument("--pixel", action="store_true")
    a = sub.add_parser("atlas"); a.add_argument("output", type=Path); a.add_argument("frames", type=Path, nargs="+")
    a.add_argument("--columns", type=int, required=True); a.add_argument("--rows", type=int, required=True); a.add_argument("--allow-empty", action="store_true")
    args = p.parse_args()
    try:
        if args.command == "normalize":
            im = normalize(load(args.source), args.size, args.alpha, args.white, args.pixel)
            m = {"operation": "normalize", "source": str(args.source), "source_sha256": digest(args.source),
                 "alpha_mode": args.alpha, "white": args.white, "pixel_resampling": args.pixel}
        else:
            im = pack([load(f) for f in args.frames], args.columns, args.rows, args.allow_empty)
            m = {"operation": "atlas", "order": "row-major, exact command-line order", "columns": args.columns, "rows": args.rows,
                 "frames": [{"path": str(f), "sha256": digest(f)} for f in args.frames], "allow_empty": args.allow_empty}
        print(json.dumps(save(im, args.output, m), indent=2))
    except Exception as e: p.exit(1, f"prepare_texture: {e}\n")

if __name__ == "__main__": main()
