# Luau Performance Optimization Skill for Roblox

## Purpose

Use this skill when reviewing, generating, refactoring, profiling, or optimizing Luau code for Roblox Studio experiences.

This skill is designed for an AI coding assistant such as Codex. Its job is to improve performance without breaking behavior. It focuses on Roblox/Luau optimization in the real engine, not generic Lua folklore.

## When to use this skill

Use this skill when the user asks for any of the following:

- optimize Luau code
- reduce lag, stutter, CPU usage, memory usage, or networking load
- improve server performance or client FPS
- audit Roblox scripts for performance problems
- refactor per-frame logic
- reduce memory leaks or garbage collection pressure
- optimize RemoteEvents, RemoteFunctions, or UnreliableRemoteEvents
- improve large-world or high-instance-count Roblox experiences
- decide whether to use Parallel Luau, Actors, buffers, or native code generation
- diagnose performance issues in Roblox Studio or a live Roblox game

Do not use this skill as a reason to rewrite working code unnecessarily. Preserve behavior first.

---

## Mandatory freshness check

Before applying specific optimization advice, perform a quick web research check for the relevant technique.

Prioritize sources in this order:

1. Roblox Creator Hub documentation
2. Roblox Creator Docs GitHub repository
3. Official Luau documentation
4. Official Luau GitHub repository and release notes
5. Roblox engineering posts and official Roblox DevForum announcements
6. High-quality community benchmarks or investigations, only when they do not conflict with official sources

Reliable starting points:

- Luau performance guide: https://luau.org/performance/
- Luau releases: https://github.com/luau-lang/luau/releases
- Roblox performance optimization: https://create.roblox.com/docs/performance-optimization
- Identify performance issues: https://create.roblox.com/docs/performance-optimization/identify
- Improve performance: https://create.roblox.com/docs/performance-optimization/improve
- MicroProfiler: https://create.roblox.com/docs/performance-optimization/microprofiler
- Script Profiler: https://create.roblox.com/docs/studio/optimization/scriptprofiler
- Memory usage: https://create.roblox.com/docs/studio/optimization/memory-usage
- Scene Analysis: https://create.roblox.com/docs/performance-optimization/scene-analysis
- Task scheduler: https://create.roblox.com/docs/scripting/scheduler
- RunService: https://create.roblox.com/docs/reference/engine/classes/RunService
- Remote events and callbacks: https://create.roblox.com/docs/scripting/events/remote
- RemoteEvent: https://create.roblox.com/docs/reference/engine/classes/RemoteEvent
- UnreliableRemoteEvent: https://create.roblox.com/docs/reference/engine/classes/UnreliableRemoteEvent
- buffer library: https://create.roblox.com/docs/reference/engine/libraries/buffer
- Parallel Luau: https://create.roblox.com/docs/scripting/multithreading
- Actor: https://create.roblox.com/docs/reference/engine/classes/Actor
- Native code generation: https://create.roblox.com/docs/luau/native-code-gen
- Instance streaming: https://create.roblox.com/docs/workspace/streaming

If web access is unavailable, state that the latest guidance could not be verified and proceed using the most recent known official Roblox/Luau guidance.

Do not trust old Lua optimization advice unless current Luau/Roblox sources still support it.

---

## Core optimization principle

Prioritize optimizations in this order:

1. Reduce work done every frame.
2. Reduce engine work caused by scripts.
3. Reduce replication, physics, rendering, and instance churn.
4. Reduce allocations and memory leaks.
5. Fix poor algorithms and bad data structures.
6. Optimize Luau hot paths only after profiling identifies them.
7. Use buffers, native code generation, or Parallel Luau only when the workload actually fits.

The biggest Roblox performance wins usually come from removing unnecessary engine work, not from tiny syntax tricks.

---

## Biggest Roblox performance drains

### 1. Too much work every frame

Be highly suspicious of code connected to:

