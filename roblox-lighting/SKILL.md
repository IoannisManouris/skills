---
name: roblox-lighting
description: >-
  Use this skill whenever a user wants to create, improve, audit, debug, optimize, script, or reproduce Roblox scene lighting/illumination—often misspelled "lightning"—including the Lighting service, Atmosphere, Sky, Clouds, shadows, PointLight, SpotLight, SurfaceLight, PBR response, fog, post-processing, day/night looks, genre or map art direction, player readability, and mobile performance. Also use it to match another game's lighting from one or more screenshots. When a Roblox experience link is supplied, research its public gameplay media and find visually consistent references before estimating settings. Do not use it for electrical lightning-bolt VFX unless scene illumination is also requested.
license: MIT
metadata:
  author: IoannisManouris
  version: "1.0.0"
  last-verified: "2026-08-24"
  domain: roblox-scene-lighting
  compatibility: "Portable Agent Skills specification. Works best with image vision, web/image search, filesystem access, and Python 3.10+. Pillow is optional. Roblox Studio access, a Studio plugin, or a Studio MCP improves direct implementation; otherwise produce a validated plan and Studio-ready Luau."
---

# Roblox Lighting Director

## Mission and terminology

Create Roblox **lighting**: illumination, atmosphere, shadows, reflections, and post-processing. Treat “lightning” as a common misspelling in scene-lighting requests, but do not confuse the task with electrical bolts or storms.

Operate as a lighting director, technical artist, gameplay designer, and performance engineer. The target is not merely a pretty still image. The result must support the map, genre, gameplay, camera, player comfort, accessibility, and target devices.

The research report that motivated this skill is the technical scope: cover the current Lighting service and related instances; map- and genre-aware design; player experience; optimization; a repeatable from-scratch workflow; and confidence-aware inverse rendering from screenshots.

## Choose the operating mode

Select one primary mode without asking the user to restate information already supplied:

1. **FROM_SCRATCH** — Build a coherent look from genre, map, art direction, gameplay, and device targets.
2. **MATCH_SCREENSHOT** — Reconstruct the visible lighting look from one or more reference images.
3. **LINK_ASSISTED_MATCH** — A Roblox URL plus a screenshot or named experience. Research public media, group references by lighting condition, then run screenshot matching.
4. **IMPROVE_OR_DEBUG** — Diagnose an existing place, settings dump, script, screenshot, or described visual problem.
5. **AUDIT_OR_OPTIMIZE** — Preserve the art direction while improving readability, fairness, scalability, or render cost.

A request can combine modes. For example, use LINK_ASSISTED_MATCH to infer the target, then FROM_SCRATCH to adapt that look to a different map.

## Load only the references needed

- Current classes, properties, interactions, and deprecations: [references/roblox-lighting-api.md](references/roblox-lighting-api.md)
- Full from-scratch workflow: [references/from-scratch.md](references/from-scratch.md)
- Single/multi-image reconstruction algorithm: [references/screenshot-matching.md](references/screenshot-matching.md)
- Roblox URL research and media clustering: [references/roblox-link-research.md](references/roblox-link-research.md)
- Genre starting hypotheses: [references/genre-recipes.md](references/genre-recipes.md)
- Map design and player-experience rules: [references/map-player-experience.md](references/map-player-experience.md)
- Performance, scalability, and validation: [references/performance-validation.md](references/performance-validation.md)
- Symptom-based troubleshooting: [references/debugging.md](references/debugging.md)
- Required deliverables and schema: [references/output-contract.md](references/output-contract.md)
- Research provenance and update checks: [references/sources.md](references/sources.md)
- Traceability from the originating research report to skill components: [references/report-traceability.md](references/report-traceability.md)

## Capability check and autonomy policy

At the start, inventory available capabilities: image understanding, web search, image search, browser, local files, Python, Roblox Studio, Studio MCP/plugin, screenshots, and profiler/device-emulation access.

Proceed with the strongest available path:

- With Studio control, inspect and edit the place non-destructively, then capture comparison views.
- Without Studio control, emit a complete JSON plan plus generated Luau and a short manual checklist.
- With a screenshot, infer a range and confidence for each parameter rather than inventing exact values.
- With a Roblox URL, research public experience media before matching.
- With sparse inputs, make explicit assumptions and produce a useful first pass. Ask for more views only after completing the best possible single-image result.
- Never claim a perfect copy from one image. State what is observable, inferred, ambiguous, and unidentifiable.

## Mandatory end-to-end workflow

### 1. Define success before touching settings

Record:

- mode and desired mood;
- genre and core actions;
- camera type/FOV tendencies;
- map scale, indoor/outdoor structure, traversal routes, landmarks, hazards, enemies, and interactables;
- art style, palette, materials, terrain, sky/weather, and time-of-day intent;
- target platforms and minimum acceptable quality tier;
- reference views and whether the goal is pixel similarity, style transfer, or gameplay adaptation.

Define measurable gates: focal hierarchy, route readability, hazard visibility, no unintended clipping, acceptable shadow/light cost, and screenshot similarity where relevant.

