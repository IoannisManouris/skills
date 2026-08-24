# Research Sources and Update Checklist

**Last verified:** 2026-08-24

The skill was structured according to the open Agent Skills specification and current skill-authoring practices, and its technical scope follows the Roblox lighting research report requested by the user.

## Agent Skills specification and authoring

- Agent Skills specification: `https://agentskills.io/specification`
- Agent Skills overview: `https://agentskills.io/`
- OpenAI Skills in ChatGPT: `https://help.openai.com/en/articles/20001066-skills-in-chatgpt`
- OpenAI Codex app / skills overview: `https://openai.com/index/introducing-the-codex-app/`
- OpenAI curated skill examples: `https://github.com/openai/skills`
- OpenAI Codex skill metadata examples: `https://github.com/openai/codex/tree/main/.codex/skills`
- Public Agent Skills examples: `https://github.com/anthropics/skills`
- Official skill-creator example: `https://github.com/anthropics/claude-plugins-official/blob/main/plugins/skill-creator/skills/skill-creator/SKILL.md`

Important points to re-check:

- allowed frontmatter keys and field limits;
- folder-name matching;
- recommended SKILL.md size;
- official validator command;
- Codex `agents/openai.yaml` fields and implicit-invocation policy;
- upload/install behavior and product eligibility;
- eval schema/tooling compatibility.

## Official Roblox environment and API documentation

Primary:

- Environment/lighting overview: `https://create.roblox.com/docs/environment`
- Global lighting: `https://create.roblox.com/docs/environment/lighting`
- Lighting API: `https://create.roblox.com/docs/reference/engine/classes/Lighting`
- Atmosphere guide: `https://create.roblox.com/docs/environment/atmosphere`
- Atmosphere API: `https://create.roblox.com/docs/reference/engine/classes/Atmosphere`
- Skyboxes: `https://create.roblox.com/docs/environment/skyboxes`
- Sky API: `https://create.roblox.com/docs/reference/engine/classes/Sky`
- Dynamic clouds: `https://create.roblox.com/docs/environment/clouds`
- Clouds API: `https://create.roblox.com/docs/reference/engine/classes/Clouds`
- Light sources: `https://create.roblox.com/docs/environment/light-sources`
- PointLight API: `https://create.roblox.com/docs/reference/engine/classes/PointLight`
- SpotLight API: `https://create.roblox.com/docs/reference/engine/classes/SpotLight`
- SurfaceLight API: `https://create.roblox.com/docs/reference/engine/classes/SurfaceLight`
- Light base API: `https://create.roblox.com/docs/reference/engine/classes/Light`
- Post-processing: `https://create.roblox.com/docs/environment/post-processing-effects`
- BloomEffect: `https://create.roblox.com/docs/reference/engine/classes/BloomEffect`
- BlurEffect: `https://create.roblox.com/docs/reference/engine/classes/BlurEffect`
- ColorCorrectionEffect: `https://create.roblox.com/docs/reference/engine/classes/ColorCorrectionEffect`
- ColorGradingEffect: `https://create.roblox.com/docs/reference/engine/classes/ColorGradingEffect`
- DepthOfFieldEffect: `https://create.roblox.com/docs/reference/engine/classes/DepthOfFieldEffect`
- SunRaysEffect: `https://create.roblox.com/docs/reference/engine/classes/SunRaysEffect`
- SurfaceAppearance: `https://create.roblox.com/docs/reference/engine/classes/SurfaceAppearance`
- MaterialVariant: `https://create.roblox.com/docs/reference/engine/classes/MaterialVariant`
- ParticleEmitter: `https://create.roblox.com/docs/reference/engine/classes/ParticleEmitter`
- Improve performance: `https://create.roblox.com/docs/performance-optimization/improve`
- MicroProfiler: `https://create.roblox.com/docs/studio/microprofiler`
- Device emulator: `https://create.roblox.com/docs/studio/testing-modes#device-emulation`
- Performance dashboard: `https://create.roblox.com/docs/production/analytics/performance`
- Thumbnails/media: `https://create.roblox.com/docs/production/promotion/experience-thumbnails`
- Roblox Open Cloud/API reference: `https://create.roblox.com/docs/cloud`

## Public Roblox metadata/media endpoints

These are used as best-effort public research helpers and must be re-verified:

- Place-to-universe resolver: `https://apis.roblox.com/universes/v1/places/{placeId}/universe`
- Game metadata: `https://games.roblox.com/v1/games?universeIds={universeId}`
- Experience media: `https://games.roblox.com/v2/games/{universeId}/media`
- Thumbnail delivery endpoints under `https://thumbnails.roblox.com/`

Endpoint availability, authentication, parameter rules, and response shape can change. The bundled script records failures and never bypasses authentication.

## Inverse rendering / single-image illumination research

The procedures are informed by the general research finding that single-image lighting recovery is underdetermined and benefits from combining multiple weak cues and separating lighting, materials, geometry, and camera response. Representative research directions include:

- Single outdoor image illumination estimation using sky, vertical surfaces, and ground cues.
- Deep sky/environment illumination estimation from one outdoor image.
- Structure-aware single-image indoor lighting estimation.
- Spatially varying indoor illumination recovery.
- Inverse rendering that jointly reasons about materials, lighting, and camera response.
- Depth-aware cast-shadow reasoning for outdoor relighting.

Use primary papers/official project pages when updating this reference. Do not treat any learned inverse-rendering model as recovering exact hidden Roblox settings.

## Required update checks before future releases

1. Compare `Lighting` current property list and deprecations.
2. Check `Enum.LightingStyle` options and property script security.
3. Check `ExtendLightRangeTo120` rollout/scriptability.
4. Verify Atmosphere-vs-fog behavior.
5. Verify ColorGradingEffect parenting/stacking and TonemapperPreset values.
6. Verify post-effect parenting and low-quality behavior.
7. Verify local-light ranges/property bounds.
8. Verify performance shadow cutoff/guidance and profiler scope names.
9. Verify Roblox public metadata/media endpoints.
10. Run skill validator, JSON parsing, Python compile, example plan validation, and trigger/behavior evals.
