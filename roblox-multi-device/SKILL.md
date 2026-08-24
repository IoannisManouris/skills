---
name: roblox-multi-device
description: Use this skill when implementing, auditing, refactoring, or debugging Roblox controls and UI across keyboard/mouse, touch/mobile/tablet, gamepad/console/TV, or VR. It creates a semantic Input Action System architecture, device-aware prompts, hot-swapping, analog movement/camera/aim, touch layouts, gamepad/TV focus navigation, VR locomotion/interactions, safe-area responsive UI, accessibility, and a cross-device test plan. Trigger when the user asks to make a Roblox experience work on every device or mentions input actions, bindings, controller support, mobile controls, console UI, ten-foot UI, or VR controls.
metadata:
  display_name: Roblox Multi-Device
  version: "1.0.0"
  domain: roblox-input-ui
  target_engine: Roblox Studio
  last_verified: "2026-07-12"
  compatibility: Agent Skills-compatible coding agents with access to a Roblox project. Web access is recommended to verify current Roblox APIs; Roblox Studio is needed for emulator and physical-device testing.
---

# Roblox Multi-Device

Implement one semantic control model that feels native on keyboard/mouse, touch, gamepad and living-room displays, and VR. Do not bolt four unrelated input systems onto gameplay code.

## Activation examples

Use this skill for requests such as:

- “make my Roblox game work on every device”
- “add mobile, controller, console, and VR support”
- “convert these key checks into cross-platform actions”
- “fix gamepad focus in my inventory”
- “make the HUD adapt when players switch from keyboard to controller”
- “design touch controls for this combat system”
- “add analog aiming and aim assist”
- “make this UI usable from a TV”
- “adapt this mechanic for Quest controllers”
- “audit all controls and menus for cross-device accessibility”

Do not activate for unrelated Roblox work that has no input, camera, UI navigation, device, or accessibility component.

## Default architecture

Use this dependency direction:

```text
hardware / pointer / hand tracking
              │
              ▼
InputBinding or narrowly-scoped raw input adapters
              │
              ▼
semantic InputActions + enabled InputContexts
              │
              ▼
action router / gameplay and UI controllers
              │
              ▼
local feedback + semantic server requests
```

Keep device presentation beside, not inside, gameplay logic:

```text
PreferredInput + capabilities + VR state + display size
                         │
                         ▼
DeviceProfile ──► prompts, focus, touch visibility, layout, hints
```

A gameplay system should understand `Interact`, `Fire`, `Move`, `OpenInventory`, or `Confirm`, not `E`, `ButtonX`, or “tap button 4.”

## Non-negotiable defaults

1. Prefer Roblox's **Input Action System** for new cross-platform action mapping.
2. Use **UserInputService** for device capabilities, `PreferredInput`, raw pointer/gesture/text-focus cases, and gaps that actions do not model cleanly.
3. Use **ContextActionService** only for an existing CAS architecture, a deliberate compatibility adapter, or a requirement the Input Action System cannot meet. Do not bind the same action in multiple stacks.
4. Preserve Roblox's default character movement and camera unless the mechanic genuinely requires replacement.
5. Use `GuiButton.Activated` for ordinary buttons; do not make a mouse-only click event the sole activation path.
6. Treat TV as a presentation mode, not a guaranteed platform identity. `GuiService:IsTenFootInterface()` is deprecated.
7. Detect VR through `VRService.VREnabled`; `UserInputService.VREnabled` is deprecated.
8. Never infer all capabilities from one label. A touch device can have a gamepad; a PC can use touch; prompts follow `PreferredInput`, while feature availability follows capability properties.
9. Device switching must work during play without respawn or reopening the experience.
10. Clients send semantic intent. Servers validate authoritative outcomes; raw inputs and client-calculated rewards, damage, or purchases are never truth.

## Required workflow

### 1. Inspect before replacing

Inventory the current project:

- input APIs and bindings
- default or custom PlayerModule controls
- character, vehicle, build, combat, camera, and interaction mechanics
- every ScreenGui, SurfaceGui, BillboardGui, TextBox, hotbar, modal, tooltip, and drag interaction
- device-specific branches and prompt assets
- remotes triggered by input
- existing accessibility settings and saved keybinds

Search for direct `KeyCode`, `UserInputType`, `MouseButton*`, `Touch*`, `ContextActionService`, `UserInputService`, `GuiService.SelectedObject`, custom camera scripts, and client-authored gameplay values.

Do not delete a working control stack until its replacement and migration path are explicit.

### 2. Verify API freshness

When web access exists, verify any API-dependent implementation against current Roblox Creator Hub pages before editing. Use the source priority in [references/sources.md](references/sources.md). Check deprecation badges, security/capability restrictions, and current Studio emulator behavior.

If web access is unavailable, state that freshness could not be rechecked and use the last-verified guidance in this package.

### 3. Build an action inventory

