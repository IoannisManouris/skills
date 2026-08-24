#!/usr/bin/env python3
"""Cluster screenshots by broad lighting appearance and rank them against a reference.

Requires Pillow. The output is a triage aid: verify map/state identity visually before
using any cluster as lighting evidence.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageStat
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required: python -m pip install Pillow") from exc

EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
FEATURE_NAMES = [
    "mean_r",
    "mean_g",
    "mean_b",
    "top_r",
    "top_g",
    "top_b",
    "bottom_r",
    "bottom_g",
    "bottom_b",
    "mean_luma",
    "luma_std",
    "mean_saturation",
    "luma_p10",
    "luma_p50",
    "luma_p90",
]
WEIGHTS = [1.0, 1.0, 1.0, 1.2, 1.2, 1.2, 0.9, 0.9, 0.9, 1.2, 0.7, 0.7, 0.6, 0.8, 0.8]


def lanczos() -> int:
    return getattr(Image, "Resampling", Image).LANCZOS


def percentile(hist: list[int], fraction: float) -> float:
    total = sum(hist) or 1
    target = total * fraction
    cumulative = 0
    for value, count in enumerate(hist):
        cumulative += count
        if cumulative >= target:
            return value / 255.0
    return 1.0


def mean_rgb(image: Image.Image) -> list[float]:
    return [value / 255.0 for value in ImageStat.Stat(image).mean[:3]]


def extract(path: Path) -> list[float]:
    image = Image.open(path).convert("RGB")
    image.thumbnail((160, 160), lanczos())
    if image.width < 2 or image.height < 3:
        raise ValueError("image is too small")

    top = image.crop((0, 0, image.width, max(1, image.height // 3)))
    bottom = image.crop((0, image.height * 2 // 3, image.width, image.height))
    luma = image.convert("L")
    saturation = image.convert("HSV").getchannel("S")
    luma_stat = ImageStat.Stat(luma)
    hist = luma.histogram()

    values = (
        mean_rgb(image)
        + mean_rgb(top)
        + mean_rgb(bottom)
        + [
            luma_stat.mean[0] / 255.0,
            luma_stat.stddev[0] / 255.0,
            ImageStat.Stat(saturation).mean[0] / 255.0,
            percentile(hist, 0.10),
            percentile(hist, 0.50),
            percentile(hist, 0.90),
        ]
    )
    return [round(value, 6) for value in values]


def distance(a: list[float], b: list[float]) -> float:
    numerator = sum(weight * (x - y) ** 2 for x, y, weight in zip(a, b, WEIGHTS))
    denominator = sum(WEIGHTS)
    return math.sqrt(numerator / denominator)


def centroid(vectors: list[list[float]]) -> list[float]:
    return [sum(row[i] for row in vectors) / len(vectors) for i in range(len(vectors[0]))]


def collect(paths: list[Path], recursive: bool) -> list[Path]:
    output: list[Path] = []
    for path in paths:
        if path.is_dir():
            iterator = path.rglob("*") if recursive else path.glob("*")
            output.extend(item for item in iterator if item.is_file() and item.suffix.lower() in EXTENSIONS)
        elif path.is_file() and path.suffix.lower() in EXTENSIONS:
            output.append(path)
    return sorted(set(item.resolve() for item in output))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--threshold", type=float, default=0.115, help="greedy cluster distance threshold")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    files = collect(args.inputs, args.recursive)
    if not files:
        print("ERROR: no supported images found", file=sys.stderr)
        return 2

    records: list[dict[str, Any]] = []
    for path in files:
        try:
            vector = extract(path)
            records.append({"file": str(path), "features": dict(zip(FEATURE_NAMES, vector)), "_vector": vector})
        except Exception as exc:  # noqa: BLE001
            records.append({"file": str(path), "error": str(exc), "_vector": None})

    valid = [record for record in records if record["_vector"] is not None]
    if not valid:
        print("ERROR: all images failed feature extraction", file=sys.stderr)
        return 1

    clusters: list[dict[str, Any]] = []
    for record in valid:
        best_index = None
        best_distance = float("inf")
        for index, cluster in enumerate(clusters):
            d = distance(record["_vector"], cluster["_centroid"])
            if d < best_distance:
                best_index, best_distance = index, d
        if best_index is None or best_distance > args.threshold:
            clusters.append({"members": [record], "_centroid": list(record["_vector"])})
        else:
            clusters[best_index]["members"].append(record)
            clusters[best_index]["_centroid"] = centroid([member["_vector"] for member in clusters[best_index]["members"]])

    reference_vector = None
    if args.reference:
        try:
            reference_vector = extract(args.reference)
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR: could not extract reference features: {exc}", file=sys.stderr)
            return 2
        for record in valid:
            record["distance_to_reference"] = round(distance(reference_vector, record["_vector"]), 6)
        valid.sort(key=lambda record: record["distance_to_reference"])

    rendered_clusters = []
    for index, cluster in enumerate(clusters, start=1):
        members = cluster["members"]
        score = None
        if reference_vector is not None:
            score = distance(reference_vector, cluster["_centroid"])
        rendered_clusters.append(
            {
                "cluster_id": f"C{index}",
                "member_count": len(members),
                "distance_to_reference": round(score, 6) if score is not None else None,
                "centroid_features": dict(zip(FEATURE_NAMES, [round(v, 6) for v in cluster["_centroid"]])),
                "members": [
                    {
                        "file": member["file"],
                        "distance_to_reference": member.get("distance_to_reference"),
                    }
                    for member in members
                ],
            }
        )
    if reference_vector is not None:
        rendered_clusters.sort(key=lambda cluster: cluster["distance_to_reference"])

    for record in records:
        record.pop("_vector", None)

    output = {
        "schema_version": "1.0",
        "reference": str(args.reference.resolve()) if args.reference else None,
        "threshold": args.threshold,
        "feature_warning": "These broad color/luma features group likely lighting states, not map identity or exact illumination. Perform visual verification.",
        "images": records,
        "ranked_matches": [
            {"file": record["file"], "distance_to_reference": record.get("distance_to_reference")}
            for record in valid
        ] if reference_vector is not None else [],
        "clusters": rendered_clusters,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}: {len(valid)} image(s), {len(clusters)} cluster(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
