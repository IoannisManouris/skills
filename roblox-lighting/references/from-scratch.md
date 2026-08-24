# Creating Roblox Lighting from Scratch

This process turns a game/map brief into a coherent, playable lighting system. Numeric values are starting hypotheses only; the correct result depends on geometry, materials, camera, and graphics quality.

## 1. Write a one-sentence lighting thesis

Use the form:

> The player should feel **[mood]** while immediately understanding **[route/action/focal subject]**, using **[dominant environmental condition]**, **[key/fill relationship]**, and **[accent language]**, while remaining readable on **[minimum device/quality]**.

Examples:

- “A playful sunny obby where colored platforms read instantly against a cool, uncluttered sky, with crisp but not punishing shadows on mobile.”
- “A damp industrial horror maze where warm practical lights reveal safe islands inside cool darkness, but doorways and threats never vanish into crushed black.”
- “A premium car showcase with controlled neutral daylight, strong environment reflections, and camera-local depth of field only in inspection mode.”

The thesis prevents random parameter accumulation.

## 2. Audit the map before lighting it

### Scale

Record approximate room sizes, outdoor sightline length, camera height, traversal speed, and landmark spacing. Atmosphere, light ranges, shadow detail, and contrast all read differently at 50, 500, and 5,000 studs.

### Geometry

Find open roofs, thin walls, gaps, overlapping shells, flipped normals, transparent partitions, and rooms that are not actually enclosed. Fix these before fighting leaks with darkness.

### Palette and materials

Create a value and hue inventory:

- darkest/lightest major materials;
- dominant warm/cool surfaces;
- reflective/metallic surfaces;
- saturated gameplay colors;
- Neon/emissive accents;
- terrain/water color.

Lighting should support material identity. A gray concrete map can accept colored light; a highly saturated simulator map often needs more neutral light.

### Gameplay information

Mark:

- spawn/onboarding;
- intended route and return route;
- jumps, ledges, traps, projectiles, enemies, cover, loot, prompts, doors, checkpoints;
- competitive silhouettes and camouflage risks;
- safe zones vs dangerous zones;
- moments where the player moves quickly or looks away from the objective.

Assign each a minimum readability requirement.

### Camera and UI

Record normal FOV, zoom range, first/third person, fixed/free camera, camera shake, motion speed, and screen UI. A look optimized for a 35° cinematic camera may fail at a 90° gameplay FOV.

## 3. Establish a neutral diagnostic baseline

The exact values vary, but a useful neutral baseline has:

- current `LightingStyle = Realistic` unless the art direction explicitly wants Soft/retro;
- global shadows on;
- a neutral sky appropriate to the time of day;
- middle-of-day or broad-angle sun while materials are checked;
- restrained Brightness and ExposureCompensation near neutral;
- low-saturation Ambient/OutdoorAmbient;
- EnvironmentDiffuse/Specular enabled enough to reveal PBR behavior;
- no heavy Atmosphere;
- all post effects disabled except the authoritative tonemapper;
- local lights temporarily disabled.

Capture diagnostic views and repair geometry/material problems. This is not the final look; it isolates inputs.

## 4. Build the global environment

### 4.1 Choose `LightingStyle`

- **Realistic:** use for directional shadows, dimensional local lights, PBR/showcase work, atmospheric worlds, and most modern looks.
- **Soft:** use deliberately for flat, retro, toy-like, or low-contrast art direction. Do not select it merely because the Realistic setup is poorly balanced.

### 4.2 Select sky and time together

Choose a skybox whose horizon, cloud implication, and sun direction are compatible with the intended time. Set `ClockTime` and `GeographicLatitude`, then inspect `GetSunDirection()` from several gameplay views.

The sun direction should:

- shape major forms;
- cast route-readable shadows rather than hide landing surfaces;
- avoid permanently backlighting competitive opponents unless intentional/fair;
- create a recognizable landmark silhouette;
- support indoor window/door light direction.

### 4.3 Set global key intensity

Tune `Brightness` while looking at neutral materials. Preserve texture/color detail in sunlit surfaces. Do not use ExposureCompensation yet to compensate for a physically incoherent balance.

### 4.4 Set fill and environment response

Tune in this order:

1. EnvironmentDiffuseScale for sky/environment fill.
2. EnvironmentSpecularScale for PBR reflections.
3. OutdoorAmbient for exterior shadow readability.
4. Ambient for interior/general minimum fill.
5. ColorShift controls only for deliberate directional stylization.

Check key-to-fill ratio: turn global shadows off temporarily or inspect matched lit/shadowed surfaces. Stronger ratio gives drama/depth; weaker ratio gives cheerful/readable/flat presentation. Preserve some form separation.

### 4.5 Set shadow character

Tune ShadowSoftness in Realistic mode. Consider:

- hard midday/stylized sun;
- soft overcast or broad-looking sun;
- object distance from receiver;
- motion/readability;
- visual noise from foliage/small parts.

Disable `CastShadow` on insignificant detail only after testing silhouettes.

## 5. Add atmosphere for depth and weather

