--!strict
-- Local +Y follows surface normal. +X/+Z are a stable orthonormal tangent basis.
local SurfaceFrame = {}
local function finite(v: Vector3): boolean
	return v.X == v.X and v.Y == v.Y and v.Z == v.Z
		and math.abs(v.X) < math.huge and math.abs(v.Y) < math.huge and math.abs(v.Z) < math.huge
end
function SurfaceFrame.fromNormal(position: Vector3, normal: Vector3, offset: number?, twist: number?): CFrame
	assert(finite(position) and finite(normal) and normal.Magnitude > 1e-6, "Expected finite position and nonzero normal")
	local bias, angle = offset or 0.025, twist or 0
	assert(bias == bias and math.abs(bias) < math.huge and angle == angle and math.abs(angle) < math.huge, "Offset/twist must be finite")
	local up = normal.Unit
	local reference = if math.abs(up.X) < 0.9 then Vector3.xAxis else Vector3.zAxis
	local right = up:Cross(reference).Unit
	local back = right:Cross(up).Unit
	return CFrame.fromMatrix(position + up * bias, right, up, back) * CFrame.Angles(0, angle, 0)
end
function SurfaceFrame.fromRaycast(result: RaycastResult, offset: number?, twist: number?): CFrame
	return SurfaceFrame.fromNormal(result.Position, result.Normal, offset, twist)
end
return SurfaceFrame