### 2. Establish a source ledger

For every reference, store URL/file, source type, capture date if known, likely authenticity, lighting cluster, and usefulness. Give highest weight to user-provided unedited gameplay captures, then official gameplay media, then creator videos, then third-party media. Treat thumbnails and promotional images as potentially edited.

For Roblox links, follow [references/roblox-link-research.md](references/roblox-link-research.md). Use `scripts/research_roblox_game.py` for official public metadata/media, supplement it with available web/image search, then use `scripts/cluster_images.py` to rank and group candidate captures by broad lighting state. Never bypass authentication, scrape private data, or infer hidden place settings from inaccessible sources.

### 3. Decompose the image or scene before estimating lighting

Keep these layers separate:

- camera: viewpoint, FOV, projection, crop, motion blur, exposure-like edits;
- geometry: scale, wall thickness, openings, occluders, normals;
- materials: base color, roughness, metalness, texture, emissive/Neon appearance;
- global illumination: sun/moon, sky/environment fill, ambient balance, shadows;
- participating media: Atmosphere/fog, clouds, aerial perspective;
- local lights: position, type, direction, range, color, brightness, shadows;
- post-processing: tone/color, bloom, sun rays, blur, depth of field;
- non-lighting accents: particles, beams, highlights, UI.

Do not compensate for a wrong camera, material, or geometry with extreme lighting values.

### 4. Extract observations with confidence and ranges

Use `assets/observation.schema.json`, then run `python scripts/validate_observations.py observations.json`. For every observation include:

- evidence visible in the image or place;
- inferred cause;
- confidence from 0 to 1;
- plausible range or alternatives;
- confounders;
- which extra view would reduce uncertainty most.

For screenshot work, infer at least: sun direction/elevation, shadow softness, key-to-fill ratio, sky/horizon color, ambient cast, exposure/dynamic range, white balance, contrast/saturation, fog depth/color, bloom, local light cues, reflections/specular response, time-of-day cues, and indoor/outdoor balance.

### 5. Build hypotheses in dependency order

Create 1–3 coherent hypotheses, not dozens of disconnected settings. Each hypothesis should explain the major cues and honor Roblox constraints. Rank them by evidence, expected gameplay quality, and implementation cost.

Use the following order because later controls can mask earlier mistakes:

1. camera/framing equivalence;
2. `LightingStyle` and tonemapper choice;
3. skybox, celestial bodies, `ClockTime`, `GeographicLatitude`;
4. sun direction, global shadows, shadow softness;
5. global intensity/exposure and ambient/environment balance;
6. Atmosphere/fog and Clouds;
7. geometry/material corrections required for believable response;
8. local lights and emissive accents;
9. color grading and restrained post-processing;
10. quality-tier and performance behavior.

### 6. Create and validate a machine-actionable plan

Write `lighting-plan.json` against `assets/lighting-plan.schema.json`. Include intent, assumptions, confidence, global settings, child instances, local lights, quality tiers, validation views, metrics, and unresolved ambiguities. For a first-pass genre scaffold, run `scripts/scaffold_plan.py`; treat its values as hypotheses, never as universal presets.

Run:

```bash
python scripts/validate_plan.py lighting-plan.json
python scripts/generate_luau.py lighting-plan.json --output apply_roblox_lighting.lua
# After reviewing existing Sky/Atmosphere/Clouds/post effects, deterministic replacement is optional:
python scripts/generate_luau.py lighting-plan.json --output apply_roblox_lighting.lua --replace-conflicts
```

Fix errors. Treat warnings as review prompts, not automatic failures.

### 7. Implement non-destructively

Before editing a place:

- save or duplicate the place;
- run `assets/audit-current-lighting.lua` when a machine-readable current-state dump is useful;
- capture current Lighting properties and the affected Lighting/Terrain/local-light state into a backup;
- tag skill-created instances with `RobloxLightingManaged = true` and a plan ID;
- update only managed instances unless the plan explicitly authorizes replacement;
- use `pcall` around rollout, hidden, deprecated, or non-scriptable properties;
- keep local light placement semantic: attach lights to the actual fixture or an Attachment, not arbitrary world coordinates when avoidable.

The generated Luau follows this policy. Its default preserves unmanaged global instances and warns about conflicts; `--replace-conflicts` backs up and replaces matching global classes for deterministic reproduction. `assets/restore-backup.lua` restores the newest backup or a named backup. Remove any separately installed Camera LocalScript during rollback.

### 8. Compare and iterate systematically

Capture the same camera views at the same resolution and graphics tier. Use masks or crops to compare sky, ground, focal subject, and shadow regions separately. Run:

```bash
python scripts/image_metrics.py reference.png candidate.png --json comparison.json --diff diff.png
```

Metrics diagnose; they do not replace visual judgment. Iterate in coarse-to-fine coordinate descent:

1. camera and dominant light direction;
2. luminance/exposure and clipping;
3. shadow/fill balance;
4. atmosphere and depth separation;
5. local sources and material response;
6. color cast/contrast/saturation;
7. bloom, sun rays, and depth of field;
8. small accents.

