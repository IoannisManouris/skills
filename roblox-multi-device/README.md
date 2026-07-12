# Roblox Multi-Device Agent Skill

`roblox-multi-device` helps an AI coding agent implement or audit a Roblox experience for keyboard and mouse, touch/mobile/tablet, gamepad/console/TV, and VR from one request.

It turns hardware input into semantic actions, coordinates input contexts, updates prompts when players switch devices, makes UI focus/navigation complete, adapts core mechanics for each input method, and produces a device test matrix instead of declaring support from code review alone.

## One-prompt use

```text
Use the roblox-multi-device skill to make this Roblox game work correctly on
keyboard/mouse, touch, gamepad/TV, and VR. Inspect the project, preserve Roblox
default movement/camera where appropriate, implement missing action bindings and
UI navigation, update prompts on input hot-swap, validate server authority, and
return the full cross-device test report.
```

The skill is also useful for narrower requests such as fixing controller focus, redesigning mobile combat controls, adding VR locomotion, or converting hard-coded key checks into Roblox Input Actions.

## Installation

Copy the entire folder into an Agent Skills-compatible skills directory. The folder name must remain exactly `roblox-multi-device` because it must match the `name` in `SKILL.md`.

```text
.agents/skills/roblox-multi-device/
```

## Package contents

```text
roblox-multi-device/
├── SKILL.md
├── README.md
├── references/
│   ├── architecture.md
│   ├── action-design.md
│   ├── ui-navigation.md
│   ├── keyboard-mouse.md
│   ├── touch.md
│   ├── gamepad-tv.md
│   ├── vr.md
│   ├── testing-accessibility.md
│   ├── migration-audit.md
│   └── sources.md
├── assets/
│   ├── action-map.template.json
│   ├── project-layout.template.md
│   ├── implementation-report.template.md
│   ├── device-profile.luau
│   ├── context-controller.luau
│   ├── action-router.luau
│   ├── prompt-glyphs.luau
│   ├── ui-focus-controller.luau
│   └── bootstrap.client.luau
├── scripts/
│   ├── validate_action_map.py
│   └── validate_package.py
└── evals/
    ├── evals.json
    ├── trigger-evals.json
    └── assertions.md
```

## Validation

From the skill folder:

```bash
python scripts/validate_package.py .
python scripts/validate_action_map.py assets/action-map.template.json
```

The official Agent Skills reference package can also validate the skill:

```bash
uvx --from skills-ref agentskills validate .
```

## Design baseline

- New cross-platform action maps default to Roblox's Input Action System.
- `UserInputService` is used for capabilities, active-input presentation, gestures, pointer/text focus, and low-level gaps.
- Gameplay consumes semantic actions, not hardware keys.
- Roblox default movement and camera are preserved unless the game needs custom behavior.
- UI uses cross-input activation, deterministic gamepad focus, responsive safe-area layout, and accessibility preferences.
- VR uses `VRService` and comfort-first interaction rules.
- Clients provide responsive feedback; servers validate authoritative outcomes.

## Version

`1.0.0`, documentation baseline verified July 12, 2026. Re-check current Creator Hub documentation before relying on API details in a production migration.
