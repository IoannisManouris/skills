--!strict
-- UIFocusController.lua
-- Owns project UI selection entry/restoration across gamepad and pointer hot-swap.
-- It does not show/hide panels or enable InputContexts; coordinate those in the modal/controller layer.

local GuiService = game:GetService("GuiService")
local UserInputService = game:GetService("UserInputService")

export type PanelEntry = {
    root: Instance,
    defaultSelection: GuiObject?,
    previousSelection: GuiObject?,
}

local UIFocusController = {}
UIFocusController.__index = UIFocusController

local function isWithin(root: Instance, object: Instance?): boolean
    return object ~= nil and (object == root or object:IsDescendantOf(root))
end

local function isUsable(candidate: GuiObject?, root: Instance): boolean
    if not candidate then
        return false
    end
    if not isWithin(root, candidate) then
        return false
    end
    if not candidate.Selectable or not candidate.Visible or not candidate.Active then
        return false
    end

    local ancestor = candidate.Parent
    while ancestor and ancestor ~= root do
        if ancestor:IsA("GuiObject") and not ancestor.Visible then
            return false
        end
        if ancestor:IsA("LayerCollector") and not ancestor.Enabled then
            return false
        end
        ancestor = ancestor.Parent
    end

    return true
end

local function firstSelectable(root: Instance): GuiObject?
    local candidates = {} :: { GuiObject }
    for _, descendant in root:GetDescendants() do
        if descendant:IsA("GuiObject") and isUsable(descendant, root) then
            table.insert(candidates, descendant)
        end
    end

    table.sort(candidates, function(a, b)
        if a.SelectionOrder ~= b.SelectionOrder then
            return a.SelectionOrder < b.SelectionOrder
        end
        if a.LayoutOrder ~= b.LayoutOrder then
            return a.LayoutOrder < b.LayoutOrder
        end
        return a:GetFullName() < b:GetFullName()
    end)

    return candidates[1]
end

function UIFocusController.new()
    local self = setmetatable({}, UIFocusController)
    self._stack = {} :: { PanelEntry }
    self._destroyed = false

    self._preferredInputConnection = UserInputService:GetPropertyChangedSignal("PreferredInput"):Connect(function()
        self:refreshForPreferredInput()
    end)

    return self
end

function UIFocusController:open(root: Instance, defaultSelection: GuiObject?)
    assert(not self._destroyed, "UIFocusController is destroyed")
    assert(root:IsA("GuiObject") or root:IsA("LayerCollector"), "UI focus root must be a GuiObject or LayerCollector")

    local entry: PanelEntry = {
        root = root,
        defaultSelection = defaultSelection,
        previousSelection = GuiService.SelectedObject,
    }

    table.insert(self._stack, entry)
    self:_focusEntry(entry)
end

function UIFocusController:close(expectedRoot: Instance?)
    assert(not self._destroyed, "UIFocusController is destroyed")

    local entry = self._stack[#self._stack]
    if not entry then
        return
    end

    if expectedRoot and entry.root ~= expectedRoot then
        error(`UI focus stack order violation: expected {expectedRoot:GetFullName()}, found {entry.root:GetFullName()}`)
    end

    table.remove(self._stack, #self._stack)

    local nextEntry = self._stack[#self._stack]
    if nextEntry then
        local restore = entry.previousSelection
        if isUsable(restore, nextEntry.root) then
            GuiService.SelectedObject = restore
        else
            self:_focusEntry(nextEntry)
        end
        return
    end

    GuiService.SelectedObject = nil
end

function UIFocusController:getCurrentRoot(): Instance?
    local entry = self._stack[#self._stack]
    return entry and entry.root or nil
end

function UIFocusController:refreshForPreferredInput()
    if self._destroyed then
        return
    end

    local entry = self._stack[#self._stack]
    if not entry then
        return
    end

    if UserInputService.PreferredInput == Enum.PreferredInput.Gamepad then
        local selected = GuiService.SelectedObject
        if not isUsable(selected, entry.root) then
            self:_focusEntry(entry)
        end
    elseif isWithin(entry.root, GuiService.SelectedObject) then
        -- Pointer/touch users should not be forced to keep a gamepad focus ring.
        GuiService.SelectedObject = nil
    end
end

function UIFocusController:ensureValidSelection()
    local entry = self._stack[#self._stack]
    if not entry then
        GuiService.SelectedObject = nil
        return
    end

    if UserInputService.PreferredInput == Enum.PreferredInput.Gamepad
        and not isUsable(GuiService.SelectedObject, entry.root)
    then
        self:_focusEntry(entry)
    end
end

function UIFocusController:_focusEntry(entry: PanelEntry)
    if UserInputService.PreferredInput ~= Enum.PreferredInput.Gamepad then
        return
    end

    local candidate = entry.defaultSelection
    if not isUsable(candidate, entry.root) then
        candidate = firstSelectable(entry.root)
    end

    GuiService.SelectedObject = candidate
end

function UIFocusController:destroy()
    if self._destroyed then
        return
    end
    self._destroyed = true

    self._preferredInputConnection:Disconnect()
    table.clear(self._stack)
    GuiService.SelectedObject = nil
end

return UIFocusController
