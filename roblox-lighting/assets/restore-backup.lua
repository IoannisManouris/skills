-- Roblox Lighting Director: restore the most recent generated backup.
-- Run from Studio Command Bar after reviewing the target backup name.
-- This restores the global properties and skill-managed instances that the
-- generated apply script replaced. Unmanaged user content is left untouched.

local Lighting = game:GetService("Lighting")
local ServerStorage = game:GetService("ServerStorage")
local Terrain = workspace:FindFirstChildOfClass("Terrain")
local MANAGED_ATTRIBUTE = "RobloxLightingManaged"
local TARGET_BACKUP_NAME = nil -- Set to a folder name to restore a specific backup; nil restores the newest.

local function resolvePath(path)
    if type(path) ~= "string" then
        return nil
    end

    local current = game
    for segment in string.gmatch(path, "[^/]+") do
        if segment == "Workspace" then
            current = workspace
        elseif segment == "Lighting" then
            current = Lighting
        elseif current then
            current = current:FindFirstChild(segment)
        end
        if not current then
            return nil
        end
    end
    return current
end

local function decodeEnum(text)
    if type(text) ~= "string" then
        return nil
    end

    local enumTypeName, itemName = string.match(text, "^Enum%.([%w_]+)%.([%w_]+)$")
    if not enumTypeName or not itemName then
        return nil
    end

    local okType, enumType = pcall(function()
        return Enum[enumTypeName]
    end)
    if not okType or enumType == nil then
        return nil
    end

    local okItem, enumItem = pcall(function()
        return enumType[itemName]
    end)
    if not okItem then
        return nil
    end
    return enumItem
end

local function restoreProperty(target, valueObject)
    local propertyName = valueObject:GetAttribute("PropertyName") or valueObject.Name
    local valueKind = valueObject:GetAttribute("ValueKind")

    if valueKind == "Unsupported" then
        warn(("Skipped unsupported backup value for %s.%s (%s)"):format(
            target:GetFullName(), propertyName, tostring(valueObject.Value)
        ))
        return
    end

    local value = valueObject.Value
    if valueKind == "EnumItem" then
        value = decodeEnum(valueObject.Value)
        if value == nil then
            warn(("Could not decode enum backup for %s.%s: %s"):format(
                target:GetFullName(), propertyName, tostring(valueObject.Value)
            ))
            return
        end
    end

    local ok, err = pcall(function()
        target[propertyName] = value
    end)
    if not ok then
        warn(("Could not restore %s.%s: %s"):format(
            target:GetFullName(), propertyName, tostring(err)
        ))
    end
end

local root = ServerStorage:FindFirstChild("_RobloxLightingBackups")
if not root then
    warn("No _RobloxLightingBackups folder exists in ServerStorage.")
    return
end

local backup
if TARGET_BACKUP_NAME then
    backup = root:FindFirstChild(TARGET_BACKUP_NAME)
    if not backup then
        warn(("Requested backup does not exist: %s"):format(TARGET_BACKUP_NAME))
        return
    end
else
    local backups = root:GetChildren()
    table.sort(backups, function(a, b)
        return a.Name > b.Name
    end)
    backup = backups[1]
end

if not backup then
    warn("No generated lighting backups were found.")
    return
end

print("Restoring Roblox lighting backup:", backup:GetFullName())

local propertiesFolder = backup:FindFirstChild("LightingProperties")
if propertiesFolder then
    for _, valueObject in propertiesFolder:GetChildren() do
        restoreProperty(Lighting, valueObject)
    end
end

local workspaceProperties = backup:FindFirstChild("WorkspaceProperties")
if workspaceProperties then
    for _, valueObject in workspaceProperties:GetChildren() do
        restoreProperty(workspace, valueObject)
    end
end

-- Remove only instances created by this skill in the current state.
for _, child in Lighting:GetChildren() do
    if child:GetAttribute(MANAGED_ATTRIBUTE) == true then
        child:Destroy()
    end
end

if Terrain then
    for _, child in Terrain:GetChildren() do
        if child:IsA("Clouds") and child:GetAttribute(MANAGED_ATTRIBUTE) == true then
            child:Destroy()
        end
    end
end

local managedLocalLights = {}
for _, descendant in workspace:GetDescendants() do
    if (descendant:IsA("PointLight") or descendant:IsA("SpotLight") or descendant:IsA("SurfaceLight"))
        and descendant:GetAttribute(MANAGED_ATTRIBUTE) == true then
        table.insert(managedLocalLights, descendant)
    end
end
for _, light in managedLocalLights do
    light:Destroy()
end

-- Restore the skill-managed state that existed before the selected apply run.
local lightingChildren = backup:FindFirstChild("LightingChildren")
if lightingChildren then
    for _, child in lightingChildren:GetChildren() do
        child:Clone().Parent = Lighting
    end
end

local terrainChildren = backup:FindFirstChild("TerrainChildren")
if Terrain and terrainChildren then
    for _, child in terrainChildren:GetChildren() do
        child:Clone().Parent = Terrain
    end
end

local workspaceLights = backup:FindFirstChild("WorkspaceManagedLights")
if workspaceLights then
    for _, savedLight in workspaceLights:GetChildren() do
        local parentPath = savedLight:GetAttribute("OriginalParentPath")
        local parent = resolvePath(parentPath)
        if parent and (parent:IsA("BasePart") or parent:IsA("Attachment")) then
            local clone = savedLight:Clone()
            clone:SetAttribute("OriginalParentPath", nil)
            clone.Parent = parent
        else
            warn(("Could not restore managed light %s because parent path is missing: %s"):format(
                savedLight.Name, tostring(parentPath)
            ))
        end
    end
end

print("Restore complete. Remove any generated camera LocalScript separately, review the scene, then save only after verification.")