Change one control family at a time. Keep an experiment log: parameter delta, expected visual effect, observed effect, metric delta, gameplay effect, keep/revert.

### 9. Validate as a game, not a screenshot

Test representative gameplay states, not only a beauty angle:

- spawn and onboarding;
- primary traversal route;
- hazard/combat/readability stress scene;
- indoor/outdoor transition;
- darkest and brightest reachable locations;
- moving camera and fast motion;
- UI over the scene;
- low, medium, and high graphics quality;
- low-end mobile emulation or real device where possible.

Reject a visually accurate match if it hides hazards, silhouettes players unfairly, causes eye strain, destroys UI contrast, depends on high-only shadows, or produces unstable frame pacing.

### 10. Deliver complete, reproducible outputs

Follow [references/output-contract.md](references/output-contract.md). At minimum provide:

- concise creative/technical rationale;
- evidence and assumptions with confidence;
- `lighting-plan.json`;
- Studio-ready Luau or direct non-destructive edits;
- hierarchy/placement instructions for local lights;
- quality-tier strategy;
- validation results and remaining mismatches;
- rollback instructions;
- source ledger for link-assisted research.

## Screenshot-matching decision summary

Use the complete algorithm in [references/screenshot-matching.md](references/screenshot-matching.md). The minimum decision sequence is:

1. **Can the camera be approximated?** Match horizon, verticals, framing, and FOV before lighting.
2. **Are cast-shadow edges visible?** Their direction estimates the projected sun direction; relative object/shadow length constrains elevation only when geometry and ground slope are known. Use `assets/sun-direction-search.lua` to solve candidate `ClockTime`/`GeographicLatitude` values after estimating a target direction.
3. **Is the key source global or local?** Parallel shadows across the scene imply sun/moon; diverging shadows or localized falloff imply nearby lights.
4. **How bright are nominally shaded neutral surfaces?** This constrains ambient/environment fill and key-to-fill ratio.
5. **Do distant objects lose contrast or shift hue?** Infer Atmosphere/fog density, color, decay, and depth onset.
6. **Do bright pixels bleed without illuminating nearby surfaces?** Infer bloom/emissive appearance; do not mistake it for physical light.
7. **Do shiny surfaces reflect the sky strongly?** Tune material roughness first, then `EnvironmentSpecularScale`.
8. **Is the whole image warm/cool or selectively colored?** Separate source color, Atmosphere, material palette, and global color grading.
9. **Are highlights/shadows clipped?** Adjust intensity/exposure before increasing contrast.
10. **Which evidence conflicts?** Keep multiple hypotheses and request the most informative additional angle after producing the first pass.

## From-scratch design summary

Use [references/from-scratch.md](references/from-scratch.md) and [references/genre-recipes.md](references/genre-recipes.md). Begin from a neutral, readable baseline. Design a hierarchy of environment/key, fill, focal/accent, and practical local lights. Make routes and interactive objects legible through value, color, silhouette, and contrast—not bloom alone. Tune Atmosphere for depth scale, not as a blanket to hide weak composition. Add post-processing last.

## Quality gates

A plan is not complete until all applicable gates pass:

- **Intent:** settings form one explainable art direction.
- **Evidence:** screenshot-derived claims cite visible cues and confidence.
- **Separation:** camera/material/geometry errors are not disguised as lighting.
- **Readability:** player, route, hazards, enemies, and interactables remain legible.
- **Comfort:** no pervasive clipped whites, crushed blacks, flicker, excessive blur, or full-screen bloom.
- **Fairness:** competitive visibility does not depend on monitor brightness or high graphics shadows.
- **Map fit:** lighting supports scale, transitions, landmarks, and pacing.
- **Roblox validity:** current classes/properties are used; deprecated behavior is flagged.
- **Performance:** shadowed/overlapping local lights are justified and quality tiers are tested.
- **Reproducibility:** plan, script, source ledger, experiment log, and rollback path exist.

## Non-negotiable gotchas

- `Lighting.Technology` is legacy/deprecated; prefer the current `LightingStyle` workflow and re-check current docs before implementation.
- An `Atmosphere` changes or supersedes legacy Lighting fog behavior; do not tune both blindly.
- `Brightness` changes emitted intensity, not a local light's coverage; use `Range`/`Angle` for coverage.
- Neon-looking material and bloom are not reliable substitutes for local illumination.
- Multiple `ColorCorrectionEffect` objects compose, but multiple `ColorGradingEffect` objects do not behave as a stack; keep one authoritative color-grading effect.
- Global depth of field is usually unsuitable for active gameplay unless deliberately camera-local and state-controlled.
- Tiny shadow-casting details may be visually unreliable and expensive relative to their value.
- Roblox thumbnails may be edited or captured under a different lighting state. Cluster references instead of averaging incompatible conditions.
- A one-image match is underdetermined. Report ranges and alternatives; never invent source settings as facts.
