# Roblox Lighting API and Systems Reference

**Verification date:** 2026-08-24
**Policy:** Re-check Roblox Creator Hub/API reference immediately before implementing a production place. Roblox can add, deprecate, secure, or roll out properties without preserving old tutorials.

This reference distinguishes scene illumination from electrical lightning effects.

## 1. System model

Roblox scene appearance is produced by interacting layers:

1. `Lighting` global environment and time controls.
2. `Sky`, sun, moon, stars, and environment maps.
3. `Atmosphere` or legacy fog for distance/air scattering.
4. `Clouds` under `Terrain`, influenced by environment lighting and wind.
5. Direct local lights: `PointLight`, `SpotLight`, and `SurfaceLight`.
6. Geometry, normals, wall thickness, `CastShadow`, transparency, and occlusion.
7. Built-in/PBR materials, `MaterialVariant`, `SurfaceAppearance`, roughness, and metalness.
8. Post-processing: bloom, blur, color correction, color grading/tonemapping, depth of field, and sun rays.
9. Adjacent visual systems such as `ParticleEmitter.LightEmission`, `LightInfluence`, Neon materials, Beams, Highlights, and world-space UI.
10. Camera, graphics quality, device capabilities, and client-specific effects.

Never evaluate a property in isolation. A setting that looks harmless under one sky, material set, or quality tier can dominate under another.

## 2. `Lighting` service

### Current properties

| Property | Role | Practical interpretation and interactions |
|---|---|---|
| `Ambient: Color3` | Baseline environmental tint/fill | Affects the whole experience, with strongest practical influence in shadowed/interior regions. It is not physically based bounce lighting. Avoid using a bright saturated Ambient to rescue every dark area; that flattens depth and colors all materials. |
| `Brightness: number` | Global direct-light intensity | Changes the intensity of global illumination from sun/moon and interacts with color-shift visibility. Treat it as a coarse key-light/intensity control, then use exposure and fill separately. |
| `ClockTime: number` | Time in decimal hours | Typically 0–24. Drives sun/moon positions and is directly linked to `TimeOfDay`. It does not advance unless scripted. Use broad time to find elevation, then `GeographicLatitude` to refine trajectory/direction. |
| `ColorShift_Bottom: Color3` | Tint on surfaces facing away from the sun/moon | Often subtle, especially with global shadows. Use sparingly as a directional color accent, not as the primary fill control. It interacts with Ambient/OutdoorAmbient and Brightness. |
| `ColorShift_Top: Color3` | Tint on surfaces facing the sun/moon | Can support warm key/cool fill stylization. It is orientation-dependent and affected by Brightness. Keep close to black for neutral/realistic looks unless evidence supports a shift. |
| `EnvironmentDiffuseScale: number` | Diffuse environment contribution | Controls diffuse light derived from the sky/environment. Higher values can improve coherent sky fill and PBR response, but usually require lowering Ambient/OutdoorAmbient to avoid washed-out shadows. |
| `EnvironmentSpecularScale: number` | Environment specular/reflection contribution | Higher values strengthen environment reflections on smooth surfaces and improve metal response. Diagnose roughness/metalness and skybox first; do not use this alone to make every object “shiny.” |
| `ExposureCompensation: number` | Camera-like global exposure offset | Current documented range is approximately −5 to +5; +1 is one stop brighter and −1 one stop darker. Set physical/scene balance first, then use exposure for final global placement. High positive exposure clips highlights and reveals weak contrast; high negative exposure crushes shadow detail. |
| `ExtendLightRangeTo120: Enum.RolloutState` | Extended local-light range rollout | Current API marks this Not Scriptable. Do not rely on changing it from generated Luau. Record it as a manual/Studio setting when relevant, guard access, and re-check rollout status. |
| `FogColor: Color3` | Legacy fog color | Use only when no `Atmosphere` is active and a simple distance fade is desired. Atmosphere presence hides/supersedes legacy fog controls in current workflows. |
| `FogEnd: number` | Legacy full-fog distance | Must exceed `FogStart`. Prefer Atmosphere for richer outdoor depth unless a deliberately simple or retro fade is desired. |
| `FogStart: number` | Legacy fog onset | Do not place so near that the player loses navigation contrast. Evaluate at map scale and camera height. |
| `GeographicLatitude: number` | Alters sun/moon path | Changes celestial positions without changing displayed time. Use with `ClockTime` to match sun direction and elevation; validate via `GetSunDirection()`. |
| `GlobalShadows: boolean` | Enables global sun/moon shadows | Important for depth, direction, and realism. When false, `OutdoorAmbient` is ignored and Ambient applies more broadly. Disabling can be a deliberate flat/retro style or low-cost fallback, but it changes gameplay contrast substantially. |
| `LightingStyle: Enum.LightingStyle` | Current artistic/rendering style | Current choices include `Realistic` and `Soft`. Realistic provides the advanced lighting/shadow look; Soft is flatter and more retro-like. `ShadowSoftness` is meaningful under Realistic. This property may have Studio/security restrictions; set with guarded code or manual instruction if needed. |
| `OutdoorAmbient: Color3` | Outdoor environmental fill | Separates exterior fill from general Ambient while global shadows are active. Use to keep outdoor shadows readable without brightening every interior equally. |
| `PrioritizeLightingQuality: boolean` | Quality-vs-view-distance priority | At reduced render quality, true prioritizes advanced lighting/shading nearer the camera; false prioritizes view distance. Choose based on whether close lighting fidelity or long sightlines are more important to gameplay. May be security-restricted for scripts. |
| `ShadowSoftness: number` | Global shadow edge softness | Current conceptual range 0–1; useful with `LightingStyle = Realistic`. Infer from penumbra width only after considering object-to-receiver distance and screenshot blur. Softer is not automatically more realistic. |
| `TimeOfDay: time string` | Time as `HH:MM:SS` | Coupled with ClockTime. Prefer one canonical representation in generated plans to avoid accidental conflicts. |