- `RunService.PreRender`
- `RunService.RenderStepped`
- `RunService.PreAnimation`
- `RunService.PreSimulation`
- `RunService.PostSimulation`
- `RunService.Heartbeat`
- custom per-frame loops
- `while true do ... task.wait()` polling loops
- frequent `workspace:GetDescendants()` scans
- frequent `CollectionService:GetTagged()` scans
- loops over all players, all characters, all parts, or all UI objects every frame

Why it hurts:

- Roblox frames also include input, physics, animation, networking, rendering, and waiting script resumption.
- `PreRender` / render-step work is especially dangerous because rendering cannot proceed until the callback finishes.
- Server CPU above a 60 FPS frame budget can reduce simulation rate and responsiveness.

Best fixes:

- Replace polling with event-driven updates.
- Cache lists and update caches when instances are added/removed.
- Chunk expensive work across frames.
- Reduce frequency from every frame to every 0.1, 0.25, 0.5, or 1 second when possible.
- Move visual-only work to clients.
- Move non-render-critical work out of `PreRender`.
- Profile before and after.

### 2. Excessive engine work

Scripts can be cheap themselves but trigger expensive engine work.

Watch for:

- creating/destroying many Instances repeatedly
- changing many properties every frame
- moving many unanchored parts
- manually animating large part assemblies
- overusing physics constraints
- excessive collision checks
- large numbers of touching parts
- frequent parenting/reparenting
- cloning large models during gameplay
- frequent attribute/value changes that replicate
- many active particle emitters, beams, trails, sounds, animations, or UI updates

Best fixes:

- Pool reusable Instances only when safe and simpler than recreation.
- Use fewer parts and fewer replicated objects.
- Anchor objects when they do not need physics.
- Disable collisions/touch/query where not needed.
- Use collision groups.
- Avoid changing replicated properties at high frequency.
- Use client-side visual effects for cosmetics.
- Use Animator/Animation systems where appropriate instead of manual per-part animation.

### 3. High instance count and large dynamic worlds

Each Instance has memory and replication cost.

Watch for:

- huge always-loaded worlds
- thousands of small parts where meshes/unions/fewer parts would work
- many nested folders and value objects
- many BillboardGuis/SurfaceGuis
- many invisible helper parts
- many duplicated scripts
- excessive constraints, attachments, particles, or sounds

Best fixes:

- Use Scene Analysis.
- Reduce Instance count.
- Use workspace streaming for large worlds.
- Store data in Luau tables instead of Instances when it does not need to exist in the DataModel.
- Prefer attributes or tables over many ValueBase objects when appropriate.
- Avoid putting runtime-only data in replicated containers.

### 4. Allocation churn and garbage collection pressure

Luau allocation is optimized, but allocation is not free.

Watch for hot loops that create:

- tables
- closures/functions
- strings through concatenation
- temporary Vector3/CFrame-heavy structures
- Instances
- arrays/maps that are immediately discarded
- large JSON strings
- buffers that could be reused
- per-frame event connections

Best fixes:

- Reuse scratch tables only when references do not escape.
- Use `table.clear(t)` for reusable tables.
- Use `table.create(n)` when size is known.
- Avoid temporary tables in hot loops.
- Avoid creating closures inside hot loops.
- Avoid unbounded caches.
- Clean up per-player/per-object state.
- Disconnect connections or use cleanup utilities.

### 5. Memory leaks

Common leak sources:

- event connections that are never disconnected
- tables keyed by Player, Character, Tool, Instance, or userId that are never cleared
- references to destroyed Instances
- callbacks retaining large tables through closures
- ModuleScript singletons storing stale state
- per-player tasks/coroutines still running after leave
- animation tracks, sounds, particles, effects, and UI not cleaned up
- caches with no size limit or expiry
- promises/threads that never resolve or cancel
- Maid/Janitor/Trove not used for objects with lifetimes

Best fixes:

- Add explicit cleanup on `PlayerRemoving`.
- Add explicit cleanup when character/object is destroyed.
- Use weak tables only when you fully understand the ownership model.
- Use a cleanup pattern for connections, threads, Instances, and state.
- Verify with Developer Console Memory, Luau Heap, Scene Analysis, and live analytics.