Use Atmosphere after the global value structure works.

1. Set Density to establish far-distance visibility.
2. Balance Offset against distant silhouette/sky blending.
3. Add Haze to create depth-plane separation.
4. Add Glare only if the sun cue requires it.
5. Tune Color and Decay for air color, not a blanket grade.
6. Add Clouds and global wind after sky/time/atmosphere agree.

Map-scale test:

- nearest important object retains full contrast;
- midground separates from foreground;
- far background loses contrast in a controlled way;
- navigation landmarks remain identifiable;
- the horizon does not ghost through terrain;
- interiors are not unintentionally fogged into gray.

## 6. Design local lights as practical, motivated sources

Create a fixture inventory. For each source record:

- visual emitter;
- light type;
- position/orientation;
- intended receiving surfaces;
- range boundary;
- source color temperature/style;
- whether shadows add value;
- whether it is static, flickering, stateful, or distance-culled.

### Key/fill/accent/environment model

This is a design model, not a requirement to place literal film lights everywhere:

- **Environment:** sky and ambient context.
- **Key:** dominant direction or practical source shaping the player/scene.
- **Fill:** maintains readable shadow information.
- **Accent/rim:** separates focal subjects or landmarks.
- **Practicals:** visible lamps/screens/portals motivating local pools.

For stylized games, the “accent” may be a colored SurfaceLight or Highlight. For outdoor maps, the sky is both environment and fill.

### Local-light sequence

1. Place only the fixtures visible in the environment.
2. Tune Range to the receiving zone.
3. Tune Angle/Face/orientation.
4. Tune Brightness.
5. Tune Color.
6. Enable Shadows only when necessary.
7. Add subtle spill lights only when visible evidence requires them.
8. Test overlap and adjacent rooms.

Do not start with brightness because a too-large Range can make a low-brightness light contaminate the whole map.

## 7. Create focal hierarchy and player guidance

Use a hierarchy:

1. primary gameplay target;
2. immediate route/hazard information;
3. landmark/secondary objective;
4. decorative background.

Guide attention through combined cues:

- value contrast;
- color-temperature contrast;
- silhouette/rim separation;
- converging geometry;
- pools of light along the route;
- reduced background contrast through atmosphere;
- material/specular accents;
- restrained motion/particles;
- Highlight/UI only where lighting cannot guarantee clarity.

Avoid making every reward, sign, lamp, and particle equally bright. If everything blooms, nothing is important.

## 8. Handle indoor/outdoor transitions

Roblox does not automatically reproduce real eye adaptation as a cinematography system. Design transitions deliberately:

- create vestibules, covered porches, tunnels, or intermediate zones;
- avoid immediate jump from near-black to clipped daylight;
- keep exterior visible through doors/windows without turning it pure white;
- add practical fill just inside entrances;
- use Camera-local, smoothly tweened color/exposure effects only when necessary;
- never change global Lighting for one player when only their camera should adapt;
- ensure adaptation does not create a competitive visibility exploit.

Test entering and exiting at sprint speed.

## 9. Apply post-processing last

### Tone/exposure

After source balance, set ExposureCompensation to place the whole image. Keep highlight and shadow detail appropriate to style.

### Color correction

Use small changes to establish mood. Compare skin/avatar colors, team colors, hazards, and UI. Avoid using saturation to compensate for gray materials.

### Bloom

Select intended highlights with Threshold, then Size and Intensity. Check white UI/particles and Neon assets for accidental activation.

### Sun rays

Use only when the sun and occlusion support the cue.

### Depth of field and blur

Use camera-local and stateful for cutscenes/showcases/menus. Do not make active platforming, combat, or navigation continuously blurry.

## 10. Build quality tiers

Design one art direction with scalable implementation:

- **Low:** no dependence on dynamic local shadows; fewer active local lights; shorter ranges; restrained particles/post effects; strong material/value readability.
- **Medium:** essential shadows and accents; moderate atmosphere and post.
- **High:** hero shadows, richer local light overlap where profiled, premium reflections/post.

Do not create three unrelated looks. The focal hierarchy and palette must survive every tier.

## 11. Validation loop

For each iteration:

1. Capture fixed validation cameras.
2. Play the critical route.
3. Check player/hazard/object silhouettes.
4. Inspect darkest 5% and brightest 5% of the image.
5. Check materials and reflections.
6. Test low/medium/high graphics.
7. Profile frames while looking at the most expensive light cluster.
8. Record one parameter-family change at a time.
9. Keep or revert based on art, gameplay, and performance—not screenshot beauty alone.

## 12. Completion checklist

- Lighting thesis remains true.
- Spawn and route are instantly legible.
- Focal hierarchy survives motion and low quality.
- No major light leaks or unjustified sources.
- Materials retain identity.
- Atmosphere supports scale without obscuring gameplay.
- Bright and dark areas preserve intentional detail.
- Local ranges/angles are minimal and motivated.
- Post effects are restrained and state-appropriate.
- Competitive visibility is fair.
- Mobile/low quality is tested.
- Plan, script, backup, validation captures, and unresolved issues are documented.
