# Performance, Scalability, and Validation

## 1. Separate official engine facts from heuristics

### Current official Roblox guidance

As of the verification date, Roblox documents that:

- shadow quality degrades as client graphics quality decreases and shadows are disabled below graphics quality level 4;
- shadow handling can be expensive, especially with dense shadow-casting lights/parts;
- creators should disable `BasePart.CastShadow` on appropriate small/far parts, disable shadows on moving objects when possible, disable `Light.Shadows` where unnecessary, limit light range/angle, use fewer lights, and disable lights outside relevant ranges or room-by-room;
- useful MicroProfiler scopes include `Perform/Scene/computeLightingPerform`, `LightGridCPU`, `ShadowMapSystem`, and `Perform/Scene/RenderView` for rendering/post-processing;
- Studio device emulation, real-device testing, MicroProfiler, and performance dashboards are complementary tools.

These are engine/platform facts. Exact “safe counts” are not universal because cost depends on device, overlap, shadows, geometry, camera, particles, resolution, and engine updates.

### Skill heuristics

Any numeric light budgets below are **starting review thresholds**, not Roblox guarantees. Profile the actual place.

## 2. Cost model

Think in terms of visible/influential work per frame:

```text
lighting cost ~
  active visible lights
  × influenced screen/space volume
  × overlap
  × shadow requirement
  × shadow-caster complexity/motion
  × graphics quality/resolution
  + post-processing full-screen cost
  + particles/transparency/material cost
```

A small non-shadowed light in an enclosed corner is not equivalent to a long-range shadowed light covering a moving crowd.

## 3. Optimization order

Preserve art direction by optimizing in this order:

1. Remove accidental duplicates and lights with no visible contribution.
2. Reduce Range/Angle to the intended receiving area.
3. Disable Shadows on decorative/fill lights.
4. Disable `CastShadow` on insignificant small/far/moving decoration after visual review.
5. Activate lights by room/zone/distance when transitions are not visible.
6. Replace many overlapping fills with stronger environment composition or fewer motivated sources.
7. Reduce transparent/particle overdraw around luminous effects.
8. Scale post effects and particles by quality/state.
9. Simplify the scene/fixtures only after targeted lighting changes.

Do not begin by turning off all shadows; that can destroy the visual hierarchy and hide the real overlap problem.

## 4. Heuristic starting thresholds

These are review triggers for a typical gameplay camera, not hard limits:

### Low-end mobile target

- Aim for 0–2 materially important shadowed local lights influencing the camera at once.
- Keep total meaningful overlapping local lights in a gameplay area roughly 4–8 before profiling.
- Prefer short ranges and room activation.
- Keep Bloom/SunRays subtle; avoid persistent DOF/Blur.
- Design readability assuming global/local shadows may disappear.

### Mid-range mobile/PC target

- Roughly 2–4 important shadowed local lights in the densest view is a review threshold.
- Roughly 8–16 overlapping active local lights warrants profiling/heatmap inspection.
- Use high-cost hero clusters only in controlled spaces.

### High-end showcase/cinematic target

- More lights/effects can be justified, but still profile and provide a fallback.
- Do not let a high-end beauty view define normal gameplay cost.

These numbers should be adjusted immediately after measuring the actual frame and light-grid/shadow scopes.

## 5. Quality-tier design

### Tier principles

- Preserve the same mood, focal hierarchy, and semantic color language.
- Remove expensive implementation details, not the core readability.
- Never make a hazard/enemy visible only through a high-tier shadow or reflection.

### Example tier table

| Feature | Low | Medium | High |
|---|---|---|---|
| Global shadows | Engine-dependent; design without reliance | On where supported | On |
| Local shadowed hero lights | 0–1/zone | 1–3/zone | profiled hero set |
| Decorative local lights | culled/grouped, short range | moderate | full profiled set |
| Bloom | low/off for gameplay | restrained | art target |
| DOF | cutscene/menu only | cutscene/menu only | cinematic states |
| Atmosphere | preserve depth/readability | art target | art target |
| Particles/light shafts | reduced rate/coverage | moderate | full |
| Reflection/specular accents | material-first | moderate | full art target |

Implement quality changes client-side where they are purely visual and do not alter game state/fairness.