### 6. Network misuse

Networking cost includes bandwidth, serialization, reliability, ordering, rate limits, and yielding behavior.

Watch for:

- RemoteEvents fired every frame per player
- large payloads
- sending full state when deltas would work
- sending tables with mixed keys or complex nested structures
- RemoteFunctions used for fire-and-forget updates
- server invoking clients and waiting on them
- client sending authoritative state
- multiple remotes where one batched message would work
- reliable remotes used for high-rate ephemeral data

Best fixes:

- Use `RemoteEvent` when no response is required.
- Use `RemoteFunction` only for true request/response logic.
- Avoid `RemoteFunction:InvokeClient()` unless absolutely necessary.
- Use `UnreliableRemoteEvent` only for transient, non-authoritative, continuously changing data.
- Batch small updates.
- Send deltas instead of full snapshots.
- Compress/quantize numeric data where appropriate.
- Use `buffer` for compact binary payloads when useful.
- Keep server authoritative.
- Rate-limit and validate client remotes.

### 7. Poor algorithms

Do not optimize syntax before fixing algorithmic cost.

Watch for:

- O(n²) loops over players/parts/items
- repeated sorting
- repeated full-table scans
- repeated `FindFirstChild` lookups in loops
- repeated raycasts where cached results/events would work
- repeated pathfinding
- recalculating static data every frame
- scanning Workspace repeatedly
- deep nested loops over all game objects

Best fixes:

- Cache lookups.
- Maintain indexes/maps.
- Use dictionaries for membership checks.
- Use spatial partitioning for proximity checks.
- Use CollectionService tags carefully with cached sets.
- Avoid sorting every frame.
- Precompute static data.
- Use dirty flags: update only when something changes.

---

## Profiling workflow

When asked to optimize code, follow this workflow:

1. Ask what symptom exists, if not obvious:
   - FPS drop
   - server lag
   - high ping
   - delayed input
   - memory growth
   - long loading
   - random stutter
   - mobile-specific lag
2. Classify the issue:
   - compute/frame time
   - memory/leak
   - load time
   - networking
   - physics
   - rendering/UI
   - replication
3. Recommend the right tool:
   - Developer Console for general live stats
   - Script Profiler for Luau CPU hotspots
   - MicroProfiler for engine frame timeline
   - Memory / Luau Heap for memory growth
   - Scene Analysis for instances, scripts, animations, audio, and unparented instances
   - Performance dashboard for production regressions
4. Identify the dominant cost.
5. Fix the highest-level cause first.
6. Make the smallest safe behavior-preserving change.
7. Add instrumentation if needed.
8. Re-profile and compare.

Do not claim an optimization worked without measurement unless it is a clear bug or obviously lower complexity.

---

## Decision tree

### If FPS is low or stuttering

1. Use MicroProfiler.
2. If scripts dominate, use Script Profiler.
3. If render/graphics dominate, reduce visual complexity, UI churn, particles, effects, and visible objects.
4. If physics dominates, reduce unanchored assemblies, constraints, collisions, touching parts, and simulation complexity.
5. If replication/networking dominates, reduce replicated changes and payload frequency.
6. If GC spikes dominate, reduce allocation churn and leaks.

### If server CPU is high

1. Check whether CPU time exceeds frame budget.
2. Use Script Profiler for Luau hot spots.
3. Look for per-frame server loops and O(n²) algorithms.
4. Move cosmetic/client-only work to the client.
5. Reduce physics and replication work.
6. If server CPU is high but CPU core usage is low, consider Parallel Luau/Actors.
7. If a compute-dense hot function dominates, consider native code generation.

### If memory grows over time

1. Use Developer Console Memory and Luau Heap.
2. Use Scene Analysis.
3. Look for retained players, characters, tools, UI, effects, animation tracks, sounds, and connections.
4. Check unbounded tables and caches.
5. Check closures retaining large state.
6. Add explicit cleanup.
7. Test player leave/rejoin, character death, round restart, and teleport paths.

