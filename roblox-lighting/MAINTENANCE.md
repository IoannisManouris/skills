# Maintaining `roblox-lighting`

## Design basis

The package follows the portable Agent Skills layout: a required `SKILL.md`, focused references, executable helpers, and reusable assets. The main file is intentionally shorter than the deep technical references so agents can discover and activate the skill cheaply, then load only the material needed for the current mode.

The technical content follows the originating Roblox-lighting research report. `references/report-traceability.md` maps each report requirement to concrete files and tests.

## Release checklist

1. Re-check `https://agentskills.io/specification` and current Codex skill metadata documentation for frontmatter, naming, progressive disclosure, `agents/openai.yaml`, invocation policy, and validator changes.
2. Re-check every official Roblox URL in `references/sources.md`, especially `Lighting`, `ColorGradingEffect`, rollout/security properties, public media endpoints, and performance guidance.
3. Update `metadata.version`, `metadata.last-verified`, `VERSION`, and `CHANGELOG.md`.
4. Run:

```bash
python scripts/validate_skill.py .
python scripts/run_checks.py .
python scripts/validate_observations.py examples/screenshot-observations.json
python scripts/validate_plan.py examples/from-scratch-plan.json
python scripts/validate_plan.py examples/screenshot-match-plan.json
python scripts/generate_luau.py examples/from-scratch-plan.json --output /tmp/apply.lua
skills-ref validate .  # when the reference validator is installed
```

5. Run trigger and behavioral evals with and without the skill. Review both machine assertions and human visual/technical quality.
6. Test generated Luau in a disposable Studio place, then test `assets/restore-backup.lua`.
7. Exercise low/medium/high graphics behavior on representative devices; never approve from a single desktop screenshot.
8. Build the zip with the `roblox-lighting/` directory as the archive root and record its SHA-256.

## Evaluation philosophy

Trigger tests should include misspellings (`lightning`), direct class/property questions, screenshot matching, Roblox URL research, optimization, and near-miss electrical-lightning requests. Behavioral tests should verify evidence/confidence separation, camera/material confounders, map/gameplay reasoning, quality tiers, public-source provenance, non-destructive implementation, and honest limitations.

A screenshot-matching result cannot be judged only by pixel metrics. Review camera equivalence, regional luminance/color, shadow direction, atmosphere depth, material response, player readability, and performance separately.
