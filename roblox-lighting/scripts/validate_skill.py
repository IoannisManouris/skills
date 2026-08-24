#!/usr/bin/env python3
"""Validate a portable Agent Skill package without requiring network access."""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

ALLOWED_FRONTMATTER = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter delimited by ---")
    marker = text.find("\n---\n", 4)
    if marker == -1:
        raise ValueError("SKILL.md frontmatter has no closing --- delimiter")
    raw = text[4:marker]
    body = text[marker + 5 :]

    try:
        import yaml  # type: ignore

        data = yaml.safe_load(raw)
        if not isinstance(data, dict):
            raise ValueError("frontmatter must parse to a mapping")
        return data, body
    except ImportError:
        # Minimal parser for the fields this package uses. It supports plain
        # scalars, folded scalars, and a single metadata mapping.
        data: dict[str, Any] = {}
        lines = raw.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip() or line.lstrip().startswith("#"):
                i += 1
                continue
            if line.startswith(" "):
                raise ValueError("fallback parser encountered unexpected indentation")
            if ":" not in line:
                raise ValueError(f"invalid frontmatter line: {line}")
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            if value in {">", ">-", "|", "|-"}:
                folded: list[str] = []
                i += 1
                while i < len(lines) and (not lines[i].strip() or lines[i].startswith("  ")):
                    folded.append(lines[i][2:] if lines[i].startswith("  ") else "")
                    i += 1
                data[key] = " ".join(part.strip() for part in folded if part.strip())
                continue
            if key == "metadata" and value == "":
                meta: dict[str, str] = {}
                i += 1
                while i < len(lines) and lines[i].startswith("  "):
                    child = lines[i].strip()
                    if ":" not in child:
                        raise ValueError(f"invalid metadata line: {lines[i]}")
                    mk, mv = child.split(":", 1)
                    meta[mk.strip()] = mv.strip().strip('"\'')
                    i += 1
                data[key] = meta
                continue
            data[key] = value.strip('"\'')
            i += 1
        return data, body