### If networking is bad

1. Inspect remote frequency and payload size.
2. Remove unnecessary round trips.
3. Replace `RemoteFunction` with `RemoteEvent` where no response is needed.
4. Batch messages.
5. Send deltas.
6. Quantize numeric data.
7. Use `UnreliableRemoteEvent` only for ephemeral data.
8. Use `buffer` only when it improves clarity, size, or throughput.

### If loading is slow

1. Reduce initial replicated Instances.
2. Use streaming for large worlds.
3. Avoid cloning huge systems on join.
4. Lazy-load optional systems.
5. Preload only assets that are needed soon.
6. Move non-critical initialization after spawn.
7. Split work across frames.

---

## Luau-specific guidance

### Modern Luau optimization myths to avoid

Do not blindly recommend these old Lua tricks:

- caching every global into a local
- localizing every `math.*`, `table.*`, or `string.*` call everywhere
- caching Roblox Instance methods into locals
- assuming numeric `for i = 1, #t` loops are always fastest
- caching `#t` everywhere
- replacing readable code with obscure micro-optimizations without profiling

Modern Luau already optimizes many common patterns:

- global library chains in pure environments
- built-in calls through fastcalls
- method calls through namecall optimization
- table iteration
- table length in many practical cases
- table literals and predictable table shapes

Use micro-optimizations only in measured hot paths.

### Pure environments

Avoid in performance-sensitive code:

```luau
getfenv()
setfenv()
loadstring()
```

These can deoptimize environment/global optimizations and make code harder to reason about.

### Calls

Prefer:

```luau
object:Method(arg)
```

Avoid:

```luau
object.Method(object, arg)
```

Do not cache Roblox Instance methods in locals as a default optimization.

For direct Luau builtins in very hot loops, direct builtin forms may help:

```luau
local b = string.byte(s, i)
```

This can be better than:

```luau
local b = s:byte(i)
```

Only prioritize this in hot loops.

### Iteration

For Luau-only code, prefer generalized iteration when semantics fit:

```luau
for key, value in dictionary do
    -- ...
end

for index, value in array do
    -- ...
end
```

Use `ipairs` when you specifically need its array/nil-stop semantics.

Use numeric loops when you need the index, custom stepping, reverse order, or mutation-sensitive logic.

Do not rewrite iteration style solely for performance unless profiling justifies it.

### Tables

For object-like records, create all fields in the literal:

```luau
local point = {
    x = 1,
    y = 2,
    z = 3,
}
```

Avoid gradual hot-path construction:

```luau
local point = {}
point.x = 1
point.y = 2
point.z = 3
```

For known-size arrays:

```luau
local result = table.create(count)

for i = 1, count do
    result[i] = compute(i)
end
```

For reusable scratch tables:

```luau
local scratch = {}

local function useScratch()
    table.clear(scratch)

    scratch.a = 1
    scratch.b = 2

    -- Use internally only.
    -- Do not return scratch if it will be reused.
end
```

Only reuse tables when references do not escape.

Bad reuse example:

```luau
local scratch = {}

local function build()
    table.clear(scratch)
    scratch.value = math.random()
    return scratch -- dangerous if caller stores it
end
```

### Metatables

Avoid deep `__index` chains in hot code.

Prefer:

```luau
local Methods = {}

local Object = {}
Object.__index = Methods
```

Avoid:

- `__index` functions in hot access paths
- inheritance chains with many levels
- dynamic metatable changes
- proxy tables for every access in hot paths

### Closures

Avoid creating functions repeatedly inside hot loops:

```luau
-- Bad in hot loop
for _, item in items do
    button.Activated:Connect(function()
        use(item)
    end)
end
```

This may be valid for UI setup, but not for constantly repeated runtime logic.

Prefer stable functions or explicit dispatch when possible.

