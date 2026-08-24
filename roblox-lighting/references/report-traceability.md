# Research Report Traceability

This file maps the technical scope requested in the originating deep-research report to the operational parts of this skill. It exists so future maintainers can verify that simplifying the core `SKILL.md` does not silently remove important report coverage.

| Report requirement | Skill implementation |
|---|---|
| Complete `Lighting` service coverage, current properties, methods, rendering style, limitations, and deprecations | `references/roblox-lighting-api.md`; `assets/audit-current-lighting.lua`; plan validator blocks deprecated `Technology` use and checks current property ranges. |
| Related classes: Atmosphere, Sky, Clouds, local lights, post effects, PBR/material interactions, adjacent visual systems | `references/roblox-lighting-api.md`; `assets/lighting-plan.schema.json`; `scripts/generate_luau.py`. |
| From-scratch method based on genre, map, gameplay, art direction, devices, time, and mood | `references/from-scratch.md`; `references/genre-recipes.md`; `assets/genre-starting-points.json`; `scripts/scaffold_plan.py`. |
| Map-aware design: scale, geometry, interiors/exteriors, palette, materials, terrain, routes, focal points | `references/map-player-experience.md`; material/geometry actions in the plan schema and examples. |
| Player enjoyment, hierarchy, readability, comfort, fairness, navigation, accessibility | `references/map-player-experience.md`; quality gates in `SKILL.md`, output contract, plan schema, and evals. |
| Performance from low-end mobile through PC/console; distinguish official facts from heuristics | `references/performance-validation.md`; plan quality tiers; validator warnings; official sources ledger. |
| Iterative production workflow and debugging checklists | Mandatory workflow in `SKILL.md`; `references/debugging.md`; `scripts/image_metrics.py`; output/iteration contract. |
| Screenshot-only reconstruction as inverse rendering | `references/screenshot-matching.md`; observation schema; confidence-aware hypotheses; image metrics and clustering helpers. |
| Decision tree from visible evidence to Roblox properties | `references/screenshot-matching.md`, especially dependency order and evidence-to-control mapping; `assets/sun-direction-search.lua`. |
| Separate lighting from camera, geometry, materials, textures, and post-processing | Mandatory decomposition in `SKILL.md`; observation categories and confounders; validation rules and examples. |
| Single-image limitations and additional-view strategy | `references/screenshot-matching.md`; required limitations/ambiguity fields; `scripts/validate_observations.py`. |
| Machine-actionable skill schema: inputs, observations, hypotheses, parameters, constraints, metrics, stopping rules | `references/output-contract.md`; `assets/observation.schema.json`; `assets/lighting-plan.schema.json`; validators and generator. |
| Practical presets labeled as starting hypotheses | `references/genre-recipes.md`; `assets/genre-starting-points.json`; scaffold output explicitly warns against treating values as universal. |
| Current 2026 official Roblox documentation and legacy/outdated advice flags | `references/sources.md`; verification date in API reference; maintenance checklist; deprecated-property checks. |
| Create a new look and reproduce a reference game from screenshots | Operating modes `FROM_SCRATCH`, `MATCH_SCREENSHOT`, and `LINK_ASSISTED_MATCH`; behavioral evals cover each. |
| Roblox URL research and retrieval of similar public gameplay references | `references/roblox-link-research.md`; `scripts/research_roblox_game.py`; `scripts/cluster_images.py`; source ledger and trust ranking. |

## Maintenance rule

A future release should not remove a mapped capability unless it also updates this table, the changelog, the relevant evals, and the skill description when trigger behavior changes.
