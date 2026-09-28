# Orchestration and reusable effect architecture

## Contents
Asset hierarchy; runtime lifecycle; animation/network timing; pooling; placement and presentation.

A recommended starting layout (adapt to the repository, don't force migration):
```text
ReplicatedStorage/
  VFX/
    Assets/<EffectName>/<Model + named layers>
    Modules/<existing or bundled controllers>
    Configs/<style and effect parameters>
    TextureIds/<verified image IDs>
    Remotes/<only if the project needs new ones>
StarterPlayer/StarterPlayerScripts/
  VFXClient/<dispatcher, quality, presentation integration>
ServerScriptService/
  Combat/<authoritative state and validated FX notification>
Workspace/
  ClientVFX/<local runtime instances; not permanent templates>
```

Give layers semantic names such as `ContactFlash`, `GroundDust`, `BladeArc`, not `ParticleEmitter17`. Store art defaults in immutable templates/configs; store per-play state in controller handles. Separate style profile, physical intent and trigger logic. An effect library should not own damage calculations.

## Finite lifecycle contract

`prepare -> place -> schedule -> emit/animate -> stop new emission -> drain tails -> release`.
Cancellation must have a declared policy: hard cancel clears particles and stops everything; graceful stop suppresses future work and drains already emitted tails. Every controller owns its connections, tweens, tasks and instances. No callback may mutate a rig after its lease ends. Runtime failure should terminate its owned work and report a useful error, not leave a glowing orphan.

The release time is the maximum over all layer end times, including delayed starts, final emission, particle/trail lifetimes, sound release and custom animations. For indefinitely paused particles or looping audio, require an explicit stop rather than guessing. Keep disposal separate from pooling: a pending Debris destruction will destroy an object even after another effect reacquires it. [Debris API](https://create.roblox.com/docs/reference/engine/classes/Debris).

## Timeline design

Anchor contact to the event actually representing contact. Attack start is not always hit confirmation. Windup VFX may be predicted locally; hit feedback should follow authoritative outcome or a reconciled prediction protocol. Bind `AnimationTrack:GetMarkerReachedSignal()` before playback, keep connections scoped to that track/ability and disconnect on end/cancel. Playback speed changes should not desynchronize a duplicated hard-coded delay schedule. [Animation events](https://create.roblox.com/docs/animation/events).

For projectiles, separate launch, flight, impact and cancellation. Moving visuals should not determine server damage solely through client particle position. On a rejected/blocked prediction, stop or correct local effects. A seeded random generator can make **your generated offsets** reproducible; it does not guarantee native ParticleEmitter trajectories match across machines.

## Multiplayer policy

The server validates ability identity, cooldown, target and impact. Send compact permitted IDs and data (origin/normal, timestamp, seed, scale within validated bounds), not arbitrary Instance paths, user-provided module names or remote code. Clients resolve local templates and own transient cosmetics. Apply rate limits and range/visibility filtering without suppressing essential telegraphs. Deduplicate predicted and confirmed playback with event IDs and an explicit policy.

RemoteEvent is suitable for significant event notifications. UnreliableRemoteEvent trades reliability/order for ephemeral updates; don't use it as the sole delivery of a critical one-shot warning. Ongoing hazards/status effects need state snapshots for join/stream-in, not only old events. Decide how late events are shortened, skipped or replayed; do not burst all missed particles at once. Source: [Roblox remote events guide](https://create.roblox.com/docs/scripting/events/remote).

Do not assume calling an emitter method on one side substitutes for a deliberately designed cross-client protocol. Test the actual replication path in a multi-client session. Avoid replicating every cosmetic fragment as a physics object.

## Pooling policy

Pool only high-churn assets that profiling justifies. Set a bounded active count and a clear overflow rule (drop optional detail or use cheaper fallback, never hide an essential warning). Every acquire returns a unique generation/lease. Only that lease can release the object. Before reuse: stop playback, cancel old updates, clear native histories, reset transforms and any mutated appearance properties. Restore baselines; don't multiply already-scaled sizes repeatedly. A pool is not a complete reset strategy for arbitrary third-party scripts.

The bundled pool is deliberately limited to inert, client-side VFX models and is paired with the bundled finite runtime. For custom mesh/camera tweens, supply a reset function that restores every mutation or use disposable instances until reset correctness is established.

## Surface and attachment conventions

Raycast along a specified direction/length with appropriate filters. Place contact a small measured distance along the returned normal to avoid z-fighting. Construct a full orientation frame with a stable tangent, not only a position. The bundled `SurfaceFrame` defines local +Y as surface normal. Design emitter EmissionDirection and mesh axes to that convention. A wall hit should not reuse a floor-only ring without reorientation. Streaming can make client raycasts miss unloaded geometry; don't use that miss as authoritative permission to pass through it. [Raycasting guide](https://create.roblox.com/docs/workspace/raycasting).

For character-following effects, distinguish local transform following from particles locked to the source. Use existing Attachments/Bones when possible. Clear trails around teleportation and discontinuous pose corrections. For a projected line or tether, endpoints may update each frame while the beam remains a single instance.

## Sound and camera

Contact sound should share the logical contact event, but may have its own spatial distance/occlusion/mix policy. Vary subtly within the style; don't replace physical weight with unlimited volume. Register camera shake/FOV/post effects as contributions to the existing mixer, with cancellation and reduced-motion controls. Never restore guessed global defaults or delete another controller's effects. Camera-local presentation belongs to the affected client. See [post-processing](https://create.roblox.com/docs/environment/post-processing-effects).