Watch for mutable captured locals in performance-sensitive closure-heavy code.

### Strings

Watch for repeated string concatenation in loops:

```luau
local s = ""

for _, part in parts do
    s ..= part.Name
end
```

Prefer array accumulation and `table.concat` for large concatenations:

```luau
local chunks = table.create(#parts)

for i, part in parts do
    chunks[i] = part.Name
end

local s = table.concat(chunks)
```

### Buffers

Use `buffer` when you need compact binary/numeric data, especially for networking or dense numeric payloads.

Good candidates:

- positions
- rotations
- velocities
- input snapshots
- projectile snapshots
- compact level data
- packed booleans/flags
- quantized numeric arrays
- large binary-like data

Bad candidates:

- normal business logic tables
- small one-off messages
- data where readability matters more than compactness
- authoritative state that needs schema clarity and validation

Example:

```luau
local b = buffer.create(12)
buffer.writef32(b, 0, position.X)
buffer.writef32(b, 4, position.Y)
buffer.writef32(b, 8, position.Z)

remote:FireServer(b)
```

---

## Roblox scheduling guidance

Prefer modern task APIs:

```luau
task.defer(fn)
task.spawn(fn)
task.delay(seconds, fn)
task.wait(seconds)
```

Avoid legacy APIs in new code:

```luau
spawn(fn)
delay(seconds, fn)
wait(seconds)
```

Use `task.defer` when the work should run soon but not immediately.

Use `task.spawn` when you intentionally want to start a new scheduled thread.

Use `task.delay` for delayed execution.

Use `task.wait` for frame-aware yielding.

Do not use task APIs to hide expensive work. If too much work is spawned, it is still too much work.

### Chunking expensive work

Use chunking when work does not need to finish in one frame:

```luau
local function processInChunks(items, chunkSize)
    local i = 1

    while i <= #items do
        local stop = math.min(i + chunkSize - 1, #items)

        for j = i, stop do
            process(items[j])
        end

        i = stop + 1
        task.wait()
    end
end
```

Use `debug.profilebegin()` and `debug.profileend()` for labeled MicroProfiler regions:

```luau
debug.profilebegin("ProcessInventory")

processInventory(player)

debug.profileend()
```

---

## RunService guidance

### `PreRender` / `RenderStepped`

Use only for visual work that must happen before rendering.

Avoid:

- expensive loops
- networking
- server communication
- pathfinding
- large table allocation
- physics-heavy logic
- scanning the world
- UI rebuilds every frame

### `PreSimulation`

Use only for logic that must happen before physics simulation.

Good for:

- setting forces/velocities before physics
- physics-prep logic

Avoid expensive logic.

### `PostSimulation`

Use for logic that depends on physics results.

### `Heartbeat`

Runs after physics and is commonly used for periodic updates.

Still avoid expensive every-frame loops. Prefer event-driven logic or lower-frequency timers.

---

## Networking guidance

### RemoteEvent

Use for asynchronous one-way communication.

Good:

```luau
RemoteEvent:FireClient(player, "HealthChanged", health)
RemoteEvent:FireServer("UseAbility", abilityId)
```

Bad:

```luau
-- firing every frame with large payloads
RemoteEvent:FireServer(hugeStateTable)
```

### RemoteFunction

Use only when a response is actually required.

Avoid:

```luau
-- Bad if no return value is needed
local result = RemoteFunction:InvokeClient(player, data)
```

Server-to-client `InvokeClient` is especially risky because a client may error, delay forever, or never return.

Prefer request/response over RemoteEvents with timeout handling when robustness matters.

### UnreliableRemoteEvent

Use only for data where dropped or out-of-order messages are acceptable.

Good uses:

- aim direction
- camera look direction
- cosmetic trails
- non-authoritative projectile visuals
- temporary animation state
- high-frequency input snapshots when newer data replaces older data

Bad uses:

- purchases
- inventory
- currency
- damage
- round results
- save data
- authoritative movement corrections
- unlocks
- anything that must arrive exactly once

