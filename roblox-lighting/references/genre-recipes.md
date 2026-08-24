# Genre and Art-Direction Starting Hypotheses

These are **starting hypotheses**, not universal presets. Values interact with sky, geometry, materials, camera, and graphics quality. Use them to choose a direction, then follow the validation loop.

Color triplets are illustrative 0–255 RGB ranges, not exact requirements.

## Shared rules

- Start with restrained post-processing.
- Preserve avatar, route, hazard, and UI readability.
- Establish time/sky/shadows before global grade.
- Use local light ranges only as large as their receiving zones.
- Build a low-quality version that keeps the same hierarchy without relying on dynamic shadows.

## 1. Horror / suspense

### Intended experience

Controlled uncertainty: the player cannot see everything, but can read immediate navigation, threats, doors, and interactables. Darkness should create tension, not random failure.

### Starting hypothesis

- `LightingStyle`: Realistic.
- Time: night, blue hour, enclosed interior, or heavily overcast—not necessarily absolute midnight.
- Global shadows: on for high/medium; design low tier to survive their absence.
- Key-to-fill ratio: high, but minimum shadow detail preserved.
- Ambient: cool and low, roughly RGB 10–35 per channel depending on materials.
- OutdoorAmbient: cool, slightly brighter than deepest interiors where applicable.
- Exposure: usually around −0.8 to 0.0 after source balance.
- Atmosphere: medium density/haze outdoors; use depth to hide distance, not nearby hazards.
- Local lights: warm practical islands, emergency red, cold fluorescent, or flashlight cones.
- Bloom: low, limited to fixtures.
- Color correction: mild desaturation/contrast; avoid crushing black.

### Why it works

Warm practical pools create safe/important zones against cool environmental darkness. Directional shadows create anticipation. Limited visible distance controls pacing.

### Failure modes

- black-on-black enemies;
- bright UI surrounded by near-black causing eye fatigue;
- flickering every light;
- heavy bloom obscuring the threat;
- relying on monitor brightness or high graphics shadows;
- full-screen blue tint that destroys material color.

## 2. Realistic / immersive outdoor

### Intended experience

Coherent sun/sky relationship, plausible PBR response, atmospheric scale, and material identity.

### Starting hypothesis

- `LightingStyle`: Realistic.
- ClockTime: choose from reference; 9–15 for neutral daylight, 6–8 or 16–19 for directional golden light.
- Brightness: often moderate, roughly 2–3 as an initial search band.
- Exposure: roughly −0.4 to +0.4.
- EnvironmentDiffuseScale: 0.7–1.0.
- EnvironmentSpecularScale: 0.7–1.0 for strong PBR response.
- Ambient/OutdoorAmbient: neutral/sky-tinted but restrained.
- ShadowSoftness: approximately 0.2–0.65 depending on weather/time.
- Atmosphere: Density 0.15–0.35, Haze 0.5–2.5 as a broad first search, map-scale dependent.
- Bloom: minimal.
- Color correction: subtle.

### Why it works

The environment contributes both diffuse and specular cues, while a directional sun establishes form. Atmosphere creates aerial perspective rather than a flat fog wall.

### Failure modes

- high exposure plus high brightness plus bright ambient;
- all metals mirror-bright because roughness is wrong;
- skybox sun and Roblox sun disagree;
- over-soft shadows at clear noon;
- fog dense enough to erase landmarks.

## 3. Stylized / cartoon

### Intended experience

Readable shapes, clean color blocks, friendly contrast, and deliberate—not necessarily realistic—light color.

### Starting hypothesis

- `LightingStyle`: Realistic for crisp form or Soft for intentionally flat/retro presentation.
- Time: midmorning/afternoon for clear platform faces.
- Ambient/OutdoorAmbient: brighter and more chromatic than realistic, but low enough to preserve form.
- EnvironmentDiffuseScale: 0.4–0.8.
- Specular: 0.2–0.7 depending on toy/plastic look.
- ShadowSoftness: 0.35–0.8; avoid noisy tiny shadows.
- Atmosphere: low density, saturated but subtle Color if used.
- Bloom: restrained on rewards/Neon only.
- Saturation: modest positive adjustment only after palette review.

### Why it works

Broad readable value groups and soft fill keep forms understandable on small mobile screens. Controlled accent colors lead attention.

### Failure modes

