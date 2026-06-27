# Game Reference Research Skill

An enhanced analysis-only skill for researching how games work as references without copying private code, protected assets, maps, thumbnails, UI, characters, branding, or implementation details.

## What this skill does

It helps analyze a game's:

- Core gameplay loop
- Player verbs and objectives
- UX/UI and onboarding
- Systems and likely data flow
- Visual style and readability
- Game feel and polish
- Level/map structure
- Monetization surface if visible or requested
- Accessibility and usability
- Possible technical architecture, clearly marked as inference unless confirmed

## What this skill does not do by default

It does not create:

- Code
- Scripts
- New game concepts
- Build plans
- Asset prompts
- UI prompts
- Thumbnail prompts
- Monetization plans
- Clone instructions

Creation is allowed only after the user explicitly asks for it and the output remains lawful and original.

## Recommended folder structure

```text
game-reference-research-skill/
  SKILL.md
  README.md
  docs/
  templates/
  schemas/
  prompts/
  checklists/
  examples/
```

## How to use

Example user prompts:

```text
Use the game-reference-research skill to analyze this Roblox game as a reference: [link]
```

```text
Analyze these screenshots and explain the game's UI, systems, game feel, and likely Roblox architecture. Do not make a clone plan.
```

```text
Compare these three games as references for onboarding and first-session clarity.
```

## Best workflow

1. Collect evidence: gameplay, screenshots, official descriptions, store pages, docs, patch notes, credits.
2. Separate observations from assumptions.
3. Break down core loop, UX, systems, style, game feel, and level design.
4. Assign confidence ratings.
5. Cite reliable sources where possible.
6. End with high-level lessons and unknowns.

## Included files

- `SKILL.md` — main upgraded skill file.
- `templates/full_report_template.md` — reusable report format.
- `templates/reference_note_template.md` — one-reference note template.
- `templates/evidence_log.csv` — spreadsheet-friendly evidence log.
- `templates/source_matrix.csv` — source hierarchy tracker.
- `schemas/research_record.schema.json` — JSON schema for structured extraction.
- `schemas/report_output.schema.json` — JSON schema for report outputs.
- `prompts/query_expansion_prompt.md` — AI prompt for finding better sources.
- `prompts/structured_extraction_prompt.md` — AI prompt for extracting source records.
- `prompts/validation_prompt.md` — AI prompt for QA/auditing reports.
- `checklists/qa_checklist.md` — final report quality checklist.
- `checklists/legal_safety_checklist.md` — anti-copying and IP-safety checklist.
- `docs/source_hierarchy.md` — source reliability guidance.
- `docs/confidence_rubric.md` — claim-confidence standards.
- `docs/roblox_analysis_notes.md` — Roblox-specific analysis guidance.
- `examples/minimal_user_prompt.md` — example prompts.

## Version

Enhanced version: 2.0.0
