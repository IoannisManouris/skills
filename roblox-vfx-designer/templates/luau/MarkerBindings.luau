--!strict
-- Bind once BEFORE track:Play(). Cosmetic callbacks only; no authoritative damage here.
local MarkerBindings = {}
function MarkerBindings.Bind(track: AnimationTrack, callbacks: {[string]: (string) -> ()}): () -> ()
	local connections: {RBXScriptConnection} = {}
	local alive = true
	local function disconnect()
		if not alive then return end
		alive = false
		for _, connection in connections do connection:Disconnect() end
		table.clear(connections)
	end
	for markerName, callback in callbacks do
		table.insert(connections, track:GetMarkerReachedSignal(markerName):Connect(function(parameter)
			if not alive then return end
			local ok, err = pcall(callback, parameter) -- Callbacks should not yield.
			if not ok then warn("VFX marker " .. markerName .. " failed: " .. tostring(err)) end
		end))
	end
	table.insert(connections, track.Stopped:Connect(disconnect))
	table.insert(connections, track.Destroying:Connect(disconnect))
	return disconnect -- Also call on ability cancellation; subsequent replay needs a fresh binding.
end
return MarkerBindings
