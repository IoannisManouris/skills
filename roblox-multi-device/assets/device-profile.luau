--!strict
-- DeviceProfile.lua
-- Client-only presentation/capability snapshot for a multi-device Roblox experience.
-- Copy into the project and require once. Do not use this module as a security boundary.

local UserInputService = game:GetService("UserInputService")
local GuiService = game:GetService("GuiService")
local VRService = game:GetService("VRService")

export type Snapshot = {
    preferredInput: Enum.PreferredInput,
    keyboardEnabled: boolean,
    mouseEnabled: boolean,
    touchEnabled: boolean,
    gamepadEnabled: boolean,
    vrEnabled: boolean,
    displaySize: Enum.DisplaySize,
    connectedGamepads: { Enum.UserInputType },
    presentationMode: string,
}

local DeviceProfile = {}
DeviceProfile.__index = DeviceProfile

local function copyGamepads(source: { Enum.UserInputType }): { Enum.UserInputType }
    local result = table.create(#source)
    for index, gamepad in source do
        result[index] = gamepad
    end
    return result
end

local function arraysEqual(a: { Enum.UserInputType }, b: { Enum.UserInputType }): boolean
    if #a ~= #b then
        return false
    end
    for index, value in a do
        if b[index] ~= value then
            return false
        end
    end
    return true
end

local function derivePresentationMode(
    preferredInput: Enum.PreferredInput,
    vrEnabled: boolean,
    displaySize: Enum.DisplaySize
): string
    if vrEnabled then
        return "VR"
    end

    if preferredInput == Enum.PreferredInput.Touch then
        return "Touch"
    end

    if preferredInput == Enum.PreferredInput.Gamepad then
        if displaySize == Enum.DisplaySize.Large then
            return "GamepadLargeDisplay"
        end
        return "Gamepad"
    end

    return "KeyboardMouse"
end

local function makeSnapshot(): Snapshot
    local preferredInput = UserInputService.PreferredInput
    local vrEnabled = VRService.VREnabled
    local displaySize = GuiService.ViewportDisplaySize

    return {
        preferredInput = preferredInput,
        keyboardEnabled = UserInputService.KeyboardEnabled,
        mouseEnabled = UserInputService.MouseEnabled,
        touchEnabled = UserInputService.TouchEnabled,
        gamepadEnabled = UserInputService.GamepadEnabled,
        vrEnabled = vrEnabled,
        displaySize = displaySize,
        connectedGamepads = copyGamepads(UserInputService:GetConnectedGamepads()),
        presentationMode = derivePresentationMode(preferredInput, vrEnabled, displaySize),
    }
end

local function snapshotsEqual(a: Snapshot, b: Snapshot): boolean
    return a.preferredInput == b.preferredInput
        and a.keyboardEnabled == b.keyboardEnabled
        and a.mouseEnabled == b.mouseEnabled
        and a.touchEnabled == b.touchEnabled
        and a.gamepadEnabled == b.gamepadEnabled
        and a.vrEnabled == b.vrEnabled
        and a.displaySize == b.displaySize
        and a.presentationMode == b.presentationMode
        and arraysEqual(a.connectedGamepads, b.connectedGamepads)
end

function DeviceProfile.new()
    local self = setmetatable({}, DeviceProfile)

    self._destroyed = false
    self._connections = {} :: { RBXScriptConnection }
    self._changedEvent = Instance.new("BindableEvent")
    self._snapshot = makeSnapshot()

    local function refresh()
        if self._destroyed then
            return
        end

        local nextSnapshot = makeSnapshot()
        if not snapshotsEqual(self._snapshot, nextSnapshot) then
            self._snapshot = nextSnapshot
            self._changedEvent:Fire(self:getSnapshot())
        end
    end

    table.insert(self._connections, UserInputService:GetPropertyChangedSignal("PreferredInput"):Connect(refresh))
    table.insert(self._connections, UserInputService:GetPropertyChangedSignal("KeyboardEnabled"):Connect(refresh))
    table.insert(self._connections, UserInputService:GetPropertyChangedSignal("MouseEnabled"):Connect(refresh))
    table.insert(self._connections, UserInputService:GetPropertyChangedSignal("TouchEnabled"):Connect(refresh))
    table.insert(self._connections, UserInputService:GetPropertyChangedSignal("GamepadEnabled"):Connect(refresh))
    table.insert(self._connections, GuiService:GetPropertyChangedSignal("ViewportDisplaySize"):Connect(refresh))
    table.insert(self._connections, VRService:GetPropertyChangedSignal("VREnabled"):Connect(refresh))
    table.insert(self._connections, UserInputService.GamepadConnected:Connect(refresh))
    table.insert(self._connections, UserInputService.GamepadDisconnected:Connect(refresh))

    return self
end

function DeviceProfile:getSnapshot(): Snapshot
    local snapshot = self._snapshot
    return {
        preferredInput = snapshot.preferredInput,
        keyboardEnabled = snapshot.keyboardEnabled,
        mouseEnabled = snapshot.mouseEnabled,
        touchEnabled = snapshot.touchEnabled,
        gamepadEnabled = snapshot.gamepadEnabled,
        vrEnabled = snapshot.vrEnabled,
        displaySize = snapshot.displaySize,
        connectedGamepads = copyGamepads(snapshot.connectedGamepads),
        presentationMode = snapshot.presentationMode,
    }
end

function DeviceProfile:getPresentationMode(): string
    return self._snapshot.presentationMode
end

function DeviceProfile:getChangedSignal(): RBXScriptSignal
    return self._changedEvent.Event
end

function DeviceProfile:getInsetArea(screenInsets: Enum.ScreenInsets): Rect?
    -- GuiService APIs can evolve. Keep this call isolated and fail safely if unavailable.
    local ok, result = pcall(function()
        return GuiService:GetInsetArea(screenInsets)
    end)

    if not ok then
        warn("DeviceProfile: GuiService:GetInsetArea failed; verify current Roblox API", result)
        return nil
    end

    return result
end

function DeviceProfile:destroy()
    if self._destroyed then
        return
    end
    self._destroyed = true

    for _, connection in self._connections do
        connection:Disconnect()
    end
    table.clear(self._connections)
    self._changedEvent:Destroy()
end

return DeviceProfile
