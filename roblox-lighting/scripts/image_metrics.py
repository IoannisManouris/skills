#!/usr/bin/env python3
"""Compute lightweight diagnostics for one image or a reference/candidate pair.

Requires Pillow. Metrics are diagnostic, not a perceptual ground truth and not a
replacement for camera alignment, region masks, or gameplay review.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageStat
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required: python -m pip install Pillow") from exc


def resampling_lanczos() -> int:
    return getattr(Image, "Resampling", Image).LANCZOS


def load_rgb(path: Path, max_dimension: int) -> Image.Image:
    image = Image.open(path).convert("RGB")
    if max(image.size) > max_dimension:
        scale = max_dimension / max(image.size)
        image = image.resize(
            (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
            resampling_lanczos(),
        )
    return image


def apply_crop(image: Image.Image, crop: tuple[int, int, int, int] | None) -> Image.Image:
    if crop is None:
        return image
    x, y, width, height = crop
    if width <= 0 or height <= 0:
        raise ValueError("crop width and height must be positive")
    return image.crop((x, y, x + width, y + height))


def load_mask(path: Path | None, size: tuple[int, int]) -> Image.Image | None:
    if path is None:
        return None
    mask = Image.open(path).convert("L").resize(size, resampling_lanczos())
    return mask.point(lambda p: 255 if p >= 128 else 0)


def masked_values(image: Image.Image, mask: Image.Image | None) -> Iterable[int]:
    data = image.getdata()
    if mask is None:
        return data
    return (value for value, keep in zip(data, mask.getdata()) if keep)


def percentile_from_hist(hist: list[int], p: float) -> int:
    total = sum(hist)
    if total == 0:
        return 0
    threshold = total * p
    cumulative = 0
    for value, count in enumerate(hist):
        cumulative += count
        if cumulative >= threshold:
            return value
    return 255


def image_stats(image: Image.Image, mask: Image.Image | None = None) -> dict[str, Any]:
    if mask is not None:
        bbox = mask.getbbox()
        if bbox is None:
            raise ValueError("mask contains no selected pixels")
        # ImageStat accepts a mask directly.
        rgb_stat = ImageStat.Stat(image, mask=mask)
    else:
        rgb_stat = ImageStat.Stat(image)

    luma = image.convert("L")
    hsv = image.convert("HSV")
    hist = luma.histogram(mask=mask)
    values = list(masked_values(luma, mask))
    total = len(values)
    if total == 0:
        raise ValueError("image/region contains no pixels")

    clipped_black = sum(1 for v in values if v <= 2) / total
    clipped_white = sum(1 for v in values if v >= 253) / total
    sat_stat = ImageStat.Stat(hsv.getchannel("S"), mask=mask)

    return {
        "size": [image.width, image.height],
        "pixel_count": total,
        "mean_rgb": [round(v, 4) for v in rgb_stat.mean[:3]],
        "mean_luma": round(sum(values) / total, 4),
        "luma_stddev": round(ImageStat.Stat(luma, mask=mask).stddev[0], 4),
        "luma_percentiles": {
            "p01": percentile_from_hist(hist, 0.01),
            "p05": percentile_from_hist(hist, 0.05),
            "p50": percentile_from_hist(hist, 0.50),
            "p95": percentile_from_hist(hist, 0.95),
            "p99": percentile_from_hist(hist, 0.99),
        },
        "clipped_black_fraction": round(clipped_black, 6),
        "clipped_white_fraction": round(clipped_white, 6),
        "mean_saturation_0_255": round(sat_stat.mean[0], 4),
        "luma_histogram": hist,
    }


def histogram_l1(a: list[int], b: list[int]) -> float:
    total_a = sum(a) or 1
    total_b = sum(b) or 1
    return 0.5 * sum(abs(x / total_a - y / total_b) for x, y in zip(a, b))


def global_ssim(a: Image.Image, b: Image.Image, mask: Image.Image | None) -> float:
    av = list(masked_values(a.convert("L"), mask))
    bv = list(masked_values(b.convert("L"), mask))
    if len(av) != len(bv) or not av:
        return 0.0
    n = len(av)
    mean_a = sum(av) / n
    mean_b = sum(bv) / n
    if n > 1:
        var_a = sum((x - mean_a) ** 2 for x in av) / (n - 1)
        var_b = sum((x - mean_b) ** 2 for x in bv) / (n - 1)
        cov = sum((x - mean_a) * (y - mean_b) for x, y in zip(av, bv)) / (n - 1)
    else:
        var_a = var_b = cov = 0.0
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    numerator = (2 * mean_a * mean_b + c1) * (2 * cov + c2)
    denominator = (mean_a**2 + mean_b**2 + c1) * (var_a + var_b + c2)
    return numerator / denominator if denominator else 1.0


def pair_metrics(reference: Image.Image, candidate: Image.Image, mask: Image.Image | None) -> dict[str, Any]:
    if candidate.size != reference.size:
        candidate = candidate.resize(reference.size, resampling_lanczos())

    diff = ImageChops.difference(reference, candidate)
    if mask is not None:
        black = Image.new("RGB", reference.size, (0, 0, 0))
        diff = Image.composite(diff, black, mask)

    hist = diff.histogram()
    channel_counts = [sum(hist[channel * 256 : (channel + 1) * 256]) for channel in range(3)]
    channel_abs = [
        sum(value * count for value, count in enumerate(hist[channel * 256 : (channel + 1) * 256]))
        for channel in range(3)
    ]
    mae_channels = [channel_abs[i] / max(1, channel_counts[i]) for i in range(3)]

    ref_pixels = list(masked_values(reference.convert("L"), mask))
    cand_pixels = list(masked_values(candidate.convert("L"), mask))
    sq = sum((a - b) ** 2 for a, b in zip(ref_pixels, cand_pixels))
    luma_rmse = math.sqrt(sq / max(1, len(ref_pixels)))

    ref_edges = reference.convert("L").filter(ImageFilter.FIND_EDGES)
    cand_edges = candidate.convert("L").filter(ImageFilter.FIND_EDGES)
    edge_diff = ImageChops.difference(ref_edges, cand_edges)
    edge_mae = ImageStat.Stat(edge_diff, mask=mask).mean[0]

    ref_stats = image_stats(reference, mask)
    cand_stats = image_stats(candidate, mask)

    result = {
        "reference": {k: v for k, v in ref_stats.items() if k != "luma_histogram"},
        "candidate": {k: v for k, v in cand_stats.items() if k != "luma_histogram"},
        "comparison": {
            "rgb_mae": round(sum(mae_channels) / 3, 6),
            "rgb_mae_channels": [round(v, 6) for v in mae_channels],
            "luma_rmse": round(luma_rmse, 6),
            "luma_histogram_l1": round(
                histogram_l1(ref_stats["luma_histogram"], cand_stats["luma_histogram"]), 6
            ),
            "edge_mae": round(edge_mae, 6),
            "global_ssim": round(global_ssim(reference, candidate, mask), 6),
            "mean_luma_delta": round(cand_stats["mean_luma"] - ref_stats["mean_luma"], 6),
            "mean_rgb_delta": [
                round(cand_stats["mean_rgb"][i] - ref_stats["mean_rgb"][i], 6) for i in range(3)
            ],
            "warning": "Metrics are meaningful only after camera/geometry alignment and should be combined with region masks and gameplay review."
        },
    }
    return result


def parse_crop(values: list[int] | None) -> tuple[int, int, int, int] | None:
    return tuple(values) if values else None  # type: ignore[return-value]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("candidate", type=Path, nargs="?")
    parser.add_argument("--mask", type=Path)
    parser.add_argument("--crop", type=int, nargs=4, metavar=("X", "Y", "W", "H"))
    parser.add_argument("--max-dimension", type=int, default=512)
    parser.add_argument("--json", dest="json_path", type=Path)
    parser.add_argument("--diff", type=Path)
    args = parser.parse_args()

    try:
        crop = parse_crop(args.crop)
        reference = apply_crop(load_rgb(args.reference, args.max_dimension), crop)
        mask = load_mask(args.mask, reference.size)

        if args.candidate is None:
            stats = image_stats(reference, mask)
            stats.pop("luma_histogram", None)
            output: dict[str, Any] = {"image": str(args.reference), "stats": stats}
        else:
            candidate = apply_crop(load_rgb(args.candidate, args.max_dimension), crop)
            if candidate.size != reference.size:
                candidate = candidate.resize(reference.size, resampling_lanczos())
            output = pair_metrics(reference, candidate, mask)
            output["reference_file"] = str(args.reference)
            output["candidate_file"] = str(args.candidate)

            if args.diff:
                diff = ImageChops.difference(reference, candidate)
                if mask is not None:
                    diff = Image.composite(diff, Image.new("RGB", diff.size, (0, 0, 0)), mask)
                diff = ImageEnhance.Contrast(diff).enhance(2.0)
                args.diff.parent.mkdir(parents=True, exist_ok=True)
                diff.save(args.diff)
                output["diff_file"] = str(args.diff)

        rendered = json.dumps(output, indent=2)
        print(rendered)
        if args.json_path:
            args.json_path.parent.mkdir(parents=True, exist_ok=True)
            args.json_path.write_text(rendered + "\n", encoding="utf-8")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