- saturation applied globally until skin/team colors clip;
- every collectible emits a giant glow;
- Ambient so bright that platforms lose depth;
- detailed realistic shadows fighting simple art.

## 4. Simulator / tycoon

### Intended experience

Bright, optimistic, instantly readable progression objects, signage, buttons, currency, and upgrade paths.

### Starting hypothesis

- `LightingStyle`: Realistic or Soft according to art style.
- Time: 9–15, usually stable.
- Fill: medium-high; shadow ratio moderate/low.
- Exposure: near neutral.
- Atmosphere: low, enough for distant separation.
- Local lights: reserve for machines, purchase pads, premium areas, and milestones.
- Bloom: small and thresholded.
- Color correction: slightly bright/saturated, but preserve economic UI contrast.

### Why it works

Players scan many objects quickly. Stable daylight and clear color coding reduce cognitive load and make growth feel rewarding.

### Failure modes

- too many equally glowing upgrade objects;
- reflections/bloom obscuring text;
- dark production interiors;
- day/night cycle changing button readability or product screenshots.

## 5. Obby / platformer

### Intended experience

Landing surfaces, gaps, moving hazards, checkpoints, and depth are readable at speed.

### Starting hypothesis

- `LightingStyle`: Realistic for useful contact shadows; Soft for intentionally classic obby visuals.
- Sun angle: side/front-side to reveal platform thickness without casting confusing long shadows across landings.
- Ambient/fill: high enough that shadowed platform faces remain distinct.
- Atmosphere: low unless distance segmentation is part of the level.
- Bloom/DOF: very low/off during gameplay.
- Hazard colors: protected from global tint.
- Checkpoints: focal accent lights or Highlights that survive low quality.

### Why it works

Contact shadows communicate height and landing. Clear silhouettes and stable values support fast repeated attempts.

### Failure modes

- long moving shadows that look like platforms;
- fog hiding the next jump;
- DOF blurring the target;
- transparent/Neon hazards disappearing in bloom;
- major contrast changes during a day/night cycle.

## 6. FPS / competitive combat

### Intended experience

Fair visibility, fast target acquisition, readable cover/doorways, and no advantage from extreme display settings.

### Starting hypothesis

- `LightingStyle`: Realistic if shadows are not required for enemy visibility.
- Time: stable and chosen to avoid persistent backlight on one team's route.
- Fill: medium; interiors and exterior thresholds controlled.
- Exposure: neutral with protected highlights.
- Atmosphere: low-to-medium; long-range visibility set by gameplay balance.
- Local light colors: restrained around combat silhouettes.
- Bloom, DOF, Blur, SunRays: minimal in active play.
- Quality tiers: enemy silhouettes and target outlines cannot depend on shadows.

### Why it works

Competitive clarity requires consistent contrast across directions, rooms, teams, and device quality.

### Failure modes

- dark skins invisible in corners;
- sunlight/blinding rays through one team's sightline;
- muzzle/emissive bloom covering targets;
- camera exposure pumping between rooms;
- fog/particles creating device-dependent visibility.

## 7. Adventure / RPG

### Intended experience

Distinct biomes, landmarks, emotional pacing, exploration depth, and readable combat/interactions.

### Starting hypothesis

- Build named lighting profiles by biome/state.
- Preserve common avatar/hazard readability across profiles.
- Use time/sky/atmosphere as the large-scale identity.
- Use local practical color to identify settlements, dungeons, magic, and objectives.
- Atmosphere: medium and scale-aware for vistas.
- Color grading: one controlled effect per profile, transitioned deliberately.
- Quality tiers: hero accents may reduce, but landmarks remain visible.

### Why it works

Lighting becomes a navigation and narrative system. Consistent local visual language helps players recognize safety, danger, and magic.

### Failure modes

- every biome using unrelated post-processing with no transition;
- global Lighting changed for one player's interior;
- distant quest landmark lost in fog;
- nighttime combat becoming unreadable.

## 8. Showcase / cinematic / product display

### Intended experience

Premium material response, controlled framing, attractive reflections, and deliberate focus.

### Starting hypothesis

- `LightingStyle`: Realistic.
- EnvironmentDiffuse/Specular: 0.7–1.0 after material calibration.
- Neutral or intentionally colored three-quarter key direction.
- Fill/rim from motivated local sources or sky.
- Exposure protects bright reflections.
- Bloom: low/medium on actual luminous sources.
- Camera-local DOF: acceptable for fixed shots/inspection mode.
- Color correction: subtle, material colors remain trustworthy.