def validate(root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not root.is_dir():
        return [f"not a directory: {root}"], warnings

    skill_file = root / "SKILL.md"
    if not skill_file.exists():
        return ["missing required SKILL.md"], warnings

    text = skill_file.read_text(encoding="utf-8")
    try:
        frontmatter, body = parse_frontmatter(text)
    except Exception as exc:  # noqa: BLE001
        return [f"frontmatter parse failed: {exc}"], warnings

    unexpected = sorted(set(frontmatter) - ALLOWED_FRONTMATTER)
    if unexpected:
        errors.append(f"unexpected frontmatter keys: {', '.join(unexpected)}")

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name:
        errors.append("frontmatter.name is required and must be a string")
    else:
        if len(name) > 64:
            errors.append("frontmatter.name exceeds 64 characters")
        if not NAME_RE.fullmatch(name):
            errors.append("frontmatter.name must use lowercase a-z, 0-9, and single hyphens")
        if name != root.name:
            errors.append(f"frontmatter.name '{name}' does not match parent directory '{root.name}'")

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("frontmatter.description is required and must be non-empty")
    elif len(description) > 1024:
        errors.append(f"frontmatter.description is {len(description)} characters; maximum is 1024")
    else:
        trigger_terms = ("roblox", "lighting", "screenshot", "use this skill")
        missing = [term for term in trigger_terms if term not in description.lower()]
        if missing:
            warnings.append(f"description may under-trigger; missing terms: {', '.join(missing)}")

    compatibility = frontmatter.get("compatibility")
    if compatibility is not None:
        if not isinstance(compatibility, str) or not compatibility.strip():
            errors.append("compatibility must be a non-empty string when present")
        elif len(compatibility) > 500:
            errors.append("compatibility exceeds 500 characters")

    metadata = frontmatter.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            errors.append("metadata must be a mapping")
        else:
            for key, value in metadata.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    errors.append("metadata keys and values must all be strings")
                    break

    line_count = text.count("\n") + 1
    if line_count > 500:
        errors.append(f"SKILL.md has {line_count} lines; recommended maximum is 500")

    if len(body.split()) > 5000:
        warnings.append("SKILL.md body appears to exceed the recommended ~5000-token instruction budget")

    for target in LINK_RE.findall(body):
        clean = target.split("#", 1)[0]
        if not clean or clean.startswith(("http://", "https://", "mailto:")):
            continue
        linked = (root / clean).resolve()
        try:
            linked.relative_to(root.resolve())
        except ValueError:
            errors.append(f"relative link escapes skill directory: {target}")
            continue
        if not linked.exists():
            errors.append(f"broken relative link in SKILL.md: {target}")
        if len(Path(clean).parts) > 2:
            warnings.append(f"deep reference path may reduce portability: {target}")

    for json_file in sorted(root.rglob("*.json")):
        try:
            json.loads(json_file.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"invalid JSON {json_file.relative_to(root)}: {exc}")

    with tempfile.TemporaryDirectory(prefix="roblox-lighting-pycompile-") as tmp:
        compile_dir = Path(tmp)
        for py_file in sorted((root / "scripts").glob("*.py")):
            try:
                py_compile.compile(
                    str(py_file),
                    cfile=str(compile_dir / f"{py_file.stem}.pyc"),
                    doraise=True,
                )
            except py_compile.PyCompileError as exc:
                errors.append(f"Python compile failed for {py_file.name}: {exc.msg}")

    required_refs = {
        "references/roblox-lighting-api.md",
        "references/from-scratch.md",
        "references/screenshot-matching.md",
        "references/roblox-link-research.md",
        "references/performance-validation.md",
        "assets/lighting-plan.schema.json",
        "assets/observation.schema.json",
        "evals/evals.json",
        "evals/trigger-evals.json",
    }
    for relative in sorted(required_refs):
        if not (root / relative).exists():
            errors.append(f"missing expected package resource: {relative}")

    evals_file = root / "evals" / "evals.json"
    if evals_file.exists():
        try:
            payload = json.loads(evals_file.read_text(encoding="utf-8"))
            if payload.get("skill_name") != name:
                errors.append("evals/evals.json skill_name does not match frontmatter.name")
            if not isinstance(payload.get("evals"), list) or not payload["evals"]:
                errors.append("evals/evals.json must contain a non-empty evals array")
        except Exception:
            pass

    trigger_file = root / "evals" / "trigger-evals.json"
    if trigger_file.exists():
        try:
            payload = json.loads(trigger_file.read_text(encoding="utf-8"))
            cases = payload.get("cases")
            if not isinstance(cases, list) or not cases:
                errors.append("trigger-evals.json must contain a non-empty cases array")
            else:
                positives = [case for case in cases if isinstance(case, dict) and case.get("should_trigger") is True]
                negatives = [case for case in cases if isinstance(case, dict) and case.get("should_trigger") is False]
                if not positives:
                    errors.append("trigger evals have no positive cases")
                if not negatives:
                    warnings.append("trigger evals have no negative near-miss cases")
                for index, case in enumerate(cases):
                    if not isinstance(case, dict):
                        errors.append(f"trigger eval case {index} must be an object")
                        continue
                    if not isinstance(case.get("id"), str) or not case["id"].strip():
                        errors.append(f"trigger eval case {index} has no non-empty id")
                    if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
                        errors.append(f"trigger eval case {index} has no non-empty prompt")
                    if not isinstance(case.get("should_trigger"), bool):
                        errors.append(f"trigger eval case {index}.should_trigger must be boolean")
        except Exception:
            pass

    openai_metadata = root / "agents" / "openai.yaml"
    if openai_metadata.exists():
        raw_openai = openai_metadata.read_text(encoding="utf-8")
        try:
            import yaml  # type: ignore

            parsed_openai = yaml.safe_load(raw_openai)
            if not isinstance(parsed_openai, dict):
                errors.append("agents/openai.yaml must parse to a mapping")
            else:
                interface = parsed_openai.get("interface")
                policy = parsed_openai.get("policy")
                if not isinstance(interface, dict):
                    errors.append("agents/openai.yaml requires an interface mapping")
                else:
                    for key in ("display_name", "short_description", "default_prompt"):
                        if not isinstance(interface.get(key), str) or not interface[key].strip():
                            errors.append(f"agents/openai.yaml interface.{key} must be a non-empty string")
                    short_description = interface.get("short_description", "")
                    if isinstance(short_description, str) and not 25 <= len(short_description) <= 64:
                        warnings.append("agents/openai.yaml interface.short_description should be 25–64 characters")
                    default_prompt = interface.get("default_prompt", "")
                    if isinstance(default_prompt, str) and f"${name}" not in default_prompt:
                        warnings.append(f"agents/openai.yaml default_prompt should explicitly mention ${name}")
                if not isinstance(policy, dict):
                    warnings.append("agents/openai.yaml has no policy mapping; implicit invocation uses product default")
                elif policy.get("allow_implicit_invocation") is not True:
                    warnings.append("agents/openai.yaml does not explicitly allow implicit invocation")
        except ImportError:
            for required_text in ("interface:", "display_name:", "short_description:", "default_prompt:"):
                if required_text not in raw_openai:
                    errors.append(f"agents/openai.yaml missing {required_text.rstrip(':')}")
            if "allow_implicit_invocation: true" not in raw_openai.lower():
                warnings.append("agents/openai.yaml does not visibly enable implicit invocation")
    else:
        warnings.append("agents/openai.yaml missing; Codex UI/discovery metadata is unavailable")

    return errors, sorted(set(warnings))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    errors, warnings = validate(root)

    print(f"Validating Agent Skill: {root}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")

    if errors:
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1

    print(f"PASS: 0 errors, {len(warnings)} warning(s)")
    print("Optional additional check: skills-ref validate", root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