Describe player intent before choosing hardware. For every action record:

- semantic name and context
- `InputActionType`: `Bool`, `Direction1D`, `Direction2D`, `Direction3D`, or `ViewportPosition`
- press, hold, release, repeat, double-activate, or continuous semantics
- gameplay owner and server validation
- keyboard/mouse, gamepad, touch, and VR binding or justified exclusion
- prompt text/glyph
- rebind policy and conflict rules
- accessibility alternatives

Start from [assets/action-map.template.json](assets/action-map.template.json). Validate edited maps with:

```bash
python scripts/validate_action_map.py path/to/action-map.json
```

Read [references/action-design.md](references/action-design.md) for action types, analog handling, aim, movement, camera, buffering, and rebinding.

### 4. Design contexts and precedence

Use a small set of explicit states, commonly:

- `GameplayContext`
- `MenuContext`
- `TextEntryContext`
- `VehicleContext`
- `BuildContext`
- `SpectatorContext`
- optional `VRContext` or mechanic-specific overlays

Enable and disable contexts as game state changes. Give modal/text-entry contexts higher project-relative priority and sink only the inputs that must not reach lower contexts. Test interaction with Roblox default controls instead of assuming a numeric priority is sufficient.

Prefer one source of truth for context state. Do not scatter `.Enabled` writes across unrelated scripts. See [references/architecture.md](references/architecture.md) and [assets/context-controller.luau](assets/context-controller.luau).

### 5. Implement the semantic layer

For new work:

- place project-owned `InputContext` trees under `ReplicatedStorage/Inputs` unless the project has a documented alternative
- give each `InputAction` all applicable bindings
- connect `Pressed`, `Released`, and `StateChanged` once in an action router
- route actions to controllers, not directly into unrelated UI or server code
- centralize cleanup and character lifecycle handling

Use [assets/action-router.luau](assets/action-router.luau) as a dependency-free starting point. Keep raw adapters small and label why each one exists.

### 6. Separate capability from presentation

Maintain one client-side device profile containing at least:

- current `PreferredInput`
- keyboard, mouse, touch, and gamepad capability flags
- connected/navigation gamepads when relevant
- `VRService.VREnabled`
- `GuiService.ViewportDisplaySize`
- safe inset data when layout code needs it

Use the profile to switch prompts, focus policy, touch-control visibility, cursor behavior, and layout density. Never use it to change the meaning of a semantic action. Start from [assets/device-profile.luau](assets/device-profile.luau).

### 7. Make every UI path device-complete

For every interactive screen:

- activation works through `Activated`
- selectable objects have obvious selected/focused states
- focus enters at a sensible default, is restored when returning, and cannot escape into hidden or disabled controls
- non-geometric grids explicitly set `NextSelectionUp/Down/Left/Right`
- mouse/touch can clear gamepad selection without breaking the next controller input
- back/cancel is consistent and closes only the top modal
- TextBox focus suppresses gameplay shortcuts and restores the prior context afterward
- drag-only interactions have gamepad/keyboard alternatives
- hover-only information has focus/tap access
- prompts update when `PreferredInput` changes
- layout respects device/Core UI safe insets and different aspect ratios
- text and controls remain usable with preferred text size, transparency, and reduced-motion settings

Read [references/ui-navigation.md](references/ui-navigation.md). Use [assets/ui-focus-controller.luau](assets/ui-focus-controller.luau) and [assets/prompt-glyphs.luau](assets/prompt-glyphs.luau) as starting points.

### 8. Apply device-specific mechanics

Load only the references needed by the task:

- keyboard/mouse, pointer lock, scroll, layouts, modifiers, and text entry: [references/keyboard-mouse.md](references/keyboard-mouse.md)
- touch layout, gestures, multi-touch, orientation, virtual controls, and mobile aim: [references/touch.md](references/touch.md)
- gamepad analog input, prompts, focus, haptics, multiple controllers, and TV/large-display UX: [references/gamepad-tv.md](references/gamepad-tv.md)
- VR tracking, hand/controller interaction, locomotion, comfort, world-space UI, and recentering: [references/vr.md](references/vr.md)
- shared movement, camera, targeting, vehicles, radial menus, inventory, and custom mechanics: [references/action-design.md](references/action-design.md)

Do not force identical mechanics where physical constraints differ. Preserve the same player intent and competitive outcome while adapting interaction, assistance, and presentation.

### 9. Keep authority and feedback correctly split

Input, camera, cursor, local UI, immediate animation, haptics, screen effects, and predicted cosmetics usually belong on the client. Damage, inventory, currency, cooldown truth, permissions, purchases, round state, and saved settings belong on the server.

Send commands such as:

```lua
ActionRequest:FireServer("UseAbility", { abilityId = "Dash", aim = aimDescriptor })
```

Do not send final truth such as `SetDamage`, `GiveCoins`, or client-computed purchase totals. Validate rate, state, ownership, range, and payload schema on the server.

