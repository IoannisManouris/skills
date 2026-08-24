# Reconstructing Roblox Lighting from Screenshots

## Purpose

Given one or more 2D images, estimate a Roblox-compatible setup that reproduces the **visible lighting look**, not unknowable source settings. This is an inverse-rendering problem: many combinations of illumination, materials, geometry, camera, atmosphere, and post-processing can produce similar pixels.

The correct output is a ranked set of hypotheses with ranges and confidence, followed by iterative matching in the target map.

## 1. Inputs

Minimum:

- one reference screenshot;
- target Roblox map or description;
- target camera/use case;
- intended performance tier.

Helpful additional inputs:

- unedited gameplay captures from multiple angles;
- indoor and outdoor views;
- view toward and away from the sun;
- same scene at different graphics quality;
- video showing camera movement;
- known map dimensions/materials;
- Roblox experience URL;
- target place file or settings dump.

## 2. Source triage

For each image record:

- provenance and URL/file;
- likely capture type: raw gameplay, Studio, thumbnail, cinematic, edited marketing art, video frame;
- resolution, crop, compression, overlays;
- probable graphics quality/platform;
- apparent time/weather/scene state;
- whether it belongs to the same lighting cluster as other images.

Do not average daytime, sunset, night, indoor, event, and thumbnail-grade images into one impossible setup.

## 3. Build an observation sheet before naming Roblox properties

Describe visible evidence in renderer-neutral language:

### Camera and composition

- horizon height;
- vanishing points and perspective strength;
- vertical convergence;
- camera elevation/tilt/roll;
- likely FOV range;
- crop/aspect ratio;
- motion blur or depth blur;
- focal subject and distance.

### Luminance and dynamic range

- darkest readable region;
- brightest unclipped region;
- clipped whites/highlights;
- crushed blacks;
- midtone placement;
- lit-to-shadow ratio on similar materials;
- sky-to-ground luminance ratio.

### Directional light

- cast-shadow direction(s);
- shadow length relative to known object height;
- shadow edge softness;
- lit face vs shadow face colors;
- rim/backlight cues;
- specular highlight direction;
- sun/moon disc or ray visibility.

### Environment and air

- zenith/horizon sky colors;
- cloud cover and density;
- distant contrast loss;
- distance hue shift;
- horizon silhouette/blending;
- glare around sun;
- fog onset and full-obscuration estimate.

### Local lights

- visible fixtures;
- pools of light;
- cone boundaries;
- localized inverse-distance falloff;
- colored spill on neighboring surfaces;
- multiple shadow directions;
- reflections of unseen sources.

### Materials and post

- rough vs sharp highlights;
- metallic reflection behavior;
- emissive-looking surfaces;
- bloom radius/threshold cues;
- global tint/white balance;
- saturation and contrast;
- depth of field;
- vignette-like composition even if Roblox has no direct built-in vignette effect;
- possible external editing.

Each observation receives confidence, plausible alternatives, and confounders using `assets/observation.schema.json`.

## 4. Camera-first matching

A wrong camera can make correct lighting look wrong.

### Estimate FOV qualitatively

- Strong size change with distance, exaggerated near objects, wide visible field: likely wide FOV.
- Compressed depth and flatter perspective: likely narrow FOV/telephoto-like.
- Use architecture vanishing lines and known avatar proportions when available.

Do not infer exact FOV from a cropped image without original sensor/view information. Start with a range such as 55–75°, render, then refine.

### Match viewpoint

Align:

- horizon and camera height;
- yaw/pitch/roll;
- focal subject screen position;
- large silhouette boundaries;
- major occluders;
- aspect/crop.

Only after the mask/silhouette alignment is credible should pixel metrics influence lighting.

## 5. Infer global light direction

### From cast shadows

For a vertical object on a level ground plane:

- the ground shadow points approximately opposite the horizontal projection of the incoming light;
- if object height `h` and shadow length `L` are known, sun elevation can be estimated as `atan(h / L)`.

But reduce confidence when:

- object height is unknown;
- ground is sloped;
- shadow is truncated/off-frame;
- perspective is not corrected;
- light is local rather than directional;
- the screenshot has blur/compression;
- multiple lights overlap.

### Multi-cue fusion

Combine:

- several cast shadows;
- lit/shadowed building faces;
- specular highlights;
- rim lighting;
- sky/sun disc;
- cloud silver lining;
- local fixture orientation.

A single weak cue should not dictate time of day.

### Map to Roblox

1. Estimate desired world-space incoming direction range.
2. In Studio or generated search code, sample `ClockTime` and `GeographicLatitude`.
3. Query `Lighting:GetSunDirection()`.
4. Minimize angular error to the hypothesis.
5. Render candidate views because the same direction can imply different sky/time color cues.

Keep at least two time/latitude candidates if the screenshot lacks sky evidence.

## 6. Infer shadow softness and fill

### Shadow softness

Observe penumbra width relative to shadow size. Distinguish:

- true soft global shadow;
- object lifted far from receiver;
- anti-aliasing/upscaling blur;
- depth of field/motion blur;
- low-resolution compression;
- semi-transparent occluder.

Map to `ShadowSoftness` as a range under Realistic lighting, then validate at the target graphics quality.

### Key-to-fill ratio

Sample or visually compare similar neutral surfaces facing the key and in shadow. A high ratio means dramatic/dark shadow; a low ratio means bright fill/flatness.

Map causes in this order:

1. EnvironmentDiffuseScale.
2. OutdoorAmbient/Ambient.
3. skybox brightness/color.
4. local fill lights.
5. ExposureCompensation only for global placement.
6. ColorCorrection Contrast only after scene lighting works.

Do not lift black level with Ambient and then restore drama with high Contrast; this often creates muddy mids and clipped extremes.

## 7. Infer exposure, white balance, and tone

### Exposure

Look for:

- sky clipped while ground is readable;
- white objects retaining or losing texture;
- emissive sources clipping;
- deep-shadow detail;
- histogram position when available.

Use Brightness/local intensity to establish source relationships. Use `ExposureCompensation` for whole-image placement. Treat one-step changes as large because exposure is measured in stops.

### White balance/color cast

Separate:

- warm/cool source light;
- blue/warm sky fill;
- Atmosphere Color/Decay;
- colored materials;
- ColorShift;
- ColorCorrection TintColor;
- external image grading.

Use nominally neutral surfaces in both lit and shadow zones. A global cast affecting everything suggests grading/white balance; different casts in lit and shadow zones suggest key/fill color separation.

### Tone mapping and contrast

Test current Default tonemapping first. Consider Retro only when the reference genuinely has the older compressed/bright Roblox response. Use ColorCorrection Contrast after exposure and light balance. Report external vignette/film effects as non-native if no direct Roblox equivalent is used.

## 8. Infer atmosphere and fog

Use depth-layer comparisons:

- foreground edge contrast;
- midground edge contrast;
- far landmark contrast;
- hue shift with distance;
- sky/terrain boundary;
- visibility of dark objects against sky.

Mapping:

- stronger continuous contrast loss → Atmosphere Density/Haze;
- distant blend into sky → lower Offset, subject to ghosting;
- strong dark silhouette against bright horizon → higher Offset;
- glow around visible sun → Atmosphere Glare + Haze;
- simple uniform distance fade → consider legacy fog, especially for retro references;
- volumetric-looking local shafts → may need Beams/particles/local effects, not global Atmosphere alone.

Estimate depth in map-relative terms. “Fog starts after two building blocks” is more useful than a false exact stud number when scale is unknown.

## 9. Infer local lights and emissive behavior

A local light is likely when:

- brightness falls off around a fixture;
- nearby surfaces receive colored spill;
- shadows diverge from a point/cone;
- a bounded cone/pool is visible;
- reflections show a bright nearby source.

Choose:

- PointLight for omnidirectional pool;
- SpotLight for a cone/flashlight/headlight;
- SurfaceLight for a panel/window/screen/strip.

Separate visual source from illumination:

- bright Neon with no spill → material/bloom only;
- colored spill without visible fixture → hidden light or reflected source;
- glowing particles/beam → particle appearance may use LightEmission but still need a local light for surface spill.

Position local lights relative to target geometry, not screenshot pixels.

## 10. Infer reflections and material response

Before changing lighting, estimate whether the target has:

- metallic vs dielectric material;
- rough vs glossy surface;
- normal-map microstructure;
- reflection of skybox vs local source;
- screen-space bright patch mistaken for light.

Adjustment order:

1. material base color;
2. metalness;
3. roughness;
4. normal maps;
5. skybox/environment orientation;
6. EnvironmentSpecularScale;
7. local source placement/intensity;
8. exposure.

A lighting-only match cannot reproduce a reference rendered with incompatible materials.

## 11. Parameter-estimation table

| Image evidence | Primary Roblox controls | Secondary controls/confounders |
|---|---|---|
| Parallel cast shadows | ClockTime, GeographicLatitude, GlobalShadows | camera transform, ground slope, local sun-like light impossible in standard setup |
| Broad/narrow penumbra | ShadowSoftness | receiver distance, blur, quality tier |
| Bright shadow regions outdoors | EnvironmentDiffuseScale, OutdoorAmbient | skybox, exposure, material albedo |
| Bright interiors everywhere | Ambient, local fills | wall leaks, exposure |
| Strong metal/sky reflections | EnvironmentSpecularScale | roughness, metalness, skybox |
| Overall clipped/underexposed image | ExposureCompensation | Brightness, local brightness, external edit |
| Distant contrast loss | Atmosphere Density/Haze | legacy FogStart/FogEnd, depth of field |
| Distant blend/silhouette | Atmosphere Offset | sky value, map LOD |
| Sun halo | Atmosphere Glare/Haze, SunRaysEffect | Bloom, skybox baked sun |
| Highlight bleed | Bloom Threshold/Size/Intensity | Neon, external glow, image resampling |
| Global color cast | ColorCorrection TintColor | sky, Atmosphere, material palette, key/fill colors |
| High/low global contrast | ColorCorrection Contrast | source ratio, exposure, tone mapper |
| Blurred near/far planes | DepthOfFieldEffect | motion blur, screenshot edit, low resolution |
| Local colored pool | Point/Spot/SurfaceLight | Decal/texture color, bloom only |
| Bright panel with directional spill | SurfaceLight | SpotLight on Attachment |
| Cone beam | SpotLight plus optional Beam/particles | Atmosphere/Haze required to see air shaft |

## 12. Confidence model

Use four levels:

- **0.80–1.00 High:** repeated direct cue with known geometry; e.g., several clear parallel shadows and visible sun.
- **0.55–0.79 Medium:** multiple compatible cues but unknown scale/material/camera.
- **0.30–0.54 Low:** one weak cue or significant confounders.
- **0.00–0.29 Speculative:** no direct cue; a starting hypothesis only.

Do not allow confidence to increase merely because a numeric estimate is precise. Precision without observability is false confidence.

For each parameter, preserve:

```json
{
  "parameter": "Lighting.ShadowSoftness",
  "estimate": {"min": 0.25, "preferred": 0.4, "max": 0.6},
  "confidence": 0.58,
  "evidence": ["cast shadow edges span roughly 2-4% of shadow width"],
  "confounders": ["JPEG blur", "unknown object-to-ground separation"],
  "next_view": "same object at higher resolution with ground contact visible"
}
```

## 13. Hypothesis generation

Create 1–3 whole-scene explanations, for example:

- H1: low warm sun + cool sky fill + medium Atmosphere + restrained warm grade.
- H2: higher neutral sun + strongly warm ColorCorrection + dense haze.
- H3: overcast sky + no direct visible sun + warm local practicals.

Reject hypotheses that require incompatible cues or extreme compensations. Rank by:

- evidence fit;
- number of assumptions;
- Roblox feasibility;
- map/gameplay compatibility;
- performance cost.

