# Installing `roblox-lighting`

This package follows the open Agent Skills directory format. Keep the outer folder named `roblox-lighting`; `SKILL.md` is the required entry point.

## ChatGPT / Codex skill upload

Where the product exposes **Skills > Create > Upload from computer**, upload a ZIP containing one top-level `roblox-lighting/` directory. Product availability can depend on plan, workspace policy, role, surface, and rollout.

## Codex local installation

Copy the folder to a supported user- or repository-level skills location used by your Codex installation, then restart or begin a fresh session so skills are re-indexed. The bundled `agents/openai.yaml` provides Codex UI metadata and explicitly allows implicit invocation.

Example repository layout:

```text
<repository>/
└── .agents/
    └── skills/
        └── roblox-lighting/
            ├── SKILL.md
            ├── agents/openai.yaml
            ├── references/
            ├── scripts/
            └── assets/
```

Codex locations and behavior have changed during product rollouts. Prefer the current Codex documentation or built-in skill installer over hard-coding a path from an old tutorial.

## Other Agent Skills-compatible clients

Install the entire `roblox-lighting/` folder in the client's documented skills directory. Compatible clients discover it from the `name` and trigger-rich `description` in `SKILL.md`, then progressively load the detailed references, scripts, and assets only when needed.

## Verify after installation

Test both implicit and explicit routing:

```text
Make the lighting in my Roblox horror map dark but readable on mobile.
```

```text
Use roblox-lighting to recreate this game's lighting from the attached screenshot and Roblox URL.
```

A correct activation should distinguish **lighting** from electrical lightning-bolt VFX, choose an operating mode, inventory available tools, and proceed without requiring the user to repeat supplied inputs.

## Local package validation

```bash
python roblox-lighting/scripts/validate_skill.py roblox-lighting
python roblox-lighting/scripts/run_checks.py roblox-lighting
```

When available, also run:

```bash
skills-ref validate ./roblox-lighting
```
