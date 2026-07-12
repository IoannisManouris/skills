# Gamepad, Console, and TV Controls

Read this reference when implementing controller gameplay, console support, gamepad menu navigation, living-room readability, controller prompts, haptics, radial menus, vehicles, or analog aiming.

The goal is not merely to make buttons respond. A polished controller implementation preserves analog range, follows familiar conventions, exposes every UI path without a mouse, and remains usable from a television viewing distance.

## 1. Separate gamepad input from TV presentation

Treat these as related but different concerns:

- **Gamepad input** describes the active control method.
- **Large-display presentation** describes readability, spacing, focus visibility, and safe margins.
- **Console platform identity** may affect product features, but must not be inferred from screen size or a controller alone.

Do not call deprecated `GuiService:IsTenFootInterface()` to decide the entire interface. Build presentation from current signals such as:

- `UserInputService.PreferredInput == Enum.PreferredInput.Gamepad`
- `GuiService.ViewportDisplaySize`
- viewport dimensions and aspect ratio
- device/Core UI inset information
- the experience's own user setting for compact versus couch layout

A PC connected to a TV and controller deserves the same readable gamepad-first UI. A console player sitting close to a monitor may not need excessively large layout changes. Use a reversible presentation policy rather than a platform assumption.

## 2. Recommended semantic mapping

Follow familiar roles unless the game's genre gives a strong reason not to:

| Physical control | Common semantic role |
|---|---|
| Left stick | Character/vehicle movement or menu cursor direction |
| Right stick | Camera, aim, look, or deliberate virtual cursor |
| Primary face button | Confirm, jump, interact, or primary context action |
| Secondary face button | Cancel/back, dodge, crouch, or secondary context action |
| Left/right triggers | Aim and fire, brake and accelerate, or analog tools |
| Left/right shoulders | Cycle, modifier, alternate ability, or tab change |
| Remaining face buttons | Reload, inventory, map, tool, ability, or contextual action |
| D-pad | Discrete navigation, hotbar, emotes, communication, or quick actions |
| Menu/options controls | Pause, system menu, scoreboard, or map as platform permits |

Roblox's documented common schema associates the primary face button with confirm/jump, the secondary face button with cancel/secondary behavior, the left stick with movement, the right stick with camera, and triggers with primary actions. Use semantic labels in code and let prompt rendering resolve the actual controller glyph.

### Confirm and cancel

- Keep confirm and cancel consistent throughout the experience.
- A modal's cancel action should close only the top modal.
- Do not use the cancel button for an irreversible action without an explicit confirmation step.
- Never require players to remember a different confirm button in one menu because a developer reused a gameplay key.

### Prompt wording

Prefer:

```text
[controller glyph] Interact
[controller glyph] Back
[controller glyph] Hold to Repair
```

Avoid platform-branded text such as “Press Xbox X” unless platform identity is truly known and the brand wording is allowed. Resolve images or strings from Roblox APIs where possible; provide an accessible text fallback.

## 3. Analog input pipeline

Preserve analog values until the mechanic deliberately converts them.

```text
raw stick/trigger
      │
      ▼
InputBinding threshold / response curve / scale
      │
      ▼
semantic Direction1D or Direction2D action
      │
      ▼
mechanic normalization, acceleration, and camera/aim tuning
```

Do not apply a deadzone in the binding and then apply an unrelated second deadzone in gameplay. That produces a large unresponsive center and makes tuning impossible to reason about.

### Radial stick deadzone

For a circular stick, apply magnitude-based deadzones rather than separate X/Y thresholds:

```lua
local function applyRadialDeadzone(value: Vector2, inner: number, outer: number): Vector2
    local magnitude = value.Magnitude
    if magnitude <= inner then
        return Vector2.zero
    end

    local usableRange = math.max(outer - inner, 1e-4)
    local normalizedMagnitude = math.clamp((magnitude - inner) / usableRange, 0, 1)
    return value.Unit * normalizedMagnitude
end
```

Guidance:

