#!/usr/bin/env python3
"""Generate non-destructive Roblox Studio Luau from a validated lighting plan."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

from validate_plan import validate_plan

COLOR_PROPERTIES = {
    "Ambient",
    "ColorShift_Bottom",
    "ColorShift_Top",
    "FogColor",
    "OutdoorAmbient",
    "Color",
    "Decay",
    "TintColor",
}
ENUM_PROPERTIES = {
    "LightingStyle": "LightingStyle",
    "TonemapperPreset": "TonemapperPreset",
    "Face": "NormalId",
}


def lua_string(value: str) -> str:
    # JSON string syntax is compatible with normal Luau string literals.
    return json.dumps(value, ensure_ascii=False)


def luau_value(value: Any, property_name: str | None = None) -> str:
    if property_name in COLOR_PROPERTIES and isinstance(value, list) and len(value) == 3:
        return f"Color3.fromRGB({int(value[0])}, {int(value[1])}, {int(value[2])})"
    if property_name in ENUM_PROPERTIES and isinstance(value, str):
        return f"Enum.{ENUM_PROPERTIES[property_name]}.{value}"
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "nil"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return lua_string(value)
    if isinstance(value, list) and len(value) == 3 and all(isinstance(v, (int, float)) for v in value):
        return f"Vector3.new({value[0]}, {value[1]}, {value[2]})"
    raise TypeError(f"unsupported value for {property_name or 'property'}: {value!r}")


def emit_set(lines: list[str], variable: str, property_name: str, value: Any, indent: str = "") -> None:
    lines.append(
        f"{indent}safeSet({variable}, {lua_string(property_name)}, {luau_value(value, property_name)})"
    )


def backup_property_names(plan: dict[str, Any]) -> list[str]:
    standard = {
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
    standard.update(plan.get("lighting", {}).get("properties", {}).keys())
    return sorted(standard)


def generate_main(
    plan: dict[str, Any], camera_script_name: str | None, replace_conflicts: bool
) -> str:
    plan_id = str(plan["plan_id"])
    generated_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    lighting = plan["lighting"]
    conflict_classes: list[str] = []
    if isinstance(lighting.get("sky"), dict):
        conflict_classes.append("Sky")
    if isinstance(lighting.get("atmosphere"), dict):
        conflict_classes.append("Atmosphere")
    for effect in lighting.get("post_effects", []):
        if effect.get("parent") == "Lighting":
            conflict_classes.append(str(effect["class"]))
    conflict_classes = sorted(set(conflict_classes))
    manage_clouds = isinstance(lighting.get("clouds"), dict)

    lines: list[str] = [
        "-- Roblox Lighting Director generated script",
        f"-- Plan ID: {plan_id}",
        f"-- Generated UTC: {generated_at}",
        "-- Run in Roblox Studio Command Bar or a trusted Studio plugin context.",
        "-- The script backs up affected state. By default it removes only prior skill-managed instances;",
        "-- --replace-conflicts also replaces matching unmanaged global environment instances after backup.",
        "",
        'local Lighting = game:GetService("Lighting")',
        'local ServerStorage = game:GetService("ServerStorage")',
        'local HttpService = game:GetService("HttpService")',
        "local Terrain = workspace:FindFirstChildOfClass(\"Terrain\")",
        f"local PLAN_ID = {lua_string(plan_id)}",
        'local MANAGED_ATTRIBUTE = "RobloxLightingManaged"',
        'local PLAN_ATTRIBUTE = "RobloxLightingPlanId"',
        f"local REPLACE_CONFLICTS = {'true' if replace_conflicts else 'false'}",
        f"local MANAGE_CLOUDS = {'true' if manage_clouds else 'false'}",
        "local REPLACE_CLOUDS = REPLACE_CONFLICTS and MANAGE_CLOUDS",
        "local CONFLICTING_LIGHTING_CLASSES = {",
    ]
    for class_name in conflict_classes:
        lines.append(f"    [{lua_string(class_name)}] = true,")
    lines += [
        "}",
        "",
        "local function safeSet(instance, propertyName, value)",
        "    local ok, err = pcall(function()",
        "        instance[propertyName] = value",
        "    end)",
        "    if not ok then",
        '        warn(("[roblox-lighting] Could not set %s.%s: %s"):format(instance:GetFullName(), propertyName, tostring(err)))',
        "    end",
        "    return ok",
        "end",
        "",
        "local function markManaged(instance, category)",
        "    instance:SetAttribute(MANAGED_ATTRIBUTE, true)",
        "    instance:SetAttribute(PLAN_ATTRIBUTE, PLAN_ID)",
        '    instance:SetAttribute("RobloxLightingCategory", category)',
        "end",
        "",
        "local function slashPath(instance)",
        "    local segments = {}",
        "    local current = instance",
        "    while current and current ~= game do",
        "        table.insert(segments, 1, current.Name)",
        "        current = current.Parent",
        "    end",
        '    return "/" .. table.concat(segments, "/")',
        "end",
        "",
        "local function resolvePath(path)",
        "    if type(path) ~= \"string\" then return nil end",
        "    local current = game",
        '    for segment in string.gmatch(path, "[^/]+") do',
        '        if segment == "Workspace" then',
        "            current = workspace",
        '        elseif segment == "Lighting" then',
        "            current = Lighting",
        "        elseif current then",
        "            current = current:FindFirstChild(segment)",
        "        end",
        "        if not current then return nil end",
        "    end",
        "    return current",
        "end",
        "",
        "local function storeProperty(folder, propertyName, value)",
        "    local valueType = typeof(value)",
        "    local object",
        '    if valueType == "Color3" then',
        '        object = Instance.new("Color3Value")',
        '    elseif valueType == "number" then',
        '        object = Instance.new("NumberValue")',
        '    elseif valueType == "boolean" then',
        '        object = Instance.new("BoolValue")',
        '    elseif valueType == "Vector3" then',
        '        object = Instance.new("Vector3Value")',
        '    elseif valueType == "string" then',
        '        object = Instance.new("StringValue")',
        '    elseif valueType == "EnumItem" then',
        '        object = Instance.new("StringValue")',
        '        object:SetAttribute("ValueKind", "EnumItem")',
        "        object.Value = tostring(value)",
        "    else",
        '        object = Instance.new("StringValue")',
        '        object:SetAttribute("ValueKind", "Unsupported")',
        "        object.Value = tostring(value)",
        "    end",
        "    object.Name = propertyName",
        '    object:SetAttribute("PropertyName", propertyName)',
        '    if valueType ~= "EnumItem" and object:GetAttribute("ValueKind") ~= "Unsupported" then',
        "        object.Value = value",
        "    end",
        "    object.Parent = folder",
        "end",
        "",
        "local backupRoot = ServerStorage:FindFirstChild(\"_RobloxLightingBackups\")",
        "if not backupRoot then",
        '    backupRoot = Instance.new("Folder")',
        '    backupRoot.Name = "_RobloxLightingBackups"',
        "    backupRoot.Parent = ServerStorage",
        "end",
        "local backup = Instance.new(\"Folder\")",
        'backup.Name = os.date("!%Y%m%dT%H%M%SZ") .. "_" .. PLAN_ID .. "_" .. string.sub(HttpService:GenerateGUID(false), 1, 8)',
        "backup.Parent = backupRoot",
        'backup:SetAttribute("PlanId", PLAN_ID)',
        f'backup:SetAttribute("GeneratedAt", {lua_string(generated_at)})',
        "",
        'local propertyFolder = Instance.new("Folder")',
        'propertyFolder.Name = "LightingProperties"',
        "propertyFolder.Parent = backup",
        "local propertiesToBackup = {",
    ]
    for prop in backup_property_names(plan):
        lines.append(f"    {lua_string(prop)},")
    lines += [
        "}",
        "for _, propertyName in propertiesToBackup do",
        "    local ok, value = pcall(function() return Lighting[propertyName] end)",
        "    if ok then",
        "        storeProperty(propertyFolder, propertyName, value)",
        "    else",
        '        warn(("[roblox-lighting] Could not back up Lighting.%s"):format(propertyName))',
        "    end",
        "end",
        "",
        'local workspacePropertyFolder = Instance.new("Folder")',
        'workspacePropertyFolder.Name = "WorkspaceProperties"',
        "workspacePropertyFolder.Parent = backup",
        'local okWind, windValue = pcall(function() return workspace.GlobalWind end)',
        "if okWind then",
        '    storeProperty(workspacePropertyFolder, "GlobalWind", windValue)',
        "end",
        "",
        'local lightingChildrenBackup = Instance.new("Folder")',
        'lightingChildrenBackup.Name = "LightingChildren"',
        "lightingChildrenBackup.Parent = backup",
        "for _, child in Lighting:GetChildren() do",
        "    local isManaged = child:GetAttribute(MANAGED_ATTRIBUTE) == true",
        "    local isConflict = CONFLICTING_LIGHTING_CLASSES[child.ClassName] == true",
        "    if isManaged or (REPLACE_CONFLICTS and isConflict) then",
        "        local ok, clone = pcall(function() return child:Clone() end)",
        "        if ok and clone then clone.Parent = lightingChildrenBackup end",
        "    elseif isConflict then",
        '        warn(("[roblox-lighting] Preserving unmanaged %s %s; it may alter the planned result. Re-generate with --replace-conflicts after review for deterministic matching."):format(child.ClassName, child:GetFullName()))',
        "    end",
        "end",
        "",
        'local terrainChildrenBackup = Instance.new("Folder")',
        'terrainChildrenBackup.Name = "TerrainChildren"',
        "terrainChildrenBackup.Parent = backup",
        "if Terrain then",
        "    for _, child in Terrain:GetChildren() do",
        '        if child:IsA("Clouds") then',
        "            local isManaged = child:GetAttribute(MANAGED_ATTRIBUTE) == true",
        "            if isManaged or REPLACE_CLOUDS then",
        "                local ok, clone = pcall(function() return child:Clone() end)",
        "                if ok and clone then clone.Parent = terrainChildrenBackup end",
        "            elseif MANAGE_CLOUDS then",
        '                warn(("[roblox-lighting] Preserving unmanaged Clouds %s; it may alter the planned result. Re-generate with --replace-conflicts after review for deterministic matching."):format(child:GetFullName()))',
        "            end",
        "        end",
        "    end",
        "end",
        "",
        'local localLightsBackup = Instance.new("Folder")',
        'localLightsBackup.Name = "WorkspaceManagedLights"',
        "localLightsBackup.Parent = backup",
        "for _, descendant in workspace:GetDescendants() do",
        '    if (descendant:IsA("PointLight") or descendant:IsA("SpotLight") or descendant:IsA("SurfaceLight"))',
        "        and descendant:GetAttribute(MANAGED_ATTRIBUTE) == true then",
        "        local ok, clone = pcall(function() return descendant:Clone() end)",
        "        if ok and clone then",
        '            clone:SetAttribute("OriginalParentPath", slashPath(descendant.Parent))',
        "            clone.Parent = localLightsBackup",
        "        end",
        "    end",
        "end",
        "",
        "-- Remove only instances created by this skill in previous runs.",
        "for _, child in Lighting:GetChildren() do",
        "    local isManaged = child:GetAttribute(MANAGED_ATTRIBUTE) == true",
        "    local isConflict = CONFLICTING_LIGHTING_CLASSES[child.ClassName] == true",
        "    if isManaged or (REPLACE_CONFLICTS and isConflict) then child:Destroy() end",
        "end",
        "if Terrain then",
        "    for _, child in Terrain:GetChildren() do",
        '        if child:IsA("Clouds") and (child:GetAttribute(MANAGED_ATTRIBUTE) == true or REPLACE_CLOUDS) then child:Destroy() end',
        "    end",
        "end",
        "local managedLocalLights = {}",
        "for _, descendant in workspace:GetDescendants() do",
        '    if (descendant:IsA("PointLight") or descendant:IsA("SpotLight") or descendant:IsA("SurfaceLight"))',
        "        and descendant:GetAttribute(MANAGED_ATTRIBUTE) == true then",
        "        table.insert(managedLocalLights, descendant)",
        "    end",
        "end",
        "for _, light in managedLocalLights do light:Destroy() end",
        "",
        "-- Apply global Lighting properties.",
    ]

    for prop, value in lighting.get("properties", {}).items():
        emit_set(lines, "Lighting", prop, value)

    manual = lighting.get("manual_properties", {})
    if manual:
        lines.append("")
        lines.append("-- Manual or rollout/security-restricted properties requested by the plan:")
        for prop, value in manual.items():
            lines.append(f"warn({lua_string(f'[roblox-lighting] Apply/re-check manually: Lighting.{prop} = {value!r}')})")

    sky = lighting.get("sky")
    if isinstance(sky, dict) and sky.get("enabled", True):
        lines += [
            "",
            'local managedSky = Instance.new("Sky")',
            f"managedSky.Name = {lua_string(sky.get('name', 'RobloxLightingSky'))}",
            'markManaged(managedSky, "Sky")',
        ]
        for prop, value in sky.get("properties", {}).items():
            emit_set(lines, "managedSky", prop, value)
        lines.append("managedSky.Parent = Lighting")

    atmosphere = lighting.get("atmosphere")
    if isinstance(atmosphere, dict) and atmosphere.get("enabled", True):
        lines += [
            "",
            'local managedAtmosphere = Instance.new("Atmosphere")',
            f"managedAtmosphere.Name = {lua_string(atmosphere.get('name', 'RobloxLightingAtmosphere'))}",
            'markManaged(managedAtmosphere, "Atmosphere")',
        ]
        for prop, value in atmosphere.get("properties", {}).items():
            emit_set(lines, "managedAtmosphere", prop, value)
        lines.append("managedAtmosphere.Parent = Lighting")

    legacy = lighting.get("legacy_fog", {})
    if isinstance(legacy, dict) and legacy.get("enabled"):
        lines.append("")
        lines.append("-- Apply the selected legacy fog profile.")
        for prop in ("FogColor", "FogStart", "FogEnd"):
            if prop in legacy:
                emit_set(lines, "Lighting", prop, legacy[prop])

    clouds = lighting.get("clouds")
    if isinstance(clouds, dict) and clouds.get("enabled", True):
        lines += [
            "",
            "if Terrain then",
            '    local managedClouds = Instance.new("Clouds")',
            f"    managedClouds.Name = {lua_string(clouds.get('name', 'RobloxLightingClouds'))}",
            '    markManaged(managedClouds, "Clouds")',
        ]
        for prop, value in clouds.get("properties", {}).items():
            emit_set(lines, "managedClouds", prop, value, indent="    ")
        lines += [
            "    managedClouds.Parent = Terrain",
            "else",
            '    warn("[roblox-lighting] Terrain not found; Clouds were not created")',
            "end",
        ]
        if "global_wind" in clouds:
            emit_set(lines, "workspace", "GlobalWind", clouds["global_wind"])

    lighting_effects = [
        effect for effect in lighting.get("post_effects", []) if effect.get("parent") == "Lighting"
    ]
    for idx, effect in enumerate(lighting_effects, start=1):
        var = f"postEffect{idx}"
        lines += [
            "",
            f"local {var} = Instance.new({lua_string(effect['class'])})",
            f"{var}.Name = {lua_string(effect.get('name', effect['class']))}",
            f'markManaged({var}, "PostEffect")',
            f"safeSet({var}, \"Enabled\", {'true' if effect.get('enabled', True) else 'false'})",
        ]
        for prop, value in effect.get("properties", {}).items():
            emit_set(lines, var, prop, value)
        tiers = effect.get("quality_tiers", [])
        if tiers:
            lines.append(f'{var}:SetAttribute("RobloxLightingQualityTiers", {lua_string(",".join(tiers))})')
        lines.append(f"{var}.Parent = Lighting")

    lines += [
        "",
        "-- Create local lights on semantic Workspace targets.",
    ]
    for idx, light in enumerate(plan.get("local_lights", []), start=1):
        parent_var = f"target{idx}"
        light_var = f"localLight{idx}"
        lines += [
            f"local {parent_var} = resolvePath({lua_string(light['target_path'])})",
            f"if {parent_var} and ({parent_var}:IsA(\"BasePart\") or {parent_var}:IsA(\"Attachment\")) then",
            f"    local {light_var} = Instance.new({lua_string(light['class'])})",
            f"    {light_var}.Name = {lua_string(light.get('name', light['class']))}",
            f'    markManaged({light_var}, "LocalLight")',
            f'    {light_var}:SetAttribute("RobloxLightingLightId", {lua_string(light["id"])})',
            f'    {light_var}:SetAttribute("RobloxLightingQualityTiers", {lua_string(",".join(light.get("quality_tiers", [])))})',
        ]
        if light.get("activation_group"):
            lines.append(
                f'    {light_var}:SetAttribute("RobloxLightingActivationGroup", {lua_string(str(light["activation_group"]))})'
            )
        for prop, value in light.get("properties", {}).items():
            emit_set(lines, light_var, prop, value, indent="    ")
        lines += [
            f"    {light_var}.Parent = {parent_var}",
            "else",
            f"    warn({lua_string('[roblox-lighting] Local-light target missing or not a BasePart/Attachment: ' + light['target_path'])})",
            "end",
        ]

    camera_effects = [
        effect for effect in lighting.get("post_effects", []) if effect.get("parent") == "Camera"
    ]
    lines += [
        "",
        f'print("[roblox-lighting] Applied plan {plan_id}. Backup: " .. backup:GetFullName())',
        'print("[roblox-lighting] Review all validation cameras and graphics tiers before saving/publishing.")',
    ]
    if camera_effects:
        if camera_script_name:
            lines.append(
                f"warn({lua_string('[roblox-lighting] Camera-local effects require the generated client script: ' + camera_script_name)})"
            )
        else:
            lines.append(
                'warn("[roblox-lighting] Camera-local effects exist in the plan but no client script path was generated")'
            )

    return "\n".join(lines) + "\n"


def generate_camera(plan: dict[str, Any]) -> str | None:
    effects = [
        effect for effect in plan["lighting"].get("post_effects", []) if effect.get("parent") == "Camera"
    ]
    if not effects:
        return None

    plan_id = str(plan["plan_id"])
    lines = [
        "-- Roblox Lighting Director camera-local effects",
        "-- Place this LocalScript under StarterPlayer > StarterPlayerScripts.",
        f"-- Plan ID: {plan_id}",
        "",
        'local Workspace = game:GetService("Workspace")',
        f"local PLAN_ID = {lua_string(plan_id)}",
        "",
        "local function safeSet(instance, propertyName, value)",
        "    local ok, err = pcall(function() instance[propertyName] = value end)",
        '    if not ok then warn(("[roblox-lighting] Camera effect property failed: %s"):format(tostring(err))) end',
        "end",
        "",
        "local function apply(camera)",
        "    for _, child in camera:GetChildren() do",
        '        if child:GetAttribute("RobloxLightingManaged") == true then child:Destroy() end',
        "    end",
    ]
    for idx, effect in enumerate(effects, start=1):
        var = f"effect{idx}"
        lines += [
            f"    local {var} = Instance.new({lua_string(effect['class'])})",
            f"    {var}.Name = {lua_string(effect.get('name', effect['class']))}",
            f'    {var}:SetAttribute("RobloxLightingManaged", true)',
            f'    {var}:SetAttribute("RobloxLightingPlanId", PLAN_ID)',
            f"    safeSet({var}, \"Enabled\", {'true' if effect.get('enabled', True) else 'false'})",
        ]
        for prop, value in effect.get("properties", {}).items():
            emit_set(lines, var, prop, value, indent="    ")
        lines.append(f"    {var}.Parent = camera")
    lines += [
        "end",
        "",
        "if Workspace.CurrentCamera then apply(Workspace.CurrentCamera) end",
        'Workspace:GetPropertyChangedSignal("CurrentCamera"):Connect(function()',
        "    if Workspace.CurrentCamera then apply(Workspace.CurrentCamera) end",
        "end)",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--camera-output", type=Path)
    parser.add_argument(
        "--replace-conflicts",
        action="store_true",
        help="back up and replace unmanaged Sky/Atmosphere/Clouds and planned Lighting post-effect classes",
    )
    parser.add_argument("--skip-validation", action="store_true")
    args = parser.parse_args()

    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: could not read plan: {exc}", file=sys.stderr)
        return 2
    if not isinstance(plan, dict):
        print("ERROR: plan root must be an object", file=sys.stderr)
        return 2

    if not args.skip_validation:
        errors, warnings = validate_plan(plan)
        for warning in warnings:
            print("WARNING:", warning, file=sys.stderr)
        if errors:
            for error in errors:
                print("ERROR:", error, file=sys.stderr)
            print("Generation stopped because the plan is invalid.", file=sys.stderr)
            return 1

    camera_text = generate_camera(plan)
    camera_path = args.camera_output
    if camera_text and camera_path is None:
        camera_path = args.output.with_name(args.output.stem + "_camera.client.lua")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        generate_main(plan, camera_path.name if camera_path else None, args.replace_conflicts),
        encoding="utf-8",
    )
    print("Wrote", args.output)

    if camera_text and camera_path:
        camera_path.parent.mkdir(parents=True, exist_ok=True)
        camera_path.write_text(camera_text, encoding="utf-8")
        print("Wrote", camera_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
