# Roblox VFX instance and system map

## Contents
Primary primitives; geometry/surfaces; scene/screen; animation/audio/services; capability boundaries.

This is a functional inventory of relevant systems, not a claim that every Roblox class is an effect primitive. Use the current [engine API](https://create.roblox.com/docs/reference/engine) to verify unfamiliar properties and engine changes. Hidden/internal fields are not production interfaces.

## Primary primitives

| Instance | Best use | Important controls and failure cases |
|---|---|---|
| ParticleEmitter | Many transient textured sprites: sparks, dust, puffs, motes, flipbook bursts | Burst/loop lifecycle, sequences and orientation; not individual physical colliders. Full operational guide: `particles.md`. |
| Attachment | Local transform anchor for particles, endpoints and equipment FX | Parent to appropriate BasePart or supported hierarchy; explicit axes and WorldCFrame interpretation. A point anchor is different from emission throughout a Part's volume. |
| Bone | Deforming-mesh attachment/animation context | Discover actual hierarchy and animated transforms; don't substitute an undeformed rest transform for the moving surface. |
| Beam | Instant connection, laser, tether, curved energy path | Attachment0/1, Width0/1, CurveSize0/1, Segments, FaceCamera, Texture, TextureMode/Length/Speed, color/alpha sequences. A ribbon, not a volumetric cylinder. |
| Trail | Swept motion history: weapon edge, fast moving object | Two attachments define ribbon span; Enabled controls new history, Lifetime controls tail, Clear removes stored history. Must actually move. |
| PointLight / SpotLight / SurfaceLight | Illuminate nearby geometry from effect | Range/brightness/color/shadows/direction as appropriate. Particle emission brightness is not a replacement for actual scene light. Keep light ownership scoped. |
| Highlight | Selection, reveal, hit or status silhouette | Fill/outline transparency/color, Adornee, depth behavior. Test readability and occlusion; avoid unlimited high-frequency allocations. |

Primary sources: [particles](https://create.roblox.com/docs/effects/particle-emitters), [beams](https://create.roblox.com/docs/effects/beams), [trails](https://create.roblox.com/docs/effects/trails), [effects overview](https://create.roblox.com/docs/effects), [Highlight API](https://create.roblox.com/docs/reference/engine/classes/Highlight), [Attachment](https://create.roblox.com/docs/reference/engine/classes/Attachment), [Bone](https://create.roblox.com/docs/reference/engine/classes/Bone).

## Geometry and surfaces

**Part, WedgePart, CornerWedgePart, MeshPart and SpecialMesh** can supply shards, rings, slashes, sheets, portals and volumes. A Model supplies a pivot/assembly container, not a visible effect by itself. Mesh topology, UVs, pivot and normals matter more than adding polygons. Set cosmetic geometry non-collidable, non-touchable and non-queryable, with shadows disabled when unnecessary. For anchored visual rigs, transform the model rather than welding it to gameplay physics. For skinned meshes, use the existing animation setup.

**Decal, Texture and SurfaceAppearance** address different surface workflows: surface image, tiled image, or PBR maps on supported meshes. MaterialVariant/MaterialService can support shared material styling. Do not assume a ground decal projects freely onto arbitrary geometry; orient a thin conforming mesh/plane or implement a deliberate surface solution. Avoid coincident coplanar faces. A transparent mesh can still be expensive and sort poorly. Test overlapping cards from several angles.

**Fire, Smoke and Sparkles** are simple built-in effects; use when their limited style is suitable, not as universal high-end defaults. **Explosion** is not a harmless decorative substitute: its physics/joint/terrain behavior must be explicitly controlled before parenting. Prefer a custom cosmetic stack rather than inserting Explosion into a live place. **ForceField** can carry gameplay protection; do not add one merely to obtain its appearance without understanding that behavior.

Sources: [SurfaceAppearance](https://create.roblox.com/docs/reference/engine/classes/SurfaceAppearance), [Explosion](https://create.roblox.com/docs/reference/engine/classes/Explosion), and class-specific pages in the engine API. The architecture choices above are recommendations.

## Scene and screen presentation

Lighting, Atmosphere, Sky, Terrain water and Clouds establish the place's environment. Inspect these, but don't rewrite global art direction to make one effect look good. Lighting technology and availability of settings can change; read current Studio properties rather than assuming legacy settings.

The current post-processing family includes **BloomEffect, BlurEffect, ColorCorrectionEffect, DepthOfFieldEffect, SunRaysEffect and ColorGradingEffect**. Camera-local effects are appropriate for local presentation when supported; use an existing mixer so overlapping effects restore correctly. A single hard-coded reset to FOV 70 or a guessed brightness is not restoration. ColorGradingEffect exposes tonemapper choices; it is not a general arbitrary shader. Verify exact options in the installed version. [Official post-processing guide](https://create.roblox.com/docs/environment/post-processing-effects).

ScreenGui, BillboardGui, SurfaceGui, Frame, ImageLabel, ImageButton, TextLabel, UIGradient, UIStroke, UICorner and UI scale/layout objects support hit indicators, damage numbers, speed accents and world-linked symbols. Respect safe areas, UI scale, Z-order and input. Do not place a full-screen flash above critical prompts by default. ViewportFrame/WorldModel provide a separate 3D display context; **do not assume all Workspace particles, lighting, post effects or shadows behave identically there**. Test required primitives or use pre-rendered licensed/original sprites for UI.

Camera controls CFrame/FieldOfView and presentation viewpoint. Use a camera-shake contribution/mixer that composes with the existing camera, ends predictably, and offers reduced motion. Never hijack the camera forever after a canceled cast.

## Animation, sound, physics and lifecycle

| System | Role / constraint |
|---|---|
| TweenService / Tween | Property interpolation for meshes, lights and UI; not every data type/property is tweenable. For ColorSequence/NumberSequence use an explicit controller or authored particle lifetime behavior rather than assuming TweenService accepts them. |
| RunService | Frame/update scheduling. Use delta time and shared controllers for scale; don't spawn a perpetual loop per mote. |
| Animation, Animator, AnimationTrack | Character/mesh animation and named marker synchronization; callbacks are not authoritative hit validation. |
| AnimationController, Motor6D, Bone | Existing rig animation infrastructure; preserve ownership and rig conventions. |
| Sound / SoundGroup | Spatial/2D audio, mixing, playback and tails. Sound approval/license is separate from texture license. |
| Modular audio instances | AudioPlayer/AudioEmitter/AudioListener/Wire and processing nodes may fit an existing project; discover current permissions/routing. Do not install a second audio framework for one effect. |
| RaycastParams / Workspace:Raycast | Surface origin/normal/material and visual placement. Client results can differ under streaming; authoritative gameplay belongs elsewhere. |
| Constraints / assemblies | Deliberate physical debris or driven props. Prefer simulated visual arcs when collisions aren't meaningful; no unnecessary server-owned physics storm. |
| ContentProvider | Preload a small relevant asset set asynchronously before the first important use; handle failures. Do not block startup on the entire place. |
| Debris | Deferred destruction for disposable non-pooled items; not a lease-aware object pool. |
| CollectionService / attributes | Tags/config on authored effects; avoid using attributes as an undocumented accidental protocol. |
| RemoteEvent / UnreliableRemoteEvent | Compact effect triggers/state, with validation and replay policy. Unreliable transport is unsuitable for unique critical cues without a fallback. |
| ReplicatedStorage / ServerStorage / StarterPlayerScripts | Asset distribution and controller placement chosen to match the project. Storage alone does not play an effect. |

Sources: [TweenService](https://create.roblox.com/docs/reference/engine/classes/TweenService), [animation events](https://create.roblox.com/docs/animation/events), [raycasting](https://create.roblox.com/docs/workspace/raycasting), [remotes](https://create.roblox.com/docs/scripting/events/remote), [ContentProvider](https://create.roblox.com/docs/reference/engine/classes/ContentProvider), [Debris](https://create.roblox.com/docs/reference/engine/classes/Debris).

## Capability-dependent advanced work

EditableImage / EditableMesh / AssetService can enable procedural art or geometry, subject to current permissions, memory budgets and API restrictions. They are not an assurance of arbitrary screen-space refraction, GPU particle simulation or custom fragment shaders. Mesh deformation, scrolling textures, multiple layers and flipbooks can approximate selected looks; name the approximation. Export complicated smoke/fire simulation from a DCC as a sprite sequence when appropriate and legally authorized; Roblox is not a general Houdini simulation player. [EditableImage](https://create.roblox.com/docs/reference/engine/classes/EditableImage).
