# Cross-Device Architecture

Read this reference when creating or restructuring the project's input layer, choosing Roblox input APIs, designing contexts, or deciding client/server ownership.

## Architectural goals

A scalable Roblox control system should satisfy all of these at once:

1. Gameplay code is independent from hardware.
2. One semantic action has one behavior path regardless of binding.
3. Device changes update presentation without mutating game rules.
4. Context changes are explicit and reversible.
5. Roblox default character controls remain available unless intentionally replaced.
6. UI and gameplay cannot consume the same input accidentally while a modal or TextBox is active.
7. Clients feel immediate; servers own authoritative results.
8. Device-specific help is loaded only when needed, rather than making every controller know every platform.

## Recommended layers

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Hardware and capability sources                                     │
│ Keyboard, mouse, touch, gamepad, VR controller/headset, display     │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│ Binding/adaptation layer                                             │
│ InputBinding children; small UIS/VR adapters only for genuine gaps  │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│ Semantic action layer                                                │
│ InputAction instances grouped by enabled InputContext instances      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│ Client controller layer                                              │
│ Character, camera, combat, vehicle, build, interaction, UI, prompts │
└──────────────────────┬───────────────────────────┬───────────────────┘
                       │                           │
             immediate local feedback      semantic remote request
                       │                           │
┌──────────────────────▼───────────────┐  ┌────────▼───────────────────┐
│ Local presentation                  │  │ Server authority           │
│ UI, cursor, VFX, SFX, haptics       │  │ validation and game truth │
└──────────────────────────────────────┘  └────────────────────────────┘
```

Separately:

```text
UserInputService.PreferredInput ─┐
UserInputService capabilities ───┼─► DeviceProfile ─► prompts/focus/layout
VRService.VREnabled ─────────────┤
GuiService.ViewportDisplaySize ──┘
```

The device profile is presentation state. It must not become a second action router.

## API selection matrix

| Need | Default API | Notes |
|---|---|---|
| Cross-platform gameplay actions | `InputContext`, `InputAction`, `InputBinding` | Preferred for new work. Author actions by intent and give each applicable device a binding. |
| Action mode/state precedence | `InputContext.Enabled`, `Priority`, `Sink` | Centralize state changes. Test against default controls. |
| Current prompt/input presentation | `UserInputService.PreferredInput` | Listen for property changes; do not sample only once. |
| Available capabilities | `KeyboardEnabled`, `MouseEnabled`, `TouchEnabled`, `GamepadEnabled` and related APIs | Capability is not the same as current preference. |
| Raw pointer delta/location, text focus, gestures, sensor data | `UserInputService` | Use narrowly and honor `gameProcessedEvent` where applicable. |
| Existing legacy action stack | `ContextActionService` | Keep if stable, or add a deliberate adapter during migration. Do not duplicate bindings in IAS and CAS. |
| GUI focus/navigation | `GuiService.SelectedObject` plus `GuiObject` selection properties | Use `Selectable`, `SelectionOrder`, `NextSelection*`, and a visible `SelectionImageObject`. Deprecated selection groups are not the default. |
| Cross-input button activation | `GuiButton.Activated` | Keep mouse-specific events only for mouse-specific behavior. |
| VR presence and tracked poses | `VRService` | Use `VREnabled`, `GetUserCFrame`, tracking events, recentering, laser/controller configuration as required. |
| Safe layout and display class | `GuiService.GetInsetArea`, `TopbarInset`, `ViewportDisplaySize` | `IsTenFootInterface()` is deprecated. |
| Controller/touch haptics | `HapticEffect` or supported GUI haptic properties | Treat haptics as optional feedback; never encode required information only through vibration. |
| UI drag behavior | `UIDragDetector` where suitable | Add non-drag alternatives for gamepad/keyboard and accessibility. |

## Input Action System model

Recommended hierarchy:

```text
ReplicatedStorage
└── Inputs
    ├── GameplayContext       (InputContext)
    │   ├── Move              (InputAction: Direction2D)
    │   │   ├── Keyboard      (InputBinding)
    │   │   ├── Gamepad       (InputBinding)
    │   │   └── TouchAdapter  (InputBinding or default movement path)
    │   ├── Interact          (InputAction: Bool)
    │   ├── PrimaryAction     (InputAction: Bool)
    │   └── Aim               (InputAction: Direction2D/ViewportPosition)
    ├── MenuContext
    │   ├── Confirm
    │   ├── Cancel
    │   ├── TabLeft
    │   └── TabRight
    ├── VehicleContext
    │   ├── Steer
    │   ├── Throttle
    │   └── ExitVehicle
    └── BuildContext
        ├── Place
        ├── Rotate
        ├── Elevate
        └── Cancel
