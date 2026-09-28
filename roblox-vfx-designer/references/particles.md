# Particle, beam and trail operations

## Contents
Emission lifecycle; parameter design; flipbooks; common bugs; production patterns.

## Emit deliberately

Create/configure emitters while `Enabled = false`, parent the fully configured rig, then call `:Emit(integerCount)` for a burst. `Rate` is sustained particles per second when enabled; it does not control the count passed to `Emit`. `Clear()` kills existing particles; disabling stops new continuous emission but is not the same as clearing the tail. Do not destroy the anchor immediately after a burst. A particle under an Attachment emits from that anchor, while a BasePart supports volume-based emission. [ParticleEmitter guide](https://create.roblox.com/docs/effects/particle-emitters).

Example for an already valid, parented emitter (not a complete effect controller):
```luau
emitter.Enabled = false
emitter:Emit(12)
-- Keep the emitter and its parent alive through the tail.
```

For a timed loop, enable for a finite window, disable at its end, then drain particles. Persistent ambience needs an explicit owner and Stop function. Restarting should clear stale particles only when a hard reset is desired. The bundled runtime covers finite windows, not an infinite ambient service.

## Parameter groups and decisions

| Group | Properties to consider | Design use and failure traps |
|---|---|---|
| Spawn | Enabled, Rate, Shape, ShapeStyle, ShapeInOut, ShapePartial, EmissionDirection, SpreadAngle | Specify where particles originate and how they depart. Check shape/parent compatibility in Studio. A broad spread is not automatically an even circular ground ring. |
| Age | Lifetime, TimeScale | Lifetimes vary across particles. Sequence time is normalized age. Cleanup must account for time scaling; a paused emitter can retain particles indefinitely. |
| Travel | Speed, Acceleration, Drag, VelocityInheritance, LockedToPart, WindAffectsDrag | Initial impulse, gravity-like fall, drag and moving-source response. World-released dust differs from a body-locked aura. Inspect wind behavior in the target place. |
| Facing | Orientation, Rotation, RotSpeed | Choose camera-facing, velocity-related or constrained behavior intentionally. Random rotation can destroy the reading of a directional slash. |
| Shape over age | Size, Squash | Primary expansion/contraction; avoid every layer scaling with the same curve. Squash is not arbitrary mesh deformation. |
| Appearance over age | Color, Transparency | NumberSequence/ColorSequence keys shape the envelope. Reserve the strongest value/opacity for the important read. |
| Lighting | LightEmission, LightInfluence, Brightness | Balance emissive appearance and scene response; none means the sprite illuminates nearby geometry. |
| Sorting | ZOffset | Small view-depth adjustments can help a specific overlap; not a license to draw effects through walls. |
| Art | Texture, flipbook fields | Texture readability, alpha quality and frame sequence matter more than emitter count. Verify current property types, including Content-related alternatives, before changing authored assets. |

The property names and methods are from the [current ParticleEmitter API](https://create.roblox.com/docs/reference/engine/classes/ParticleEmitter). **VelocitySpread is deprecated**; use the documented current spread controls. Do not use hidden local/internal fields. The current public method list does not provide a general production particle `FastForward()`/prewarm method: do not invent one.

### Sequences and emission time

For an impact flash, use a fast onset and short decay. For smoke, separate the opacity envelope from growth so a tiny fully opaque square does not pop before expanding. Sequence keypoints should be ordered and include endpoints. Random envelopes are useful for material variation but do not replace a designed curve. A data-driven effect spec should declare whether values apply at spawn, per-particle normalized age, or global effect time.

An approximate steady-state occupancy estimate is `Rate × average Lifetime` at ordinary time scale, absent caps/culling and after warm-up. Bursts add temporary occupancy. Do not treat it as a guaranteed number visible on every device. With non-unit TimeScale, measure actual behavior and adjust cleanup; the starter runtime scales tail duration conservatively but does not claim to predict every emitter's perceptual timing.

### Warm-up and first use

Preload known textures before critical gameplay without blocking the whole client. For persistent ambience, a controlled advance start or authored initial burst can approximate a populated state; it is not physically identical to aging particles forward. Late joiners need explicit state reconstruction, not replay of every historical burst. If a newly cloned effect appears blank for a frame, investigate parent/datamodel, asset permission/loading, camera, enabled state and lifecycle before adding arbitrary wait calls everywhere.

## Flipbook workflow

Use a consistent sprite grid and known frame order, matching the layout selected on the emitter. Check cell dimensions, blank-cell padding, edge bleed and how the last frame disappears. Inspect `FlipbookLayout`, `FlipbookMode`, frame rate/start-random/blend behavior and, where supported, custom `FlipbookSizeX/Y`. Current versions expose custom-layout-related properties; an older beta announcement is not sufficient evidence of today's rollout status. Feature-detect in the target build.

A one-shot explosion normally needs ordered start-to-end motion, while ambient smoke can tolerate varied starting frames. Do not randomize the first frame of an authored contact event unless the design supports it. Frame blending may smooth motion but can muddy graphic/pixel styles. Assess actual screen resolution, not just a large atlas in an image editor. Repack external frame sequences into a supported grid rather than assuming any GIF/video is an emitter texture. Sources: [particle guide](https://create.roblox.com/docs/effects/particle-emitters), [API](https://create.roblox.com/docs/reference/engine/classes/ParticleEmitter).

## Beam and Trail differ from particles

Beam connects two attachments and can curve with endpoint axes/tangents. Author attachments so their local axes are intentional; use FaceCamera only when that view behavior is desired. Increase segments only as needed for curvature and appearance interpolation. Texture scrolling does not physically move a projectile. Use a mesh cylinder or crossed ribbons when required by the camera, and assess added cost. [Beam guide](https://create.roblox.com/docs/effects/beams).

Trail records the motion between two anchors. Place them across the blade or object width, enable just before the intended movement, and disable after. Keep the owner alive for `Lifetime` to see the tail; clear before teleporting/reusing so an accidental long streak is not recorded. A stationary trail does not produce an equivalent weapon slash. [Trail guide](https://create.roblox.com/docs/effects/trails).

## Troubleshooting matrix

| Symptom | Check / fix |
|---|---|
| Nothing emits | Correct Client/Workspace; valid parent; texture permission; count; size/alpha; immediate cleanup; camera; graphics quality |
| Flash appears as a square | Real alpha absent; checkerboard baked into pixels; wrong atlas cell; border not transparent |
| Ground dust flies sideways/up a wall | Attachment axes and EmissionDirection; use surface normal frame, not position alone |
| Aura leaves particles behind | Decide whether LockedToPart or following anchor is intended; velocity inheritance has a different role |
| Slash rotates unpredictably | Remove random rotation for directional art; correct orientation and blade anchors |
| Beam does not show | Both attachments valid; width/alpha; curve axes; not a physical rope; check view angle |
| Trail bridges teleport | Disable and Clear before discontinuous move, then re-enable after new anchors settle |
| Same delayed layer fires twice | Cancel old schedule or invalidate generation/lease token |
| Smoke vanishes abruptly | Owner destroyed or Clear called before maximum tail; paused/changed TimeScale miscounted |
| Looks great in black preview, bad in map | Examine lighting influence, alpha, depth overlap, contrast and bloom in actual scene |
