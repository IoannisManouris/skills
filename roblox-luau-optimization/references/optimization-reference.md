# Roblox Luau Optimization Reference

This reference supports `SKILL.md`. Load it when the user asks for a full audit, deep optimization plan, examples, or a more detailed explanation.

## Expanded source strategy

Use official sources first. Confirm whether APIs, limits, names, and recommendations changed. Search targeted queries such as:
- "site:create.roblox.com/docs RunService PreRender performance"
- "site:create.roblox.com/docs RemoteEvent RemoteFunction UnreliableRemoteEvent buffer Roblox"
- "site:luau.org performance table.create table.clear fastcall namecall"
- "site:create.roblox.com/docs native code generation Luau Roblox"
- "site:create.roblox.com/docs Parallel Luau Actor task.desynchronize"
- "site:create.roblox.com/docs Scene Analysis memory usage Roblox"

When sources conflict, prefer current official Roblox/Luau docs.

## More detailed optimization notes

### Per-frame work

Every frame can include scripts, physics, animation, rendering, networking, replication, and resuming waiting scripts. Per-frame code has multiplicative cost: a small operation can become expensive if it runs for every player, every part, or every UI row every frame.

Common fixes:
- event-driven state updates
- dirty flags
- cached dynamic sets
- amortized/chunked processing
- lower tick rates
- client-side cosmetic work
- avoiding render-critical callbacks for non-render work

### Engine-side cost

Scripts often look cheap while causing expensive engine work. Examples include moving physical parts, changing replicated properties, parenting many objects, cloning large models, and triggering physics or rendering updates.

### Allocation and GC

Luau allocation is optimized, but temporary allocation is still not free. In hot paths, avoid building tables just to pass multiple values, repeated string concatenation, closure churn, and repeated Instance creation. Reuse scratch buffers/tables only when there are no escaping references.

### Networking

Remote design should consider frequency, payload shape, serialization, reliability, ordering, and authority. Reliable remotes are not free. Unreliable remotes are for data where the next update replaces the previous one. Server validation must never be removed for speed.

### Native code generation

Use only for hot compute-heavy server functions. It can increase memory/startup cost and not all code benefits. Code dominated by Roblox API calls usually gains less.

### Parallel Luau

Use only for partitionable CPU work. Shared mutable state, synchronization, and non-parallel-safe APIs can remove the benefit or make code unsafe.

## Benchmark harness

Use local microbenchmarks only to confirm direction in your own place and hardware. Use Script Profiler and MicroProfiler for real conclusions. Microbenchmarks can mislead when engine work, replication, or physics dominates.

```luau
local function bench(name, iterations, fn)
    for _ = 1, 200 do fn() end
    local memBefore = collectgarbage("count")
    local t0 = os.clock()
    for i = 1, iterations do
        fn(i)
    end
    local dt = os.clock() - t0
    local memAfter = collectgarbage("count")
    print(string.format("%-24s  %8.3f ms  %+8.1f KB", name, dt * 1000, memAfter - memBefore))
end
```

## Examples

Avoid one-use allocation:
```luau
for _, enemy in enemies do
    local distance = (enemy.Position - origin).Magnitude
    process(enemy, distance)
end
```

Known-size array:
```luau
local result = table.create(count)
for i = 1, count do
    result[i] = compute(i)
end
```

String accumulation:
```luau
local chunks = table.create(#lines)
for i, line in lines do
    chunks[i] = line
end
local output = table.concat(chunks, "\n")
```

Compact buffer payload:
```luau
local b = buffer.create(12)
buffer.writef32(b, 0, position.X)
buffer.writef32(b, 4, position.Y)
buffer.writef32(b, 8, position.Z)
unreliableRemote:FireServer(b)
```

Use buffer/unreliable remotes only when the data is safe to drop or arrive out of order.

Replace polling with events:
```luau
local function onCharacterAdded(character)
    local humanoid = character:WaitForChild("Humanoid")
    humanoid.HealthChanged:Connect(function(health)
        updateHealth(health)
    end)
end

if player.Character then
    onCharacterAdded(player.Character)
end
player.CharacterAdded:Connect(onCharacterAdded)
```

Cache dynamic sets:
```luau
local CollectionService = game:GetService("CollectionService")
local zones = {}

local function addZone(zone) zones[zone] = true end
local function removeZone(zone) zones[zone] = nil end

for _, zone in CollectionService:GetTagged("DamageZone") do
    addZone(zone)
end

CollectionService:GetInstanceAddedSignal("DamageZone"):Connect(addZone)
CollectionService:GetInstanceRemovedSignal("DamageZone"):Connect(removeZone)

RunService.Heartbeat:Connect(function()
    for zone in zones do
        updateZone(zone)
    end
end)
```

Clean per-player state:
```luau
local playerState = {}

Players.PlayerAdded:Connect(function(player)
    playerState[player] = { connections = {}, data = {} }
end)

Players.PlayerRemoving:Connect(function(player)
    local state = playerState[player]
    if not state then return end
    for _, connection in state.connections do
        connection:Disconnect()
    end
    playerState[player] = nil
end)
```

## Minimal cleanup utility shape

A cleanup utility should handle:
- RBXScriptConnection
- Instance
- thread
- callback function
- table with Destroy/Cleanup

```luau
local Cleaner = {}
Cleaner.__index = Cleaner

function Cleaner.new()
    return setmetatable({ _items = {} }, Cleaner)
end

function Cleaner:Add(item)
    table.insert(self._items, item)
    return item
end

function Cleaner:Cleanup()
    for i = #self._items, 1, -1 do
        local item = self._items[i]
        self._items[i] = nil
        if typeof(item) == "RBXScriptConnection" then
            item:Disconnect()
        elseif typeof(item) == "Instance" then
            item:Destroy()
        elseif type(item) == "thread" then
            task.cancel(item)
        elseif type(item) == "function" then
            item()
        elseif type(item) == "table" and item.Destroy then
            item:Destroy()
        elseif type(item) == "table" and item.Cleanup then
            item:Cleanup()
        end
    end
end

return Cleaner
```

## Optimization output template

```markdown
The likely bottleneck is [specific cause]. This is mainly [category].

I changed [specific thing] so the code now [does less work / allocates less / sends less / avoids engine churn].

[updated code]

Tradeoffs:
- [tradeoff]
- [risk]

Verify by:
1. [Profiler/tool]
2. [Metric]
3. [Before/after comparison]
```

## Guardrails

Never optimize by:
- removing server validation
- trusting client state
- moving authoritative logic to the client
- using unreliable remotes for must-arrive state
- making unreadable code without proof
- adding native everywhere
- parallelizing unsafe shared state
- ignoring cleanup
- inventing performance numbers
