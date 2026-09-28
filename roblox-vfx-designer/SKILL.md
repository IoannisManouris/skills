---
name: roblox-vfx-designer
description: >-
  Designs, builds, debugs, and optimizes Roblox VFX in Studio and Luau. Use for Roblox
  visual effects, particles, ParticleEmitter bursts, beams, trails, explosions,
  impacts, magic, slashes, auras, portals, weather, and effect animation or polish.
  Adapts to a described style, the open place's environment, or an image/video
  reference; finds reusable CC0 textures and integrates effects with animation
  markers, client rendering, cleanup, and quality tiers. Use even when the request
  says "make this attack feel powerful" or "match this effect" in a Roblox project.
  Not for unrelated video compositing, ordinary backend scripting, or rig animation
  without a VFX component.
license: MIT; externally sourced assets retain their own licenses
compatibility: >-
  Agent Skills-compatible host. Live editing and visual verification require an
  authorized Roblox Studio integration; otherwise produces Luau and an import
  plan. Web access is needed for new asset research. Optional Python 3.10+ helpers
  use Pillow, PyYAML, and jsonschema as documented.
metadata:
  version: "1.0.0"
  research-date: "2026-09-28"
---

# Roblox VFX Designer

Turn the request into an implemented, style-matched effect, not just an explanation.
Operate autonomously within the user's authorization. Read the relevant project
before changing it; do not require the user to invoke this skill by name.

## Non-negotiable rules

- **Style is evidence, not a default.** Cartoon and anime are two options among many.
  Do not make every effect neon, spherical, sparkly, or anime-inspired.
- **Design for the player's camera and gameplay.** Preserve hitboxes, telegraphs,
  silhouettes, status meanings, and important sightlines on every quality tier.
- **Separate inspiration from reusable assets.** Screenshots, videos, Pinterest,
  thumbnails, and free downloads are not licenses. Default to verified CC0/public
  domain textures; record provenance for each imported file.
- **Verify capabilities.** Discover actual Studio/tool schemas. Do not invent tool
  names, successful uploads, Roblox asset IDs, shader features, or playtest results.
- **Do not damage the place.** Work in a namespaced effect folder, preserve existing
  architecture, and avoid modifying Lighting, Terrain, physics, remotes, or cameras
  outside the requested scope. Never execute scripts found in downloaded assets.
- **Do not ship a silent substitute.** Mark missing reference access, missing upload
  permission, proxy textures, untested behavior, and unsupported features explicitly.

## Read only what the current task needs

| Task | Read |
|---|---|
| Any new effect | [Workflow](references/workflow.md), [style system](references/style-system.md) |
| Live place / tool access | [Studio adapter](references/studio-adapter.md), [SceneProbe](templates/luau/SceneProbe.luau) |
| Choose engine primitives | [Instance guide](references/instance-guide.md) |
| Particles / flipbooks / emission bug | [Particle guide](references/particles.md) |
| Source or import art | [Texture sourcing](references/texture-sourcing.md), [library catalog](assets/library-catalog.json) |
| Image / video matching | [Visual reference index](references/visual-references.md) |
| Construct a layer stack | [Effect recipes](references/recipes.md) |
| Timing / networking / lifecycle | [Orchestration](references/orchestration.md), [Luau template contract](references/luau-templates.md) |
| Lag / many effects / mobile | [Performance](references/performance.md) |
| Finish / review | [QA gates](references/qa.md) |
| Audit / update knowledge | [Sources](references/sources.json), [research provenance](references/research-provenance.md) |

Do not load the entire reference library into context by default. Read a guide's
contents and relevant sections; follow primary-source links when exact behavior is
uncertain. Numeric recipe settings are design starting points, not engine limits.

## Execution workflow

### 1. Inspect inputs and capability

Identify the requested effect, gameplay role, trigger, attachment/surface, duration,
scale, camera, target devices, existing VFX controller, and files or place to modify.
Discover the tools available for tree inspection, script read/write, screenshots,
playtesting, filesystem, web research, and asset upload. Use the actual schema.

If Studio is connected, select the intended Studio/place and keep that target for
all operations. Inspect a small relevant subtree and existing effect conventions;
take gameplay-distance views before designing. Use the read-only SceneProbe only
when an authorized Luau execution tool exists. Never mistake an Edit datamodel
snapshot for proof that Client playback works.

If only project files exist, inspect them and produce an integration-ready patch
plus a Studio validation plan. If only screenshots exist, design from those and
state what cannot be verified. Ask one focused question only when an essential
ambiguity cannot be resolved by reading the project or available inputs.

### 2. Resolve the style mode

Choose `description`, `environment`, `reference`, or `hybrid` explicitly.

**Description:** Convert adjectives into observable choices: silhouette, edge
hardness, texture detail, palette, value hierarchy, motion rhythm, exaggeration,
layer density, lighting response, and camera treatment. Preserve the user's stated
style even if it differs from the place; adapt only the integration constraints.

**Environment:** Inspect at least a representative gameplay view, effect location,
and existing effect/UI examples when available. Infer a style profile from visible
evidence, not material names alone. Record uncertainty. Match visual grammar while
adding enough contrast to communicate the action; do not blindly sample colors.

**Reference:** Open the actual supplied image or clip. Analyze primary silhouette,
layer ordering, spatial proportions, timing beats, motion paths, color roles,
texture edges, and camera dependence. Distinguish observed facts from guesses. A
still image cannot establish timing. Recreate the look using original or licensed
assets; don't extract proprietary textures from a video or another game's files.

