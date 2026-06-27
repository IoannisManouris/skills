---
name: roblox-luau-optimization
description: Use this skill when the user asks to optimize, profile, refactor, or audit Roblox/Luau code for performance, including FPS, server CPU, memory leaks, garbage collection, RemoteEvents/RemoteFunctions, UnreliableRemoteEvents, buffers, Parallel Luau, Actors, native code generation, RunService loops, physics, replication, instance count, streaming, UI, or load time. First verify current Roblox/Luau guidance from official web sources before changing code.
compatibility: Designed for Codex, Claude Code, and Agent Skills-compatible coding agents with file editing and optional web access.
metadata:
  version: "1.2.0"
  domain: roblox-luau
  target_engine: Roblox Studio
---

# Roblox Luau Performance Optimization Skill

Use this skill to optimize Roblox Studio experiences written in Luau. Optimize for correctness, security, maintainability, and measured performance. Preserve behavior first.

Read `references/optimization-reference.md` when the user asks for a full audit, deep optimization plan, examples, benchmark snippets, or detailed refactor.

## Mandatory freshness check

Before applying a specific optimization technique, verify current guidance from reliable web sources when web access is available.

Source priority:
1. Roblox Creator Hub documentation
2. Roblox Creator Docs GitHub repository
3. Official Luau documentation
4. Official Luau GitHub repository/releases
5. Roblox engineering posts or official Roblox DevForum announcements
6. Recent community benchmarks only when specific, reproducible, and not conflicting with official sources

Reliable starting URLs:
- https://luau.org/performance/
- https://github.com/luau-lang/luau/releases
- https://create.roblox.com/docs/performance-optimization
- https://create.roblox.com/docs/performance-optimization/microprofiler
- https://create.roblox.com/docs/studio/optimization/scriptprofiler
- https://create.roblox.com/docs/studio/optimization/memory-usage
- https://create.roblox.com/docs/performance-optimization/scene-analysis
- https://create.roblox.com/docs/scripting/scheduler
- https://create.roblox.com/docs/reference/engine/classes/RunService
- https://create.roblox.com/docs/scripting/events/remote
- https://create.roblox.com/docs/reference/engine/classes/RemoteEvent
- https://create.roblox.com/docs/reference/engine/classes/UnreliableRemoteEvent
- https://create.roblox.com/docs/reference/engine/libraries/buffer
- https://create.roblox.com/docs/scripting/multithreading
- https://create.roblox.com/docs/reference/engine/classes/Actor
- https://create.roblox.com/docs/luau/native-code-gen
- https://create.roblox.com/docs/workspace/streaming

If web access is unavailable, say current guidance could not be verified and proceed using the most recent known official Roblox/Luau guidance. Never rely on old Lua folklore unless current Luau/Roblox sources still support it.

## Core priority order

1. Remove unnecessary per-frame work.
2. Reduce engine work caused by scripts: physics, replication, rendering, instance churn.
3. Fix poor algorithms, repeated scans, and O(n²) behavior.
4. Reduce allocation churn, garbage collection pressure, and memory leaks.
5. Reduce network frequency, payload size, yielding, and bad authority patterns.
6. Reduce instance count, replicated state, and load-time work.
7. Apply Luau hot-path optimizations only after profiling.
8. Use buffers, native code generation, and Parallel Luau only when the workload fits.

The largest Roblox wins usually come from doing less engine work, not tiny syntax tricks.

## Profiling workflow

When optimizing:
1. Identify symptom: low FPS, server CPU, memory growth, high ping, delayed input, slow load, stutter, mobile lag.
2. Classify cause: compute/frame time, memory/leak/GC, networking/replication, physics, rendering/UI, load time.
3. Use tools:
   - Developer Console for live memory, network, scripts, and general stats
   - Script Profiler for Luau CPU hotspots
   - MicroProfiler for full engine frame timeline
   - Luau Heap/Memory tools for retained objects and leaks
   - Scene Analysis for instance count, scripts, animations, audio, and unparented instances
   - Performance dashboard for live regressions
4. Locate the dominant cost.
5. Make the smallest safe behavior-preserving change.
6. Add instrumentation if needed.
7. Re-profile before claiming success.

Do not invent benchmark numbers. If measurement is unavailable, explain expected direction and why.

## Biggest performance drains

### 1. Per-frame work

Suspicious:
- `RunService.PreRender`, `RenderStepped`, `PreAnimation`, `PreSimulation`, `PostSimulation`, `Heartbeat`
- `while true do ... task.wait()` polling loops
- frequent `workspace:GetDescendants()` or `CollectionService:GetTagged()` scans
- loops over all players, characters, parts, UI objects, projectiles, NPCs, tools, or effects every frame