### Deprecated or legacy properties/methods

- `Technology` — deprecated. Old tutorials that set `Future`, `ShadowMap`, `Voxel`, or `Compatibility` can be misleading under the current `LightingStyle` workflow. Preserve only when auditing a legacy place, and migrate intentionally.
- `Outlines` — deprecated.
- `ShadowColor` — deprecated.
- lowercase `getMinutesAfterMidnight` / `setMinutesAfterMidnight` — deprecated; use capitalized methods.
- `GetMoonPhase` — deprecated in the current API.

### Methods

- `GetSunDirection(): Vector3` — use as the ground truth for current Roblox sun direction after setting time/latitude. For automated matching, search ClockTime/latitude combinations and minimize angular error to the inferred reference direction.
- `GetMoonDirection(): Vector3` — equivalent for moon direction.
- `GetMinutesAfterMidnight(): number` — numeric time query.
- `SetMinutesAfterMidnight(minutes)` — convenient for scripted time cycles.

### Important rendering implications

- Global shadows are not infinitely precise. Small details may not cast or receive the exact shadows expected from offline rendering. Roblox documentation describes voxelized shadow behavior; do not build gameplay around tiny shadow silhouettes.
- Sun position is not set directly. Estimate a direction, then solve for `ClockTime` and `GeographicLatitude`, checking the result with `GetSunDirection()`.
- Brightening Ambient, OutdoorAmbient, EnvironmentDiffuseScale, Brightness, and Exposure simultaneously is a common cause of flat, overexposed scenes. Assign each control a job.

## 3. `Atmosphere`

Parent an `Atmosphere` to `Lighting`. Current properties:

