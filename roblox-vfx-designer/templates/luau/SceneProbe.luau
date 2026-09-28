--!strict
-- Read-only bounded scene hints, NOT an automatic visual-style verdict.
-- Return data locally; don't upload private scene details/screenshots to public services.
local Lighting = game:GetService("Lighting")
local SceneProbe = {}
local function rgb(c: Color3): {number} return {math.round(c.R * 255), math.round(c.G * 255), math.round(c.B * 255)} end
function SceneProbe.Inspect(root: Instance?, maxNodes: number?)
	local limit = math.clamp(math.floor(maxNodes or 600), 1, 5000)
	local queue: {Instance} = {root or workspace}
	local cursor, visited = 1, 0
	local counts: {[string]: number} = {}
	local samples = {}
	while cursor <= #queue and visited < limit do
		local item = queue[cursor]
		cursor += 1
		visited += 1
		counts[item.ClassName] = (counts[item.ClassName] or 0) + 1
		if item:IsA("BasePart") and #samples < 40 then
			table.insert(samples, { Path = item:GetFullName(), Color = rgb(item.Color), Material = item.Material.Name,
				Size = {item.Size.X, item.Size.Y, item.Size.Z}, Transparency = item.Transparency })
		end
		local skip = item == workspace.CurrentCamera or item.Name == "ClientVFX"
		if item:IsA("Model") and item:FindFirstChildOfClass("Humanoid") then skip = true end
		if not skip then
			for _, child in item:GetChildren() do
				if #queue >= limit then break end
				table.insert(queue, child)
			end
		end
	end
	local light = {}
	for _, property in {"Brightness", "ClockTime", "ExposureCompensation", "Ambient", "OutdoorAmbient", "LightingStyle"} do
		local ok, value = pcall(function() return (Lighting :: any)[property] end)
		if ok then
			light[property] = if typeof(value) == "Color3" then rgb(value) elseif typeof(value) == "EnumItem" then tostring(value) else value
		end
	end
	local camera = workspace.CurrentCamera
	return { Visited = visited, Bound = limit, PotentiallyTruncated = #queue >= limit, Classes = counts,
		PartSamples = samples, Lighting = light,
		Camera = if camera then {FOV = camera.FieldOfView, Position = {camera.CFrame.X, camera.CFrame.Y, camera.CFrame.Z}} else nil,
		Warning = "Bounded structural sample, not visibility-weighted palette. Inspect gameplay screenshots and existing effects." }
end
return SceneProbe
