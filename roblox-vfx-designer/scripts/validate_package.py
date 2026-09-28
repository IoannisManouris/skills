#!/usr/bin/env python3
"""Validate skill metadata, local links, JSON plans and Python syntax (not Luau/Studio)."""
from __future__ import annotations
import argparse
import ast
import json
import math
from pathlib import Path
import re
from urllib.parse import urlparse, unquote
import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str):
    if not condition: raise ValueError(message)


def finite_numbers(value):
    if isinstance(value, float): require(math.isfinite(value), "NaN/Infinity not allowed in plans")
    elif isinstance(value, dict):
        for item in value.values(): finite_numbers(item)
    elif isinstance(value, list):
        for item in value: finite_numbers(item)


def validate_spec(spec: dict, schema: dict):
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(spec)
    finite_numbers(spec)
    layers = {layer["id"]: layer for layer in spec["layers"]}
    require(len(layers) == len(spec["layers"]), "Layer IDs must be unique")
    require(any(layer["role"] == "primary" for layer in layers.values()), "Effect needs a primary read")
    asset_roles = {asset["role"] for asset in spec["assets"]}
    require(len(asset_roles) == len(spec["assets"]), "Asset roles must be unique")
    for layer in layers.values():
        require(layer["texture_role"] is None or layer["texture_role"] in asset_roles, "Unmapped texture role")
    for tier in spec["quality_tiers"].values():
        for id in tier["disabled_layers"]:
            require(id in layers, "Tier disables nonexistent layer")
            require(layers[id]["role"] != "primary" and not layers[id]["critical"], "Tier removes primary/critical cue")
    cleanup = spec["cleanup"]
    if cleanup["mode"] == "finite":
        last = max(l["start_seconds"] + l["active_seconds"] + l["tail_seconds"] for l in layers.values())
        require(cleanup["maximum_seconds"] is not None and cleanup["maximum_seconds"] >= last, "Cleanup truncates layer tail")
    else:
        require(bool(cleanup["stop_owner"]), "Persistent effect needs an explicit stop owner")
    if spec["status"] == "validated":
        require(bool(spec["evidence"]), "Validated plans need actual evidence")
        require(all(a["status"] == "verified_in_place" and a["image_content_id"] for a in spec["assets"]), "Validated plans contain pending assets")


def validate_package(root: Path) -> dict:
    checks = []
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    require(skill.startswith("---\n"), "SKILL.md missing YAML frontmatter")
    front, body = skill[4:].split("\n---\n", 1)
    data = yaml.safe_load(front)
    require(isinstance(data, dict), "Frontmatter must be a mapping")
    name = data.get("name", "")
    require(name == "roblox-vfx-designer" and name == root.name, "Skill/folder name mismatch")
    require(bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)) and len(name) <= 64, "Invalid skill name")
    require(isinstance(data.get("description"), str) and 1 <= len(data["description"]) <= 1024, "Description length/type invalid")
    require(len(data.get("compatibility", "")) <= 500, "Compatibility too long")
    require(all(isinstance(k, str) and isinstance(v, str) for k, v in data.get("metadata", {}).items()), "Metadata must map strings to strings")
    require(len(skill.splitlines()) < 500, "Entry point exceeds recommended 500 lines")
    checks.append("agent_skill_frontmatter_and_size")
    host = yaml.safe_load((root / "agents/openai.yaml").read_text(encoding="utf-8"))
    require(host["policy"]["allow_implicit_invocation"] is True, "Implicit invocation disabled")
    require("$roblox-vfx-designer" in host["interface"]["default_prompt"], "Default prompt missing explicit invocation")
    checks.append("codex_metadata")
    linked = 0
    for md in root.rglob("*.md"):
        for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", md.read_text(encoding="utf-8")):
            if urlparse(target).scheme or target.startswith("#"): continue
            target = unquote(target.split("#")[0])
            resolved = (md.parent / target).resolve()
            require(resolved.is_relative_to(root.resolve()), f"Local link leaves package: {md.name} -> {target}")
            require(resolved.exists(), f"Broken local link: {md.name} -> {target}")
            linked += 1
    checks.append(f"local_markdown_links:{linked}")
    for path in root.rglob("*.json"):
        finite_numbers(json.loads(path.read_text(encoding="utf-8")))
    for path in root.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    checks.extend(["json_parse_and_finite_values", "python_ast_parse"])
    specdir = root / "templates/specs"
    for schema_path in specdir.glob("*.schema.json"):
        schema = json.loads(schema_path.read_text())
        Draft202012Validator.check_schema(schema)
        example_path = schema_path.with_name(schema_path.name.replace(".schema.json", ".example.json"))
        if example_path.exists():
            Draft202012Validator(schema, format_checker=FormatChecker()).validate(json.loads(example_path.read_text()))
    schema = json.loads((specdir / "effect-spec.schema.json").read_text())
    validate_spec(json.loads((specdir / "effect-spec.example.json").read_text()), schema)
    checks.extend(["json_schema_definitions_and_examples", "effect_plan_semantics"])
    catalog = json.loads((root / "assets/library-catalog.json").read_text())
    ids = [x["id"] for x in catalog["libraries"]]
    require(len(ids) == len(set(ids)), "Duplicate catalog IDs")
    for entry in catalog["libraries"]:
        require(entry["license"] == "CC0-1.0", "Unexpected default catalog license")
        for field in ("page_url", "license_evidence_url"):
            require(urlparse(entry[field]).scheme == "https", "Catalog URL must be HTTPS")
    checks.append("catalog_structure_not_live_download_verification")
    for name in ("VFXRuntime", "EffectPool", "SurfaceFrame", "BuildImpact", "MarkerBindings", "SceneProbe", "StudioSmokeTest"):
        require((root / "templates/luau" / (name + ".luau")).is_file(), f"Missing module {name}")
    checks.append("luau_file_presence_only")
    return {"status": "passed", "checks": checks, "skill_lines": len(skill.splitlines()), "skill_body_words": len(body.split()),
            "not_tested": ["Luau parsing/type-checking", "Roblox Studio execution", "visual quality", "device profiling", "live asset transfers", "model routing"]}


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("--root", type=Path, default=ROOT); p.add_argument("--spec", type=Path)
    args = p.parse_args()
    try:
        if args.spec:
            schema = json.loads((args.root / "templates/specs/effect-spec.schema.json").read_text())
            validate_spec(json.loads(args.spec.read_text()), schema)
            result = {"status": "passed", "check": "effect_spec_structure_and_semantics_only"}
        else: result = validate_package(args.root)
        print(json.dumps(result, indent=2))
    except Exception as exc: p.exit(1, f"validate_package: {exc}\n")

if __name__ == "__main__": main()