- Measure drift on real controllers before choosing the inner deadzone.
- Keep the outer threshold below or at 1 only when hardware cannot reliably reach full scale.
- Expose sensitivity and, for aim-heavy games, deadzone options when feasible.
- Use one radial transformation for movement and separately tune camera/aim curves; their desired feel differs.

### Response curves

A common aim curve gives lower gain near center for precision and higher gain near the edge for turning speed. Avoid hidden, extreme acceleration that makes muscle memory inconsistent.

Document:

- inner and outer deadzones
- response curve/exponent
- base sensitivity
- scoped/ADS multiplier
- maximum turn speed
- acceleration time, if any
- smoothing method and latency cost

Use `InputBinding.ResponseCurve`, thresholds, scale, and clamp behavior when those properties express the desired transformation cleanly. Put remaining mechanic-level processing in one controller, not several scripts.

### Triggers

Triggers are analog. For boolean actions:

- define press and release thresholds with hysteresis so input does not chatter near one threshold
- avoid treating tiny trigger noise as a shot
- do not require a full 1.0 press unless the mechanic intentionally needs it

For accelerator/brake or variable tools, use `Direction1D` and retain the analog value.

## 4. Movement, camera, and aim

### Movement

Preserve Roblox default character movement when it meets the game's needs. For custom movement:

- rotate stick input relative to the intended camera/body frame
- keep diagonal magnitude at or below one
- decide whether walk speed scales linearly with stick magnitude
- provide predictable transitions between walk, run, sprint, and crouch
- avoid sudden digital snapping unless the genre intentionally uses a grid
- test low-magnitude movement for animation and network ownership edge cases

### Camera

Controller camera requires both precision and turning range:

- small stick displacement should support fine correction
- full displacement should turn quickly enough for combat
- vertical sensitivity should be independently considered, though a single setting may be the default
- inversion should be a user option where appropriate
- camera smoothing must not create obvious input lag
- frame-rate-independent integration is required

Do not multiply a per-frame input by frame rate. Integrate using time correctly or consume the action value through the camera system's expected update loop.

### Aim assistance

Aim assistance is a device adaptation, not permission to remove player agency. Build it from separable components:

- target candidate filtering
- friction/slowdown near a valid target
- mild rotational assistance when input direction supports it
- optional snap only for genres that expect it
- occlusion, distance, team, and state checks
- target-switch rules
- strength settings and accessibility options

Do not let aim assist acquire targets through walls, outside the weapon's valid range, or behind the player's intended camera cone. The server still validates hits and damage.

### Lock-on

A robust lock-on system defines:

- acquire action and release action
- maximum angle/distance and line-of-sight rules
- stick flick or shoulder-button target switching
- camera behavior at close range and around obstacles
- behavior when the target dies, streams out, or becomes invalid
- a visible lock indicator
- optional accessibility preference

Lock-on should consume a semantic `LockOn` action, not hard-code one button in the combat module.

## 5. Gamepad-friendly mechanic patterns

### Hotbar

Useful patterns include:

- D-pad left/right cycles items; confirm equips or uses
- shoulders cycle tabs/categories
- holding a modifier exposes a second quick-action layer
- direct face-button actions for a small, stable ability set

Always show the selected item and never rely on hover.

### Radial menus

For a radial menu:

1. Hold a semantic action to open.
2. Use the left or right stick as a `Direction2D` selection vector.
3. Add a center neutral zone so players can cancel.
4. Apply angular hysteresis so the selection does not flicker at segment boundaries.
5. Confirm on release only when a valid wedge is selected.
6. Keep the player safe from accidental gameplay actions while the radial context is enabled.
7. Provide a list/grid alternative where accessibility or large item counts demand it.

### Inventory

- Enter focus at the last selected item or a stable default.
- Keep item grid movement predictable.
- Scroll the selected item into view.
- Put item actions in a focused command area or context menu.
- Provide explicit sort/filter/tab actions.
- Do not require drag-and-drop; add pick-up/place, equip, move, split, or context commands.

### Vehicles

Use analog inputs for steering, throttle, brake, pitch/yaw, or altitude where the vehicle supports them. Define:

- enter/exit context transition
- camera recenter behavior
- steering return and speed sensitivity
- trigger behavior and reverse rules
- handbrake/boost/weapon actions
- controller disconnect behavior
- accessible alternatives for simultaneous trigger/shoulder demands

### Building and editor-like tools

Controller building needs discrete alternatives to precise pointer manipulation:

- ray-based placement from screen center or a controlled virtual cursor
- grid snap and rotation steps
- axis/mode cycling
- depth/distance adjustment
- undo/redo
- visible placement validity
- direct focus paths for property panels

Avoid exposing a raw desktop gizmo with tiny handles as the only path.

## 6. UI focus and navigation

A controller-ready interface is a focus graph, not a pile of clickable buttons.

For every screen:

- all interactive elements that should be reachable are `Selectable`
- hidden, disabled, clipped, or non-actionable elements cannot retain selection
- the selected state is unmistakable at viewing distance
- entry focus is deterministic
- directional movement matches spatial expectation
- scroll containers reveal selection
- selection is restored after a child modal closes
- cancel/back has one predictable result
- no essential information exists only on hover

Use `GuiService.SelectedObject` for focus ownership and explicit `NextSelection*` links when automatic geometric navigation is unreliable. Do not build new systems around deprecated selection-group APIs.

### Automatic versus explicit links

Automatic navigation is suitable for simple, regular layouts. Set explicit links when:

- cards overlap or use irregular positions
- a grid wraps unexpectedly
- sidebars and content panes should not cross unintentionally
- disabled/hidden entries create gaps
- a carousel, radial, or virtualized list changes dynamically
- the desired next item is not geometrically nearest

Recompute explicit links when a dynamic collection changes.

### Virtual cursor

Prefer direct focus navigation for ordinary menus. A virtual cursor may be justified for:

- world maps
- freeform canvas/editors
- dense interfaces designed around arbitrary coordinates
- mechanics where position itself is meaningful

When implementing one:

- use the right stick or a dedicated stick action
- provide acceleration and fine-control behavior
- constrain it to the usable viewport
- snap or magnetize to meaningful targets when helpful
- expose cursor speed
- return to direct navigation when leaving cursor mode
- ensure confirm, cancel, scroll, drag, and context actions are fully mapped

A virtual cursor is not a shortcut for avoiding a usable focus graph.

## 7. Device switching and controller lifecycle

Listen for both presentation and capability changes:

- `PreferredInput` changes: update prompts, selection policy, and cursor/touch presentation.
- gamepad connection/disconnection: update availability and recover safely.
- navigation gamepad changes: do not assume `Gamepad1` is always the active navigation device.

On a controller disconnect:

- pause only if the game's design requires it and multiplayer fairness allows it
- show a clear reconnect or alternate-input message
- avoid leaving a held action logically active
- clear transient stick/trigger state
- preserve menu state and selection when possible

On hot-swap back to gamepad, restore a sensible selected object rather than forcing the player to click first.

### Multiple controllers

Roblox exposes connected gamepad information and navigation-gamepad behavior. Unless local multiplayer is explicitly supported:

- route UI navigation from the active navigation controller
- avoid binding gameplay state globally to every connected controller
- test what happens when another controller connects or becomes preferred
- never identify a player solely by gamepad ordinal

## 8. Prompts and glyphs

Use `UserInputService:GetImageForKeyCode()` and `GetStringForKeyCode()` where appropriate, with a text fallback. Re-render when `PreferredInput` changes.

The prompt system should receive a semantic action ID and return presentation:

```text
PromptCatalog["Interact"]
    ├── keyboard binding → localized key string/image
    ├── gamepad binding → controller glyph/string
    ├── touch binding → short button label/icon
    └── VR binding → hand/controller role label
```

Do not let gameplay scripts choose prompt assets. See `assets/prompt-glyphs.luau`.

## 9. Haptics

Use haptics as redundant feedback, not the only signal. Roblox supports `HapticEffect` on supported PlayStation, Xbox, and Quest Touch controllers.

Good uses:

- UI click/selection confirmation
- collision or impact
- weapon recoil
- successful interaction
- low-health or environmental cues used sparingly

Rules:

- match effect intensity/duration to event importance
- avoid constant rumble that causes fatigue
- do not vibrate for every focus move unless the effect is subtle and tested
- stop/cancel effects during teardown and state transitions
- provide a haptics setting or honor accessibility preferences where applicable
- pair haptics with visual/audio feedback

## 10. TV and living-room presentation

### Readability

Test at realistic distance, not only at a desktop monitor. Use:

- larger base text and control labels for large-display presentation
- high-contrast selected states
- fewer simultaneous columns and dense controls
- short, readable prompt text
- clear hierarchy and generous spacing
- scalable text/layout constraints rather than fixed pixel assumptions alone

Use `GuiService.ViewportDisplaySize` as one signal and inspect actual dimensions. Do not assume all large displays share resolution, DPI, or safe edges.

### Safe margins

Keep critical HUD, focus rings, subtitles, confirmation controls, and notifications inside device/Core UI safe areas. Add conservative visual breathing room for couch displays, but do not double-apply inset padding.

### Navigation latency

Living-room UI feels slow when every selection waits for network data. Move selection, tabs, animation, and local previews immediately; request authoritative data asynchronously and show loading/error states.

### Text entry

Console text entry can interrupt flow. Minimize required typing by offering:

- presets
- recent choices
- searchable lists that do not require text
- optional rather than mandatory custom names
- clear focus recovery after keyboard overlay/text entry closes

Never let gameplay actions fire from key events used to enter text.

## 11. Performance and networking

Do not send raw stick values every rendered frame merely because they change continuously. Gameplay should usually:

- use local input for camera and immediate motion intent
- let Roblox character controls/replication handle default movement
- send rate-limited semantic requests for custom authoritative mechanics
- send high-rate transient data only when justified, compact, and safe to drop
- keep UI navigation entirely local

Avoid allocating tables and reconnecting events every input frame. Reuse action connections and update presentation only when state changes.

## 12. Testing matrix

At minimum, test:

- generic Controller Emulator
- supported physical controller families available to the team
- connect/disconnect during gameplay, menu, modal, vehicle, death, and loading
- keyboard/mouse → gamepad and touch → gamepad hot-swap
- stick drift and low-magnitude input
- fast diagonal menu navigation and repeat behavior
- disabled/hidden items, empty lists, virtualized grids, and scrolling
- large-display device presets and several aspect ratios
- all tasks with no mouse or touch
- text entry and focus restoration
- haptics on supported hardware, with no-haptics fallback
- network latency while navigating inventory/shop screens

Emulation proves mappings and many UI paths; physical testing proves feel, glyph expectations, drift, haptics, display distance, and platform overlays.

## 13. Anti-patterns

Repair these immediately:

- `if KeyCode == ButtonA then` scattered through mechanics
- converting a stick into four booleans before movement/aim processing
- multiple deadzones in unrelated layers
- prompts hard-coded to one controller family
- `IsTenFootInterface()` as the only console/TV decision
- a selected object with no visible focus style
- hidden controls remaining selectable
- a virtual cursor used for every menu because focus was not designed
- menu selection or tabs requiring server round trips
- drag-only inventory and hover-only tooltips
- assuming one connected controller equals one platform or player
- sending raw controller state as authoritative gameplay truth

## 14. Completion checklist

- [ ] Every promised action has a gamepad binding or documented exclusion.
- [ ] Common confirm/cancel/movement/camera roles are respected.
- [ ] Analog values remain analog through the action layer.
- [ ] Deadzone, curve, sensitivity, and trigger thresholds are documented and applied once.
- [ ] Camera and aim are frame-rate independent and configurable where appropriate.
- [ ] UI focus entry, direction, scrolling, cancel, and restoration are complete.
- [ ] The entire experience can be completed without a pointer.
- [ ] Prompts update on `PreferredInput` changes and have text fallbacks.
- [ ] Controller disconnect and hot-swap recover safely.
- [ ] Haptics are optional, restrained, and paired with another cue.
- [ ] Large-display text, selected states, and safe margins are tested at distance.
- [ ] Physical controllers and displays are represented in the final test report.
