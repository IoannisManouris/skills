# Map-Aware Lighting and Player Experience

## 1. Lighting is spatial information

Players read a scene through:

- value groups and contrast;
- silhouettes and contact shadows;
- color-temperature relationships;
- atmospheric depth;
- specular/material cues;
- motion and temporal changes;
- learned visual language.

A technically realistic image can still be a poor game if these cues do not support decisions.

## 2. Map scale

### Small rooms and corridors

- Keep local light ranges close to room boundaries.
- Use fixtures and wall/ceiling bounce-like fill rather than one giant PointLight.
- Seal walls/ceilings to avoid exterior leaks.
- Use repeated pools to establish rhythm and direction.
- Avoid global Atmosphere values that gray every room.

### Medium arenas/hubs

- Establish a dominant landmark and several secondary zones.
- Separate routes by value or temperature.
- Prevent every shop/portal/sign from competing at the same brightness.
- Test the center and perimeter; local-light overlap often peaks in hubs.

### Large open worlds

- Use sun/sky as the primary large-scale system.
- Use Atmosphere for depth-plane separation and scale.
- Preserve distant landmark silhouette and color identity.
- Reserve local lights for settlements, objectives, caves, vehicles, and hero moments.
- Design for StreamingEnabled: local effects should tolerate missing distant geometry and activate by zone.

## 3. Geometry and occlusion

Lighting depends on actual geometry:

- wall/roof thickness;
- gaps and seams;
- surface normals;
- concave spaces;
- transparent layers;
- moving doors/platforms;
- foliage density;
- terrain cavities;
- water surfaces.

Before adding compensating lights, test with neutral materials and local lights disabled. A leak is usually not fixed by darkening Ambient; that harms the whole map.

Use occlusion to compose:

- doorways framing brighter destinations;
- overhangs creating cool transition shade;
- trees/buildings breaking sunlight into rhythm;
- tunnels providing intentional adaptation zones;
- vertical structures catching rim/key light as landmarks.

## 4. Interior/exterior transitions

Analyze both directions:

- interior looking out;
- exterior looking in;
- player crossing slowly;
- player sprinting;
- camera turning during the crossing.

Design goals:

- exterior should not become a flat white rectangle;
- interior should not become black on entry;
- doorway silhouette should remain readable;
- enemies/hazards cannot exploit adaptation;
- UI contrast remains stable.

Use architectural buffer zones, practical fill, and camera-local transitions. Avoid per-player needs being implemented as global Lighting changes.

## 5. Palette-aware lighting

Create a palette matrix:

| Element | Base hue/value | Required distinction | Lighting risk |
|---|---|---|---|
| Player/avatar | variable | background/enemy | global tint or backlight |
| Route | map-specific | scenery/hazard | shadow/fog merge |
| Hazard | semantic | safe surfaces | bloom/clipping/tint |
| Interactable | semantic | decoration | low contrast at low quality |
| Landmark | distinctive | background | atmosphere loss |
| UI/world text | high contrast | all backgrounds | bloom/reflections |

Rules:

- A red hazard in warm sunset light may lose hue contrast; give it value/silhouette support.
- A blue objective in blue fog needs a warm rim, shape cue, or Highlight.
- Saturated materials under saturated source light can clip a color channel and lose texture.
- Skin/avatar colors must remain acceptable in social games.

## 6. Materials and terrain

### Rough/matte surfaces

Read mainly through diffuse value and shadow. Strong specular settings will not create the same cues as on glossy surfaces.

### Glossy/metallic surfaces

Read through environment and source reflections. Match roughness/metalness before changing global specular scale.

### Terrain

- Grass and rock normals create high-frequency shading; overly hard low sun can become noisy.
- Snow/sand/bright terrain can clip under high exposure.
- Dark soil/caves may require local fill rather than raising global Ambient.
- Terrain distance benefits from Atmosphere, but landmarks must survive.

### Water