Keep payloads small and within documented limits.

### Payload design

Prefer:

```luau
remote:FireClient(player, {
    t = "Damage",
    id = targetId,
    amount = amount,
})
```

For high-volume systems, consider compact positional arrays or buffers:

```luau
remote:FireClient(player, targetId, amount)
```

Avoid sending entire Instances or huge nested tables when small IDs/deltas work.

Validate all client data on the server.

---

## Native code generation guidance

Native code generation can compile Luau directly to machine code for server-side scripts.

Consider `--!native` or `@native` only when:

- profiling shows a hot compute-heavy function
- the function runs many times
- the function does math-heavy work
- the function works with numbers, arrays, vectors, or buffers
- the code is server-side
- the code is not dominated by Roblox API calls

Good candidate:

```luau
--!native

local function dot(a: Vector3, b: Vector3): number
    return a.X * b.X + a.Y * b.Y + a.Z * b.Z
end
```

Bad candidates:

- UI scripts
- scripts dominated by Instance property access
- scripts dominated by events/remotes
- one-time initialization
- code that is not hot
- tiny scripts where compile/memory tradeoffs are not worth it

Prefer type annotations for native hot functions.

Do not add `--!native` everywhere.

Always mention tradeoffs:

- native compilation can increase memory usage
- native compilation can increase startup/compile cost
- not all code benefits
- code-size limits may apply
- profiling is required

---

## Parallel Luau / Actor guidance

Parallel Luau can improve performance when work can be safely split across threads.

Consider Parallel Luau when:

- server CPU time is high
- CPU core usage is low
- the task is CPU-heavy
- work can be partitioned into independent chunks
- the code can obey parallel safety rules
- shared mutable state can be avoided or carefully synchronized

Good candidates:

- independent NPC perception calculations
- independent spatial queries when APIs are parallel-safe
- expensive math over independent data
- large independent simulation chunks
- terrain/level analysis
- batch computation not requiring shared mutation

Bad candidates:

- tiny tasks
- heavily shared mutable state
- code that constantly synchronizes back to serial
- code dominated by non-parallel-safe API calls
- UI code
- remote handling that must mutate shared game state immediately

Use Actors to partition parallel work.

Be careful with:

- `task.desynchronize()`
- `task.synchronize()`
- Actor messaging
- SharedTable usage
- API parallel-safety tags
- serial/parallel transition overhead

Do not recommend Parallel Luau as a first fix for simple performance issues.

---

## UI performance guidance

Watch for:

- rebuilding UI every frame
- creating/destroying many UI objects
- updating text every frame unnecessarily
- many animated gradients/strokes
- many SurfaceGuis/BillboardGuis in 3D
- expensive layout recalculation
- frequent AutomaticSize changes
- too many nested UI objects
- viewport frames with complex models

Best fixes:

- update UI only when data changes
- pool UI rows/cards for scrolling lists
- virtualize long lists
- throttle frequently changing labels
- avoid full UI rebuilds
- reduce SurfaceGui/BillboardGui count
- avoid expensive per-frame text changes

---

## Physics performance guidance

Watch for:

- many unanchored parts
- many constraints
- complex assemblies
- high-speed physics interactions
- large numbers of collisions/touches
- `Touched` connections on many parts
- frequent network ownership changes
- physics-based projectiles when raycasts would work
- unnecessary CanCollide/CanTouch/CanQuery enabled

Best fixes:

- anchor static parts
- disable `CanTouch` where touch events are not needed
- disable `CanQuery` where raycasts/spatial queries do not need the object
- use collision groups
- simplify assemblies
- use raycasts for simple projectile/hit detection
- reduce constraints
- reduce moving physical parts
- keep server authoritative where needed

---

## Instance and replication guidance

Do not use Instances as data containers when tables are enough.

Avoid:

```luau
local value = Instance.new("IntValue")
value.Name = "Coins"
value.Value = coins
value.Parent = player
```

For internal server-only data, prefer:

