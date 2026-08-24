#!/usr/bin/env python3
"""Run deterministic offline checks for the roblox-lighting skill package.

The checks do not require Roblox Studio or network access. Optional JSON Schema and
Pillow checks run only when their libraries are installed.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import py_compile
import sys
import tempfile
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from generate_luau import generate_camera, generate_main  # noqa: E402
from validate_observations import validate as validate_observations  # noqa: E402
from validate_plan import validate_plan  # noqa: E402
from validate_skill import validate as validate_skill  # noqa: E402


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_json_schema(root: Path, errors: list[str], notes: list[str]) -> None:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        notes.append("SKIP: jsonschema not installed; custom validators still ran")
        return

    cases = [
        (root / "assets" / "lighting-plan.schema.json", root / "examples" / "from-scratch-plan.json"),
        (root / "assets" / "lighting-plan.schema.json", root / "examples" / "screenshot-match-plan.json"),
        (root / "assets" / "observation.schema.json", root / "examples" / "screenshot-observations.json"),
    ]
    for schema_path, document_path in cases:
        schema = load_json(schema_path)
        document = load_json(document_path)
        try:
            cls = jsonschema.validators.validator_for(schema)
            cls.check_schema(schema)
            cls(schema).validate(document)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"JSON Schema validation failed for {document_path.relative_to(root)}: {exc}")


def validate_python(root: Path, errors: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="roblox-lighting-checks-") as tmp:
        compile_dir = Path(tmp)
        for source in sorted((root / "scripts").glob("*.py")):
            try:
                py_compile.compile(
                    str(source),
                    cfile=str(compile_dir / f"{source.stem}.pyc"),
                    doraise=True,
                )
            except py_compile.PyCompileError as exc:
                errors.append(f"Python compile failed for {source.name}: {exc.msg}")


def validate_examples(root: Path, errors: list[str], warnings: list[str]) -> None:
    for relative in ("examples/from-scratch-plan.json", "examples/screenshot-match-plan.json"):
        plan = load_json(root / relative)
        plan_errors, plan_warnings = validate_plan(plan)
        errors.extend(f"{relative}: {message}" for message in plan_errors)
        warnings.extend(f"{relative}: {message}" for message in plan_warnings)

        default_luau = generate_main(plan, None, False)
        replacement_luau = generate_main(plan, None, True)
        for label, source in (("default", default_luau), ("replace-conflicts", replacement_luau)):
            check("_RobloxLightingBackups" in source, f"{relative} {label} Luau has no backup root", errors)
            check("RobloxLightingManaged" in source, f"{relative} {label} Luau has no managed tag", errors)
            check("safeSet" in source, f"{relative} {label} Luau has no guarded property writes", errors)
            check("Lighting.Technology" not in source, f"{relative} {label} Luau writes deprecated Technology", errors)
            check("Applied plan" in source, f"{relative} {label} Luau has no completion message", errors)
        check("local REPLACE_CONFLICTS = false" in default_luau, f"{relative} default replacement flag is wrong", errors)
        check("local REPLACE_CONFLICTS = true" in replacement_luau, f"{relative} replacement flag is wrong", errors)

        camera = generate_camera(plan)
        if camera is not None:
            check("CurrentCamera" in camera, f"{relative} camera script does not resolve CurrentCamera", errors)
            check("RobloxLightingManaged" in camera, f"{relative} camera script has no managed tag", errors)

    relative = "examples/screenshot-observations.json"
    payload = load_json(root / relative)
    observation_errors, observation_warnings = validate_observations(payload)
    errors.extend(f"{relative}: {message}" for message in observation_errors)
    warnings.extend(f"{relative}: {message}" for message in observation_warnings)


def validate_evals(root: Path, errors: list[str]) -> None:
    behavior = load_json(root / "evals" / "evals.json")
    trigger = load_json(root / "evals" / "trigger-evals.json")

    evals = behavior.get("evals")
    check(isinstance(evals, list) and len(evals) >= 6, "behavioral eval set should contain at least 6 cases", errors)
    if isinstance(evals, list):
        modes = {item.get("mode") for item in evals if isinstance(item, dict)}
        required_modes = {
            "FROM_SCRATCH",
            "MATCH_SCREENSHOT",
            "LINK_ASSISTED_MATCH",
            "IMPROVE_OR_DEBUG",
            "AUDIT_OR_OPTIMIZE",
        }
        check(required_modes.issubset(modes), "behavioral evals do not cover every operating mode", errors)
        for index, item in enumerate(evals):
            if not isinstance(item, dict):
                errors.append(f"behavioral eval {index} must be an object")
                continue
            for key in ("id", "prompt", "expected_output", "assertions"):
                check(key in item, f"behavioral eval {index} missing {key}", errors)
            check(isinstance(item.get("assertions"), list) and bool(item.get("assertions")), f"behavioral eval {index} has no assertions", errors)

    cases = trigger.get("cases")
    check(isinstance(cases, list) and len(cases) >= 20, "trigger eval set should contain at least 20 cases", errors)
    if isinstance(cases, list):
        positive = sum(1 for case in cases if isinstance(case, dict) and case.get("should_trigger") is True)
        negative = sum(1 for case in cases if isinstance(case, dict) and case.get("should_trigger") is False)
        check(positive >= 10, "trigger evals need at least 10 positive cases", errors)
        check(negative >= 6, "trigger evals need at least 6 negative/near-miss cases", errors)
        ids = [case.get("id") for case in cases if isinstance(case, dict)]
        check(len(ids) == len(set(ids)), "trigger eval IDs must be unique", errors)


def validate_optional_image_tools(root: Path, errors: list[str], notes: list[str]) -> None:
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        notes.append("SKIP: Pillow not installed; image metric/cluster smoke test not run")
        return

    image_metrics_path = root / "scripts" / "image_metrics.py"
    cluster_path = root / "scripts" / "cluster_images.py"

    def import_path(path: Path, module_name: str):
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"could not import {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    try:
        metrics = import_path(image_metrics_path, "roblox_lighting_image_metrics")
        cluster = import_path(cluster_path, "roblox_lighting_cluster_images")
        with tempfile.TemporaryDirectory(prefix="roblox-lighting-images-") as tmp:
            tmpdir = Path(tmp)
            first = tmpdir / "first.png"
            second = tmpdir / "second.png"
            Image.new("RGB", (32, 32), (40, 80, 120)).save(first)
            Image.new("RGB", (32, 32), (44, 84, 124)).save(second)
            a = metrics.load_rgb(first, 64)
            b = metrics.load_rgb(second, 64)
            result = metrics.pair_metrics(a, b, None)
            check(isinstance(result.get("comparison"), dict) and "global_ssim" in result["comparison"], "image metrics smoke test returned no global_ssim", errors)
            vector_a = cluster.extract(first)
            vector_b = cluster.extract(second)
            check(len(vector_a) == len(cluster.FEATURE_NAMES), "cluster feature length mismatch", errors)
            check(cluster.distance(vector_a, vector_b) >= 0, "cluster distance was negative", errors)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"optional image-tool smoke test failed: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []

    skill_errors, skill_warnings = validate_skill(root)
    errors.extend(skill_errors)
    warnings.extend(skill_warnings)
    validate_python(root, errors)
    validate_json_schema(root, errors, notes)
    validate_examples(root, errors, warnings)
    validate_evals(root, errors)
    validate_optional_image_tools(root, errors, notes)

    print(f"Checking roblox-lighting package: {root}")
    for note in sorted(set(notes)):
        print(note)
    for warning in sorted(set(warnings)):
        print(f"WARNING: {warning}")
    for error in sorted(set(errors)):
        print(f"ERROR: {error}")

    if errors:
        print(f"FAILED: {len(set(errors))} error(s), {len(set(warnings))} warning(s)")
        return 1
    print(f"PASS: 0 errors, {len(set(warnings))} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