```

Roblox recommends a top-level primary context even for simple projects and commonly places the hierarchy in `ReplicatedStorage/Inputs`. Input action state is client input state; do not expect it to replicate authoritative values to the server.

### Runtime connections

Connect each action centrally and forward to controller methods:

```lua
router:bind("Interact", {
    pressed = function()
        interactionController:requestCurrentTarget()
    end,
})

router:bind("Aim", {
    changed = function(value: Vector2)
        combatController:setAimInput(value)
    end,
})
```

Avoid placing business logic in dozens of child scripts under actions. Central routing makes cleanup, mode changes, diagnostics, and migrations visible.

### Action state rules

- `Pressed` and `Released` are appropriate for boolean edges.
- `StateChanged` is appropriate for analog and pointer values.
- `GetState()` is useful when a controller needs the current value after entering a state.
- Do not use deprecated `InputAction:Fire()`.
- `InputBinding:Fire()` can bridge a deliberate custom adapter, but document why a normal binding or UI button link cannot perform the job.

## Context state model

Treat contexts as a state machine, not a collection of independent toggles.

Example:

```text
                           ┌───────────────┐
                           │ TextEntry     │
                           │ highest modal │
                           └───────▲───────┘
                                   │ focus TextBox
┌──────────────┐ open menu ┌───────┴───────┐ enter vehicle ┌─────────────┐
│ Gameplay     ├──────────►│ Menu          │◄──────────────┤ Vehicle     │
└──────▲───────┘           └───────┬───────┘               └──────┬──────┘
       │ close menu                 │ close                         │ exit
       └────────────────────────────┴───────────────────────────────┘
```

Real projects often need overlays rather than one exclusive context. Model them explicitly:

- **base mode**: gameplay, vehicle, spectator, build
- **modal layer**: menu, dialog, radial menu
- **text-entry layer**: TextBox/IME input
- **global layer**: accessibility shortcut or emergency cancel, if justified

A modal context generally has a higher project-relative priority. Set `Sink` only when lower input must be blocked. An inventory that still permits walking should not sink movement accidentally; a pause or confirmation dialog usually should block gameplay actions.

### Priority guidance

Numeric values are project conventions, not universal truths. A workable internal scheme is spaced values such as base `100`, mechanic `200`, modal `300`, text entry `400`, leaving gaps for future overlays. Verify behavior against Roblox PlayerScripts and Core UI in Studio. Do not claim safety merely because a number is “high.”

### One context owner

Create one controller that applies the desired set of enabled contexts. Other systems request a mode or push/pop a layer; they do not mutate context instances directly. This prevents close-order bugs such as a dialog re-enabling gameplay while another modal remains open.

## Capability versus current input

These questions are different:

- **Can this client use touch?** `TouchEnabled`/`TouchScreenEnabled` and project constraints.
- **What is the player using now?** `PreferredInput`.
- **Is VR active?** `VRService.VREnabled`.
- **How much UI space is available?** camera viewport, safe insets, and `ViewportDisplaySize`.
- **Is this a TV?** Roblox no longer provides a recommended simple ten-foot identity check; treat TV as a UX profile derived from large-display needs and gamepad-first interaction, not as a security/platform fact.

Examples:

- Keep touch controls available as a backup on a touch-capable device, but visually de-emphasize or hide optional buttons when a gamepad is preferred.
- Switch prompt glyphs immediately when a gamepad becomes preferred on PC.
- Do not hide keyboard shortcuts forever because `GamepadEnabled` is true.
- VR should override flat-screen presentation where required, while still allowing the physical controller's buttons to drive semantic actions.

## Presentation services

Recommended client services:

### `DeviceProfile`

Publishes a snapshot and a change signal for input preference, capabilities, VR, display class, and optionally safe insets. It contains no gameplay decisions.

### `PromptService`

Receives semantic action IDs and displays text/images for the active presentation mode. It uses Roblox key-code image/string APIs where possible and falls back to localized text.

### `UIFocusService`

Owns `GuiService.SelectedObject` for project UI. It remembers selection per panel, validates visibility/selectability, enters focus for gamepad navigation, clears focus for pointer/touch modes, and restores focus after nested modals.

### `TouchLayoutService`

Controls the visibility and placement of project touch buttons, taking default movement controls, safe insets, orientation, and two-thumb reach into account. It must not duplicate the gameplay action implementation.

### `AccessibilityService`

Applies project settings plus Roblox preferences such as text size, transparency, and reduced motion where accessible. It owns remappable sensitivity, hold/toggle preferences, subtitle/visual feedback settings, and input-assistance options.

## Gameplay controller boundaries

A controller consumes semantic state and emits local behavior or commands:

```text
ActionRouter
  ├── CharacterController
  ├── CameraController
  ├── CombatController
  ├── InteractionController
  ├── VehicleController
  ├── BuildController
  └── UIController