```luau
playerData[player] = {
    coins = coins,
}
```

Use Instances/Attributes/ValueObjects only when:

- the data needs to replicate
- Studio visibility is useful
- other engine systems need it
- designers need to configure it
- attributes are more convenient and update frequency is low

Avoid high-frequency replicated property or attribute changes.

---

## Cleanup pattern

When creating temporary objects, connections, or tasks, ensure cleanup.

Example pattern:

```luau
local Cleaner = {}
Cleaner.__index = Cleaner

function Cleaner.new()
    return setmetatable({
        _items = {},
    }, Cleaner)
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

Use a robust existing Maid/Janitor/Trove-style utility if the project already has one.

---

## Code review checklist

When reviewing Luau code for performance, check:

### Frame path

- Is this code running every frame?
- Does it need to run every frame?
- Can it be event-driven?
- Can it run at lower frequency?
- Can it be chunked?

### Algorithm

- Is there an O(n²) loop?
- Is it scanning Workspace repeatedly?
- Is it sorting repeatedly?
- Is it recalculating static data?
- Can a map/index/cache reduce work?

### Allocation

- Does it create tables in a hot loop?
- Does it create closures in a hot loop?
- Does it create Instances during gameplay repeatedly?
- Does it concatenate strings in a loop?
- Can scratch data be reused safely?

### Memory

- Are connections cleaned up?
- Is per-player state removed?
- Are destroyed Instances still referenced?
- Are caches bounded?
- Are tasks cancelled?
- Are animation tracks/sounds/effects cleaned up?

### Networking

- Is a RemoteFunction being used unnecessarily?
- Is a RemoteEvent fired too often?
- Is data batched?
- Are deltas used instead of snapshots?
- Is payload size reasonable?
- Is unreliable networking only used for safe ephemeral state?
- Is the server validating everything?

### Roblox engine work

- Is the script causing physics work?
- Is it changing many replicated properties?
- Is it cloning/destroying large models?
- Is it creating too many Instances?
- Is streaming appropriate?

### Advanced options

- Is this compute-dense enough for native code generation?
- Is this parallel-safe and large enough for Parallel Luau?
- Are buffers appropriate for this data?

---

## Optimization anti-patterns to flag

Flag these strongly:

- giant `Heartbeat` loops over many Instances
- expensive `PreRender` / `RenderStepped` callbacks
- frequent `workspace:GetDescendants()` in runtime loops
- frequent full-table scans where an index would work
- repeated `FindFirstChild` in hot loops
- `RemoteFunction` for fire-and-forget updates
- `InvokeClient` without timeout/failure design
- reliable remotes for high-rate cosmetic state
- unreliable remotes for authoritative state
- creating/destroying Instances every frame
- creating event connections inside repeated loops without cleanup
- unbounded caches
- storing Player/Character references forever
- many ValueObjects for internal data
- using old `wait()` / `spawn()` in new code
- blindly adding `--!native` everywhere
- recommending old Lua folklore without profiling evidence

---

## Safe refactoring rules

When modifying code:

1. Preserve behavior first.
2. Keep public APIs compatible unless the user approves breaking changes.
3. Avoid changing networking authority unless explicitly requested.
4. Avoid weakening server validation.
5. Avoid moving authoritative logic to the client.
6. Avoid optimizing by making code unreadable unless the path is truly hot.
7. Add comments only where they clarify non-obvious performance decisions.
8. Prefer small, measurable changes.
9. Include before/after explanation.
10. Recommend profiling after changes.

---

## Common optimization recipes

### Replace polling with events

Bad:

```luau
while true do
    if player.Character and player.Character:FindFirstChild("Humanoid") then
        updateHealth(player.Character.Humanoid.Health)
    end

    task.wait()
end
```

Better:

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

### Cache a dynamic set

Bad:

```luau
RunService.Heartbeat:Connect(function()
    for _, inst in workspace:GetDescendants() do
        if inst:GetAttribute("DamageZone") then
            updateZone(inst)
        end
    end
end)
```

Better:

```luau
local CollectionService = game:GetService("CollectionService")