Water brightness/reflection can dominate vistas. Check sun direction, sky color, and camera angle. Do not grade the whole map merely to fix one water highlight.

## 7. Sightlines and traversal routes

For every primary route, inspect:

- approach view;
- decision point;
- destination view;
- reverse/return view;
- off-route failure view.

Use lighting to answer:

- Where can I go?
- What is safe/dangerous?
- What is interactive?
- What is the next landmark?
- How high/far is the jump?
- Where did the threat/projectile come from?

Use a route heatmap and a light-overlap heatmap when Studio tooling permits.

## 8. Landmarks and focal points

A landmark can be separated by:

- brighter or darker value than surroundings;
- warm/cool contrast;
- rim/edge light;
- atmospheric silhouette;
- unique reflection/emissive pattern;
- repeated local-light rhythm leading toward it.

Do not make a distant landmark depend on tiny detail or high-quality specular. Its silhouette and broad color block must carry identity.

## 9. Enemies, players, and fairness

### PvE

Threats can emerge from darkness, but telegraphing and reaction time must remain fair. Use eye/glow/outline/audio only as complements, not excuses for invisible bodies.

### PvP

Audit:

- dark and bright avatar outfits;
- all team spawn directions;
- backlit doorways/windows;
- camouflage against dominant materials;
- low graphics where shadows disappear;
- color-vision deficiencies;
- monitor brightness/gamma variation.

Competitive silhouettes should not depend on bloom, tiny rim lights, or subtle hue differences alone.

## 10. Interactables and rewards

Use a visual language:

- one accent family for interactables;
- one stronger family for rare rewards;
- stable shape/icon/prompt support;
- light/Highlight intensity proportional to importance.

Avoid “rarity inflation” where normal objects glow like legendary rewards.

## 11. Visual hierarchy

Rank scene elements. A practical luminance allocation concept:

- Focal subject: strongest local contrast, not always highest absolute brightness.
- Route/hazard: clear functional contrast.
- Secondary landmarks: medium contrast.
- Background: reduced contrast/detail through fill/atmosphere.

A focal object can be dark against a bright field or bright against a dark field. Use local contrast and isolation.

## 12. Player comfort and eye strain

Avoid:

- frequent hard transitions between near-black and clipped white;
- full-screen intense saturated color for long periods;
- excessive bloom around UI-sized elements;
- persistent blur/DOF in active play;
- rapid high-contrast flicker;
- SunRays/glare covering the center of common sightlines;
- crushed blacks requiring players to increase display brightness;
- over-sharpened/noisy shadow patterns during camera motion.

Use gradual transitions, protected midtones, and stateful effects. Test in a dim and bright room when possible.

## 13. Accessibility

Do not encode important state through hue alone. Combine at least two of:

- value/brightness;
- shape/silhouette;
- icon/text;
- motion pattern;
- sound;
- outline/Highlight;
- placement.

Check common color-vision simulations and grayscale. Ensure flashing content follows platform safety and accessibility guidance.

## 14. Making lighting enjoyable

Players tend to enjoy lighting when it:

- makes them feel competent by revealing actionable information;
- creates anticipation and reward through contrast transitions;
- makes materials/world feel responsive;
- provides beautiful discoveries without obstructing control;
- supports a coherent fantasy;
- changes with meaningful game state rather than randomly;
- preserves visual novelty by reserving the strongest effects for important moments.

Design an emotional curve:

1. readable onboarding;
2. escalating mystery/danger;
3. contrast release at checkpoint/reward;
4. visual landmark for progress;
5. memorable hero lighting at climax;
6. comfortable recovery/social area.

## 15. Gameplay validation rubric

Score 1–5 for each representative view/state:

- route comprehension within two seconds;
- player/enemy silhouette;
- hazard/interactable visibility;
- depth and scale perception;
- material identity;
- focal hierarchy;
- comfort in motion;
- UI contrast;
- low-quality resilience;
- art-direction coherence.

Any score below 3 requires a fix or an explicit design exception.
