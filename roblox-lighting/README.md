# roblox-lighting

A portable, autonomous Agent Skill for designing, improving, optimizing, and reconstructing Roblox scene **lighting**. The canonical name is `roblox-lighting`; its discovery metadata still recognizes “lightning” as a common misspelling while distinguishing illumination from electrical lightning-bolt VFX.

The technical scope comes directly from the originating deep-research report: current Roblox Lighting systems, related instances, map/genre design, player experience, performance, iterative production, and confidence-aware inverse rendering from screenshots. See `references/report-traceability.md` for a requirement-by-requirement map.

## Core operating modes

1. `FROM_SCRATCH` — designs a coherent look from genre, map, gameplay, art direction, camera, and target devices.
2. `MATCH_SCREENSHOT` — reconstructs a Roblox-compatible look from one or more images using evidence, ranges, confidence, and competing hypotheses.
3. `LINK_ASSISTED_MATCH` — resolves a public Roblox experience link, gathers public official media and web references, clusters similar lighting states, and then performs screenshot matching.
4. `IMPROVE_OR_DEBUG` — audits an existing place, settings dump, script, screenshot, or visual symptom.
5. `AUDIT_OR_OPTIMIZE` — preserves the art direction while improving readability, fairness, comfort, scalability, and render cost.

## Why agents can discover and use it independently

- `SKILL.md` has a trigger-rich `name` and `description`, including the common `lightning` misspelling, Roblox class names, screenshot matching, link research, debugging, and performance requests.
- The main instructions choose a mode, inventory available tools, make explicit assumptions, and continue with a best-effort result instead of requiring the user to restate supplied information.
- Detailed material is progressively disclosed through focused `references/`, deterministic `scripts/`, schemas/templates in `assets/`, and realistic `evals/`.
- `agents/openai.yaml` gives Codex-compatible UI metadata and enables implicit invocation.
- Positive, negative, and near-miss trigger cases test automatic routing, including the boundary between scene lighting and electrical bolt VFX.

## Main outputs

Depending on tool access, the skill produces or directly applies:

- a source and observation ledger;
- ranked lighting hypotheses with confidence and rejection conditions;
- a validated `lighting-plan.json`;
- reversible Studio-ready Luau and optional Camera-local effects;
- semantic fixture/local-light placement instructions;
- low/medium/high quality strategies;
- matched-camera validation results and an experiment log;
- unresolved ambiguities, limitations, and rollback instructions.

## Package layout

```text
roblox-lighting/
├── SKILL.md                         # Required Agent Skills entry point
├── agents/openai.yaml               # Codex discovery/UI/invocation metadata
├── references/                      # Detailed technical and workflow guidance
├── scripts/                         # Validation, research, matching, and codegen helpers
├── assets/                          # Schemas, templates, Studio audit/restore tools
├── examples/                        # Valid from-scratch and screenshot-match examples
├── evals/                           # Behavioral and trigger regression cases
├── INSTALL.md
├── MAINTENANCE.md
├── BUILD-INFO.json                 # Build-time validation and known test limits
├── MANIFEST.sha256                 # Per-file integrity hashes
└── manifest.json
```

## Install

Upload a ZIP containing the skill where the client supports Agent Skill uploads, or place the complete `roblox-lighting/` directory in the client's documented skills directory. Keep the outer folder name unchanged because it must match `name: roblox-lighting` in `SKILL.md`.

See `INSTALL.md` for ChatGPT/Codex and generic Agent Skills-compatible installation notes.

## Useful commands

Validate the whole package offline:

```bash
python roblox-lighting/scripts/validate_skill.py roblox-lighting
python roblox-lighting/scripts/run_checks.py roblox-lighting
```

Create a first-pass plan from a genre hypothesis:

```bash
python roblox-lighting/scripts/scaffold_plan.py \
  --genre "adventure-rpg" \
  --goal "Readable misty forest exploration" \
  --output lighting-plan.json
```

Validate and generate reversible Studio Luau:

```bash
python roblox-lighting/scripts/validate_plan.py lighting-plan.json
python roblox-lighting/scripts/generate_luau.py lighting-plan.json \
  --output apply_roblox_lighting.lua
```

After auditing existing global instances, deterministic conflict replacement is available explicitly:

```bash
python roblox-lighting/scripts/generate_luau.py lighting-plan.json \
  --output apply_roblox_lighting.lua \
  --replace-conflicts
```

Research a Roblox experience's public metadata/media:

```bash
python roblox-lighting/scripts/research_roblox_game.py \
  "https://www.roblox.com/games/<placeId>/<slug>" \
  --output research.json \
  --download-dir media
```

Group downloaded candidates by broad lighting appearance and rank them against a user snapshot:

```bash
python roblox-lighting/scripts/cluster_images.py media \
  --reference snapshot.png \
  --recursive \
  --output clusters.json
```

Compare aligned reference/candidate captures:

```bash
python roblox-lighting/scripts/image_metrics.py \
  reference.png candidate.png \
  --json comparison.json \
  --diff diff.png
```

Only the image diagnostics/clustering helpers require Pillow; the core plan, validation, research, and code-generation scripts use the Python standard library.

## Safety and limitations

Generated Luau backs up affected state, tags skill-managed instances, preserves unmanaged conflicts by default, and provides a restore script. Still duplicate/save a place before applying changes and test rollback in a disposable Studio place.

Public Roblox media can reveal visible style, map states, and lighting cues, but not private source settings. Official thumbnails may be staged, edited, personalized, outdated, or captured under a special state. Single-image reconstruction is underdetermined, so the skill reports evidence, parameter ranges, alternatives, and confidence instead of claiming exact hidden values.