| Property | Visible role | Tuning logic |
|---|---|---|
| `Color` | Overall atmospheric hue | Use for subtle environmental cast. Its effect is more visible with Haze. Avoid forcing the entire palette through a saturated value. |
| `Decay` | Hue away from the sun | Works with Haze/Glare to shape color falloff. Useful for warm sun side vs cooler anti-sun side. |
| `Density` | Amount of airborne particles/obscuration | Controls how strongly objects and terrain lose visibility with distance. Determine from map scale: a value tolerable in a 100-stud room can erase a 2,000-stud vista. |
| `Glare` | Glow around the sun | Requires Haze to be visible. Distinguish from `SunRaysEffect` and Bloom: glare belongs to atmospheric sun scattering. |
| `Haze` | Horizon and distance haziness | Adds aerial perspective and mood. Use to separate depth planes, not to cover unfinished areas unless that is an intentional composition choice. |
| `Offset` | Object/sky transmission balance | Lower values can blend distant objects into the sky; higher values silhouette them more. Balance with Density. Too low can produce sky-through-geometry “ghosting”; too high can expose distant LOD popping. |

### Atmosphere workflow

1. Temporarily disable strong post effects.
2. Set the sky/time and global exposure first.
3. Start with low Density/Haze.
4. Tune Density to the farthest gameplay sightline.
5. Tune Offset for horizon integration without ghosting.
6. Add Haze for depth and Glare only when the sun cue requires it.
7. Tune Color/Decay after neutral value structure works.
8. Re-test indoors; Atmosphere is global, so use geometry, portals, and local camera effects rather than making the exterior atmosphere destroy interior readability.

### Atmosphere vs legacy fog

Do not treat them as additive independent layers. Current Roblox behavior hides legacy fog properties when an Atmosphere exists. A plan should normally choose one system:

- Atmosphere for aerial perspective, outdoor depth, haze, sun glare, weather mood.
- Legacy fog for simple/retro distance fade, special constrained cases, or legacy compatibility.

## 4. `Sky`

Parent one authoritative `Sky` to `Lighting` unless the experience intentionally swaps skies.

Key properties/roles:

- `SkyboxBk`, `SkyboxDn`, `SkyboxFt`, `SkyboxLf`, `SkyboxRt`, `SkyboxUp` — six skybox faces. The skybox affects visible background and environment reflection/diffuse cues.
- `SkyboxOrientation` — rotates skybox orientation; useful for matching a reference horizon or reflection direction without changing the texture files.
- `CelestialBodiesShown` — toggles sun, moon, and stars.
- `SunTextureId`, `SunAngularSize` — visible sun disc appearance/size. The disc is not the same thing as shadow softness.
- `MoonTextureId`, `MoonAngularSize` — visible moon appearance/size.
- `StarCount` — visible stars.

### Sky rules

- Match the sky's value and hue near the horizon before global color correction. A wrong sky poisons reflections and perceived white balance.
- A photographed/HDR-like skybox may imply light directions or clouds that do not match Roblox's actual sun. Align or hide the celestial disc, or choose a compatible sky.
- Avoid copyright-infringing extraction of another game's assets. Reproduce the visible lighting style with licensed/original sky assets.

## 5. `Clouds`

Create `Clouds` under `Terrain` in current Studio workflows. Properties:

- `Enabled` — toggle render state.
- `Cover` — 0–1 cloud coverage.
- `Density` — cloud particle density.
- `Color` — material color, but the final visible color is influenced by Lighting and Atmosphere. Do not use it as the only sunset control.

`Workspace.GlobalWind` influences cloud movement. Treat cloud direction/speed as environmental animation rather than a static color setting. Check current API/security before scripting it.

Clouds alter sky value, sun visibility, and mood. When matching a screenshot, decide whether a dim sky is caused by cloud cover, a dark skybox, low sun, exposure, or color grading. Do not compensate with four controls at once.

## 6. Local light hierarchy

All local lights inherit common `Light` properties:

- `Enabled`
- `Color`
- `Brightness`
- `Shadows`

