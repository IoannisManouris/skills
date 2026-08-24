#!/usr/bin/env python3
"""Validate a Roblox lighting observation ledger without external dependencies."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

MODES = {
    "FROM_SCRATCH",
    "MATCH_SCREENSHOT",
    "LINK_ASSISTED_MATCH",
    "IMPROVE_OR_DEBUG",
    "AUDIT_OR_OPTIMIZE",
}
CATEGORIES = {
    "camera",
    "geometry",
    "materials",
    "global_light",
    "shadows",
    "ambient_fill",
    "exposure_tone",
    "sky_clouds",
    "atmosphere_fog",
    "local_lights",
    "emissive_bloom",
    "reflections",
    "post_processing",
    "gameplay_readability",
    "performance",
    "accessibility",
    "other",
}


def finite_probability(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= 1


def validate(payload: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    if payload.get("mode") not in MODES:
        errors.append(f"mode must be one of {sorted(MODES)}")

    sources = payload.get("sources")
    if not isinstance(sources, list):
        errors.append("sources must be an array")
        sources = []
    source_ids: set[str] = set()
    included_count = 0
    for index, source in enumerate(sources):
        path = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{path} must be an object")
            continue
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"{path}.source_id is required")
        elif source_id in source_ids:
            errors.append(f"duplicate source_id: {source_id}")
        else:
            source_ids.add(source_id)
        if not isinstance(source.get("included"), bool):
            errors.append(f"{path}.included must be boolean")
        elif source["included"]:
            included_count += 1
        for key in ("experience_identity_confidence", "raw_gameplay_confidence"):
            if key in source and not finite_probability(source[key]):
                errors.append(f"{path}.{key} must be between 0 and 1")
        similarity = source.get("similarity_to_primary")
        if similarity is not None and not finite_probability(similarity):
            errors.append(f"{path}.similarity_to_primary must be null or between 0 and 1")

    observations = payload.get("observations")
    if not isinstance(observations, list) or not observations:
        errors.append("observations must be a non-empty array")
        observations = []
    observation_ids: set[str] = set()
    categories_seen: set[str] = set()
    for index, observation in enumerate(observations):
        path = f"observations[{index}]"
        if not isinstance(observation, dict):
            errors.append(f"{path} must be an object")
            continue
        oid = observation.get("id")
        if not isinstance(oid, str) or not oid:
            errors.append(f"{path}.id is required")
        elif oid in observation_ids:
            errors.append(f"duplicate observation id: {oid}")
        else:
            observation_ids.add(oid)
        category = observation.get("category")
        if category not in CATEGORIES:
            errors.append(f"{path}.category must be one of {sorted(CATEGORIES)}")
        else:
            categories_seen.add(category)
        evidence = observation.get("evidence")
        if not isinstance(evidence, list) or not evidence or not all(isinstance(v, str) and v for v in evidence):
            errors.append(f"{path}.evidence must be a non-empty string array")
        if not isinstance(observation.get("inference"), str) or not observation["inference"]:
            errors.append(f"{path}.inference is required")
        if not finite_probability(observation.get("confidence")):
            errors.append(f"{path}.confidence must be between 0 and 1")
        for key in ("alternatives", "confounders"):
            if not isinstance(observation.get(key), list):
                errors.append(f"{path}.{key} must be an array")
        refs = observation.get("source_ids", [])
        if not isinstance(refs, list):
            errors.append(f"{path}.source_ids must be an array")
        else:
            unknown = sorted({ref for ref in refs if ref not in source_ids})
            if unknown:
                errors.append(f"{path}.source_ids reference unknown sources: {', '.join(map(str, unknown))}")

    hypotheses = payload.get("hypotheses")
    if not isinstance(hypotheses, list) or not 1 <= len(hypotheses) <= 3:
        errors.append("hypotheses must contain 1 to 3 items")
        hypotheses = []
    hypothesis_ids: set[str] = set()
    for index, hypothesis in enumerate(hypotheses):
        path = f"hypotheses[{index}]"
        if not isinstance(hypothesis, dict):
            errors.append(f"{path} must be an object")
            continue
        hid = hypothesis.get("id")
        if not isinstance(hid, str) or not hid:
            errors.append(f"{path}.id is required")
        elif hid in hypothesis_ids:
            errors.append(f"duplicate hypothesis id: {hid}")
        else:
            hypothesis_ids.add(hid)
        for key in ("confidence", "roblox_feasibility", "gameplay_fit"):
            if not finite_probability(hypothesis.get(key)):
                errors.append(f"{path}.{key} must be between 0 and 1")
        for key in ("explains", "assumptions"):
            if not isinstance(hypothesis.get(key), list):
                errors.append(f"{path}.{key} must be an array")

    preferred = payload.get("preferred_hypothesis_id")
    if preferred is not None and preferred not in hypothesis_ids:
        errors.append("preferred_hypothesis_id must reference an existing hypothesis")
    if preferred is None and hypotheses:
        warnings.append("No preferred hypothesis selected")

    limitations = payload.get("limitations")
    if not isinstance(limitations, list):
        errors.append("limitations must be an array")
    elif payload.get("mode") in {"MATCH_SCREENSHOT", "LINK_ASSISTED_MATCH"} and not limitations:
        warnings.append("Screenshot matching ledger has no limitations; check for false certainty")

    if payload.get("mode") in {"MATCH_SCREENSHOT", "LINK_ASSISTED_MATCH"}:
        recommended = {"camera", "global_light", "shadows", "exposure_tone", "atmosphere_fog", "post_processing"}
        missing = sorted(recommended - categories_seen)
        if missing:
            warnings.append("Screenshot ledger is missing recommended observation categories: " + ", ".join(missing))
        if included_count == 0:
            warnings.append("No source is marked included")

    return errors, sorted(set(warnings))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    try:
        payload = json.loads(args.ledger.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: could not read JSON: {exc}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("ERROR: ledger root must be a JSON object", file=sys.stderr)
        return 2

    errors, warnings = validate(payload)
    result = {"valid": not errors, "errors": errors, "warnings": warnings}
    for warning in warnings:
        print("WARNING:", warning)
    for error in errors:
        print("ERROR:", error)
    print(f"{'PASS' if not errors else 'FAILED'}: {len(errors)} error(s), {len(warnings)} warning(s)")

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
