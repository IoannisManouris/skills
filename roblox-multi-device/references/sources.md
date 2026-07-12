# Documentation Sources and Freshness Policy

Last verified: **2026-07-12**.

Roblox and Agent Skills APIs can change. Before applying API-specific code, re-check current documentation when web access is available. The skill's architecture is intentionally semantic so most game logic remains stable when bindings or platform APIs evolve.

## Source priority

Use sources in this order:

1. Roblox Creator Hub conceptual documentation.
2. Roblox engine API reference pages and deprecation/security annotations.
3. Roblox Creator documentation source repository, official engineering posts, and official DevForum announcements.
4. Official Luau documentation and repository when language behavior matters.
5. Platform documentation linked by Roblox for OpenXR/controller behavior.
6. Recent, reproducible community findings only for gaps not covered officially.

For Agent Skills packaging:

1. Agent Skills specification.
2. Agent Skills creator best practices, description optimization, evaluation, and scripts guides.
3. The official `skills-ref` validator/source repository.

Do not let an old DevForum snippet override a current API reference or deprecation marker.

## Agent Skills specification

- https://agentskills.io/specification
- https://agentskills.io/skill-creation/best-practices
- https://agentskills.io/skill-creation/optimizing-descriptions
- https://agentskills.io/skill-creation/evaluating-skills
- https://agentskills.io/skill-creation/using-scripts
- https://github.com/agentskills/agentskills

Key packaging rules reflected by this skill:

- the folder name matches `name: roblox-multi-device`
- `SKILL.md` contains YAML frontmatter and core instructions
- detailed material is progressively disclosed through `references/`
- reusable templates/code live in `assets/`
- deterministic validation lives in `scripts/`
- evaluation prompts/assertions live in `evals/`
- `SKILL.md` remains under the recommended 500-line boundary

## Roblox input overview

- https://create.roblox.com/docs/input
- https://create.roblox.com/docs/input/input-action-system
- https://create.roblox.com/docs/input/input-type-detection
- https://create.roblox.com/docs/input/mouse-and-keyboard
- https://create.roblox.com/docs/input/mobile-input
- https://create.roblox.com/docs/input/gamepad

## Input Action System API

- https://create.roblox.com/docs/reference/engine/classes/InputContext
- https://create.roblox.com/docs/reference/engine/classes/InputAction
- https://create.roblox.com/docs/reference/engine/classes/InputBinding
- https://create.roblox.com/docs/reference/engine/enums/InputActionType
- https://create.roblox.com/docs/reference/engine/enums/PreferredInput

Implementation facts to re-check:

- `InputContext.Enabled`, `Priority`, and `Sink`
- `InputAction.Type`, `Pressed`, `Released`, and `StateChanged`
- `InputBinding` key, directional, modifier, threshold, response-curve, scale, clamp, and `UIButton` behavior
- supported action value types
- default/reserved bindings and interaction with PlayerScripts

## General input services

- https://create.roblox.com/docs/reference/engine/classes/UserInputService
- https://create.roblox.com/docs/reference/engine/classes/ContextActionService
- https://create.roblox.com/docs/reference/engine/classes/GuiService

Re-check:

- `UserInputService.PreferredInput`
- keyboard, mouse, touch, and gamepad capability properties
- raw input and gesture events
- gamepad connection/navigation APIs
- `GetImageForKeyCode()` and `GetStringForKeyCode()`
- mouse behavior, sensitivity, focus/text APIs
- window-focus events
- `GuiService.SelectedObject`
- display-size, safe-inset, text-size, transparency, and reduced-motion properties
- deprecation of older ten-foot and selection-group patterns

## UI navigation and layout

- https://create.roblox.com/docs/ui
- https://create.roblox.com/docs/ui/buttons
- https://create.roblox.com/docs/ui/layouts
- https://create.roblox.com/docs/ui/positioning-and-sizing-ui-objects
- https://create.roblox.com/docs/ui/appearance-modifiers
- https://create.roblox.com/docs/reference/engine/classes/GuiObject
- https://create.roblox.com/docs/reference/engine/classes/GuiButton
- https://create.roblox.com/docs/reference/engine/classes/ScrollingFrame
- https://create.roblox.com/docs/reference/engine/classes/ScreenGui
- https://create.roblox.com/docs/reference/engine/classes/UIDragDetector
- https://create.roblox.com/docs/reference/engine/enums/ScreenInsets
- https://create.roblox.com/docs/reference/engine/enums/DisplaySize

Re-check:

- `Selectable`, `SelectionOrder`, `SelectionImageObject`
- `NextSelectionUp/Down/Left/Right`
- `GuiButton.Activated`
- drag event semantics
- `ScreenInsets` and inset-area APIs
- automatic sizing, constraints, and text scaling behavior

## Character controls and camera

