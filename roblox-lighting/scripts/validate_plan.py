#!/usr/bin/env python3
"""Validate a roblox-lighting lighting-plan.json using standard Python only."""

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
GLOBAL_PROPERTIES = {
    "Ambient",
    "Brightness",
    "ClockTime",
    "ColorShift_Bottom",
    "ColorShift_Top",
    "EnvironmentDiffuseScale",
    "EnvironmentSpecularScale",
    "ExposureCompensation",
    "FogColor",
    "FogEnd",
    "FogStart",
    "GeographicLatitude",
    "GlobalShadows",
    "LightingStyle",
    "OutdoorAmbient",
    "PrioritizeLightingQuality",
    "ShadowSoftness",
    "TimeOfDay",
}
COLORS = {
    "Ambient",
    "ColorShift_Bottom",
    "ColorShift_Top",
    "FogColor",
    "OutdoorAmbient",
    "Color",
    "Decay",
    "TintColor",
}
POST_CLASSES = {
    "BloomEffect",
    "BlurEffect",
    "ColorCorrectionEffect",
    "ColorGradingEffect",
    "DepthOfFieldEffect",
    "SunRaysEffect",
}
LOCAL_CLASSES = {"PointLight", "SpotLight", "SurfaceLight"}
NORMAL_IDS = {"Front", "Back", "Left", "Right", "Top", "Bottom"}


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def is_color(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 255 for v in value)
    )


def add_range_error(errors: list[str], path: str, value: Any, low: float, high: float) -> None:
    if not finite_number(value) or not low <= float(value) <= high:
        errors.append(f"{path} must be a finite number in [{low}, {high}]")


