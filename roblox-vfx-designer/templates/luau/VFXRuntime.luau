--!strict
-- Original finite, client-only world-space VFX player. Read references/luau-templates.md.
-- Public API basis: Roblox ParticleEmitter, Beam, Trail, Light, Sound, RunService.
local RunService = game:GetService("RunService")
local VFXRuntime = {}

type Event = { at: number, order: number, run: (number) -> () }
export type Options = { Parent: Instance, CFrame: CFrame?, Release: (() -> ())? }
export type Handle = {
	Stop: (self: Handle, immediate: boolean?) -> (),
	SetCFrame: (self: Handle, frame: CFrame) -> boolean,
	IsFinished: (self: Handle) -> boolean,
}

local function numberAttribute(instance: Instance, name: string, fallback: number): number
	local value = instance:GetAttribute(name)
	if value == nil then return fallback end
	assert(typeof(value) == "number", instance:GetFullName() .. "." .. name .. " must be numeric")
	local n = value :: number
	assert(n == n and n >= 0 and n < math.huge, name .. " must be finite and nonnegative")
	return n
end

local function isLight(instance: Instance): boolean
	return instance:IsA("PointLight") or instance:IsA("SpotLight") or instance:IsA("SurfaceLight")
end

-- Only clears native histories/state. Custom mesh/tween mutations need their own reset.
function VFXRuntime.Reset(rig: Model)
	for _, item in rig:GetDescendants() do
		if item:IsA("ParticleEmitter") then
			item.Enabled = false
			item:Clear()
		elseif item:IsA("Trail") then
			item.Enabled = false
			item:Clear()
		elseif item:IsA("Beam") then
			item.Enabled = false
		elseif isLight(item) then
			(item :: Light).Enabled = false
		elseif item:IsA("Sound") then
			item:Stop()
		end
	end
end

-- Validates inert cosmetics BEFORE parenting. Does not sandbox arbitrary models.
function VFXRuntime.Prepare(rig: Model)
	assert(rig.Parent == nil, "Prepare requires an unparented, exclusively owned Model")
	local items = rig:GetDescendants()
	for _, item in items do
		assert(not item:IsA("LuaSourceContainer"), "VFX prefab must not contain scripts/modules")
		assert(not item:IsA("Explosion") and not item:IsA("ForceField"), "Gameplay-affecting instances are not allowed in this cosmetic player")
		assert(not item:IsA("Constraint") and not item:IsA("JointInstance"), "This player expects an inert anchored rig, not physics/rig joints")
	end
	for _, item in items do
		if item:IsA("BasePart") then
			item.Anchored = true
			item.CanCollide = false
			item.CanTouch = false
			item.CanQuery = false
			item.CastShadow = false
		end
	end
	VFXRuntime.Reset(rig)
end

