--!strict
-- ModuleScript fixture. NOT executed during package creation.
-- require(...StudioSmokeTest).Run() from the CLIENT of a disposable Studio test place.
local RunService = game:GetService("RunService")
local Runtime = require(script.Parent.VFXRuntime)
local Pool = require(script.Parent.EffectPool)
local BuildImpact = require(script.Parent.BuildImpact)
local SurfaceFrame = require(script.Parent.SurfaceFrame)
local SmokeTest = {}
local function waitUntil(predicate: () -> boolean, timeout: number)
	local started = os.clock()
	while not predicate() do
		assert(os.clock() - started < timeout, "Smoke test timed out")
		RunService.Heartbeat:Wait()
	end
end
function SmokeTest.Run()
	assert(RunService:IsStudio() and RunService:IsClient(), "Run in a Studio CLIENT, not production or Edit mode")
	local folder = Instance.new("Folder")
	folder.Name = "VFXDesignerSmokeTest"
	folder.Parent = workspace
	local template = BuildImpact.Create({PreviewOnly = true})
	local pool = Pool.new(template, 1)
	local results = {}
	local ok, err = pcall(function()
		for _, normal in {Vector3.yAxis, -Vector3.yAxis, Vector3.xAxis, Vector3.new(1, 1, 1).Unit} do
			local frame = SurfaceFrame.fromNormal(Vector3.zero, normal)
			assert(frame.UpVector:Dot(normal) > 0.9999, "Surface +Y not aligned")
			assert(math.abs(frame.RightVector:Dot(frame.UpVector)) < 0.001, "Surface basis not orthogonal")
		end
		table.insert(results, "surface_basis")
		local rig1, release1 = pool:Acquire()
		assert(rig1 and release1, "Initial acquire failed")
		local extra = pool:Acquire()
		assert(extra == nil, "Pool exceeded capacity")
		local h1 = Runtime.Play(rig1, {Parent = folder, Release = function() release1() end})
		h1:Stop(true)
		h1:Stop(true)
		assert(pool:Stats().Active == 0 and #folder:GetChildren() == 0, "Immediate cleanup failed")
		table.insert(results, "capacity_and_double_stop")
		local rig2, release2 = pool:Acquire()
		assert(rig2 and release2, "Reacquire failed")
		assert(release1() == false and pool:Stats().Active == 1, "Old lease released current owner")
		local h2 = Runtime.Play(rig2, {Parent = folder, Release = function() release2() end})
		waitUntil(function() return h2:IsFinished() end, 3)
		assert(pool:Stats().Active == 0, "Natural tail didn't release")
		table.insert(results, "stale_lease_and_natural_tail")
		local rig3 = BuildImpact.Create({PreviewOnly = true})
		for _, item in rig3:GetDescendants() do
			if item:IsA("ParticleEmitter") then item:SetAttribute("StartDelay", 0.5) end
		end
		local h3 = Runtime.Play(rig3, {Parent = folder})
		h3:Stop(false) -- No layer has fired: should finish without waiting for future bursts.
		assert(h3:IsFinished(), "Pre-burst cancellation didn't finish")
		table.insert(results, "cancel_before_delay")
		local h4 = Runtime.Play(BuildImpact.Create({PreviewOnly = true}), {Parent = folder})
		h4:Stop(false)
		waitUntil(function() return h4:IsFinished() end, 3)
		assert(#folder:GetChildren() == 0, "Graceful cancellation leaked a rig")
		table.insert(results, "graceful_tail")
	end)
	pool:Destroy()
	template:Destroy()
	folder:Destroy()
	if not ok then error("VFX smoke test failed: " .. tostring(err)) end
	return {Passed = results, VisualQuality = "NOT_ASSESSED", DevicePerformance = "NOT_ASSESSED", Textures = "PROXIES"}
end
return SmokeTest
