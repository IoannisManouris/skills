---
name: game-reference-research
description: Research and analyze a game as a design or technical reference using gameplay, screenshots, public sources, or authorized project files. Use when the user wants an evidence-backed breakdown of gameplay loops, systems, UX/UI, visual style, game feel, level design, likely architecture, monetization, accessibility, or a comparison between games. This is analysis-first; do not turn it into clone instructions, code, assets, or an implementation plan unless the user separately requests lawful original creation.
---

# Game Reference Research

Analyze how a reference game works and feels without copying its protected expression or presenting speculation as fact. Produce the strongest useful result from the evidence already available; ask for more material only when a missing fact prevents a responsible analysis.

## Select the mode

Choose the narrowest mode that satisfies the request:

- **Quick scan** — identity, core loop, main systems, UX/style/game-feel highlights, lessons, and unknowns.
- **Full report** — evidence log plus gameplay, experience, systems, presentation, technical, accessibility, and optional monetization analysis.
- **Focused analysis** — only the requested area, such as onboarding, combat feel, UI, level flow, or likely Roblox architecture.
- **Comparison** — a side-by-side evidence-backed comparison, followed by shared patterns, important differences, and high-level lessons.

If the user provides a game without a focus, default to a full report. If access is limited, complete a reduced report and state the limitations instead of inventing missing details.

## Evidence discipline

Keep evidence and interpretation distinct:

- **Observed** — directly visible in supplied material, gameplay, screenshots, footage, or a public page.
- **Confirmed** — supported by an official source, reliable documentation, or authorized source/project files.
- **Inferred** — a reasonable explanation suggested by evidence but not directly verified.
- **Unknown** — cannot be determined from the available material.

Use High, Medium, Low, or Unknown confidence for claims where uncertainty matters. Read [docs/confidence_rubric.md](docs/confidence_rubric.md) when the report contains substantial technical inference or conflicting evidence.

Prefer evidence in this order: user-provided material; direct gameplay/capture; official sources; structured databases; professional or academic sources; curated archives; corroborated community commentary. Read [docs/source_hierarchy.md](docs/source_hierarchy.md) when choosing among several source types.

Browse when the user supplies a public game link, current version/platform/monetization facts matter, the game is unfamiliar, or citations are requested. Do not browse when the supplied material fully supports the requested analysis and no current facts are needed.

## Workflow

1. Identify the game, platform, genre, perspective, player/social context, requested focus, evidence, and important gaps.
2. Build a compact source map containing only evidence that supports a meaningful claim.
3. Analyze the relevant layers:
   - primary verbs and short-, medium-, and long-term gameplay loops;
   - objectives, challenge, failure, recovery, reward cadence, pacing, and player motivation;
   - onboarding, UX/UI hierarchy, readability, error recovery, and accessibility;
   - visible systems and their interactions;
   - visual direction, animation, audio feedback, camera, responsiveness, and game feel;
   - level/map flow, landmarks, guidance, safe/social spaces, and difficulty rhythm;
   - monetization only when visible or requested;
   - technical architecture, clearly separated into confirmed code behavior and cautious inference.
4. Extract high-level lessons without converting them into a clone or build plan.
5. Run the quality and legal checks before delivering the report.

For the detailed sequence, read [docs/workflow.md](docs/workflow.md). For Roblox-specific system and architecture cues, read [docs/roblox_analysis_notes.md](docs/roblox_analysis_notes.md).

## Technical analysis

When the user supplies source or project files they own or may lawfully inspect, analyze the actual code, server/client boundaries, data flow, remotes, persistence, security, performance, bugs, and maintainability.

Without source files, describe only possible architecture. Tie each inference to visible behavior and use language such as “likely,” “appears to,” or “cannot be confirmed without source.” Never claim to know private scripts, exact values, or hidden implementation details from public gameplay alone.

## Boundaries

Do not provide instructions to rip, decompile, dump, bypass protections, extract private code/assets, or reproduce proprietary maps, characters, UI, icons, branding, thumbnails, sounds, or animations. If supplied project files may not belong to the user, confirm authorization before inspecting them or limit the work to public and visible behavior.

Research does not itself authorize creation. Provide code, assets, mechanics, implementation plans, or monetization plans only after the user explicitly requests that separate work, and keep the result lawful and original. Read [checklists/legal_safety_checklist.md](checklists/legal_safety_checklist.md) for borderline requests.

## Output resources

Use only the resources relevant to the requested deliverable:

- Full narrative report: [templates/full_report_template.md](templates/full_report_template.md)
- Per-reference notes: [templates/reference_note_template.md](templates/reference_note_template.md)
- Evidence/source spreadsheets: [templates/evidence_log.csv](templates/evidence_log.csv) and [templates/source_matrix.csv](templates/source_matrix.csv)
- Structured JSON: [schemas/research_record.schema.json](schemas/research_record.schema.json) and [schemas/report_output.schema.json](schemas/report_output.schema.json)
- Source-query expansion: [prompts/query_expansion_prompt.md](prompts/query_expansion_prompt.md)
- Structured evidence extraction: [prompts/structured_extraction_prompt.md](prompts/structured_extraction_prompt.md)
- Report validation: [prompts/validation_prompt.md](prompts/validation_prompt.md)

Before finalizing, read [checklists/qa_checklist.md](checklists/qa_checklist.md) and verify that material claims are sourced, uncertainty is labeled, limitations are explicit, conclusions answer the request, and the report has not drifted into clone-like instructions.
