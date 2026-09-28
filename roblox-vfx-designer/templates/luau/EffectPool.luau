--!strict
-- Bounded pool for inert models. Pair with VFXRuntime; never schedule Debris on leases.
local RunService = game:GetService("RunService")
local Runtime = require(script.Parent.VFXRuntime)
local EffectPool = {}

function EffectPool.new(template: Model, capacity: number, customReset: ((Model) -> ())?)
	assert(RunService:IsClient(), "Cosmetic pool is client-only")
	assert(capacity > 0 and capacity % 1 == 0 and capacity < math.huge, "Capacity must be a finite positive integer")
	assert(template.Archivable, "Template must be cloneable")
	local free: {Model} = {}
	local active: {[Model]: number} = {}
	local count = 0
	local serial = 0
	local closed = false
	local pool = {}

	local function reset(model: Model)
		Runtime.Reset(model)
		model.Parent = nil
		if customReset then customReset(model) end -- Must not yield; restore all custom mutations.
		Runtime.Prepare(model)
	end

	function pool:Acquire(): (Model?, (() -> boolean)?)
		if closed then return nil, nil end
		local model = table.remove(free)
		if model == nil then
			if count >= capacity then return nil, nil end -- Caller chooses optional-drop/essential fallback.
			model = template:Clone()
			count += 1
		end
		local rig = model :: Model
		local ok, err = pcall(reset, rig)
		if not ok then
			count -= 1
			rig:Destroy()
			error("Pool reset failed: " .. tostring(err))
		end
		serial += 1
		local lease = serial
		active[rig] = lease
		local function release(): boolean
			if closed or active[rig] ~= lease then return false end -- Stale/double release cannot affect a new owner.
			active[rig] = nil
			local resetOK, resetError = pcall(reset, rig)
			if not resetOK then
				count -= 1
				rig:Destroy()
				warn("Pooled rig discarded: " .. tostring(resetError))
				return false
			end
			table.insert(free, rig)
			return true
		end
		return rig, release
	end

	function pool:Stats()
		local activeCount = 0
		for _ in active do activeCount += 1 end
		return { Total = count, Free = #free, Active = activeCount, Capacity = capacity, Closed = closed }
	end

	function pool:Destroy()
		if closed then return end
		closed = true
		for rig in active do rig:Destroy() end
		for _, rig in free do rig:Destroy() end
		table.clear(active)
		table.clear(free)
		count = 0
	end
	return pool
end
return EffectPool