- https://create.roblox.com/docs/characters
- https://create.roblox.com/docs/workspace/camera
- https://create.roblox.com/docs/reference/engine/classes/StarterPlayer
- https://create.roblox.com/docs/reference/engine/classes/PlayerModule

Re-check default touch/computer movement and camera modes before replacing PlayerScripts behavior.

## Touch/mobile

- https://create.roblox.com/docs/input/mobile-input
- https://create.roblox.com/docs/input/input-action-system
- https://create.roblox.com/docs/reference/engine/classes/TouchInputService
- https://create.roblox.com/docs/reference/engine/classes/UserInputService
- https://create.roblox.com/docs/reference/engine/classes/GuiService
- https://create.roblox.com/docs/studio/testing-modes

Verify current gesture, sensor, virtual-control, safe-area, orientation, and Studio touch-simulation APIs before implementation.

## Gamepad, console, TV, and haptics

- https://create.roblox.com/docs/input/gamepad
- https://create.roblox.com/docs/reference/engine/classes/HapticEffect
- https://create.roblox.com/docs/reference/engine/enums/HapticEffectType
- https://create.roblox.com/docs/reference/engine/classes/GuiService
- https://create.roblox.com/docs/studio/testing-modes

The gamepad guide documents common control roles, `PreferredInput`, supported haptics, and Controller Emulator usage. Treat TV/large-display layout as presentation. Do not infer a security or entitlement platform identity from display size.

## VR

- https://create.roblox.com/docs/reference/engine/classes/VRService
- https://create.roblox.com/docs/reference/engine/enums/UserCFrame
- https://create.roblox.com/docs/reference/engine/classes/HapticEffect
- https://create.roblox.com/docs/studio/testing-modes
- https://create.roblox.com/docs/performance-optimization

Re-check:

- `VRService.VREnabled`
- tracked `UserCFrame` APIs and events
- recenter/navigation methods
- controller models, laser pointer, avatar gesture, camera, and collision-related properties
- OpenXR/Studio and standalone Quest testing instructions
- any platform/hardware support changes

Do not use deprecated VR detection from `UserInputService` in new code.

## Networking and security

- https://create.roblox.com/docs/scripting/events/remote
- https://create.roblox.com/docs/reference/engine/classes/RemoteEvent
- https://create.roblox.com/docs/reference/engine/classes/RemoteFunction
- https://create.roblox.com/docs/reference/engine/classes/UnreliableRemoteEvent
- https://create.roblox.com/docs/scripting/security/server-side-detection
- https://create.roblox.com/docs/physics/network-ownership

Use server authority for damage, inventory, economy, permissions, purchases, cooldown truth, and saved state. Device adaptations must not create separate trust rules.

## Performance and profiling

- https://create.roblox.com/docs/performance-optimization
- https://create.roblox.com/docs/performance-optimization/microprofiler
- https://create.roblox.com/docs/studio/optimization/scriptprofiler
- https://create.roblox.com/docs/studio/optimization/memory-usage
- https://create.roblox.com/docs/performance-optimization/scene-analysis
- https://create.roblox.com/docs/scripting/scheduler
- https://create.roblox.com/docs/reference/engine/classes/RunService

Profile target device classes. VR and mobile require physical-device frame-time, thermal, and interaction testing.

## Studio and automated testing

- https://create.roblox.com/docs/studio/testing-modes
- https://create.roblox.com/docs/reference/engine/classes/StudioDeviceSimulatorService
- https://create.roblox.com/docs/reference/engine/classes/StudioTestService
- https://create.roblox.com/docs/reference/engine/classes/VirtualInput

Current testing documentation describes Device Emulator, touch simulation, Controller Emulator, network simulation, scripted services, VR emulation, compatible OpenXR headset testing, and standalone Quest testing. Re-check operating-system and hardware restrictions.

## Accessibility

- https://create.roblox.com/docs/ui/accessibility
- https://create.roblox.com/docs/reference/engine/classes/GuiService
- https://create.roblox.com/docs/reference/engine/classes/LocalizationService
- https://create.roblox.com/docs/production/localization
- https://create.roblox.com/docs/studio/testing-modes

Check current preferred text size, transparency, reduced motion, localization/pseudolocalization, subtitles, and other relevant APIs. Accessibility decisions also require product design and human testing; an API list is not proof of usability.

## Freshness checklist

Before a production change:

- [ ] Open the current conceptual page and API reference.
- [ ] Check deprecation and thread/security/capability annotations.
- [ ] Confirm enum members and method signatures.
- [ ] Confirm Studio emulator behavior and target-platform restrictions.
- [ ] Prefer current examples over cached forum snippets.
- [ ] Record the verification date in the implementation report.
- [ ] Mark any unverified API or unavailable target hardware as a limitation.