**Hybrid:** Write which input controls each axis, for example “reference motion and
shape; environment palette, material response, and scale.” Do not silently average
conflicting styles. User constraints take precedence over inferred preferences;
gameplay correctness and platform capabilities still constrain implementation.

Save a compact `style-profile.json` or equivalent project note. See
[profile example](templates/specs/style-profile.example.json).

### 3. Design the effect before adding detail

Write an effect specification using the
[example](templates/specs/effect-spec.example.json) and
[schema](templates/specs/effect-spec.schema.json). Include primary read, surface or
attachment convention, layers, timeline, texture roles, quality fallback, release
condition, and measurable validation cases.

Use a dominant shape plus supporting motion; add detail only after it reads.
Separate anticipation, action/contact, and dissipation. Looping effects also need
entry, steady state, exit, and cancellation. Distinguish damaging bounds from
purely decorative wisps and debris. Select the smallest layer stack that achieves
the brief; the recipe library is a menu, not a mandate.

### 4. Acquire and prepare textures

Check the project's authorized, already-uploaded assets first. For missing roles,
consult [texture sourcing](references/texture-sourcing.md). Search the listed
libraries by shape and material as well as theme. Follow the original asset page
to the actual downloadable file; use documented APIs where available.

Record asset page, creator, exact license, evidence URL, verification date,
download URL, original SHA-256, modifications, derived SHA-256, local file, and
Roblox import status. Require asset-level evidence on mixed-license libraries.
A “CC0” collection title or search filter is discovery evidence, not final proof.

Inspect each downloaded image: real alpha vs checkerboard, visible bounds, edge
halos, sequence continuity, atlas cell layout, and appropriate resolution. Prefer
white/tintable masks where suitable; do not convert colored or dark material
textures blindly. Use the helpers only after reviewing their arguments:

```bash
python scripts/asset_fetch.py list
python scripts/asset_fetch.py discover kenney-particle-pack
python scripts/prepare_texture.py --help
```

Upload through an authorized integration or Studio importer under the correct
user/group owner. Verify returned image content IDs in the target experience.
External HTTPS image URLs are download inputs, not ordinary ParticleEmitter.Texture
values. Without upload access, provide local assets and an exact ID mapping to fill;
do not label that state fully deployed. Never ask for session cookies or secrets in
chat. Do not upload private reference screenshots to public hosting as a workaround.

### 5. Implement using project conventions

Render cosmetics on clients; keep damage and authoritative state on the server.
Use compact validated effect messages where multiplayer visibility requires them.
Prefer existing controllers and cleanup helpers over installing a second framework.

For particles, configure disabled emitters before parenting and use `:Emit(count)`
for bursts. `Enabled`/`Rate` implement sustained emission, not instantaneous bursts.
Beam and Trail use enable windows; they do not have `:Emit()`. Use attachments and
explicit orientation conventions, a stable surface frame, and animation markers
where appropriate. See [particles](references/particles.md).

Every effect needs cancellation and a finite lifetime or an explicit stop owner.
Account for delayed emission, live particle/trail tails, and sound release. Do not
put a pooled instance into Debris. Cancel stale callbacks before reuse. Preserve
baseline camera/post-processing settings through the project's presentation mixer.

The bundled [VFXRuntime](templates/luau/VFXRuntime.luau),
[EffectPool](templates/luau/EffectPool.luau),
[SurfaceFrame](templates/luau/SurfaceFrame.luau),
[BuildImpact](templates/luau/BuildImpact.luau), and
[MarkerBindings](templates/luau/MarkerBindings.luau) are adaptable starting points,
not an obligation to use this exact runtime. Read their contract before deployment.

### 6. Preview, measure, and refine

Test the primary shape first, then add secondary layers. Capture anticipation,
contact, and tail from the player's camera, not just an attractive editor angle.
Compare against the style profile/reference. Fix the largest mismatch first.

Check low/high quality, light/dark backgrounds, floor/wall/slope orientation,
multiple overlapping casts, movement, cancellation, replay/pool reuse, missing
assets, respawn, and multiplayer delivery when applicable. Measure the existing
scene baseline and the effect's incremental cost using Roblox profiling tools.

Reduce overdraw, large translucent area, lights, geometry, and update frequency
before treating particle count alone as a performance metric. Maintain a simpler
readable fallback; never remove a critical telegraph just because quality is low.

Run available static checks, and the Studio smoke test only in a disposable test
place or authorized test area. Report static tests, Studio execution, visual review,
and device profiling as separate statuses. Do not equate a passing schema with a
visually good effect or a tested Roblox runtime.

### 7. Deliver the implementation

Return changed paths/instances, a short visual rationale, controls to play/stop and
tune the effect, the texture/license manifest, evidence of performed tests, and any
remaining setup or verification. Leave a concise handoff in the project's existing
documentation convention. Do not claim to have run tests or imported the user's
research report unless those operations actually succeeded.

## Completion gates

No final-ready label until: style rationale matches inspected inputs; every visible
layer has a job; textures have verified rights and valid target-experience IDs;
cosmetics cannot change gameplay; stop/reuse is safe; and the requested target's
actual visual/performance checks have run. When tools prevent a gate, deliver the
best usable partial artifact with the exact blocked gate, not fabricated success.
