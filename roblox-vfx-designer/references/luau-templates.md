# Bundled Luau contract and integration

## Status and scope

Original source templates, **not executed or type-checked in Roblox Studio during this build**. There is no Roblox runtime/compiler in the build container. Read and run the included smoke test in a disposable Studio client before using a new integration. Static Python tests do not certify these modules.

These templates implement a deliberately small finite world-space VFX player, not a full animation editor, networking framework, universal shader engine or persistent ambience service. Agents should extend/adapt the design with the project's existing controller for mesh animation, cameras, infinite loops, character rigs and authoritative combat. The broader skill is not limited to this example impact.

## Installation for the optional example

Create `ReplicatedStorage/VFXDesignerExample/Modules`. Import each `.luau` module as a ModuleScript named exactly `VFXRuntime`, `EffectPool`, `SurfaceFrame`, `BuildImpact`, `MarkerBindings`, `SceneProbe`, `StudioSmokeTest`. Remove the extension from Roblox instance names. `Demo.client.luau` becomes an optional **LocalScript** in StarterPlayerScripts in a disposable test place. Do not place modules inside the effect prefab: the finite player rejects script-bearing assets.

Existing projects should use their own folders/import mappings. Do not claim a filesystem edit automatically changed Studio unless the repository's sync tool or actual editing integration did so.

## Runtime API

`VFXRuntime.Prepare(unparentedModel)` validates inert cosmetics, sets BaseParts anchored/non-collidable/non-touchable/non-queryable/no-shadow, and resets native emitter/trail/beam/light/sound state. It rejects embedded scripts, Explosion/ForceField and physics constraints/joints. It does not certify arbitrary model safety.

`VFXRuntime.Play(model, {Parent = workspaceFolder, CFrame = optionalFrame, Release = optionalFunction})` runs on **Client**, assumes exclusive ownership of an unparented prepared/cloneable model and returns a handle. It compiles timing attributes before parenting. Invalid configuration raises an error; the caller must destroy its clone or return its lease on that path.

`handle:Stop(true)` immediately clears/reset/releases. `handle:Stop(false)` (also default Stop) suppresses future events, stops beam/light/audio and new emission, then drains particle/trail tails. It is not an audio fade controller. `handle:SetCFrame(frame)` moves a live rig, useful with a project-owned update loop. `handle:IsFinished()` reports release. Native particle TimeScale must stay positive and unchanged during play; paused particles need a custom stop owner. Do not mutate lifetimes during a lease without extending the runtime's cleanup contract.

| Instance attribute | Interpretation |
|---|---|
| `StartDelay` | Nonnegative real seconds from start; default zero |
| ParticleEmitter `BurstCount` | Nonnegative integer burst; default zero |
| ParticleEmitter `EmitDuration` | Finite enabled window; default zero; authored Rate must be positive |
| Beam/Trail/Light `ActiveDuration` | Finite enabled window; default zero |
| Sound `ActiveDuration` | Required positive playback window; sound stopped at its end |

You may combine a particle burst and a finite loop on one emitter intentionally. Beam/Trail do not use `BurstCount`. `Lifetime.Max / TimeScale` is a conservative authored tail duration in this template, not a complete predictor of every platform's apparent particle behavior. Delayed events run on a frame boundary. After a long frame, a burst receives its full tail but a missed continuous window can be compressed; this is not deterministic timeline resimulation. For a synchronized long cinematic, use an appropriate project timeline/reconciliation policy.

The runtime owns one Heartbeat connection per active effect. That is a clear small-library starting point, not the final architecture for thousands of simultaneous effects. Use shared scheduling if profiling justifies it. No task.delay callbacks survive release.

## Pool API and safe error handling

`EffectPool.new(immutableTemplate, capacity, optionalCustomReset)` bounds active plus idle clones. `pool:Acquire()` returns `(model, releaseClosure)` or `(nil, nil)` at capacity/after destruction. The closure is lease-specific; stale/double release returns false. Pass a no-return wrapper as Runtime.Release. **Never call the release closure while the runtime still owns a playing rig**: stop the handle and let it release. Never put a pooled rig into Debris.

```luau
local rig, release = pool:Acquire()
if rig and release then
    local ok, result = pcall(function()
        return Runtime.Play(rig, {
            Parent = effectsFolder,
            CFrame = impactFrame,
            Release = function() release() end,
        })
    end)
    if not ok then
        release() -- Play validation failed before a handle took ownership.
        warn(tostring(result))
    end
else
    -- Drop only optional cosmetics, or use the project's essential-cue fallback.
end
```

The custom reset function must not yield and must restore all authored properties modified by custom logic. Native histories reset, but arbitrary Size/ColorSequence/tween changes are **not automatically rolled back**. Keep immutable baselines or avoid pooling that rig. `pool:Destroy()` invalidates leases and destroys owned clones; stop active handles first when possible. External destruction is an error path, not a normal release protocol.

## Placement and marker helpers

`SurfaceFrame.fromRaycast(result, optionalOffset, optionalTwist)` / `fromNormal(position, normal, offset, twist)` produce a frame whose local +Y follows the normal. Offset is in studs; twist in radians. Match mesh and EmissionDirection conventions to this frame. No raycast is performed by the helper; caller chooses filters and authoritative/non-authoritative purpose.

`MarkerBindings.Bind(track, {Contact = function(parameter) ... end})` connects before `track:Play()` and returns disconnect. It disconnects on Stopped/Destroying; replay requires a new binding. Markers on looped tracks can repeat while bound. Callbacks should not yield and must not establish authoritative damage. Cancel the effect handles separately when canceling an ability.

`SceneProbe.Inspect(optionalRoot, optionalNodeBound)` returns bounded structural hints and current camera/Lighting fields. It changes nothing. It is not a computer-vision style classifier, complete scene inventory, or substitute for gameplay screenshots.

## BuildImpact and texture mapping

`BuildImpact.Create({Textures = {flash=..., spark=..., smoke=...}, Accent=..., Dust=..., Scale=...})` returns an unparented three-layer example. Texture values must be real verified `rbxassetid://...` image content IDs. The function checks syntax only; content availability/license must be checked elsewhere.

`PreviewOnly=true` permits missing role IDs and leaves the built-in sparkle as an explicitly tagged proxy. The demo and smoke test intentionally use this mode so they do not require fake IDs. **This is not a finished smoke texture, final style, or production effect.** Replace proxies through the sourcing/import workflow and visually review the result before shipping.

## Test fixture

Run `require(Modules.StudioSmokeTest).Run()` using an actual Client execution capability in a disposable Studio play session. It checks surface basis, capacity, immediate/double stop, stale lease, natural cleanup, pre-delay cancel and graceful tail. It does not measure device performance, verify final assets or grade visual quality. Record the actual results, errors and environment; the shipped fixture has no pre-populated runtime pass claim.
