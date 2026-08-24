-- Roblox Lighting Director: current-scene audit helper.
-- Run from the Roblox Studio Command Bar. This script is read-only and prints JSON.
-- It intentionally uses guarded property reads so it remains useful across engine rollouts.

local HttpService = game:GetService("HttpService")
local Lighting = game:GetService("Lighting")
local MaterialService = game:GetService("MaterialService")
local Workspace = game:GetService("Workspace")
local Terrain = Workspace:FindFirstChildOfClass("Terrain")

local function pathOf(instance)
    local segments = {}
    local current = instance
    while current and current ~= game do
        table.insert(segments, 1, current.Name)
        current = current.Parent
    end
    return "/" .. table.concat(segments, "/")
end

local function serialize(value)
    local kind = typeof(value)
    if kind == "Color3" then
        return {
            type = "Color3",
            rgb = {
                math.round(value.R * 255),
                math.round(value.G * 255),
                math.round(value.B * 255),
            },
        }
    elseif kind == "Vector2" then
        return {type = "Vector2", xy = {value.X, value.Y}}
    elseif kind == "Vector3" then
        return {type = "Vector3", xyz = {value.X, value.Y, value.Z}}
    elseif kind == "CFrame" then
        return {type = "CFrame", components = {value:GetComponents()}}
    elseif kind == "EnumItem" then
        return {type = "EnumItem", value = tostring(value)}
    elseif kind == "number" or kind == "boolean" or kind == "string" then
        return value
    elseif value == nil then
        return nil
    end
    return {type = kind, value = tostring(value)}
end

local function readProperties(instance, names)
    local result = {}
    for _, name in names do
        local ok, value = pcall(function()
            return instance[name]
        end)
        if ok then
            result[name] = serialize(value)
        else
            result[name] = {unreadable = true, error = tostring(value)}
        end
    end
    return result
end

