--!strict
-- An ORIGINAL small three-layer example, not a universal high-quality style preset.
-- Supply approved uploaded IMAGE content IDs, not URLs/Decal IDs guessed from a page.
local BuildImpact = {}
export type Config = {
	Textures: {[string]: string}?,
	Accent: Color3?,
	Dust: Color3?,
	Scale: number?,
	PreviewOnly: boolean?,
}
local function textureFor(emitter: ParticleEmitter, role: string, config: Config)
	local id = if config.Textures then config.Textures[role] else nil
	if id ~= nil then
		assert(string.match(id, "^rbxassetid://[1-9]%d*$") ~= nil, "Texture needs an actual verified image content ID for " .. role)
		emitter.Texture = id -- Syntactic validation only. Agent must verify permissions/rendering separately.
	else
		assert(config.PreviewOnly == true, "Missing uploaded texture for " .. role)
		emitter:SetAttribute("ProxyTexture", true) -- Leaves built-in default sparkle: lifecycle preview ONLY.
	end
end
function BuildImpact.Create(config: Config): Model
	local scale = config.Scale or 1
	assert(scale > 0 and scale < math.huge, "Scale must be finite and positive")
	local model = Instance.new("Model")
	model.Name = "VFX_ImpactExample"
	model:SetAttribute("PreviewOnly", config.PreviewOnly == true)
	local root = Instance.new("Part")
	root.Name = "Anchor"
	root.Size = Vector3.one * 0.1
	root.Transparency = 1
	root.Anchored = true
	root.CanCollide = false
	root.CanTouch = false
	root.CanQuery = false
	root.CastShadow = false
	root.Parent = model
	model.PrimaryPart = root
	local attachment = Instance.new("Attachment")
	attachment.Name = "SurfaceOrigin"
	attachment.Parent = root

	local function layer(name: string, role: string, count: number, delay: number): ParticleEmitter
		local emitter = Instance.new("ParticleEmitter")
		emitter.Name = name
		emitter.Enabled = false
		emitter.Rate = 0
		emitter.EmissionDirection = Enum.NormalId.Top
		emitter.LockedToPart = false
		emitter:SetAttribute("BurstCount", count)
		emitter:SetAttribute("StartDelay", delay)
		textureFor(emitter, role, config)
		emitter.Parent = attachment
		return emitter
	end
	local ok, err = pcall(function()
		local flash = layer("ContactFlash", "flash", 1, 0)
		flash.Lifetime = NumberRange.new(0.10)
		flash.Speed = NumberRange.new(0)
		flash.LightEmission = 0.8
		flash.LightInfluence = 0
		flash.Color = ColorSequence.new(config.Accent or Color3.fromRGB(255, 218, 145))
		flash.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.2 * scale), NumberSequenceKeypoint.new(1, 2.1 * scale)})
		flash.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.1), NumberSequenceKeypoint.new(1, 1)})

		local sparks = layer("DirectedSparks", "spark", 8, 0)
		sparks.Lifetime = NumberRange.new(0.16, 0.28)
		sparks.Speed = NumberRange.new(5 * scale, 11 * scale)
		sparks.SpreadAngle = Vector2.new(70, 70)
		sparks.Drag = 4
		sparks.LightEmission = 0.7
		sparks.Color = flash.Color
		sparks.Size = NumberSequence.new(0.13 * scale)
		sparks.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(0.45, 0.1), NumberSequenceKeypoint.new(1, 1)})

		local dust = layer("MaterialDust", "smoke", 5, 0.025)
		dust.Lifetime = NumberRange.new(0.35, 0.6)
		dust.Speed = NumberRange.new(1 * scale, 4 * scale)
		dust.SpreadAngle = Vector2.new(85, 85)
		dust.Drag = 5
		dust.Rotation = NumberRange.new(0, 360)
		dust.RotSpeed = NumberRange.new(-20, 20)
		dust.LightEmission = 0
		dust.LightInfluence = 0.7
		dust.Color = ColorSequence.new(config.Dust or Color3.fromRGB(135, 123, 102))
		dust.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.35 * scale), NumberSequenceKeypoint.new(0.3, 1.0 * scale), NumberSequenceKeypoint.new(1, 1.5 * scale)})
		dust.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.8), NumberSequenceKeypoint.new(0.15, 0.48), NumberSequenceKeypoint.new(1, 1)})
	end)
	if not ok then model:Destroy(); error(err) end
	return model
end
return BuildImpact