function VFXRuntime.Play(rig: Model, options: Options): Handle
	assert(RunService:IsClient(), "VFXRuntime.Play must run on a client")
	assert(options.Parent:IsDescendantOf(workspace) or options.Parent == workspace, "Parent must be in Workspace")
	VFXRuntime.Prepare(rig)
	local events: {Event} = {}
	local drainUntil = 0
	local cursor = 1
	local elapsed = 0
	local finished = false
	local stopping = false
	local connection: RBXScriptConnection? = nil
	local particles: {ParticleEmitter} = {}
	local trails: {Trail} = {}
	local beams: {Beam} = {}
	local lights: {Light} = {}
	local sounds: {Sound} = {}

	local function add(at: number, callback: (number) -> ())
		table.insert(events, { at = at, order = #events + 1, run = callback })
	end
	local function tail(emitter: ParticleEmitter): number
		assert(emitter.TimeScale > 0, "Paused particles need a custom explicit cleanup controller")
		return emitter.Lifetime.Max / emitter.TimeScale
	end

	-- Compile the finite timeline before exposing any instance to Workspace.
	for _, item in rig:GetDescendants() do
		local delay = numberAttribute(item, "StartDelay", 0)
		if item:IsA("ParticleEmitter") then
			local emitter = item
			table.insert(particles, emitter)
			local life = tail(emitter)
			local count = numberAttribute(emitter, "BurstCount", 0)
			assert(count % 1 == 0, "BurstCount must be an integer")
			local duration = numberAttribute(emitter, "EmitDuration", 0)
			if count > 0 then
				add(delay, function(now)
					emitter:Emit(count)
					drainUntil = math.max(drainUntil, now + life)
				end)
			end
			if duration > 0 then
				assert(emitter.Rate > 0, "Timed emission requires a positive authored Rate")
				add(delay, function(_now) emitter.Enabled = true end)
				add(delay + duration, function(now)
					emitter.Enabled = false
					drainUntil = math.max(drainUntil, now + life)
				end)
			end
		elseif item:IsA("Trail") then
			local trail = item
			table.insert(trails, trail)
			local duration = numberAttribute(trail, "ActiveDuration", 0)
			if duration > 0 then
				add(delay, function(_now) trail:Clear(); trail.Enabled = true end)
				add(delay + duration, function(now)
					trail.Enabled = false
					drainUntil = math.max(drainUntil, now + trail.Lifetime)
				end)
			end
		elseif item:IsA("Beam") then
			local beam = item
			table.insert(beams, beam)
			local duration = numberAttribute(beam, "ActiveDuration", 0)
			if duration > 0 then
				add(delay, function(_now) beam.Enabled = true end)
				add(delay + duration, function(_now) beam.Enabled = false end)
			end
		elseif isLight(item) then
			local light = item :: Light
			table.insert(lights, light)
			local duration = numberAttribute(light, "ActiveDuration", 0)
			if duration > 0 then
				add(delay, function(_now) light.Enabled = true end)
				add(delay + duration, function(_now) light.Enabled = false end)
			end
		elseif item:IsA("Sound") then
			local sound = item
			table.insert(sounds, sound)
			local duration = numberAttribute(sound, "ActiveDuration", 0)
			assert(duration > 0, "Sound requires explicit ActiveDuration; no guessed loading-dependent lifetime")
			add(delay, function(_now) sound:Play() end)
			add(delay + duration, function(_now) sound:Stop() end)
		end
	end
	assert(#events > 0, "Rig has no scheduled layers; author BurstCount/EmitDuration/ActiveDuration")
	table.sort(events, function(a, b)
		if a.at == b.at then return a.order < b.order end
		return a.at < b.at
	end)

	local function finish()
		if finished then return end
		finished = true
		if connection then connection:Disconnect(); connection = nil end
		table.clear(events)
		local resetOK, resetError = pcall(function()
			VFXRuntime.Reset(rig)
			rig.Parent = nil
		end)
		if not resetOK then warn("VFX reset failed: " .. tostring(resetError)) end
		if options.Release then
			local ok, err = pcall(options.Release)
			if not ok then
				warn("VFX release failed: " .. tostring(err))
				rig:Destroy()
			end
		else
			rig:Destroy()
		end
	end

	local function tickTimeline(dt: number)
		if finished then return end
		if rig.Parent ~= options.Parent then finish(); return end
		elapsed += dt
		while cursor <= #events and events[cursor].at <= elapsed do
			local event = events[cursor]
			cursor += 1
			event.run(elapsed) -- Late frames retain a full burst tail, not a truncated one.
		end
		if cursor > #events and elapsed >= drainUntil then finish() end
	end

	local function safeTick(dt: number)
		local ok, err = pcall(tickTimeline, dt)
		if not ok then
			warn("VFX playback failed: " .. tostring(err))
			finish()
		end
	end

	local handle = {} :: Handle
	function handle:IsFinished(): boolean return finished end
	function handle:SetCFrame(frame: CFrame): boolean
		if finished then return false end
		rig:PivotTo(frame)
		return true
	end
	function handle:Stop(immediate: boolean?)
		if finished then return end
		if immediate == true then finish(); return end
		if stopping then return end
		stopping = true
		cursor = #events + 1 -- Suppress future delayed work; no task.delay callbacks survive.
		for _, emitter in particles do
			if emitter.Enabled then drainUntil = math.max(drainUntil, elapsed + tail(emitter)) end
			emitter.Enabled = false
		end
		for _, trail in trails do
			if trail.Enabled then drainUntil = math.max(drainUntil, elapsed + trail.Lifetime) end
			trail.Enabled = false
		end
		for _, beam in beams do beam.Enabled = false end
		for _, light in lights do light.Enabled = false end
		for _, sound in sounds do sound:Stop() end
		if elapsed >= drainUntil then finish() end
	end

	if options.CFrame then rig:PivotTo(options.CFrame) end
	rig.Parent = options.Parent
	connection = RunService.Heartbeat:Connect(safeTick)
	safeTick(0)
	return handle
end
return VFXRuntime