Fix:
- replace polling with events
- cache dynamic sets and update them on added/removed signals
- lower update frequency when possible
- chunk expensive work across frames
- move cosmetic work to clients
- keep `PreRender` tiny because it blocks rendering
- avoid networking and large allocations inside frame callbacks

### 2. Engine work triggered by scripts

Suspicious:
- creating/destroying many Instances repeatedly
- cloning large models during gameplay
- changing many replicated properties every frame
- moving many unanchored parts
- overusing constraints, collisions, touch events, particles, beams, trails, sounds, or animations
- frequent parenting/reparenting
- frequent replicated attributes or ValueObjects

Fix:
- reduce part/Instance count
- use client-side cosmetic effects
- anchor static objects
- disable `CanCollide`, `CanTouch`, and `CanQuery` when not needed
- use collision groups
- avoid high-frequency replicated property changes
- pool Instances only when profiling shows churn and lifecycle is safe
- use Animator/Animation systems instead of manual per-part animation where appropriate

### 3. Large worlds and high instance count

Each Instance has memory and replication cost.

Fix:
- use Scene Analysis
- enable and design around streaming for large worlds
- store internal runtime data in Luau tables, not DataModel Instances
- use Attributes/ValueObjects only for replication, Studio visibility, configuration, or engine integration
- avoid high-frequency replicated attributes
- reduce always-loaded objects, SurfaceGuis, BillboardGuis, attachments, constraints, particles, sounds, and duplicated scripts

### 4. Allocation churn and GC pressure

Suspicious hot-path allocations:
- tables, closures/functions, large strings, Instances, temporary arrays/maps, JSON strings, buffers, event connections

Fix:
- avoid temporary tables in hot loops
- use `table.create(n)` when array size is known
- use `table.clear(t)` for scratch tables only when references do not escape
- pass multiple values instead of one-use tables
- avoid closure creation inside repeated runtime loops
- avoid unbounded caches
- clean per-player/per-object state
- disconnect events and cancel tasks

### 5. Memory leaks

Common leaks:
- connections never disconnected
- tables keyed by Player/Character/Tool/Instance/userId never cleared
- references to destroyed Instances
- closures retaining large tables
- ModuleScript singletons storing stale state
- per-player tasks/coroutines after leave
- animation tracks, sounds, particles, effects, UI not cleaned up
- caches with no size limit/expiry
- promises/threads never resolving or cancelling

Fix:
- clean on `PlayerRemoving`
- clean on character death/removal and object destruction
- use existing Maid/Janitor/Trove-style lifecycle utility if available
- use weak tables only when ownership is fully understood
- test leave/rejoin, character reset, round restart, teleport, and destruction paths

### 6. Networking misuse

Suspicious:
- RemoteEvents fired every frame per player
- full snapshots where deltas would work
- large nested or mixed-key tables
- RemoteFunctions for fire-and-forget updates
- `RemoteFunction:InvokeClient()` without timeout/failure design
- client-authoritative state
- many small remotes instead of batching
- reliable remotes for ephemeral high-rate data

Fix:
- use `RemoteEvent` when no response is required
- use `RemoteFunction` only for true request/response logic
- avoid server-to-client invoke unless necessary
- use `UnreliableRemoteEvent` only for transient, non-authoritative data where drops/out-of-order delivery are acceptable
- batch updates and send deltas
- use small IDs instead of Instances or huge objects
- quantize numeric data when appropriate
- consider `buffer` for compact binary/numeric payloads
- rate-limit and validate all client remotes
- keep server authoritative for purchases, inventory, currency, damage, unlocks, saves, and round results

### 7. Poor algorithms

Suspicious:
- O(n²) loops
- repeated sorting
- repeated full-table scans
- repeated `FindFirstChild` in hot loops
- repeated raycasts/pathfinding where events/cache would work
- recalculating static data every frame
- scanning Workspace repeatedly
- deep nested loops over game objects

Fix:
- maintain dictionaries/maps for membership checks
- index by id/tag/type/team/owner
- use dirty flags and update only when data changes
- precompute static data
- avoid sorting every frame
- cache references when lifetime is clear
- use spatial partitioning for many-object proximity checks

## Decision tree

Low FPS/stutter:
1. Use MicroProfiler.
2. If scripts dominate, use Script Profiler.
3. If rendering/UI dominates, reduce visible objects, UI churn, particles, effects, SurfaceGuis, BillboardGuis, ViewportFrames, and per-frame text updates.
4. If physics dominates, reduce unanchored assemblies, constraints, collisions, touch events, and high-speed physical interactions.
5. If replication/networking dominates, reduce replicated property changes, remote frequency, and payload size.
6. If GC spikes dominate, reduce allocations/leaks.