def validate_plan(plan: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in (
        "schema_version",
        "plan_id",
        "mode",
        "intent",
        "confidence",
        "lighting",
        "local_lights",
        "quality_tiers",
        "validation",
        "unresolved_ambiguities",
    ):
        if key not in plan:
            errors.append(f"missing required top-level key: {key}")

    if plan.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    if not isinstance(plan.get("plan_id"), str) or len(plan.get("plan_id", "")) < 3:
        errors.append("plan_id must be a string with at least 3 characters")
    if plan.get("mode") not in MODES:
        errors.append(f"mode must be one of {sorted(MODES)}")

    confidence = plan.get("confidence")
    if not finite_number(confidence) or not 0 <= float(confidence) <= 1:
        errors.append("confidence must be a finite number in [0, 1]")

    intent = plan.get("intent")
    if not isinstance(intent, dict):
        errors.append("intent must be an object")
    else:
        for key in ("thesis", "genre", "mood", "target_state"):
            if key not in intent:
                errors.append(f"intent.{key} is required")
        if isinstance(intent.get("thesis"), str) and len(intent["thesis"].strip()) < 10:
            errors.append("intent.thesis must be descriptive, not a label")
        if "mood" in intent and not isinstance(intent.get("mood"), list):
            errors.append("intent.mood must be an array")

    lighting = plan.get("lighting")
    if not isinstance(lighting, dict):
        errors.append("lighting must be an object")
        return errors, warnings

    for key in ("properties", "sky", "atmosphere", "legacy_fog", "clouds", "post_effects"):
        if key not in lighting:
            errors.append(f"lighting.{key} is required")

    props = lighting.get("properties", {})
    if not isinstance(props, dict):
        errors.append("lighting.properties must be an object")
        props = {}

    unknown = sorted(set(props) - GLOBAL_PROPERTIES)
    if unknown:
        errors.append("unsupported/deprecated Lighting properties: " + ", ".join(unknown))

    for key, value in props.items():
        path = f"lighting.properties.{key}"
        if key in COLORS and not is_color(value):
            errors.append(f"{path} must be [R,G,B] integers in 0..255")
        elif key == "Brightness" and (not finite_number(value) or value < 0):
            errors.append(f"{path} must be a non-negative number")
        elif key == "ClockTime":
            add_range_error(errors, path, value, 0, 24)
        elif key in {"EnvironmentDiffuseScale", "EnvironmentSpecularScale", "ShadowSoftness"}:
            add_range_error(errors, path, value, 0, 1)
        elif key == "ExposureCompensation":
            add_range_error(errors, path, value, -5, 5)
        elif key == "GeographicLatitude":
            add_range_error(errors, path, value, -90, 90)
        elif key in {"GlobalShadows", "PrioritizeLightingQuality"} and not isinstance(value, bool):
            errors.append(f"{path} must be boolean")
        elif key == "LightingStyle" and value not in {"Realistic", "Soft"}:
            errors.append(f"{path} must be Realistic or Soft")
        elif key in {"FogStart", "FogEnd"} and not finite_number(value):
            errors.append(f"{path} must be a finite number")
        elif key == "TimeOfDay":
            if not isinstance(value, str) or len(value.split(":")) != 3:
                errors.append(f"{path} must be HH:MM:SS")

    if "ClockTime" in props and "TimeOfDay" in props:
        warnings.append("Both ClockTime and TimeOfDay are set; keep only one canonical time control unless exact equivalence is verified")
    if props.get("LightingStyle") == "Soft" and "ShadowSoftness" in props:
        warnings.append("ShadowSoftness has limited/no intended effect under LightingStyle Soft")
    if finite_number(props.get("ExposureCompensation")) and abs(float(props["ExposureCompensation"])) > 1.5:
        warnings.append("ExposureCompensation is extreme; verify it is not masking source/fill/material problems")
    if finite_number(props.get("Brightness")) and float(props["Brightness"]) > 5:
        warnings.append("Global Brightness is high; check highlight clipping and tonemapper interaction")

    atmosphere = lighting.get("atmosphere")
    if atmosphere is not None:
        if not isinstance(atmosphere, dict):
            errors.append("lighting.atmosphere must be null or an object")
        else:
            aprops = atmosphere.get("properties", {})
            if not isinstance(aprops, dict):
                errors.append("lighting.atmosphere.properties must be an object")
                aprops = {}
            for key in ("Color", "Decay"):
                if key in aprops and not is_color(aprops[key]):
                    errors.append(f"lighting.atmosphere.properties.{key} must be [R,G,B]")
            if "Density" in aprops:
                add_range_error(errors, "lighting.atmosphere.properties.Density", aprops["Density"], 0, 1)
            if "Offset" in aprops:
                add_range_error(errors, "lighting.atmosphere.properties.Offset", aprops["Offset"], -1, 1)
            for key in ("Glare", "Haze"):
                if key in aprops and (not finite_number(aprops[key]) or aprops[key] < 0):
                    errors.append(f"lighting.atmosphere.properties.{key} must be non-negative")
            if finite_number(aprops.get("Density")) and float(aprops["Density"]) > 0.6:
                warnings.append("Atmosphere Density is very high; validate nearby route and landmark visibility")
            if finite_number(aprops.get("Offset")) and float(aprops["Offset"]) < -0.4:
                warnings.append("Low Atmosphere Offset can cause sky-through-geometry ghosting; inspect horizons")

    legacy = lighting.get("legacy_fog")
    if not isinstance(legacy, dict):
        errors.append("lighting.legacy_fog must be an object with enabled")
        legacy = {}
    elif not isinstance(legacy.get("enabled"), bool):
        errors.append("lighting.legacy_fog.enabled must be boolean")

    if atmosphere and isinstance(atmosphere, dict) and atmosphere.get("enabled", True) and legacy.get("enabled"):
        warnings.append("Atmosphere and legacy fog are both enabled; current Roblox behavior does not make them an independent additive stack")

    fog_start = legacy.get("FogStart", props.get("FogStart"))
    fog_end = legacy.get("FogEnd", props.get("FogEnd"))
    if finite_number(fog_start) and finite_number(fog_end) and float(fog_end) <= float(fog_start):
        errors.append("FogEnd must be greater than FogStart")

    clouds = lighting.get("clouds")
    if clouds is not None:
        if not isinstance(clouds, dict):
            errors.append("lighting.clouds must be null or an object")
        else:
            cprops = clouds.get("properties", {})
            if not isinstance(cprops, dict):
                errors.append("lighting.clouds.properties must be an object")
                cprops = {}
            if "Color" in cprops and not is_color(cprops["Color"]):
                errors.append("lighting.clouds.properties.Color must be [R,G,B]")
            for key in ("Cover", "Density"):
                if key in cprops:
                    add_range_error(errors, f"lighting.clouds.properties.{key}", cprops[key], 0, 1)
            wind = clouds.get("global_wind")
            if wind is not None and not (
                isinstance(wind, list) and len(wind) == 3 and all(finite_number(v) for v in wind)
            ):
                errors.append("lighting.clouds.global_wind must be [x,y,z] numbers")

    effects = lighting.get("post_effects", [])
    if not isinstance(effects, list):
        errors.append("lighting.post_effects must be an array")
        effects = []

    grade_count = 0
    names: set[str] = set()
    for index, effect in enumerate(effects):
        path = f"lighting.post_effects[{index}]"
        if not isinstance(effect, dict):
            errors.append(f"{path} must be an object")
            continue
        cls = effect.get("class")
        if cls not in POST_CLASSES:
            errors.append(f"{path}.class must be one of {sorted(POST_CLASSES)}")
            continue
        name = effect.get("name")
        if not isinstance(name, str) or not name:
            errors.append(f"{path}.name is required")
        elif name in names:
            warnings.append(f"duplicate post-effect name: {name}")
        else:
            names.add(name)
        parent = effect.get("parent")
        if parent not in {"Lighting", "Camera"}:
            errors.append(f"{path}.parent must be Lighting or Camera")
        if not isinstance(effect.get("enabled"), bool):
            errors.append(f"{path}.enabled must be boolean")
        eprops = effect.get("properties", {})
        if not isinstance(eprops, dict):
            errors.append(f"{path}.properties must be an object")
            eprops = {}

        if cls == "ColorGradingEffect":
            grade_count += 1
            if parent != "Lighting":
                errors.append(f"{path}: ColorGradingEffect must be parented to Lighting")
            if eprops.get("TonemapperPreset", "Default") not in {"Default", "Retro"}:
                errors.append(f"{path}.properties.TonemapperPreset must be Default or Retro")
        elif cls == "BloomEffect":
            for key in ("Intensity", "Size", "Threshold"):
                if key in eprops and (not finite_number(eprops[key]) or eprops[key] < 0):
                    errors.append(f"{path}.properties.{key} must be non-negative")
            if finite_number(eprops.get("Intensity")) and float(eprops["Intensity"]) > 2:
                warnings.append(f"{path} has very high Bloom Intensity; check full-screen glow and clipping")
            if finite_number(eprops.get("Threshold")) and float(eprops["Threshold"]) < 0.2:
                warnings.append(f"{path} has a low Bloom Threshold; ordinary bright materials may glow")
        elif cls == "BlurEffect":
            if "Size" in eprops and (not finite_number(eprops["Size"]) or eprops["Size"] < 0):
                errors.append(f"{path}.properties.Size must be non-negative")
            if effect.get("enabled") and parent == "Lighting":
                warnings.append(f"{path} is a global BlurEffect; verify active gameplay readability")
        elif cls == "ColorCorrectionEffect":
            for key in ("Brightness", "Contrast", "Saturation"):
                if key in eprops:
                    add_range_error(errors, f"{path}.properties.{key}", eprops[key], -1, 1)
            if "TintColor" in eprops and not is_color(eprops["TintColor"]):
                errors.append(f"{path}.properties.TintColor must be [R,G,B]")
        elif cls == "DepthOfFieldEffect":
            for key in ("FocusDistance", "InFocusRadius"):
                if key in eprops and (not finite_number(eprops[key]) or eprops[key] < 0):
                    errors.append(f"{path}.properties.{key} must be non-negative")
            for key in ("NearIntensity", "FarIntensity"):
                if key in eprops:
                    add_range_error(errors, f"{path}.properties.{key}", eprops[key], 0, 1)
            if effect.get("enabled") and parent == "Lighting":
                warnings.append(f"{path} is global depth of field; prefer Camera-local/stateful use for gameplay")
        elif cls == "SunRaysEffect":
            for key in ("Intensity", "Spread"):
                if key in eprops:
                    add_range_error(errors, f"{path}.properties.{key}", eprops[key], 0, 1)

    if grade_count > 1:
        errors.append("Only one ColorGradingEffect is allowed; Roblox does not combine multiple instances")

    local_lights = plan.get("local_lights", [])
    if not isinstance(local_lights, list):
        errors.append("local_lights must be an array")
        local_lights = []

    ids: set[str] = set()
    shadowed_count = 0
    for index, light in enumerate(local_lights):
        path = f"local_lights[{index}]"
        if not isinstance(light, dict):
            errors.append(f"{path} must be an object")
            continue
        cls = light.get("class")
        if cls not in LOCAL_CLASSES:
            errors.append(f"{path}.class must be one of {sorted(LOCAL_CLASSES)}")
        lid = light.get("id")
        if not isinstance(lid, str) or not lid:
            errors.append(f"{path}.id is required")
        elif lid in ids:
            errors.append(f"duplicate local light id: {lid}")
        else:
            ids.add(lid)
        target = light.get("target_path")
        if not isinstance(target, str) or not target.startswith("/Workspace"):
            errors.append(f"{path}.target_path must start with /Workspace")
        lprops = light.get("properties", {})
        if not isinstance(lprops, dict):
            errors.append(f"{path}.properties must be an object")
            lprops = {}
        if "Color" in lprops and not is_color(lprops["Color"]):
            errors.append(f"{path}.properties.Color must be [R,G,B]")
        for key in ("Brightness", "Range"):
            if key in lprops and (not finite_number(lprops[key]) or lprops[key] < 0):
                errors.append(f"{path}.properties.{key} must be non-negative")
        if "Shadows" in lprops and not isinstance(lprops["Shadows"], bool):
            errors.append(f"{path}.properties.Shadows must be boolean")
        if "Enabled" in lprops and not isinstance(lprops["Enabled"], bool):
            errors.append(f"{path}.properties.Enabled must be boolean")
        if lprops.get("Shadows") is True:
            shadowed_count += 1
        if cls == "PointLight":
            if "Angle" in lprops or "Face" in lprops:
                errors.append(f"{path}: PointLight does not use Angle or Face")
        else:
            if "Angle" in lprops:
                add_range_error(errors, f"{path}.properties.Angle", lprops["Angle"], 0, 180)
            if "Face" in lprops and lprops["Face"] not in NORMAL_IDS:
                errors.append(f"{path}.properties.Face must be a NormalId name")
        if finite_number(lprops.get("Range")) and float(lprops["Range"]) > 60:
            warnings.append(f"{path} Range exceeds 60 studs; verify rollout support, overlap, leaks, and performance")
        if finite_number(lprops.get("Brightness")) and float(lprops["Brightness"]) > 5:
            warnings.append(f"{path} Brightness is high; verify clipping and whether Range/materials are the real issue")
        tiers = light.get("quality_tiers")
        if not isinstance(tiers, list) or not tiers or any(t not in {"low", "medium", "high"} for t in tiers):
            errors.append(f"{path}.quality_tiers must be a non-empty subset of low/medium/high")

    if shadowed_count > 4:
        warnings.append(f"{shadowed_count} local lights cast shadows; profile the densest overlapping camera view")

    tiers = plan.get("quality_tiers")
    if not isinstance(tiers, dict):
        errors.append("quality_tiers must be an object")
    else:
        for tier in ("low", "medium", "high"):
            entry = tiers.get(tier)
            if not isinstance(entry, dict):
                errors.append(f"quality_tiers.{tier} must be an object")
                continue
            enabled_ids = entry.get("enabled_light_ids", [])
            if not isinstance(enabled_ids, list):
                errors.append(f"quality_tiers.{tier}.enabled_light_ids must be an array")
            else:
                missing = sorted(set(enabled_ids) - ids)
                if missing:
                    errors.append(f"quality_tiers.{tier} references unknown light IDs: {', '.join(missing)}")

    validation = plan.get("validation")
    if not isinstance(validation, dict):
        errors.append("validation must be an object")
    else:
        for key in ("views", "gameplay_gates", "performance_gates", "stopping_criteria"):
            if not isinstance(validation.get(key), list) or not validation.get(key):
                errors.append(f"validation.{key} must be a non-empty array")

    ambiguities = plan.get("unresolved_ambiguities")
    if not isinstance(ambiguities, list):
        errors.append("unresolved_ambiguities must be an array")
    if plan.get("mode") in {"MATCH_SCREENSHOT", "LINK_ASSISTED_MATCH"} and not ambiguities:
        warnings.append("Screenshot matching has no unresolved ambiguities; verify the plan is not claiming false certainty")

    manual = lighting.get("manual_properties", {})
    if isinstance(manual, dict) and "Technology" in manual:
        errors.append("Technology is deprecated; do not include it even as a manual property without an explicit legacy migration note")

    return errors, sorted(set(warnings))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--json-output", type=Path, help="write validation result JSON")
    args = parser.parse_args()

    try:
        payload = json.loads(args.plan.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: could not read JSON: {exc}")
        return 2
    if not isinstance(payload, dict):
        print("ERROR: plan root must be a JSON object")
        return 2

    errors, warnings = validate_plan(payload)
    result = {"valid": not errors, "errors": errors, "warnings": warnings}

    for warning in warnings:
        print("WARNING:", warning)
    for error in errors:
        print("ERROR:", error)
    print(f"{'PASS' if not errors else 'FAILED'}: {len(errors)} error(s), {len(warnings)} warning(s)")

    if args.json_output:
        args.json_output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
