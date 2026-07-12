--!strict
-- ContextController.lua
-- Central, LIFO-safe owner for project InputContext enabled state.

export type Layer = {
    id: string,
    contexts: { string },
}

local ContextController = {}
ContextController.__index = ContextController

local function toSet(names: { string }): { [string]: boolean }
    local result = {}
    for _, name in names do
        assert(type(name) == "string" and name ~= "", "Context names must be non-empty strings")
        result[name] = true
    end
    return result
end

function ContextController.new(root: Instance)
    assert(root ~= nil, "ContextController requires an Inputs root")

    local self = setmetatable({}, ContextController)
    self._root = root
    self._contexts = {} :: { [string]: InputContext }
    self._baseContexts = {} :: { string }
    self._layers = {} :: { Layer }
    self._destroyed = false

    self:refresh()
    return self
end

function ContextController:refresh()
    assert(not self._destroyed, "ContextController is destroyed")

    table.clear(self._contexts)
    for _, descendant in self._root:GetDescendants() do
        if descendant:IsA("InputContext") then
            if self._contexts[descendant.Name] then
                error(`Duplicate InputContext name: {descendant.Name}`)
            end
            self._contexts[descendant.Name] = descendant
        end
    end
end

function ContextController:getContext(name: string): InputContext?
    return self._contexts[name]
end

function ContextController:setBaseContexts(names: { string })
    assert(not self._destroyed, "ContextController is destroyed")
    self._baseContexts = table.clone(names)
    self:_apply()
end

function ContextController:setOnlyEnabled(names: { string })
    assert(not self._destroyed, "ContextController is destroyed")
    self._baseContexts = table.clone(names)
    table.clear(self._layers)
    self:_apply()
end

function ContextController:pushLayer(id: string, contextNames: { string })
    assert(not self._destroyed, "ContextController is destroyed")
    assert(id ~= "", "Layer id must be non-empty")

    for _, layer in self._layers do
        assert(layer.id ~= id, `Context layer already exists: {id}`)
    end

    table.insert(self._layers, {
        id = id,
        contexts = table.clone(contextNames),
    })
    self:_apply()
end

function ContextController:popLayer(expectedId: string?): Layer?
    assert(not self._destroyed, "ContextController is destroyed")

    local top = self._layers[#self._layers]
    if not top then
        return nil
    end

    if expectedId and top.id ~= expectedId then
        error(`Context layer order violation: expected {expectedId}, found {top.id}`)
    end

    table.remove(self._layers, #self._layers)
    self:_apply()
    return top
end

function ContextController:clearLayers()
    assert(not self._destroyed, "ContextController is destroyed")
    table.clear(self._layers)
    self:_apply()
end

function ContextController:getLayerStack(): { Layer }
    local result = table.create(#self._layers)
    for index, layer in self._layers do
        result[index] = {
            id = layer.id,
            contexts = table.clone(layer.contexts),
        }
    end
    return result
end

function ContextController:_apply()
    local enabled = toSet(self._baseContexts)

    for _, layer in self._layers do
        for _, contextName in layer.contexts do
            enabled[contextName] = true
        end
    end

    for contextName in enabled do
        assert(self._contexts[contextName], `Unknown InputContext: {contextName}`)
    end

    for name, context in self._contexts do
        context.Enabled = enabled[name] == true
    end
end

function ContextController:destroy()
    if self._destroyed then
        return
    end

    self._destroyed = true
    table.clear(self._contexts)
    table.clear(self._baseContexts)
    table.clear(self._layers)
end

return ContextController
