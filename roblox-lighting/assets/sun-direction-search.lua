-- Roblox Lighting Director: solve ClockTime + GeographicLatitude for a target sun direction.
-- Run from Studio Command Bar. The script restores the original time/latitude before finishing.
-- TARGET_DIRECTION is the apparent unit vector from the scene toward the sun, not the direction
-- a cast shadow travels. When inferring from a ground shadow, reverse the horizontal shadow vector
-- and combine it with an estimated positive elevation before normalizing.

local Lighting = game:GetService("Lighting")

local TARGET_DIRECTION = Vector3.new(-0.55, 0.62, 0.56).Unit
local COARSE_LATITUDE_STEP = 5
local COARSE_MINUTE_STEP = 10
local REFINE_LATITUDE_RADIUS = 6
local REFINE_LATITUDE_STEP = 0.5
local REFINE_MINUTE_RADIUS = 25
local REFINE_MINUTE_STEP = 1

local originalClockTime = Lighting.ClockTime
local originalLatitude = Lighting.GeographicLatitude

local function angularError(a, b)
    local dot = math.clamp(a.Unit:Dot(b.Unit), -1, 1)
    return math.deg(math.acos(dot))
end

local best = {
    error_degrees = math.huge,
    latitude = originalLatitude,
    minutes = originalClockTime * 60,
    direction = Lighting:GetSunDirection(),
}

local function test(latitude, minutes)
    Lighting.GeographicLatitude = math.clamp(latitude, -90, 90)
    Lighting:SetMinutesAfterMidnight((minutes % 1440 + 1440) % 1440)
    local direction = Lighting:GetSunDirection()
    local errorDegrees = angularError(direction, TARGET_DIRECTION)
    if errorDegrees < best.error_degrees then
        best.error_degrees = errorDegrees
        best.latitude = Lighting.GeographicLatitude
        best.minutes = Lighting:GetMinutesAfterMidnight()
        best.direction = direction
    end
end

local ok, err = xpcall(function()
    for latitude = -90, 90, COARSE_LATITUDE_STEP do
        for minutes = 0, 1439, COARSE_MINUTE_STEP do
            test(latitude, minutes)
        end
    end

    local coarseLatitude = best.latitude
    local coarseMinutes = best.minutes
    for latitude = coarseLatitude - REFINE_LATITUDE_RADIUS, coarseLatitude + REFINE_LATITUDE_RADIUS, REFINE_LATITUDE_STEP do
        for minuteOffset = -REFINE_MINUTE_RADIUS, REFINE_MINUTE_RADIUS, REFINE_MINUTE_STEP do
            test(latitude, coarseMinutes + minuteOffset)
        end
    end
end, debug.traceback)

Lighting.ClockTime = originalClockTime
Lighting.GeographicLatitude = originalLatitude

if not ok then
    warn("[roblox-lighting] Sun-direction search failed:\n" .. tostring(err))
    return
end

local hours = math.floor(best.minutes / 60)
local minutes = math.floor(best.minutes % 60 + 0.5)
if minutes >= 60 then
    hours = (hours + 1) % 24
    minutes = 0
end

print(("[roblox-lighting] Best sun match: ClockTime ≈ %02d:%02d, GeographicLatitude ≈ %.2f, angular error ≈ %.3f°"):format(
    hours, minutes, best.latitude, best.error_degrees
))
print("[roblox-lighting] Resulting Roblox sun direction:", best.direction)
print("[roblox-lighting] Original Lighting time and latitude were restored. Apply the printed values only after visual validation.")