local zones = {}

local function addZone(zone)
    zones[zone] = true
end

local function removeZone(zone)
    zones[zone] = nil
end

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

### Lower update frequency

Bad:

```luau
RunService.Heartbeat:Connect(function()
    updateLeaderboard()
end)
```

Better:

```luau
task.spawn(function()
    while true do
        updateLeaderboard()
        task.wait(5)
    end
end)
```

### Batch network updates

Bad:

```luau
for _, item in changedItems do
    remote:FireClient(player, "ItemChanged", item.id, item.value)
end
```

Better:

```luau
local payload = table.create(#changedItems)

for i, item in changedItems do
    payload[i] = {
        id = item.id,
        value = item.value,
    }
end

remote:FireClient(player, "ItemsChanged", payload)
```

### Use deltas instead of snapshots

Bad:

```luau
remote:FireClient(player, fullInventory)
```

Better:

```luau
remote:FireClient(player, {
    added = addedItems,
    removed = removedItemIds,
    changed = changedItems,
})
```

### Avoid string concatenation loops

Bad:

```luau
local output = ""

for _, line in lines do
    output ..= line .. "\n"
end
```

Better:

```luau
local chunks = table.create(#lines)

for i, line in lines do
    chunks[i] = line
end

local output = table.concat(chunks, "\n")
```

### Avoid table allocation in hot loop

Bad:

```luau
for _, enemy in enemies do
    local data = {
        distance = (enemy.Position - origin).Magnitude,
        enemy = enemy,
    }

    process(data)
end
```

Better:

```luau
for _, enemy in enemies do
    local distance = (enemy.Position - origin).Magnitude
    process(enemy, distance)
end
```

### Clean up per-player state

```luau
local playerState = {}

Players.PlayerAdded:Connect(function(player)
    playerState[player] = {
        connections = {},
        data = {},
    }
end)

Players.PlayerRemoving:Connect(function(player)
    local state = playerState[player]
    if not state then
        return
    end

    for _, connection in state.connections do
        connection:Disconnect()
    end

    playerState[player] = nil
end)
```

---

## Output format when optimizing for the user

When responding to the user:

1. Briefly identify the likely bottleneck.
2. State whether the issue is algorithmic, engine-side, memory, networking, or Luau hot-path.
3. Explain the optimization in plain language.
4. Provide the updated code.
5. Mention tradeoffs.
6. Suggest how to profile/verify.

Example response structure:

```md
The main issue is that this code scans every part in Workspace every frame. That is usually much more expensive than the Luau syntax inside the loop.

I changed it to maintain a cached set of tagged objects, so the frame loop only touches relevant objects.

[code]

Verify it by comparing Script Profiler CPU time before and after, and by checking MicroProfiler if physics/rendering is still the dominant cost.
```

---

## What not to do

Do not:

- invent benchmark numbers
- claim performance gains without profiling
- use community myths as facts
- optimize tiny code paths while ignoring obvious frame loops
- move server-authoritative logic to clients
- remove validation for speed
- suggest `--!native` everywhere
- suggest Parallel Luau for simple scripts
- use unreliable remotes for important state
- convert readable code into obscure code unless there is a measured hot path
- ignore mobile performance
- ignore memory cleanup

---

## Final priority list

When in doubt, optimize in this order:

1. Stop unnecessary per-frame work.
2. Stop unnecessary engine/physics/replication work.
3. Stop unnecessary allocations and leaks.
4. Fix bad algorithms and repeated scans.
5. Reduce network frequency and payload size.
6. Reduce Instance count and replicated state.
7. Use better tables, buffers, and data layouts.
8. Apply Luau hot-path optimizations.
9. Consider native code generation for compute-heavy server functions.
10. Consider Parallel Luau for large, partitionable, CPU-heavy workloads.

Performance optimization is successful only when the experience remains correct, secure, maintainable, and measurably faster.