Server CPU high:
1. Check server CPU/frame and simulation health.
2. Use Script Profiler.
3. Find per-frame server loops and repeated scans.
4. Move cosmetic/client-only work to clients.
5. Reduce physics and replication.
6. If CPU time is high but core usage is low, consider Parallel Luau/Actors.
7. If one compute-heavy function dominates, consider native code generation.

Memory grows:
1. Use Developer Console Memory, Luau Heap, and Scene Analysis.
2. Find retained players, characters, tools, UI, effects, animations, sounds, connections, caches, closures, tasks.
3. Add cleanup.
4. Re-test lifecycle paths.

Networking bad:
1. Inspect remote frequency and payload size.
2. Remove unnecessary round trips.
3. Replace `RemoteFunction` with `RemoteEvent` where no response is needed.
4. Batch, delta, quantize, and validate.
5. Use `UnreliableRemoteEvent` only for safe ephemeral state.
6. Use `buffer` only when it improves size, throughput, or clarity.

Loading slow:
1. Reduce initial replicated Instances.
2. Use streaming for large worlds.
3. Avoid cloning huge systems on join.
4. Lazy-load optional systems.
5. Preload only assets needed soon.
6. Move non-critical initialization after spawn.
7. Split work across frames.

## Modern Luau guidance

Avoid old Lua myths:
- caching every global into a local
- localizing every `math.*`, `table.*`, or `string.*` call everywhere
- caching Roblox Instance methods into locals
- assuming numeric `for i = 1, #t` is always fastest
- caching `#t` everywhere
- making code obscure without profiling

Modern Luau optimizes many common patterns: global library chains in pure environments, built-in fastcalls, namecall method calls, table iteration, table length in many practical cases, and predictable table shapes.

Avoid in performance-sensitive code: `getfenv()`, `setfenv()`, `loadstring()`.

Prefer `object:Method(arg)` over `object.Method(object, arg)`.

In very hot loops, direct builtin forms may help, such as `string.byte(s, i)` instead of `s:byte(i)`. Only prioritize this in measured hot paths.

For Luau-only code, generalized iteration is usually fine: `for key, value in dictionary do`. Use `ipairs` for nil-stop array semantics. Use numeric loops for custom stepping, reverse order, mutation-sensitive logic, or direct index control.

For object records, create fields in the literal: `local point = { x = 1, y = 2, z = 3 }`.

For known-size arrays, use `table.create(count)` and direct indexed writes.

For scratch tables, use `table.clear(t)` only when references do not escape. Never return a shared scratch table that will be reused.

Avoid deep `__index` chains, hot-path `__index` functions, dynamic metatable changes, proxy tables for every access, and multi-level inheritance chains in hot objects.

Avoid creating closures repeatedly inside hot runtime loops. UI setup can create callbacks once, but repeated setup without cleanup leaks memory.

Avoid large string concatenation loops; use array accumulation and `table.concat`.

Use `buffer` for compact binary/numeric data such as positions, rotations, velocities, input snapshots, projectile snapshots, compact level data, packed flags, and quantized arrays. Avoid buffers for normal small messages where readability/schema clarity matters more.

## Scheduling and RunService

Prefer modern task APIs: `task.defer`, `task.spawn`, `task.delay`, `task.wait`.

Avoid legacy APIs in new code: `spawn`, `delay`, `wait`.

Use task APIs intentionally; spawned work still consumes frame time. Chunk expensive non-urgent work across frames with `task.wait()` between chunks. Use `debug.profilebegin()` and `debug.profileend()` for labeled profiler regions.

RunService rules:
- `PreRender`/`RenderStepped`: only tiny visual work that must happen before rendering.
- `PreSimulation`: tiny logic needed before physics.
- `PostSimulation`: logic depending on physics results.
- `Heartbeat`: after physics; still avoid expensive every-frame loops.

## Networking rules

`RemoteEvent`: asynchronous one-way communication.

`RemoteFunction`: only when a response is required. Avoid server-to-client invoke unless necessary and failure-safe.

`UnreliableRemoteEvent`: only when dropped/out-of-order messages are acceptable, such as aim direction, camera look direction, cosmetic trails, non-authoritative projectile visuals, temporary animation state, and high-frequency input snapshots where newer data replaces older data.

Never use unreliable remotes for purchases, inventory, currency, damage, round results, save data, unlocks, or authoritative state.

Prefer small IDs and deltas. Batch multiple changes. Always validate client data on the server.

## Native code generation

Consider `--!native` or `@native` only when profiling shows a hot compute-heavy server function that runs many times and works mostly with numbers, arrays, vectors, or buffers.

Good candidates: numeric kernels, vector math, dense array/buffer processing, repeated deterministic computations.

Bad candidates: UI scripts, remote/event-heavy scripts, Instance property dominated scripts, one-time initialization, tiny scripts, non-hot code.

Prefer type annotations. Mention tradeoffs: startup/compile cost, memory use, code-size limits, and uneven benefit. Do not add `--!native` everywhere.

