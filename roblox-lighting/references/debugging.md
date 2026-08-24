# Roblox Lighting Debugging Playbook

Use symptom → isolation test → likely cause → fix. Disable post effects and local-light groups during diagnosis.

## Scene is washed out / flat

**Isolation tests**

- Set ExposureCompensation near neutral.
- Temporarily zero/reduce Ambient and OutdoorAmbient.
- Reduce EnvironmentDiffuseScale.
- Disable ColorCorrection.

**Likely causes**

- Brightness, exposure, ambient, and environment diffuse all elevated.
- High material albedo.
- Contrast restored through post rather than actual lighting ratio.

**Fix**

Assign roles: Brightness for key, environment scale for sky fill, Ambient/OutdoorAmbient for minimum fill, exposure for final placement. Preserve lit/shadow difference.

## Scene is too dark / crushed

**Isolation tests**

- Inspect histogram/percentile luma.
- Raise exposure by a small step without changing contrast.
- Disable ColorCorrection Contrast/Tint.
- Inspect same material in lit and shadow.

**Likely causes**

- negative exposure plus high contrast;
- too-low fill;
- dark material palette;
- night sky with no practical lights;
- monitor-dependent design.

**Fix**

Restore shadow information with environment/outdoor/interior fill, then set exposure. Add motivated practical lights. Do not make every shadow gray.

## Highlights are clipped / white surfaces lose texture

**Likely causes**

- high Brightness/local brightness/exposure;
- low Bloom threshold causing apparent clipping;
- overly bright material/Neon;
- Retro tonemapper interaction.

**Fix**

Lower source intensity first, then exposure. Raise Bloom threshold/lower intensity. Verify tonemapper and material.

## Shadows point the wrong way

**Isolation tests**

- Print `Lighting:GetSunDirection()`.
- Disable local lights.
- Verify camera/world orientation and skybox baked sun.

**Likely causes**

- wrong ClockTime/latitude;
- skybox sun conflicts with Roblox sun;
- local light creates the visible shadow;
- reference image mirrored/cropped.

**Fix**

Search time/latitude for desired world direction; rotate/replace skybox or hide incompatible celestial body; identify local source.

## Shadows are too hard/soft

**Check**

- LightingStyle is Realistic;
- ShadowSoftness;
- object-to-receiver distance;
- image blur/quality tier;
- source type.

Do not infer softness from a single compressed edge.

## Light leaks through walls/ceilings

**Isolation tests**

- Disable local lights one group at a time.
- Inspect shell thickness, gaps, normals, transparency.
- Reduce offending light Range.
- add temporary opaque diagnostic boxes.

**Fix**

Seal/thicken geometry, correct normals, reduce ranges, move fixtures, split rooms, and review `CastShadow`. Do not darken the entire game.

## Local light seems to do nothing

**Check**

- Enabled true;
- direct child of BasePart/Attachment under Workspace;
- range/angle/face/orientation;
- parent/attachment location;
- source and receiver not already overexposed;
- graphics quality/editor quality;
- color/brightness values;
- occlusion/geometry.

Brightness does not expand coverage.

## Light covers too much / contaminates adjacent rooms

Reduce Range/Angle, use SurfaceLight/SpotLight rather than PointLight, reposition to fixture, split into multiple shorter-range sources, activate by room, and seal geometry.

## Neon glows but does not light surroundings

Bloom/emissive appearance is visible, but no physical local light is supplying spill. Add an appropriately colored Point/Spot/SurfaceLight and tune receiving surfaces. Avoid a giant range.

## Bloom affects everything

Raise Threshold first. Identify overbright whites, particles, Neon, world-space UI, and unclamped effects. Then tune Size/Intensity. Check low quality.

## Atmosphere makes everything gray

Lower Density/Haze, neutralize Color, review exposure, and scale values to actual sightline length. Use Offset for horizon relation rather than more density. Check whether global atmosphere is inappropriate for interiors.

## Sky appears through terrain/objects

Atmosphere Offset may be too low relative to Density, or geometry/transparency/LOD may be involved. Increase Offset cautiously; inspect distant popping.

## Distant terrain pops strongly

Atmosphere Offset may be too high, revealing LOD transition. Reduce Offset or adjust horizon composition/streaming/LOD.

## Fog settings do nothing

An Atmosphere likely exists, hiding/superseding legacy FogStart/FogEnd/FogColor. Choose one system.

## Reflections look wrong

Check, in order:

1. material metalness;
2. roughness;
3. normal map;
4. skybox content/orientation;
5. EnvironmentSpecularScale;
6. source positions;
7. exposure.

Do not use high specular scale to repair a wrong material.

## Indoor/outdoor doorway is white/black

Balance source intensities; add transition/vestibule and interior entrance fill; use camera-local smooth adaptation if required; protect competitive fairness. Do not globally change Lighting for one player.

## Low graphics looks completely different

Expected causes include reduced/disabled shadows and lower effect quality. Rebuild hierarchy using material values, silhouettes, local non-shadowed lights, Highlights, and restrained atmosphere. Do not require shadows for hazards/enemies.

## Performance drops near a light cluster

Profile `computeLightingPerform`, `LightGridCPU`, `ShadowMapSystem`, and `RenderView`. Reduce overlapping range/angle, shadowed lights, moving casters, particles/transparency, and activate by room/zone. Verify under the same camera/state.

## Generated script fails on a property

The property may be Not Scriptable, security-restricted, renamed, deprecated, or changed in rollout. The generator uses `pcall`; review warnings, apply manually in Studio if current docs allow, and update the schema/reference.

## Multiple color grades behave unexpectedly

Keep one `ColorGradingEffect`; current Roblox behavior does not stack multiple instances. Name and audit ColorCorrection effects because those can compose.

## Depth of field blurs gameplay target

Move DOF to Camera, control it by state, update focus distance dynamically where appropriate, reduce Near/Far intensity, or disable during active gameplay.

## Screenshot match has low metric error but looks bad

The optimizer may have flattened, blurred, or globally recolored the image. Use region masks and perceptual/gameplay review; restore correct camera, edges, local contrast, and materials. Do not optimize one scalar.
