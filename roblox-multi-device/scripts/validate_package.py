#!/usr/bin/env python3
"""Validate the roblox-multi-device Agent Skill package.

Usage:
    python scripts/validate_package.py .

Checks Agent Skills naming/frontmatter conventions, package completeness, local
links, JSON/eval structure, Python syntax, action-map coverage, and selected
Roblox deprecation hazards. Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from validate_action_map import as_payload as action_payload  # noqa: E402
from validate_action_map import validate_file as validate_action_file  # noqa: E402

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "CHANGELOG.md",
    "references/architecture.md",
    "references/action-design.md",
    "references/ui-navigation.md",
    "references/keyboard-mouse.md",
    "references/touch.md",
    "references/gamepad-tv.md",
    "references/vr.md",
    "references/testing-accessibility.md",
    "references/migration-audit.md",
    "references/sources.md",
    "assets/action-map.template.json",
    "assets/project-layout.template.md",
    "assets/implementation-report.template.md",
    "assets/device-profile.luau",
    "assets/context-controller.luau",
    "assets/action-router.luau",
    "assets/prompt-glyphs.luau",
    "assets/ui-focus-controller.luau",
    "assets/bootstrap.client.luau",
    "scripts/validate_action_map.py",
    "scripts/validate_package.py",
    "evals/evals.json",
    "evals/trigger-evals.json",
    "evals/assertions.md",
]


@dataclass
class PackageResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)
    action_map: dict[str, Any] | None = None

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, path: str, message: str) -> None:
        self.errors.append(f"{path}: {message}")

    def warn(self, path: str, message: str) -> None:
        self.warnings.append(f"{path}: {message}")


def _strip_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, str], str, list[str]]:
    errors: list[str] = []
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, ["SKILL.md must start with a YAML frontmatter delimiter (---)"]

    try:
        end_index = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return {}, text, ["SKILL.md frontmatter has no closing delimiter (---)"]

    fields: dict[str, str] = {}
    current_top_level: str | None = None
    for line_number, line in enumerate(lines[1:end_index], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            if current_top_level != "metadata":
                errors.append(f"unsupported indented frontmatter at line {line_number}")
            continue
        if ":" not in line:
            errors.append(f"invalid frontmatter line {line_number}: missing ':'")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        current_top_level = key
        fields[key] = _strip_scalar(value)

    body = "\n".join(lines[end_index + 1 :])
    return fields, body, errors


def _load_json(result: PackageResult, path: Path, label: str) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        result.error(label, f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
    except OSError as exc:
        result.error(label, f"could not read file: {exc}")
    return None


def _validate_eval_files(result: PackageResult, root: Path) -> None:
    evals = _load_json(result, root / "evals/evals.json", "evals/evals.json")
    if isinstance(evals, dict):
        if evals.get("skill_name") != "roblox-multi-device":
            result.error("evals/evals.json", "skill_name must equal 'roblox-multi-device'")
        items = evals.get("evals")
        if not isinstance(items, list) or len(items) < 3:
            result.error("evals/evals.json", "must contain at least three evaluation cases")
        else:
            ids: set[int] = set()
            for index, item in enumerate(items):
                path = f"evals/evals.json:evals[{index}]"
                if not isinstance(item, dict):
                    result.error(path, "must be an object")
                    continue
                item_id = item.get("id")
                if not isinstance(item_id, int):
                    result.error(path, "id must be an integer")
                elif item_id in ids:
                    result.error(path, f"duplicate id {item_id}")
                else:
                    ids.add(item_id)
                if not isinstance(item.get("prompt"), str) or not item["prompt"].strip():
                    result.error(path, "prompt must be a non-empty string")
                expected = item.get("expected_output")
                if not isinstance(expected, str) or not expected.strip():
                    result.error(path, "expected_output must be a non-empty string")
                assertions = item.get("assertions")
                if not isinstance(assertions, list) or not assertions:
                    result.error(path, "assertions must be a non-empty array")

    triggers = _load_json(result, root / "evals/trigger-evals.json", "evals/trigger-evals.json")
    if isinstance(triggers, list):
        positive: list[str] = []
        negative: list[str] = []
        for index, item in enumerate(triggers):
            path = f"evals/trigger-evals.json[{index}]"
            if not isinstance(item, dict):
                result.error(path, "must be an object")
                continue
            query = item.get("query")
            should_trigger = item.get("should_trigger")
            if not isinstance(query, str) or not query.strip():
                result.error(path, "query must be a non-empty string")
                continue
            if not isinstance(should_trigger, bool):
                result.error(path, "should_trigger must be a boolean")
                continue
            (positive if should_trigger else negative).append(query)
        if len(positive) < 8:
            result.error("evals/trigger-evals.json", "must contain at least eight should-trigger queries")
        if len(negative) < 8:
            result.error("evals/trigger-evals.json", "must contain at least eight should-not-trigger queries")
        overlap = set(positive) & set(negative)
        if overlap:
            result.error("evals/trigger-evals.json", f"queries appear in both labels: {sorted(overlap)}")
    elif triggers is not None:
        result.error("evals/trigger-evals.json", "root must be an array of {query, should_trigger} objects")


def _validate_python(result: PackageResult, root: Path) -> None:
    for path in sorted((root / "scripts").glob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            result.error(path.relative_to(root).as_posix(), f"Python syntax error: {exc}")


def _validate_links(result: PackageResult, root: Path, skill_text: str) -> None:
    for target in LINK_RE.findall(skill_text):
        target = target.strip()
        if not target or target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        clean_target = target.split("#", 1)[0]
        resolved = (root / clean_target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            result.error("SKILL.md", f"link escapes skill root: {target}")
            continue
        if not resolved.exists():
            result.error("SKILL.md", f"broken local link: {target}")
        if clean_target.startswith("references/") and len(Path(clean_target).parts) > 2:
            result.warn("SKILL.md", f"deep reference path reduces progressive disclosure clarity: {target}")


def _scan_luau_hazards(result: PackageResult, root: Path) -> None:
    hazards = [
        (re.compile(r"\bGuiService\s*:\s*IsTenFootInterface\s*\("), "deprecated GuiService:IsTenFootInterface() call"),
        (re.compile(r"\bUserInputService\s*\.\s*VREnabled\b"), "deprecated UserInputService.VREnabled use"),
        (re.compile(r"\bUserInputService\s*:\s*GetUserCFrame\s*\("), "deprecated UserInputService:GetUserCFrame() call"),
        (re.compile(r"\bInputAction\s*:\s*Fire\s*\("), "deprecated InputAction:Fire() call"),
        (re.compile(r"\bAddSelection(?:Parent|Tuple)\s*\("), "deprecated GuiService selection-group call"),
    ]

    for path in sorted((root / "assets").glob("*.luau")):
        text = path.read_text(encoding="utf-8")
        for pattern, message in hazards:
            if pattern.search(text):
                result.error(path.relative_to(root).as_posix(), message)

        if "MouseButton1Click:Connect" in text:
            result.warn(path.relative_to(root).as_posix(), "mouse-only GuiButton activation found; prefer Activated")


def validate_package(root: Path) -> PackageResult:
    result = PackageResult()
    root = root.resolve()

    if not root.is_dir():
        result.error("$", f"not a directory: {root}")
        return result

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            result.error(relative, "required package file is missing")

    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        return result

    try:
        skill_text = skill_path.read_text(encoding="utf-8")
    except OSError as exc:
        result.error("SKILL.md", f"could not read: {exc}")
        return result

    fields, body, frontmatter_errors = parse_frontmatter(skill_text)
    for message in frontmatter_errors:
        result.error("SKILL.md", message)

    name = fields.get("name", "")
    description = fields.get("description", "")
    compatibility = fields.get("compatibility", "")

    if not name:
        result.error("SKILL.md:name", "required field is missing or empty")
    else:
        if len(name) > 64:
            result.error("SKILL.md:name", "must be at most 64 characters")
        if not NAME_RE.fullmatch(name):
            result.error("SKILL.md:name", "must contain lowercase letters, digits, and single hyphens only")
        if name != root.name:
            result.error("SKILL.md:name", f"must match parent directory name {root.name!r}")

    if not description:
        result.error("SKILL.md:description", "required field is missing or empty")
    else:
        if len(description) > 1024:
            result.error("SKILL.md:description", "must be at most 1024 characters")
        lowered = description.lower()
        if "use this skill" not in lowered and "use when" not in lowered:
            result.warn("SKILL.md:description", "description should explicitly say when to use the skill")
        for keyword in ("roblox", "touch", "gamepad", "vr"):
            if keyword not in lowered:
                result.warn("SKILL.md:description", f"trigger description omits important keyword {keyword!r}")

    if compatibility and len(compatibility) > 500:
        result.error("SKILL.md:compatibility", "must be at most 500 characters")

    lines = skill_text.splitlines()
    if len(lines) > 500:
        result.error("SKILL.md", f"has {len(lines)} lines; recommended/required package target is <= 500")
    approx_tokens = max(1, len(skill_text) // 4)
    if approx_tokens > 5500:
        result.warn("SKILL.md", f"rough token estimate is {approx_tokens}; target is around 5000 or less")
    if not body.strip():
        result.error("SKILL.md", "body is empty")

    _validate_links(result, root, skill_text)
    _validate_python(result, root)
    _validate_eval_files(result, root)
    _scan_luau_hazards(result, root)

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = path.relative_to(root).as_posix()
        try:
            raw = path.read_bytes()
        except OSError as exc:
            result.error(relative, f"could not read: {exc}")
            continue
        if b"\x00" in raw:
            result.error(relative, "contains NUL bytes")
        if raw and not raw.endswith(b"\n") and path.suffix.lower() in {".md", ".json", ".py", ".luau"}:
            result.warn(relative, "text file should end with a newline")

        if path.parent.name == "references":
            line_count = raw.count(b"\n") + 1
            if line_count > 550:
                result.warn(relative, f"large reference ({line_count} lines); consider splitting if agents load it inefficiently")

    action_result = validate_action_file(root / "assets/action-map.template.json")
    result.action_map = action_payload(action_result)
    for error in action_result.errors:
        result.error("assets/action-map.template.json", error)
    for warning in action_result.warnings:
        result.warn("assets/action-map.template.json", warning)

    try:
        changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
        if "1.0.0" not in changelog:
            result.warn("CHANGELOG.md", "does not mention metadata version 1.0.0")
    except OSError:
        pass

    result.stats = {
        "root": str(root),
        "skillName": name,
        "skillLines": len(lines),
        "roughSkillTokens": approx_tokens,
        "files": sum(1 for path in root.rglob("*") if path.is_file()),
        "references": sum(1 for path in (root / "references").glob("*.md")),
        "assets": sum(1 for path in (root / "assets").glob("*")),
        "scripts": sum(1 for path in (root / "scripts").glob("*.py")),
    }
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path, help="Skill package directory")
    parser.add_argument("--warnings-as-errors", action="store_true")
    args = parser.parse_args(argv)

    result = validate_package(args.root)
    payload = {
        "status": "pass" if result.ok else "fail",
        "errors": result.errors,
        "warnings": result.warnings,
        "stats": result.stats,
        "actionMap": result.action_map,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))

    if not result.ok:
        return 1
    if args.warnings_as_errors and result.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