## 14. Iterative image-comparison loop

### Required fixed conditions

- same target camera and aspect ratio;
- same map state/geometry;
- same graphics quality;
- same UI visibility;
- same resolution and crop;
- same dynamic object positions where possible.

### Region masks

Compare separately:

- sky;
- distant background;
- midground;
- focal subject/player;
- ground and cast shadows;
- emissive/local-light regions;
- UI-excluded gameplay frame.

### Useful diagnostics

- mean/percentile luminance;
- black/white clipping percentage;
- RGB and luminance histogram distance;
- average color cast in neutral patches;
- edge/silhouette mismatch;
- shadow-mask direction/area;
- bloom-mask radius and intensity;
- fog contrast by depth layer;
- perceptual comparison by a vision model with explicit rubric.

Run `scripts/image_metrics.py` for lightweight diagnostics. Do not optimize a single scalar blindly; a low error can come from blurring or flattening the image.

### Coordinate-descent schedule

1. Camera/silhouette.
2. Sun direction and time.
3. Exposure/luminance.
4. Fill and shadows.
5. Atmosphere/depth.
6. Material/reflection corrections.
7. Local lights.
8. Global color/contrast/saturation.
9. Bloom/sun rays/DOF.
10. Fine accents.

At each step:

- vary one parameter family across 3–5 candidates;
- render fixed views;
- score regions and inspect visually;
- retain the best candidate;
- narrow the range;
- backtrack if later changes require extreme compensation.

## 15. Distinguish lighting from non-lighting failures

| Mismatch | Likely non-lighting cause | Test |
|---|---|---|
| Shadows align but subject proportions differ | camera/FOV/geometry | overlay silhouettes with flat unlit colors |
| Highlight position wrong on only one asset | normals/material/roughness | replace with neutral material and compare |
| Far object too large/small | camera/FOV/depth placement | match bounding boxes before fog |
| Interior too bright near wall seams | geometry leak | inspect shell thickness and gaps with local lights off |
| Source glows but no surface spill | bloom/Neon only | disable Bloom and inspect receiving surfaces |
| Whole image warm, shadows and highlights equally | grade/white balance | neutralize ColorCorrection and inspect key/fill colors |
| Background soft but foreground edges sharp | DOF/fog | inspect whether blur follows depth or merely contrast loss |
| Pixel error high at moving foliage/particles | dynamic state | mask those regions |

## 16. Single-image limitations

A single image usually cannot reveal exactly:

- original camera FOV, crop, or exposure;
- whether the screenshot was edited;
- hidden lights and their positions;
- material albedo/roughness/metalness maps;
- object dimensions and ground slope;
- baked/global illumination from another engine;
- tone mapper/camera response curve;
- weather animation state;
- quality tier/platform;
- lighting behavior from other viewpoints;
- whether a glow is physically illuminating geometry;
- what lies outside the frame.

A different engine may use baked lightmaps, volumetric GI, area lights, ray tracing, temporal exposure, reflection probes, or LUTs that Roblox cannot reproduce exactly. Translate the perceptual effect rather than promising parameter equivalence.

## 17. Most informative additional views

After the first pass, request only views with high information gain:

1. same scene facing roughly 90° away;
2. view toward the sun/brightest sky;
3. contact-shadow view with known-size object;
4. interior looking out and exterior looking in;
5. neutral gray/white surface under the same lighting;
6. short gameplay video showing movement and exposure stability;
7. low and high graphics captures.

Explain what ambiguity each view resolves.

## 18. Stopping criteria

Stop when:

- camera/silhouette is acceptably aligned;
- dominant light direction and shadow character match within the uncertainty range;
- luminance and clipping are within target tolerances;
- sky/atmosphere depth and major color relationships are visually consistent;
- focal and gameplay regions pass readability gates;
- further metric gains require incorrect materials/geometry, excessive post effects, or unacceptable cost;
- residual differences are documented as engine/source/asset uncertainty.

Deliver the best hypothesis, alternatives, confidence ledger, remaining mismatches, and next high-value evidence.