local lightingProperties = {
    "Ambient",
    "Brightness",
    "ClockTime",
    "ColorShift_Bottom",
    "ColorShift_Top",
    "EnvironmentDiffuseScale",
    "EnvironmentSpecularScale",
    "ExposureCompensation",
    "ExtendLightRangeTo120",
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

local classProperties = {
    Atmosphere = {"Color", "Decay", "Density", "Glare", "Haze", "Offset"},
    Sky = {
        "CelestialBodiesShown",
        "MoonAngularSize",
        "MoonTextureId",
        "SkyboxBk",
        "SkyboxDn",
        "SkyboxFt",
        "SkyboxLf",
        "SkyboxRt",
        "SkyboxUp",
        "StarCount",
        "SunAngularSize",
        "SunTextureId",
    },
    BloomEffect = {"Enabled", "Intensity", "Size", "Threshold"},
    BlurEffect = {"Enabled", "Size"},
    ColorCorrectionEffect = {"Enabled", "Brightness", "Contrast", "Saturation", "TintColor"},
    ColorGradingEffect = {"Enabled", "TonemapperPreset"},
    DepthOfFieldEffect = {"Enabled", "FocusDistance", "InFocusRadius", "NearIntensity", "FarIntensity"},
    SunRaysEffect = {"Enabled", "Intensity", "Spread"},
    Clouds = {"Enabled", "Color", "Cover", "Density"},
    PointLight = {"Enabled", "Color", "Brightness", "Shadows", "Range"},
    SpotLight = {"Enabled", "Color", "Brightness", "Shadows", "Range", "Angle", "Face"},
    SurfaceLight = {"Enabled", "Color", "Brightness", "Shadows", "Range", "Angle", "Face"},
    SurfaceAppearance = {"AlphaMode", "ColorMap", "MetalnessMap", "NormalMap", "RoughnessMap"},
    MaterialVariant = {"BaseMaterial", "ColorMap", "MetalnessMap", "NormalMap", "RoughnessMap", "StudsPerTile"},
}

local report = {
    schema_version = "1.1",
    generated_utc = os.date("!%Y-%m-%dT%H:%M:%SZ"),
    place_id = game.PlaceId,
    universe_id = game.GameId,
    lighting = readProperties(Lighting, lightingProperties),
    sun_direction = serialize(Lighting:GetSunDirection()),
    moon_direction = serialize(Lighting:GetMoonDirection()),
    workspace = readProperties(Workspace, {"GlobalWind"}),
    terrain = Terrain and readProperties(Terrain, {
        "Decoration",
        "WaterColor",
        "WaterReflectance",
        "WaterTransparency",
        "WaterWaveSize",
        "WaterWaveSpeed",
    }) or nil,
    lighting_children = {},
    camera_effects = {},
    terrain_clouds = {},
    local_lights = {},
    local_light_counts = {PointLight = 0, SpotLight = 0, SurfaceLight = 0, shadowed = 0},
    material_summary = {
        base_parts = 0,
        cast_shadow_false = 0,
        neon_parts = 0,
        surface_appearances = 0,
        material_variants = 0,
        material_variant_usage = {},
    },
    surface_appearances = {},
    material_variants = {},
    warnings = {},
}

for _, descendant in Lighting:GetDescendants() do
    local names = classProperties[descendant.ClassName]
    table.insert(report.lighting_children, {
        class = descendant.ClassName,
        name = descendant.Name,
        path = pathOf(descendant),
        managed = descendant:GetAttribute("RobloxLightingManaged") == true,
        properties = names and readProperties(descendant, names) or {},
    })
end

local camera = Workspace.CurrentCamera
if camera then
    for _, descendant in camera:GetDescendants() do
        local names = classProperties[descendant.ClassName]
        if names then
            table.insert(report.camera_effects, {
                class = descendant.ClassName,
                name = descendant.Name,
                path = pathOf(descendant),
                managed = descendant:GetAttribute("RobloxLightingManaged") == true,
                properties = readProperties(descendant, names),
            })
        end
    end
end

if Terrain then
    for _, child in Terrain:GetChildren() do
        if child:IsA("Clouds") then
            table.insert(report.terrain_clouds, {
                class = child.ClassName,
                name = child.Name,
                path = pathOf(child),
                managed = child:GetAttribute("RobloxLightingManaged") == true,
                properties = readProperties(child, classProperties.Clouds),
            })
        end
    end
end

local localLightLimit = 500
local surfaceAppearanceLimit = 300
for _, descendant in Workspace:GetDescendants() do
    if descendant:IsA("BasePart") then
        report.material_summary.base_parts += 1
        if descendant.CastShadow == false then
            report.material_summary.cast_shadow_false += 1
        end
        if descendant.Material == Enum.Material.Neon then
            report.material_summary.neon_parts += 1
        end

        local variant = descendant.MaterialVariant
        if variant ~= "" then
            report.material_summary.material_variant_usage[variant] =
                (report.material_summary.material_variant_usage[variant] or 0) + 1
        end
    elseif descendant:IsA("SurfaceAppearance") then
        report.material_summary.surface_appearances += 1
        if #report.surface_appearances < surfaceAppearanceLimit then
            table.insert(report.surface_appearances, {
                class = descendant.ClassName,
                name = descendant.Name,
                path = pathOf(descendant),
                properties = readProperties(descendant, classProperties.SurfaceAppearance),
            })
        end
    end

    if descendant:IsA("PointLight") or descendant:IsA("SpotLight") or descendant:IsA("SurfaceLight") then
        report.local_light_counts[descendant.ClassName] += 1
        if descendant.Shadows then
            report.local_light_counts.shadowed += 1
        end
        if #report.local_lights < localLightLimit then
            table.insert(report.local_lights, {
                class = descendant.ClassName,
                name = descendant.Name,
                path = pathOf(descendant),
                parent_path = descendant.Parent and pathOf(descendant.Parent) or nil,
                managed = descendant:GetAttribute("RobloxLightingManaged") == true,
                properties = readProperties(descendant, classProperties[descendant.ClassName]),
            })
        end
    end
end

local materialVariantLimit = 300
for _, descendant in MaterialService:GetDescendants() do
    if descendant:IsA("MaterialVariant") then
        report.material_summary.material_variants += 1
        if #report.material_variants < materialVariantLimit then
            table.insert(report.material_variants, {
                class = descendant.ClassName,
                name = descendant.Name,
                path = pathOf(descendant),
                properties = readProperties(descendant, classProperties.MaterialVariant),
            })
        end
    end
end

local atmospheres = 0
local skies = 0
local colorGraders = 0
for _, descendant in Lighting:GetDescendants() do
    if descendant:IsA("Atmosphere") then atmospheres += 1 end
    if descendant:IsA("Sky") then skies += 1 end
    if descendant:IsA("ColorGradingEffect") then colorGraders += 1 end
end

if atmospheres > 1 then
    table.insert(report.warnings, "Multiple Atmosphere instances require review.")
end
if skies > 1 then
    table.insert(report.warnings, "Multiple Sky instances require review.")
end
if colorGraders > 1 then
    table.insert(report.warnings, "Multiple ColorGradingEffect instances do not combine as a controllable stack; keep one authoritative grader per active container.")
end
if atmospheres > 0 then
    table.insert(report.warnings, "Atmosphere is present. Treat legacy FogStart/FogEnd/FogColor as a compatibility clue, not automatically as the active depth model.")
end
if #report.local_lights >= localLightLimit then
    table.insert(report.warnings, "Local-light detail list was capped at 500; aggregate counts are complete.")
end
if #report.surface_appearances >= surfaceAppearanceLimit then
    table.insert(report.warnings, "SurfaceAppearance detail list was capped at 300; aggregate counts are complete.")
end
if #report.material_variants >= materialVariantLimit then
    table.insert(report.warnings, "MaterialVariant detail list was capped at 300; aggregate counts are complete.")
end

print(HttpService:JSONEncode(report))
print("[roblox-lighting] Read-only audit complete. Copy the JSON from Output into a file for the AI.")