### Why it works

Materials are sold through highlight shape, edge separation, and reflection environment rather than brute brightness.

### Failure modes

- wrong roughness “fixed” with more specular;
- DOF obscuring inspected details;
- clipped chrome/white surfaces;
- reflections showing an incompatible sky;
- beauty camera settings applied to free gameplay.

## 9. Cozy / social / roleplay

### Intended experience

Warmth, safety, flattering avatars, comfortable long sessions, and inviting social zones.

### Starting hypothesis

- Time: warm morning/late afternoon or soft overcast daylight.
- Key-to-fill ratio: low-to-medium.
- Ambient: gentle warm/neutral interior fill.
- Outdoor fill: sky-cool enough to retain depth.
- Local lights: warm pools around seating, shops, homes, and gathering areas.
- Atmosphere: light haze for softness/depth.
- Bloom: subtle.
- Contrast: moderate/low; avoid flatness by retaining edge separation.

### Why it works

Warm practicals and readable faces encourage lingering. Mild cool fill prevents the whole world from becoming orange.

### Failure modes

- yellow tint on every surface/skin;
- no shadows or depth;
- fireplace/lamp bloom covering avatars;
- dark corners in social seating areas.

## 10. Sci-fi / neon / cyberpunk

### Intended experience

Dark structural base, vivid motivated colored accents, readable silhouettes, reflections, and depth.

### Starting hypothesis

- `LightingStyle`: Realistic.
- Global environment: dark neutral/cool with enough fill for navigation.
- Local lights: SurfaceLights on panels/signs, SpotLights for cones, PointLights for cores.
- Color palette: limit to 1–2 dominant accent families plus neutral support.
- Specular: medium-high where PBR surfaces justify it.
- Atmosphere/Haze: enough for depth and beams, not enough to wash all colors together.
- Bloom: thresholded so only sources trigger; moderate Size, restrained Intensity.
- Color correction: protect saturated channel detail.

### Why it works

Colored spill and reflections make Neon feel embedded in the world. A neutral structural base gives accents room to dominate.

### Failure modes

- bloom without colored surface spill;
- every object using a different saturated hue;
- crushed black hiding the map;
- all glossy materials reflecting equally;
- global purple/blue tint replacing source design.

## 11. Racing / driving

### Intended experience

Road edges, braking points, opponents, signage, and horizon remain readable at high speed and changing camera angles.

### Starting hypothesis

- Stable time/weather for competitive modes.
- Sun placed to avoid prolonged direct glare on the main racing line.
- Strong road/edge value separation.
- Moderate atmosphere for scale without hiding turns.
- Night modes use repeated practical pools and reflective markers.
- Headlights use SpotLights with controlled range/angle; avoid huge overlap.
- Bloom/motion effects restrained enough to read signs.

### Failure modes

- alternating clipped sun and black tunnels;
- headlight overlap destroying frame time;
- road and shoulder same value;
- fog hiding braking markers;
- dynamic weather changing fairness.

## 12. Retro / classic Roblox

### Intended experience

Deliberately simple/nostalgic shading and color response, not an accidental low-quality modern scene.

### Starting hypothesis

- `LightingStyle`: Soft or current Retro tonemapper where appropriate.
- Consider `ColorGradingEffect.TonemapperPreset = Retro` after verifying all lights.
- Lower light brightness and simpler fill.
- Minimal Atmosphere/post effects.
- Legacy fog only when the visual language calls for it.
- Crisp palette and uncomplicated practical lighting.

### Failure modes

- mixing Retro tonemapping with high modern brightness values;
- using deprecated `Technology` settings from old tutorials without checking current behavior;
- adding modern heavy bloom/DOF that contradicts the style.

## 13. Profile adaptation rather than copying

When applying a reference game's look to a different genre/map:

1. preserve perceptual relationships: warm/cool split, shadow ratio, atmosphere depth, highlight character;
2. rescale fog/light ranges to the new map dimensions;
3. reduce or relocate darkness around critical gameplay;
4. adapt sun direction to new routes and landmarks;
5. preserve target materials rather than forcing source-game colors;
6. rebuild quality tiers for the new performance budget;
7. report deviations made for gameplay and why.