## 6. Spatial activation

For indoor or segmented maps:

- group fixtures by room/zone;
- pre-activate adjacent zones before the doorway becomes visible;
- fade/tween rather than pop when needed;
- keep emergency/navigation lights active if they can be seen through portals;
- avoid rapidly creating/destroying large trees; toggle `Enabled` or use pooled instances where appropriate;
- account for StreamingEnabled and missing streamed geometry.

Distance-only activation can fail through walls or long sightlines. Combine portals/zones with distance and visibility logic.

## 7. Shadow optimization

Audit every shadowed light:

- Is its shadow visible from gameplay cameras?
- Does it communicate depth, threat, or source realism?
- Is the source moving?
- How many moving casters enter its range?
- Could a non-shadowed fill plus one shadowed key preserve the effect?
- Does its range cross multiple rooms?

Audit `CastShadow` candidates:

- tiny bolts, grass cards, clutter, particles, transparent decorations;
- distant repeated props;
- rapidly moving debris;
- hidden/interior faces.

Capture before/after views because disabling shadows can create floating objects or light leaks.

## 8. Post-processing performance/quality

Post effects operate over the screen and can vary by quality/device.

- Bloom: restrict threshold/coverage; bright particles and UI-like world objects can trigger large areas.
- DOF/Blur: reserve for controlled states; they reduce readability even when frame cost is acceptable.
- SunRays: test occlusion changes and common camera directions.
- ColorCorrection/ColorGrading: generally inexpensive relative to shadow clusters but can destroy dynamic range; performance is not the only constraint.

Profile `RenderView` while toggling effects to identify actual contribution.

## 9. Testing matrix

Minimum matrix:

| Dimension | Cases |
|---|---|
| Device | low-end mobile or emulation; representative mobile; desktop/console target |
| Graphics | lowest meaningful; around shadow cutoff; medium; maximum |
| Camera | spawn; densest light cluster; longest vista; interior/exterior doorway; fast motion |
| State | normal; combat/hazard; weather/time transition; UI/menu; maximum players/effects |
| Network/streaming | cold load; streamed boundary; teleport/respawn; zone transition |

Record resolution, FPS/frame time, graphics quality, device, scene, and exact plan ID.

## 10. Frame-time targets

Roblox performance guidance commonly frames 60 FPS as approximately 16.67 ms per frame. Use the actual product target:

- 60 FPS target: total frame budget about 16.67 ms;
- 30 FPS target: about 33.33 ms, but unstable pacing still feels poor;
- leave headroom for gameplay, UI, networking, particles, and worst-case player counts.

Do not allocate the entire frame budget to a static lighting test.

## 11. Profiling workflow

1. Reproduce the worst representative view.
2. Capture baseline MicroProfiler data.
3. Inspect `computeLightingPerform`, `LightGridCPU`, `ShadowMapSystem`, `RenderView`.
4. Toggle all managed local lights to determine upper-bound contribution.
5. Re-enable by group: shadowed keys, non-shadowed fills, decorative accents, particles/post.
6. Reduce range/angle and shadows in the highest-cost group.
7. Re-capture under identical camera/state.
8. Test low/medium/high quality and a real mobile device when possible.
9. Monitor live performance after release; Studio-only results are not enough.

## 12. Validation metrics

### Technical

- median, p95, and worst frame time in each test scene;
- lighting/shadow scope time;
- number of active/visible/overlapping lights;
- number of shadowed lights;
- bright/clipped pixel percentage;
- dark/crushed pixel percentage;
- quality-tier instance/effect counts.

### Visual/gameplay

- route/hazard/player readability rubric;
- reference/candidate image metrics;
- shadow direction/area agreement;
- atmosphere depth-plane contrast;
- user comfort/playtest feedback;
- fairness checks.

## 13. Release gates

Do not ship until:

- low graphics remains playable with shadows reduced/disabled;
- no single camera direction causes a major lighting spike without mitigation;
- local-light activation does not visibly pop in normal traversal;
- UI/world text remains readable;
- interior/exterior transitions are comfortable;
- profiler captures and test conditions are archived;
- the rollback plan is tested;
- live dashboards/analytics are identified for post-release monitoring.
