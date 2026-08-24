#!/usr/bin/env python3
"""Create a valid first-pass Roblox lighting plan from a genre starting hypothesis."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_plan import validate_plan

ROOT = Path(__file__).resolve().parents[1]
PROFILES_PATH = ROOT / "assets" / "genre-starting-points.json"
MODES = [
    "FROM_SCRATCH",
    "MATCH_SCREENSHOT",
    "LINK_ASSISTED_MATCH",
    "IMPROVE_OR_DEBUG",
    "AUDIT_OR_OPTIMIZE",
]


def midpoint(profile: dict[str, Any], key: str, default: float) -> float:
    values = profile.get(key)
    if isinstance(values, list) and len(values) == 2 and all(isinstance(v, (int, float)) for v in values):
        return round((float(values[0]) + float(values[1])) / 2, 4)
    return default


def slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")
    return value[:80] or "roblox-lighting-plan"


def make_plan(args: argparse.Namespace, profile: dict[str, Any]) -> dict[str, Any]:
    lighting_style = profile.get("LightingStyle")
    if not isinstance(lighting_style, str):
        options = profile.get("LightingStyle_options", ["Realistic"])
        lighting_style = options[0] if isinstance(options, list) and options else "Realistic"

    clock_time = midpoint(profile, "ClockTime_range", 13.5)
    exposure = midpoint(profile, "ExposureCompensation_range", 0.0)
    softness = midpoint(profile, "ShadowSoftness_range", 0.55)
    diffuse = midpoint(profile, "EnvironmentDiffuseScale_range", 0.7)
    specular = midpoint(profile, "EnvironmentSpecularScale_range", 0.7)
    density = midpoint(profile, "AtmosphereDensity_range", 0.16)
    haze = round(min(3.0, max(0.0, density * 4.0)), 4)

    screenshot_mode = args.mode in {"MATCH_SCREENSHOT", "LINK_ASSISTED_MATCH"}
    ambiguity = []
    if screenshot_mode:
        ambiguity.append(
            {
                "question": "Is the reference exposure/color native gameplay output or an edited capture?",
                "impact": "May shift exposure, contrast, saturation, and bloom estimates without changing scene illumination.",
                "best_next_evidence": "A second raw gameplay frame from the same location and lighting state.",
                "confidence": 0.35,
            }
        )

    base_light_ids: list[str] = []
    plan: dict[str, Any] = {
        "schema_version": "1.0",
        "plan_id": slug(args.plan_id),
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "mode": args.mode,
        "intent": {
            "thesis": f"Starting hypothesis for {args.genre}: {profile.get('posture', 'coherent, readable Roblox lighting')}",
            "genre": args.genre,
            "mood": args.mood or ["coherent", "readable"],
            "target_state": args.target_state,
            "camera_use": args.camera_use,
            "minimum_platform": args.minimum_platform,
        },
        "sources": [],
        "assumptions": [
            "Values are profile midpoints, not final calibrated settings.",
            "The map, camera, material response, and gameplay routes still require visual audit.",
        ],
        "confidence": 0.35 if screenshot_mode else 0.45,
        "lighting": {
            "properties": {
                "Ambient": [65, 68, 76],
                "Brightness": 2.0,
                "ClockTime": clock_time,
                "ColorShift_Bottom": [0, 0, 0],
                "ColorShift_Top": [0, 0, 0],
                "EnvironmentDiffuseScale": diffuse,
                "EnvironmentSpecularScale": specular,
                "ExposureCompensation": exposure,
                "GeographicLatitude": 41.0,
                "GlobalShadows": True,
                "LightingStyle": lighting_style,
                "OutdoorAmbient": [125, 128, 138],
                "PrioritizeLightingQuality": True,
                "ShadowSoftness": softness,
            },
            "manual_properties": {},
            "sky": {
                "enabled": True,
                "name": "RobloxLightingSky",
                "properties": {
                    "CelestialBodiesShown": True,
                    "StarCount": 3000,
                    "SunAngularSize": 21,
                    "MoonAngularSize": 11,
                },
            },
            "atmosphere": {
                "enabled": True,
                "name": "RobloxLightingAtmosphere",
                "properties": {
                    "Color": [199, 199, 199],
                    "Decay": [106, 112, 125],
                    "Density": density,
                    "Glare": 0.0,
                    "Haze": haze,
                    "Offset": 0.0,
                },
            },
            "legacy_fog": {"enabled": False},
            "clouds": None,
            "post_effects": [
                {
                    "class": "ColorGradingEffect",
                    "name": "RobloxLightingToneMapper",
                    "parent": "Lighting",
                    "enabled": True,
                    "properties": {"TonemapperPreset": "Default"},
                    "quality_tiers": ["low", "medium", "high"],
                    "rationale": "Keep one explicit tone-mapper authority.",
                },
                {
                    "class": "ColorCorrectionEffect",
                    "name": "RobloxLightingGrade",
                    "parent": "Lighting",
                    "enabled": True,
                    "properties": {
                        "Brightness": 0.0,
                        "Contrast": 0.02,
                        "Saturation": 0.0,
                        "TintColor": [255, 255, 255],
                    },
                    "quality_tiers": ["low", "medium", "high"],
                    "rationale": "Near-neutral starting grade; solve illumination first.",
                },
                {
                    "class": "BloomEffect",
                    "name": "RobloxLightingBloom",
                    "parent": "Lighting",
                    "enabled": True,
                    "properties": {"Intensity": 0.12, "Size": 18, "Threshold": 1.1},
                    "quality_tiers": ["medium", "high"],
                    "rationale": "Restrained highlight spread; tune threshold before intensity.",
                },
            ],
        },
        "local_lights": [],
        "material_geometry_actions": [
            {
                "target": "Map-wide",
                "action": "Audit wall thickness, gaps, normals, CastShadow, albedo, roughness, and metalness before compensating with lighting.",
                "reason": "Geometry/material errors can imitate lighting errors.",
                "priority": "required",
            }
        ],
        "runtime_profiles": [],
        "quality_tiers": {
            "low": {
                "goal": "Preserve route, hazard, avatar, and interactable readability with minimal optional effects.",
                "enabled_light_ids": base_light_ids,
                "enabled_post_effects": ["RobloxLightingToneMapper", "RobloxLightingGrade"],
                "notes": ["Do not depend on dynamic shadows or bloom for gameplay information."],
            },
            "medium": {
                "goal": "Preserve the intended mood with restrained effects and selected local lights.",
                "enabled_light_ids": base_light_ids,
                "enabled_post_effects": ["RobloxLightingToneMapper", "RobloxLightingGrade", "RobloxLightingBloom"],
                "notes": ["Profile the densest camera view."],
            },
            "high": {
                "goal": "Full approved art direction without sacrificing gameplay clarity.",
                "enabled_light_ids": base_light_ids,
                "enabled_post_effects": ["RobloxLightingToneMapper", "RobloxLightingGrade", "RobloxLightingBloom"],
                "notes": ["Validate specular response, shadow quality, and atmosphere at native resolution."],
            },
        },
        "validation": {
            "views": [
                {"id": "spawn", "purpose": "first-impression hierarchy and adaptation"},
                {"id": "critical-route", "purpose": "route, hazard, enemy, and interactable readability"},
                {"id": "worst-performance", "purpose": "maximum overlapping lights/shadows/effects"},
            ],
            "image_metrics": ["regional luma percentiles", "clipped black/white fraction", "shadow-direction agreement"],
            "gameplay_gates": [
                "Primary route is readable within two seconds.",
                "Critical hazards and interactables remain distinguishable on low quality.",
                "No required information depends only on color, bloom, or dynamic shadows.",
            ],
            "performance_gates": [
                "Profile representative low, medium, and high graphics conditions.",
                "No avoidable dense overlap of large shadow-casting local lights.",
            ],
            "stopping_criteria": [
                "All gameplay and performance gates pass.",
                "Two consecutive fine adjustments produce no meaningful perceptual improvement.",
            ],
        },
        "unresolved_ambiguities": ambiguity,
    }
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--genre", default="stylized_cartoon")
    parser.add_argument("--mode", choices=MODES, default="FROM_SCRATCH")
    parser.add_argument("--plan-id", default="roblox-lighting-first-pass")
    parser.add_argument("--target-state", default="primary gameplay")
    parser.add_argument("--mood", action="append", help="repeat for multiple mood words")
    parser.add_argument("--camera-use", default="third-person gameplay")
    parser.add_argument("--minimum-platform", default="low-end mobile")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--list-genres", action="store_true")
    args = parser.parse_args()

    try:
        payload = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
        profiles = payload["profiles"]
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: could not read profiles: {exc}", file=sys.stderr)
        return 2

    if args.list_genres:
        print("\n".join(sorted(profiles)))
        return 0
    if args.genre not in profiles:
        print(f"ERROR: unknown genre '{args.genre}'. Available: {', '.join(sorted(profiles))}", file=sys.stderr)
        return 2

    plan = make_plan(args, profiles[args.genre])
    errors, warnings = validate_plan(plan)
    for warning in warnings:
        print("WARNING:", warning, file=sys.stderr)
    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print("This is a starting hypothesis. Audit the map and tune one parameter family at a time.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