```

A controller should not query `PreferredInput` to decide whether `Fire` is legal. Device-specific tuning can be injected as configuration, but game state and validation remain consistent.

## Client/server boundary

### Client owns

- hardware collection and action state
- camera, cursor, selection, local HUD, button visibility
- immediate animation, audio, VFX, haptic feedback
- predicted non-authoritative visuals
- local sensitivity, layout, and accessibility presentation

### Server owns

- damage, health, cooldown truth, ammo truth
- inventory, currency, rewards, purchases, permissions
- authoritative interaction eligibility
- round, objective, vehicle ownership, and saved settings
- validation of aim descriptors, timing, distance, rate, state, and target

### Shared

- action identifiers and public schemas
- non-secret presentation config
- public ability/item identifiers
- protocol versioning

Send compact semantic intent:

```lua
ActionRequest:FireServer("Interact", {
    targetId = targetId,
    requestId = requestId,
})
```

For high-rate aim presentation, throttle/quantize and use an unreliable channel only if loss and reordering are acceptable. Important hits and outcomes still require reliable authoritative processing.

## Recommended source layout

Adapt to the project's framework; preserve a single dependency direction.

```text
ReplicatedStorage
├── Inputs                         -- InputContext hierarchy
└── Shared
    ├── InputIds.luau
    ├── InputConfig.luau
    └── NetSchema.luau

StarterPlayer
└── StarterPlayerScripts
    ├── Main.client.luau
    └── Client
        ├── Input
        │   ├── DeviceProfile.luau
        │   ├── ContextController.luau
        │   ├── ActionRouter.luau
        │   └── RawAdapters.luau
        ├── UI
        │   ├── PromptService.luau
        │   ├── UIFocusService.luau
        │   └── TouchLayoutService.luau
        └── Controllers
            ├── CharacterController.luau
            ├── CameraController.luau
            ├── CombatController.luau
            └── InteractionController.luau

ServerScriptService
└── Server
    ├── ActionRouter.server.luau
    ├── Validators.luau
    └── Services
```

See `assets/project-layout.template.md` for an implementation worksheet.

## Integration patterns

### Preserve default movement and camera

For standard Roblox character movement, keep the default PlayerModule and add project actions around it. Do not reimplement WASD, thumbstick, dynamic thumbstick, jump, and camera solely to claim cross-device support.

Replace default movement/camera only when the product needs mechanics such as tank controls, fixed-camera movement, a custom flight controller, a vehicle, an RTS cursor, or VR-specific locomotion. When replacing, disable the relevant default control intentionally and provide complete equivalents on every promised device.

### Custom movement overlay

A sprint action can modify a local movement request or request a server-approved state. It should not clone movement input for each device. All bindings trigger one `Sprint` action.

### Temporary modal

1. Push `MenuContext`.
2. Set the panel visible.
3. If gamepad is preferred, focus the remembered/default selectable object.
4. On close, hide panel, clear invalid selection, pop context, restore prior panel focus.
5. If TextBox focus occurs, push `TextEntryContext` until focus is released.

### Device hot-swap

1. Observe `PreferredInput` change.
2. Update prompt glyphs and control hints.
3. Change cursor/touch visibility and focus policy.
4. Preserve current game state, held action rules, and menu position.
5. Avoid replaying an action merely because the presentation mode changed.

## Lifecycle and cleanup

- Connect actions once per client session where possible.
- Rebind character references on `CharacterAdded`; do not reconnect global input events every respawn.
- Disconnect temporary panel, tool, vehicle, and character connections when their owner is removed.
- Reset held/analog state when a context is disabled, focus is lost, a controller disconnects, or the app resumes.
- Guard asynchronous callbacks against destroyed UI and stale characters.
- Do not poll `PreferredInput`, safe insets, or GUI selection every frame; use property/event signals.

## Performance notes

Input collection is rarely the primary bottleneck, but poor architecture can multiply work:

- avoid one `InputBegan` listener per button or item when a single action/router can dispatch
- avoid rebuilding all prompt UI every frame
- cache static action metadata and update only changed presentation
- process analog input in the controller's existing update loop, not in several services
- throttle networked aim or cursor descriptors; never stream unchanged values
- keep VR pose rendering local unless replication is actually required
- avoid expensive workspace scans inside input events

## Architecture review checklist

- [ ] Every gameplay input maps to a semantic action.
- [ ] Each action has one behavior path.
- [ ] Context state has one owner.
- [ ] Capability and preferred-input state are separate.
- [ ] Default Roblox movement/camera are preserved or deliberately replaced.
- [ ] UI focus has one owner and nested modal behavior is defined.
- [ ] Prompt switching is event-driven and works mid-session.
- [ ] Client/server authority is documented per action.
- [ ] No deprecated API is the core of a new implementation.
- [ ] Cleanup covers respawn, modal close, controller disconnect, focus loss, and project shutdown.