`Brightness` controls intensity, not coverage. Coverage comes from Range and, for directional lights, Angle/Face. Local lights must be direct children of a `BasePart` or `Attachment` that descends from Workspace to illuminate the world.

### `PointLight`

- Spherical emission from a point.
- `Range` defines illuminated radius/coverage.
- When parented to an Attachment, origin is `Attachment.WorldPosition`; when parented to a part, origin is the part position.

Best for bulbs, flames, magical orbs, omnidirectional lamps, and soft accent pools. Avoid using one huge PointLight to fake room lighting: it leaks through openings, flattens direction, and creates broad overlap.

### `SpotLight`

- Cone-shaped emission.
- `Angle` defines cone width.
- `Face` chooses direction when attached to a BasePart.
- `Range` defines reach.

Best for flashlights, stage lights, headlights, security lights, sunshafts through small fixtures, and directional emphasis. Prefer an Attachment for precise orientation. Match cone edge and falloff visually; a reference cone can also be a Beam/particle effect rather than illumination.

### `SurfaceLight`

- Emits from a selected face of a BasePart.
- `Angle`, `Face`, and `Range` control spread/direction/reach.
- When parented to an Attachment, current documentation describes behavior equivalent to a SpotLight.

Best for panels, windows, monitors, fluorescent strips, portals, and broad practical sources. Use multiple modest fixtures rather than a giant range when the map contains occluding rooms.

### Local-light placement principles

- Attach the light to the visible source and align it physically.
- Keep Range only as large as the meaningful receiving area.
- Enable `Shadows` only when the shadow communicates depth/gameplay or the fixture is visually important.
- Avoid dense overlapping shadowed volumes.
- Turn off or reduce distant/hidden room lights where the design permits.
- Warm/cool contrast works best when source colors are plausible relative to material palette and global fill.
- Use flicker sparingly and avoid high-contrast rapid temporal changes that can cause discomfort.

## 7. Post-processing

Post-processing effects in `Lighting` apply globally to all players. Effects in the current `Camera` are per-player and appropriate for temporary UI, damage, focus, cutscene, underwater, or other local states. `ColorGradingEffect` is a special case: current docs say it is expected under `Lighting` and ignored elsewhere.

All inherit `PostEffect.Enabled`.

### `BloomEffect`

- `Intensity` — strength of glow.
- `Size` — spread radius/appearance.
- `Threshold` — brightness threshold before bloom.

Use bloom to model bright-source spread, not to make every object luminous. Tune Threshold first so only intended highlights trigger; then Size; then Intensity. Validate on low graphics quality because appearance can differ. Bloom does not illuminate nearby geometry.

### `BlurEffect`

- `Size` — global Gaussian blur amount.

Use mostly for menu states, transitions, dreams, or controlled camera effects. A global persistent BlurEffect damages gameplay readability and screenshot matching metrics.

### `ColorCorrectionEffect`

- `Brightness`
- `Contrast`
- `Saturation`
- `TintColor`

Use after lighting balance. It is a display-space mood/grade layer, not a substitute for source color or fill. Multiple color-correction effects can combine; keep them named and purposeful to avoid an untraceable stack.

### `ColorGradingEffect`

- `TonemapperPreset` — current enum includes `Default` and `Retro`.

Current behavior: expected under `Lighting`; multiple instances do not combine, and only the most recently parented one applies. Keep exactly one authoritative managed instance. `Retro` aims to imitate pre-2019 Roblox tonemapping; audit all light brightness and highlight behavior when using it.

### `DepthOfFieldEffect`

- `FocusDistance`
- `InFocusRadius`
- `NearIntensity`
- `FarIntensity`

Excellent for cutscenes, showcases, portraits, inspection modes, or fixed-camera experiences. Dangerous as a global gameplay default because the correct focal distance changes continuously, low-end output can differ, and blurred hazards/UI context reduce comfort. Prefer Camera-local state control.

### `SunRaysEffect`

- `Intensity`
- `Spread`

