#!/usr/bin/env python3
"""Validate a roblox-multi-device action map using only the Python standard library.

Usage:
    python scripts/validate_action_map.py assets/action-map.template.json

The script prints structured JSON and exits with status 1 when validation errors exist.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

DEVICE_IDS = {"keyboardMouse", "touch", "gamepad", "vr"}
ACTION_TYPES = {"Bool", "Direction1D", "Direction2D", "Direction3D", "ViewportPosition"}
AUTHORITIES = {"local", "client", "server", "split"}
BINDING_KINDS = {
    "KeyCode",
    "UIButton",
    "GuiButtonActivated",
    "Composite1D",
    "Composite2D",
    "CompositeTriggers",
    "Axis1D",
    "Axis2D",
    "ViewportPosition",
    "VirtualAxis",
    "VirtualStick",
    "Gesture",
    "Sensor",
    "VRPose",
}
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, path: str, message: str) -> None:
        self.errors.append(f"{path}: {message}")

    def warn(self, path: str, message: str) -> None:
        self.warnings.append(f"{path}: {message}")


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _expect_list(result: ValidationResult, value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        result.error(path, "must be an array")
        return []
    return value


def _expect_nonempty_string(result: ValidationResult, value: Any, path: str) -> str | None:
    if not isinstance(value, str) or not value.strip():
        result.error(path, "must be a non-empty string")
        return None
    return value


def _duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return repeated


def _validate_device_list(
    result: ValidationResult,
    value: Any,
    path: str,
    *,
    allow_empty: bool = False,
) -> list[str]:
    raw = _expect_list(result, value, path)
    devices: list[str] = []
    for index, device in enumerate(raw):
        item_path = f"{path}[{index}]"
        if not isinstance(device, str):
            result.error(item_path, "must be a string")
            continue
        if device not in DEVICE_IDS:
            result.error(item_path, f"unknown device {device!r}; allowed: {sorted(DEVICE_IDS)}")
            continue
        devices.append(device)

    if not devices and not allow_empty:
        result.error(path, "must contain at least one supported device")
    for duplicate in sorted(_duplicates(devices)):
        result.error(path, f"contains duplicate device {duplicate!r}")
    return devices


def _validate_binding(
    result: ValidationResult,
    binding: Any,
    path: str,
    action_devices: set[str],
    action_type: str | None,
) -> str | None:
    if not isinstance(binding, dict):
        result.error(path, "must be an object")
        return None

    device = binding.get("device")
    if not isinstance(device, str) or device not in DEVICE_IDS:
        result.error(f"{path}.device", f"must be one of {sorted(DEVICE_IDS)}")
        return None
    if device not in action_devices:
        result.error(f"{path}.device", f"{device!r} is not listed in the action's devices")

    kind = binding.get("kind")
    if not isinstance(kind, str) or kind not in BINDING_KINDS:
        result.error(f"{path}.kind", f"must be one of {sorted(BINDING_KINDS)}")

    has_primary_value = any(
        key in binding
        for key in ("value", "positive", "negative", "up", "down", "left", "right")
    )
    if not has_primary_value:
        result.error(path, "must define a binding value or composite directions")

    for threshold_name in ("deadzone", "pressedThreshold", "releasedThreshold"):
        if threshold_name in binding:
            value = binding[threshold_name]
            if not _is_number(value) or not 0 <= float(value) <= 1:
                result.error(f"{path}.{threshold_name}", "must be a finite number from 0 to 1")

    press = binding.get("pressedThreshold")
    release = binding.get("releasedThreshold")
    if _is_number(press) and _is_number(release) and float(release) >= float(press):
        result.error(
            path,
            "releasedThreshold must be below pressedThreshold to provide hysteresis",
        )

    if action_type == "Bool" and kind in {"Axis1D", "Axis2D", "VirtualAxis", "VirtualStick"}:
        if "pressedThreshold" not in binding:
            result.warn(path, "analog binding for Bool action should document a pressed threshold")

    if action_type in {"Direction1D", "Direction2D", "Direction3D"} and kind == "KeyCode":
        result.warn(path, "one KeyCode alone cannot express the full directional action")

    if device == "touch" and kind == "UIButton":
        value = binding.get("value")
        if not isinstance(value, str) or "/" not in value:
            result.warn(path, "touch UIButton should usually use a stable project UI path/id")

    return device


def validate_data(data: Any, source: str = "<memory>") -> ValidationResult:
    result = ValidationResult()

    if not isinstance(data, dict):
        result.error("$", "root must be a JSON object")
        return result

    schema_version = data.get("$schemaVersion")
    if schema_version != "1.0.0":
        result.warn("$.$schemaVersion", "expected template schema version '1.0.0'")

    _expect_nonempty_string(result, data.get("experience"), "$.experience")

    required_devices = _validate_device_list(result, data.get("requiredDevices"), "$.requiredDevices")
    optional_devices = _validate_device_list(
        result,
        data.get("optionalDevices", []),
        "$.optionalDevices",
        allow_empty=True,
    )
    overlap = set(required_devices) & set(optional_devices)
    if overlap:
        result.error("$.optionalDevices", f"also listed as required: {sorted(overlap)}")

    defaults = data.get("defaults")
    if not isinstance(defaults, dict):
        result.error("$.defaults", "must be an object")
    else:
        if defaults.get("inputSystem") not in {"InputActionSystem", "LegacyCASAdapter"}:
            result.warn(
                "$.defaults.inputSystem",
                "recommended default is 'InputActionSystem' (or a deliberate 'LegacyCASAdapter')",
            )
        if defaults.get("promptPolicy") != "PreferredInput":
            result.warn("$.defaults.promptPolicy", "prompts should normally follow PreferredInput")

    contexts = _expect_list(result, data.get("contexts"), "$.contexts")
    if not contexts:
        result.error("$.contexts", "must contain at least one context")

    context_ids: list[str] = []
    action_ids: list[str] = []
    device_binding_counts = {device: 0 for device in DEVICE_IDS}
    authority_counts = {authority: 0 for authority in AUTHORITIES}
    type_counts = {action_type: 0 for action_type in ACTION_TYPES}

    for context_index, context in enumerate(contexts):
        context_path = f"$.contexts[{context_index}]"
        if not isinstance(context, dict):
            result.error(context_path, "must be an object")
            continue

        context_id = _expect_nonempty_string(result, context.get("id"), f"{context_path}.id")
        if context_id:
            context_ids.append(context_id)
            if not ID_RE.fullmatch(context_id):
                result.error(f"{context_path}.id", "must use letters, numbers, and underscores and start with a letter")

        priority = context.get("priority")
        if not isinstance(priority, int) or isinstance(priority, bool):
            result.error(f"{context_path}.priority", "must be an integer")

        for boolean_field in ("sink", "enabledByDefault"):
            if not isinstance(context.get(boolean_field), bool):
                result.error(f"{context_path}.{boolean_field}", "must be a boolean")

        actions = _expect_list(result, context.get("actions"), f"{context_path}.actions")
        if not actions:
            result.warn(f"{context_path}.actions", "context contains no actions")

        for action_index, action in enumerate(actions):
            action_path = f"{context_path}.actions[{action_index}]"
            if not isinstance(action, dict):
                result.error(action_path, "must be an object")
                continue

            action_id = _expect_nonempty_string(result, action.get("id"), f"{action_path}.id")
            if action_id:
                action_ids.append(action_id)
                if not ID_RE.fullmatch(action_id):
                    result.error(f"{action_path}.id", "must use letters, numbers, and underscores and start with a letter")

            action_type = action.get("type")
            if action_type not in ACTION_TYPES:
                result.error(f"{action_path}.type", f"must be one of {sorted(ACTION_TYPES)}")
                normalized_type: str | None = None
            else:
                normalized_type = str(action_type)
                type_counts[normalized_type] += 1

            _expect_nonempty_string(result, action.get("semantics"), f"{action_path}.semantics")

            authority = action.get("authority")
            if authority not in AUTHORITIES:
                result.error(f"{action_path}.authority", f"must be one of {sorted(AUTHORITIES)}")
            else:
                authority_counts[str(authority)] += 1

            devices = _validate_device_list(result, action.get("devices"), f"{action_path}.devices")
            device_set = set(devices)

            bindings = _expect_list(result, action.get("bindings"), f"{action_path}.bindings")
            binding_devices: list[str] = []
            for binding_index, binding in enumerate(bindings):
                device = _validate_binding(
                    result,
                    binding,
                    f"{action_path}.bindings[{binding_index}]",
                    device_set,
                    normalized_type,
                )
                if device:
                    binding_devices.append(device)
                    device_binding_counts[device] += 1

            missing_bindings = device_set - set(binding_devices)
            if missing_bindings:
                result.error(
                    f"{action_path}.bindings",
                    f"missing bindings for declared devices: {sorted(missing_bindings)}",
                )

            prompt = action.get("prompt")
            if not isinstance(prompt, dict):
                result.error(f"{action_path}.prompt", "must be an object")
            else:
                _expect_nonempty_string(result, prompt.get("label"), f"{action_path}.prompt.label")

            server_validation = action.get("serverValidation")
            if not isinstance(server_validation, list) or not all(
                isinstance(item, str) and item.strip() for item in server_validation
            ):
                result.error(f"{action_path}.serverValidation", "must be an array of non-empty strings")
            elif authority in {"server", "split"} and not server_validation:
                result.warn(
                    f"{action_path}.serverValidation",
                    "authoritative/split action should document server checks",
                )

            accessibility = action.get("accessibility")
            if not isinstance(accessibility, list) or not all(
                isinstance(item, str) and item.strip() for item in accessibility
            ):
                result.error(f"{action_path}.accessibility", "must be an array of non-empty strings")

    for duplicate in sorted(_duplicates(context_ids)):
        result.error("$.contexts", f"duplicate context id {duplicate!r}")
    for duplicate in sorted(_duplicates(action_ids)):
        result.error("$.contexts[*].actions", f"duplicate semantic action id {duplicate!r}")

    present_devices = {device for device, count in device_binding_counts.items() if count > 0}
    for device in required_devices:
        if device not in present_devices:
            result.error("$.requiredDevices", f"required device {device!r} has no action bindings")
    for device in optional_devices:
        if device not in present_devices:
            result.warn("$.optionalDevices", f"optional device {device!r} has no sample bindings")

    ui_tasks = _expect_list(result, data.get("uiTasks", []), "$.uiTasks")
    task_ids: list[str] = []
    for index, task in enumerate(ui_tasks):
        task_path = f"$.uiTasks[{index}]"
        if not isinstance(task, dict):
            result.error(task_path, "must be an object")
            continue
        task_id = _expect_nonempty_string(result, task.get("id"), f"{task_path}.id")
        if task_id:
            task_ids.append(task_id)
        steps = _expect_list(result, task.get("steps"), f"{task_path}.steps")
        if not steps or not all(isinstance(step, str) and step.strip() for step in steps):
            result.error(f"{task_path}.steps", "must contain non-empty task-step strings")
        _validate_device_list(result, task.get("requiredDevices"), f"{task_path}.requiredDevices")
    for duplicate in sorted(_duplicates(task_ids)):
        result.error("$.uiTasks", f"duplicate UI task id {duplicate!r}")

    hot_swap_tests = _expect_list(result, data.get("hotSwapTests", []), "$.hotSwapTests")
    if len(hot_swap_tests) < 2:
        result.warn("$.hotSwapTests", "include multiple stateful input-switch scenarios")

    exclusions = data.get("knownExclusions", [])
    if not isinstance(exclusions, list) or not all(isinstance(item, str) for item in exclusions):
        result.error("$.knownExclusions", "must be an array of strings")
    elif any("replace this entry" in item.lower() for item in exclusions):
        result.warn("$.knownExclusions", "template placeholder remains; replace or remove before project use")

    result.stats = {
        "source": source,
        "contexts": len(context_ids),
        "actions": len(action_ids),
        "uiTasks": len(task_ids),
        "bindingsByDevice": dict(sorted(device_binding_counts.items())),
        "actionsByType": dict(sorted(type_counts.items())),
        "actionsByAuthority": dict(sorted(authority_counts.items())),
    }
    return result


def validate_file(path: Path) -> ValidationResult:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        result = ValidationResult()
        result.error("$", f"file not found: {path}")
        return result
    except json.JSONDecodeError as exc:
        result = ValidationResult()
        result.error("$", f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}")
        return result
    except OSError as exc:
        result = ValidationResult()
        result.error("$", f"could not read {path}: {exc}")
        return result

    return validate_data(data, str(path))


def as_payload(result: ValidationResult) -> dict[str, Any]:
    return {
        "status": "pass" if result.ok else "fail",
        "errors": result.errors,
        "warnings": result.warnings,
        "stats": result.stats,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Path to an action-map JSON file")
    parser.add_argument(
        "--warnings-as-errors",
        action="store_true",
        help="Return failure when warnings exist",
    )
    args = parser.parse_args(argv)

    result = validate_file(args.path)
    print(json.dumps(as_payload(result), indent=2, sort_keys=True))

    if not result.ok:
        return 1
    if args.warnings_as_errors and result.warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
