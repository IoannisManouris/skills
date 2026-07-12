--!strict
-- Bootstrap.client.lua
-- Wiring example for the dependency-free templates in this skill.
-- Replace paths, context/action IDs, and callbacks with the actual project architecture.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local localPlayer = Players.LocalPlayer
local playerGui = localPlayer:WaitForChild("PlayerGui")
local inputsRoot = ReplicatedStorage:WaitForChild("Inputs")

-- Example location after copying these modules into StarterPlayerScripts/Client/Input.
local modules = script.Parent:WaitForChild("Input")
local DeviceProfile = require(modules:WaitForChild("DeviceProfile"))
local ContextController = require(modules:WaitForChild("ContextController"))
local ActionRouter = require(modules:WaitForChild("ActionRouter"))
local UIFocusController = require(modules:WaitForChild("UIFocusController"))

local deviceProfile = DeviceProfile.new()
local contextController = ContextController.new(inputsRoot)
local actionRouter = ActionRouter.new(inputsRoot)
local uiFocusController = UIFocusController.new()

contextController:setBaseContexts({ "GameplayContext" })

local cleanups = {} :: { () -> () }

local function bindIfPresent(actionId: string, handlers: {
    pressed: (() -> ())?,
    released: (() -> ())?,
    changed: ((value: any) -> ())?,
})
    if not actionRouter:hasAction(actionId) then
        warn(`Bootstrap: InputAction not found, skipping example binding: {actionId}`)
        return
    end
    table.insert(cleanups, actionRouter:bind(actionId, handlers))
end

-- Replace this with the project's InteractionController.
bindIfPresent("Interact", {
    pressed = function()
        -- interactionController:tryInteract()
        print("Interact pressed")
    end,
})

-- Replace this with the project's press/hold/release weapon controller.
bindIfPresent("PrimaryAction", {
    pressed = function()
        -- weaponController:beginPrimaryAction()
        print("PrimaryAction pressed")
    end,
    released = function()
        -- weaponController:endPrimaryAction()
        print("PrimaryAction released")
    end,
})

-- Example menu transition. Rename MainUI/Inventory and default button for the actual project.
local function findInventoryUI(): (Instance?, GuiObject?)
    local mainUI = playerGui:FindFirstChild("MainUI")
    if not mainUI then
        return nil, nil
    end

    local inventory = mainUI:FindFirstChild("Inventory", true)
    if not inventory then
        return nil, nil
    end

    local defaultSelection = inventory:FindFirstChild("DefaultSelection", true)
    if defaultSelection and not defaultSelection:IsA("GuiObject") then
        defaultSelection = nil
    end

    return inventory, defaultSelection :: GuiObject?
end

local inventoryOpen = false
local function setInventoryOpen(open: boolean)
    if inventoryOpen == open then
        return
    end

    local inventoryRoot, defaultSelection = findInventoryUI()
    if not inventoryRoot then
        warn("Bootstrap: configure the actual inventory UI path before using this example")
        return
    end

    inventoryOpen = open
    if inventoryRoot:IsA("GuiObject") then
        inventoryRoot.Visible = open
    elseif inventoryRoot:IsA("LayerCollector") then
        inventoryRoot.Enabled = open
    end

    if open then
        contextController:pushLayer("Inventory", { "MenuContext" })
        uiFocusController:open(inventoryRoot, defaultSelection)
    else
        uiFocusController:close(inventoryRoot)
        contextController:popLayer("Inventory")
    end
end

bindIfPresent("OpenInventory", {
    pressed = function()
        setInventoryOpen(not inventoryOpen)
    end,
})

bindIfPresent("MenuCancel", {
    pressed = function()
        if inventoryOpen then
            setInventoryOpen(false)
        end
    end,
})

-- Presentation updates belong here or in a dedicated Prompt/Layout controller.
local profileConnection = deviceProfile:getChangedSignal():Connect(function(snapshot)
    print("Preferred presentation mode:", snapshot.presentationMode)
    -- promptRenderer:renderAll(snapshot.preferredInput)
    -- touchControlsController:setVisible(snapshot.preferredInput == Enum.PreferredInput.Touch)
    -- responsiveLayoutController:apply(snapshot.displaySize, snapshot.presentationMode)
end)

script.Destroying:Connect(function()
    for _, cleanup in cleanups do
        cleanup()
    end
    profileConnection:Disconnect()
    uiFocusController:destroy()
    actionRouter:destroy()
    contextController:destroy()
    deviceProfile:destroy()
end)