### 10. Test, fix, and report

Use Roblox Studio's Device Emulator, touch simulation, Controller Emulator, and VR emulation, then test physical target hardware for release confidence. Test hot-swapping between inputs during every major state.

Run the package validators after modifying this skill itself:

```bash
python scripts/validate_package.py .
python scripts/validate_action_map.py assets/action-map.template.json
```

Use [references/testing-accessibility.md](references/testing-accessibility.md) for the matrix and [references/migration-audit.md](references/migration-audit.md) for audit/refactor work.

## Device acceptance requirements

### Keyboard and mouse

- movement, camera, primary/secondary actions, scroll, modifiers, and pointer interactions are covered
- keyboard layout and displayed key names are not hard-coded when Roblox can resolve them
- text entry cannot trigger gameplay actions
- mouse capture/lock is intentional and released for menus
- all pointer interactions have non-pointer alternatives when console support is promised

### Touch

- controls avoid the default movement/camera zones and device safe areas
- important targets are comfortably tappable and not packed together
- simultaneous movement, camera, and action touches work
- no required hover, right-click, or precision drag without an alternative
- orientation/aspect-ratio changes do not hide actions
- aim assistance and automation are tuned by outcome, not copied from mouse behavior

### Gamepad and TV

- common confirm/cancel and movement/camera conventions are followed
- analog deadzones and response curves are measured, configurable where appropriate, and applied once
- every menu can be completed without a virtual cursor unless a deliberate cursor mode is implemented
- selection is always visible and deterministic
- prompts use the current controller glyph/string APIs where possible
- large-display UI is readable at distance and keeps critical content inside safe margins

### VR

- headset pose is never overridden like a normal camera
- locomotion offers comfort choices appropriate to the game, commonly snap/smooth turn and teleport/smooth movement
- recentering and seated/standing differences are handled
- world-space UI is readable, reachable, and not attached uncomfortably to the face
- interactions account for missing hand/controller tracking and controller disconnects
- frame-time, physics, effects, and UI are tested in a headset-class performance budget

## Common failure patterns

Reject or repair these patterns:

- gameplay code checks hardware keys directly in many files
- one boolean such as `TouchEnabled` is treated as the active input mode
- prompts are chosen only at spawn
- touch buttons duplicate actions but bypass the same cooldown/state logic
- gamepad UI relies on deprecated selection groups or `IsTenFootInterface()`
- a menu sets `SelectedObject` but never restores or clears it
- hidden buttons remain selectable
- mouse-only `MouseButton1Click` is the only activation path
- analog input is thresholded into digital movement too early
- deadzones are applied both in bindings and mechanics
- per-frame remote events send raw sticks, mouse delta, or headset poses without a justified network contract
- VR uses desktop camera shake, forced head rotation, or screen-space UI fixed to the face
- the implementation claims support based only on emulation and skips physical-device checks

## Required output from the agent

For implementation or audit tasks, provide:

1. **Scope and assumptions** — target devices, existing systems preserved, and exclusions.
2. **Action map** — contexts, action types, bindings, prompts, and authority.
3. **Architecture** — file tree and state/context flow.
4. **Implementation** — complete modules/scripts or concrete patches, not disconnected snippets.
5. **UI navigation map** — entry focus, directional links, cancel behavior, and touch/mouse paths.
6. **Device-specific decisions** — movement, camera, aim, layout, assistance, haptics, and VR comfort.
7. **Security boundary** — semantic requests and server validation.
8. **Test results** — emulator and physical-device status, hot-swap cases, failures, and remaining manual checks.
9. **Known limitations** — APIs not verified, unsupported hardware, or project information unavailable.

Use [assets/implementation-report.template.md](assets/implementation-report.template.md) for large changes.

## Single-prompt behavior

When the user simply says “make this game work on all devices,” do not respond with a generic checklist. Inspect the available project, choose the defaults above, create the action inventory, implement the highest-impact missing paths, validate them, and return the required report. Ask a question only when a missing product decision prevents a safe implementation; otherwise make a documented, reversible default.

## Reference map

- [references/architecture.md](references/architecture.md) — system design and API choice
- [references/action-design.md](references/action-design.md) — actions and core mechanics
- [references/ui-navigation.md](references/ui-navigation.md) — focus, prompts, safe layout, accessibility
- [references/keyboard-mouse.md](references/keyboard-mouse.md) — desktop controls
- [references/touch.md](references/touch.md) — phone and tablet controls
- [references/gamepad-tv.md](references/gamepad-tv.md) — controller, console, and living-room UX
- [references/vr.md](references/vr.md) — immersive controls and comfort
- [references/testing-accessibility.md](references/testing-accessibility.md) — test matrix and release gates
- [references/migration-audit.md](references/migration-audit.md) — audit and staged conversion
- [references/sources.md](references/sources.md) — current official documentation index