## Parallel Luau and Actors

Consider Parallel Luau when server CPU time is high, core usage is low, work is CPU-heavy, work can be partitioned, shared mutable state can be avoided, and required APIs are parallel-safe.

Good candidates: independent NPC perception, expensive math over independent data, independent simulation chunks, terrain/level analysis, large batch computations.

Bad candidates: tiny tasks, UI, heavily shared mutable state, constant serial synchronization, non-parallel-safe API-heavy code, immediate shared game-state mutation.

Use Actors to partition work. Be careful with `task.desynchronize()`, `task.synchronize()`, Actor messaging, SharedTable, API parallel-safety tags, and transition overhead.

## UI, physics, and instances

UI watchlist: rebuilding UI every frame, many UI create/destroy operations, per-frame text updates, animated gradients/strokes, many SurfaceGuis/BillboardGuis, layout recalculation, frequent AutomaticSize, deep UI trees, complex ViewportFrames.

UI fixes: update only when data changes, pool/virtualize long lists, throttle labels, reduce SurfaceGui/BillboardGui count, avoid full UI rebuilds.

Physics watchlist: many unanchored parts, constraints, complex assemblies, high-speed physics, many collisions/touches, many `Touched` connections, frequent network ownership changes, physics projectiles where raycasts would work, unnecessary `CanCollide`, `CanTouch`, `CanQuery`.

Physics fixes: anchor static parts, disable touch/query/collision when not needed, use collision groups, simplify assemblies, use raycasts for simple projectile/hit detection, reduce constraints and moving physical parts.

Instance/data rules: do not use Instances as internal server data containers when tables are enough. Use Instances/Attributes/ValueObjects only for replication, designer configuration, Studio visibility, or engine integration. Avoid high-frequency replicated property/attribute changes.

## Cleanup rules

When creating temporary objects, connections, or tasks, ensure cleanup. Prefer the project’s existing Maid/Janitor/Trove if present.

Cleanup must handle:
- `RBXScriptConnection:Disconnect()`
- `Instance:Destroy()`
- `task.cancel(thread)`
- callback functions
- table `Destroy` or `Cleanup` methods

## Review checklist

Frame path:
- Does this run every frame?
- Can it be event-driven, lower-frequency, or chunked?

Algorithm:
- O(n²), repeated scans, repeated sorting, recalculated static data, missing maps/indexes?

Allocation:
- Tables, closures, strings, buffers, Instances, or connections in hot loops?
- Can values be passed directly?

Memory:
- Connections disconnected?
- Per-player state removed?
- Destroyed Instances dereferenced?
- Caches bounded?
- Tasks cancelled?
- Animation/sound/effect/UI cleaned up?

Networking:
- Is `RemoteFunction` necessary?
- Are RemoteEvents too frequent?
- Are payloads small, batched, delta-based?
- Is unreliable networking only ephemeral?
- Does server validate everything?

Engine:
- Is this causing physics work, replicated property churn, large clone/destroy operations, too many Instances, or a streaming opportunity?

Advanced:
- Is native justified by profiling?
- Is Parallel Luau justified by high CPU and low core usage?
- Are buffers appropriate?

## Anti-patterns to flag

Flag:
- giant `Heartbeat` loops
- expensive `PreRender`/`RenderStepped`
- frequent `workspace:GetDescendants()` in runtime loops
- full-table scans where indexes work
- repeated `FindFirstChild` in hot loops
- `RemoteFunction` for fire-and-forget updates
- `InvokeClient` without timeout/failure design
- reliable remotes for high-rate cosmetic state
- unreliable remotes for authoritative state
- creating/destroying Instances every frame
- creating connections inside repeated loops without cleanup
- unbounded caches
- retaining Player/Character references forever
- many ValueObjects for internal data
- old `wait()`/`spawn()` in new code
- blindly adding `--!native`
- recommending Lua folklore without profiling evidence

## Safe refactoring rules

1. Preserve behavior.
2. Keep public APIs compatible unless user approves breaking changes.
3. Do not weaken server validation.
4. Do not move authoritative logic to clients.
5. Avoid changing networking authority unless requested.
6. Prefer small measurable changes.
7. Keep readability unless the path is proven hot.
8. Add comments only for non-obvious performance decisions.
9. Explain tradeoffs.
10. Recommend profiling after changes.

## User response format

When optimizing for the user:
1. Identify likely bottleneck.
2. Name category: algorithmic, engine-side, memory/GC, networking, physics, UI/rendering, or Luau hot-path.
3. Explain what changed and why.
4. Provide updated code.
5. Mention tradeoffs/risks.
6. Explain how to profile/verify.

Final rule: performance optimization is successful only when the experience remains correct, secure, maintainable, and measurably faster.