Renders a sun-linked halo/ray effect shaped by occlusion. Use when the sun is actually visible or strongly implied. Do not use as generic fog or indoor god rays; local Beams/particles may be more controllable for stylized shafts.

## 8. Materials, PBR, and geometry

### Built-in materials

Built-in Roblox materials use physically based texture information and respond to environment diffuse/specular controls. The same light values will look different on concrete, grass, metal, glass, and smooth plastic.

### `MaterialVariant` and `SurfaceAppearance`

- Base color/albedo controls reflected color and must not be “fixed” through lighting.
- Roughness controls highlight spread. If a screenshot's highlights are too broad/narrow, adjust roughness before `EnvironmentSpecularScale`.
- Metalness changes whether reflections dominate. Wrong metalness can make lighting matching impossible.
- Normal maps influence local shading and highlight shape.

### Neon and emissive appearance

Neon material and bloom can appear self-luminous, but do not assume they provide enough physical illumination. Add a local Light for nearby surfaces when the reference shows colored spill. Keep the visible source bright enough to motivate the spill but below clipping unless clipping is intentional.

### Geometry and light leaks

- Walls, ceilings, and floors need sufficient thickness and sealed joins for believable shadowing. Roblox's indoor-lighting guidance recommends enclosing spaces; sample workflows use at least roughly one stud and sometimes thicker shells depending on geometry.
- Single-sided or thin imported meshes, inverted normals, gaps, and transparent parts can produce leaks or missing shadows.
- An oversized local light range can illuminate through adjacent rooms even when geometry seems closed.
- `BasePart.CastShadow = false` can be appropriate for tiny, distant, transparent-looking, or fast-moving decorative objects, but audit silhouette changes.

## 9. Adjacent appearance controls that are not scene lights

- `ParticleEmitter.LightEmission` — makes particles appear more self-lit.
- `ParticleEmitter.LightInfluence` — controls how much scene light affects particles.
- `SurfaceGui`/`BillboardGui.LightInfluence` and `Brightness` — control world-space UI response/visibility.
- `Beam`, `Trail`, `Fire`, `Smoke`, `Sparkles` — can suggest luminous energy but do not replace scene illumination.
- `Highlight` — strong gameplay guidance layer; use when lighting alone cannot guarantee interactable visibility across quality tiers.
- `Decal`/`Texture` colors and transparency can alter perceived brightness without changing light.

Separate these from physical illumination in the plan.

## 10. Scripting and replication cautions

- Some Lighting properties are Studio/security restricted or Not Scriptable. Generated scripts should use `pcall` and emit a manual checklist for anything that fails.
- `ClockTime` is listed as not replicated in current API metadata; test server/client behavior for runtime cycles rather than assuming Studio property behavior.
- Keep global persistent settings server/place-owned; use Camera-local effects in `StarterPlayerScripts` for per-player states.
- For a day/night cycle, transition coherent groups (time, exposure, atmosphere, local fixtures) with explicit state logic rather than independently tweening every property.
- Do not delete all Lighting children blindly. Tag managed instances, back up, and preserve unrelated effects/scripts.

## 11. Current-instance checklist

A comprehensive audit should inspect:

- `Lighting` and every current property listed above.
- `Atmosphere`, `Sky`, and all post effects under Lighting.
- `Terrain` for `Clouds` and water/terrain visual properties.
- Workspace descendants for `PointLight`, `SpotLight`, `SurfaceLight`, Attachments, and fixture geometry.
- BaseParts for `CastShadow`, material, transparency, reflectance, and geometry leaks.
- MeshParts/SurfaceAppearance/MaterialVariant for PBR maps.
- Camera and StarterPlayerScripts for local post effects.
- Particles, Beams, Neon materials, world-space UI, and Highlights that affect perceived lighting.
- Runtime scripts that mutate time, environment, local lights, or post effects.
- Streaming/room activation logic that toggles light groups.
- Device quality and accessibility settings that may alter the final look.
