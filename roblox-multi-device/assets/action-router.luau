--!strict
-- ActionRouter.lua
-- Routes semantic InputAction events to project controllers.
-- Give every action a unique ActionId attribute, or use unique InputAction names.

export type Handlers = {
    pressed: (() -> ())?,
    released: (() -> ())?,
    changed: ((value: any) -> ())?,
}

local ActionRouter = {}
ActionRouter.__index = ActionRouter

local function getActionId(action: InputAction): string
    local attribute = action:GetAttribute("ActionId")
    if type(attribute) == "string" and attribute ~= "" then
        return attribute
    end
    return action.Name
end

function ActionRouter.new(root: Instance)
    assert(root ~= nil, "ActionRouter requires an Inputs root")

    local self = setmetatable({}, ActionRouter)
    self._root = root
    self._actions = {} :: { [string]: InputAction }
    self._bindings = {} :: { [string]: { RBXScriptConnection } }
    self._destroyed = false

    self:refresh()
    return self
end

function ActionRouter:refresh()
    assert(not self._destroyed, "ActionRouter is destroyed")

    table.clear(self._actions)
    for _, descendant in self._root:GetDescendants() do
        if descendant:IsA("InputAction") then
            local id = getActionId(descendant)
            if self._actions[id] then
                error(`Duplicate semantic InputAction id: {id}`)
            end
            self._actions[id] = descendant
        end
    end
end

function ActionRouter:hasAction(actionId: string): boolean
    return self._actions[actionId] ~= nil
end

function ActionRouter:getAction(actionId: string): InputAction?
    return self._actions[actionId]
end

function ActionRouter:bind(actionId: string, handlers: Handlers): () -> ()
    assert(not self._destroyed, "ActionRouter is destroyed")
    assert(self._bindings[actionId] == nil, `Action already bound: {actionId}`)

    local action = self._actions[actionId]
    assert(action, `Unknown InputAction: {actionId}`)

    local connections = {} :: { RBXScriptConnection }

    if handlers.pressed then
        table.insert(connections, action.Pressed:Connect(handlers.pressed))
    end
    if handlers.released then
        table.insert(connections, action.Released:Connect(handlers.released))
    end
    if handlers.changed then
        table.insert(connections, action.StateChanged:Connect(handlers.changed))
    end

    assert(#connections > 0, `No handlers supplied for action: {actionId}`)
    self._bindings[actionId] = connections

    local disconnected = false
    return function()
        if disconnected then
            return
        end
        disconnected = true
        self:unbind(actionId)
    end
end

function ActionRouter:unbind(actionId: string)
    local connections = self._bindings[actionId]
    if not connections then
        return
    end

    for _, connection in connections do
        connection:Disconnect()
    end
    self._bindings[actionId] = nil
end

function ActionRouter:destroy()
    if self._destroyed then
        return
    end
    self._destroyed = true

    local ids = {}
    for actionId in self._bindings do
        table.insert(ids, actionId)
    end
    for _, actionId in ids do
        self:unbind(actionId)
    end

    table.clear(self._actions)
end

return ActionRouter
