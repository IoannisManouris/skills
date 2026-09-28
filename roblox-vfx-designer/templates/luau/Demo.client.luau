--!strict
-- OPTIONAL lifecycle preview. Install only in a disposable test place, as a LocalScript.
-- Modules belong in ReplicatedStorage/VFXDesignerExample/Modules (see template contract).
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local modules = ReplicatedStorage:WaitForChild("VFXDesignerExample"):WaitForChild("Modules")
local Runtime = require(modules:WaitForChild("VFXRuntime"))
local BuildImpact = require(modules:WaitForChild("BuildImpact"))
local SurfaceFrame = require(modules:WaitForChild("SurfaceFrame"))
local camera = workspace.CurrentCamera
if not camera then warn("VFX preview needs an active client camera"); return end
local folder = Instance.new("Folder")
folder.Name = "VFXDesignerDisposablePreview"
folder.Parent = workspace
local params = RaycastParams.new()
params.FilterType = Enum.RaycastFilterType.Exclude
local exclude: {Instance} = {folder}
local character = Players.LocalPlayer.Character
if character then table.insert(exclude, character) end
params.FilterDescendantsInstances = exclude
local hit = workspace:Raycast(camera.CFrame.Position, camera.CFrame.LookVector * 60, params)
if not hit then folder:Destroy(); warn("Aim at a nearby surface and rerun the preview"); return end
warn("VFX PREVIEW ONLY: default sparkle proxies, not final texture/style validation")
local rig = BuildImpact.Create({PreviewOnly = true, Dust = Color3.fromRGB(140, 125, 110)})
local ok, err = pcall(function()
	local handle = Runtime.Play(rig, {Parent = folder, CFrame = SurfaceFrame.fromRaycast(hit)})
	while not handle:IsFinished() do task.wait() end
end)
if not ok then rig:Destroy(); warn(tostring(err)) end
folder:Destroy()
