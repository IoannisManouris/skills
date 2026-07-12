# Semantic Actions and Core Mechanics

Read this reference when building the action map or adapting movement, camera, aiming, combat, vehicles, radial menus, building, hotbars, or other core mechanics across devices.

## Start with intent

An action name should describe the player's intent, not the control used to express it.

Good:

- `Move`
- `Look`
- `Jump`
- `Interact`
- `PrimaryAction`
- `AimDownSights`
- `Reload`
- `OpenInventory`
- `SelectHotbarSlot`
- `VehicleThrottle`
- `BuildRotate`
- `RecenterVR`

Avoid:

- `PressE`
- `LeftClick`
- `GamepadX`
- `MobileAttackButton`
- `QuestTrigger`

Use stable IDs because prompts, bindings, settings, telemetry, tutorials, and remotes may all reference them.

## Choose the correct InputAction type

| Type | State | Typical actions | Design notes |
|---|---|---|---|
| `Bool` | `boolean` | jump, confirm, interact, reload, fire edge, menu | Define tap/hold/repeat semantics separately. |
| `Direction1D` | `number` | throttle, brake, zoom, lean, scroll-like axis | Preserve analog magnitude when useful. |
| `Direction2D` | `Vector2` | move, look, aim, menu vector, radial selection | Prefer radial magnitude handling for sticks. |
| `Direction3D` | `Vector3` | custom six-axis controls or spatial input | Use only when the mechanic consumes three axes; VR tracked poses normally come from `VRService`. |
| `ViewportPosition` | `Vector2` | pointer/touch aim position, screen-space selection | Convert to a ray/world descriptor at the controller boundary. |

Do not represent every input as `Bool`. Throwing away analog magnitude early makes movement, camera, vehicles, menus, and accessibility worse.

## Action contract worksheet

For every action, define:

```text
ID: Interact
Context: GameplayContext
Type: Bool
Semantics: Press once to request the highest-priority valid nearby interaction.
Repeat: No
Cancel: Release has no gameplay effect
Authority: Client chooses candidate; server validates target, range, state, and rate.
Keyboard/mouse: E
Gamepad: ButtonX / platform-equivalent west/left face button as chosen by schema
Touch: contextual InteractButton
VR: dominant-hand trigger or grip according to object interaction model
Prompt: localized “Interact” plus active binding glyph
Accessibility: optional hold duration and auto-select target setting
```

Use `assets/action-map.template.json` to keep this machine-checkable.

## Baseline action catalog

Use only actions the game needs. This catalog is a starting point, not a mandatory list.

| Domain | Suggested action | Type | Notes |
|---|---|---:|---|
| Character | `Move` | Direction2D | Keep Roblox default movement when standard. |
| Character | `Jump` | Bool | Preserve default jump unless replacing full controls. |
| Character | `Sprint` | Bool/Direction1D | Decide hold vs toggle; server owns stamina/speed permission. |
| Character | `Crouch` | Bool | Toggle/hold accessibility option; collision/state server-validated. |
| Camera | `Look` | Direction2D | Device adapters use different units; normalize in camera controller. |
| Camera | `Zoom` | Direction1D | Mouse wheel, buttons, pinch, or stick/trigger combination. |
| Interaction | `Interact` | Bool | One target resolver; contextual touch button. |
| Combat | `PrimaryAction` | Bool | Define automatic repeat in weapon controller, not binding duplication. |
| Combat | `SecondaryAction` | Bool | Aim, block, alternate fire, or context-specific behavior. |
| Combat | `Aim` | Direction2D/ViewportPosition | Convert to a common world-space aim descriptor. |
| Combat | `Reload` | Bool | Provide touch and controller path even if auto-reload exists. |
| UI | `OpenInventory` | Bool | Opening action plus `MenuContext` cancel path. |
| UI | `Confirm` | Bool | Prefer GUI `Activated` for focused buttons; action is useful for non-GUI systems. |
| UI | `Cancel` | Bool | Close the top modal only; use consistent back stack. |
| UI | `TabLeft`/`TabRight` | Bool | Shoulders, Q/E, swipe only as optional enhancement. |
| Hotbar | `CycleSlot` | Direction1D | Wheel, shoulders, swipe; discrete debounce/repeat policy. |
| Vehicle | `VehicleSteer` | Direction1D/2D | Analog for gamepad/touch; keyboard synthesizes extremes. |
| Vehicle | `VehicleThrottle` | Direction1D | Separate brake/reverse when handling requires it. |
| Build | `Place` | Bool | Server validates placement and cost. |
| Build | `Rotate` | Direction1D/Bool | Fine/coarse modes and accessible buttons. |
| VR | `GrabLeft`/`GrabRight` | Bool | Pair with tracked hand pose, not a flat-screen cursor assumption. |
| VR | `TeleportAim` | Bool + pose | Press/hold previews, release commits valid destination. |
| VR | `RecenterVR` | Bool | Calls current VR recenter API locally. |

## Movement

### Preserve the default when possible

Roblox's default character controls already cover keyboard, touch, and gamepad. For a standard humanoid, add actions such as sprint, dash, interact, or abilities around the default instead of recreating movement.

Before replacing default controls, answer:

- Does the mechanic require a non-humanoid movement model?
- Does movement need a different reference frame?
- Is this a vehicle, flight, swimming, RTS, click-to-move, or fixed-camera game?
- Can a thin modifier around default movement meet the design?

A custom controller inherits responsibility for movement, jump, camera interaction, touch controls, analog behavior, reset/focus handling, and every promised device.

### Analog vector processing

For stick-like input, use a radial deadzone so diagonal directions remain consistent:

```lua
local function applyRadialDeadzone(value: Vector2, deadzone: number): Vector2
    local magnitude = value.Magnitude
    if magnitude <= deadzone then
        return Vector2.zero
    end

    local normalizedMagnitude = math.clamp((magnitude - deadzone) / (1 - deadzone), 0, 1)
    return value.Unit * normalizedMagnitude
end
```

Apply a deadzone exactly once. If `InputBinding` thresholds/response curves already provide the desired shape, do not repeat the same transformation in the mechanic.

Choose deadzones from physical-device testing. Too small causes drift; too large removes fine control. Avoid one unexplained global constant for movement, aim, driving, and radial menus—their needs differ.

### Keyboard synthesis

Keyboard movement is digital. Combine directions into a vector and clamp magnitude so diagonals are not faster. The Input Action System can use direction properties and `ClampMagnitudeToOne`; a custom adapter should produce equivalent normalized state.

### Movement reference frame

Document whether movement is:

- camera-relative
- character-relative
- world-relative
- vehicle-relative
- hand/controller-relative in VR

Do not let each device choose a different frame accidentally. Differences should be deliberate options, not implementation leakage.

### Acceleration and deceleration

Apply acceleration to the movement model, not to input-device identity. Keyboard can feed a target magnitude of 0 or 1 while a stick feeds intermediate values. Vehicles and weighty characters may smooth target velocity; an agile avatar often should not.

For frame-rate-independent exponential convergence:

```lua
local alpha = 1 - math.exp(-responsiveness * dt)
current = current:Lerp(target, alpha)
```

Do not smooth twice. Excess input filtering creates latency, especially on touch and mouse.

## Camera and look

Different devices express look differently:

- mouse: relative delta with high precision
- gamepad: angular velocity controlled by stick displacement
- touch: swipe delta or direct drag region
- VR: headset pose plus optional snap/smooth body turning

Normalize these in a camera controller with device-specific adapters/configuration, then expose common camera intent such as desired yaw/pitch delta or angular velocity.

### Sensitivity

Maintain separate settings when units differ:

- mouse sensitivity
- gamepad horizontal/vertical sensitivity and response curve
- touch swipe sensitivity
- VR smooth-turn rate

Allow invert-Y where appropriate. Save settings on the server or approved profile system; apply locally.

### Camera smoothing

Smooth camera targets only when the design calls for it. Never filter headset tracking. For flat-screen cameras:

- use `dt`-based smoothing
- keep direct mouse response crisp
- avoid stacking engine smoothing, input smoothing, recoil smoothing, and spring smoothing without measuring total latency
- reset spring/velocity state on respawn, camera-mode change, and focus regain

### Mouse lock and menus

Release pointer lock/capture when a pointer-driven menu opens unless the menu intentionally uses a virtual cursor. Restore the previous mode on close rather than forcing a hard-coded state.

## Aiming contract

Convert device-specific aim into a common descriptor at the combat boundary:

```lua
type AimDescriptor = {
    origin: Vector3,
    direction: Vector3,
    screenPosition: Vector2?,
    candidateTargetId: string?,
    timestamp: number?,
}
```

- Mouse/touch: create a viewport ray from pointer position.
- Gamepad: move a reticle or rotate camera, then ray through reticle/center.
- VR: ray or trajectory from the relevant hand/controller pose, or use physical object interaction.

The server validates range, fire rate, player state, origin plausibility, target eligibility, obstruction, and lag policy. It does not trust `candidateTargetId` or client damage.

## Aim assistance

Aim assistance is an outcome-balancing tool, not one global “mobile buff.” Separate components:

- **target scoring**: distance from reticle, world distance, visibility, team, priority
- **friction**: lower look speed near a valid target
- **magnetism**: bias shot/reticle direction within a bounded cone
- **adhesion**: follow a target while input remains compatible
- **snap**: one-time adjustment, usually for noncompetitive or accessibility use
- **automation**: auto-fire or auto-target, a separate product/fairness decision

Requirements:

- no target through walls unless the mechanic explicitly allows it
- deterministic target tie-breaking
- clear break conditions when the user moves away
- separate tuning for gamepad and touch where needed
- do not apply assistance to mouse by accident through a shared camera path
- expose accessibility controls without silently changing competitive rules
- record tuning and test against moving, overlapping, off-screen, friendly, and occluded targets

## Firing, holds, repeats, and buffering

Define the action semantics independently of input events:

### Tap versus hold

Record press time in the controller, not in separate device scripts. Use the same thresholds across bindings unless touch accessibility requires a deliberate alternate gesture.

### Automatic fire/repeat

A held boolean action starts a controller-owned repeat loop governed by weapon fire rate. The server enforces the actual cadence. Stop on release, context disable, character death, focus loss, or weapon unequip.

### Input buffering

For actions such as jump, dodge, or combo attacks:

- buffer the semantic action for a short, tuned window
- consume it once when state permits
- clear it when the context changes or the action becomes invalid
- server-authoritative mechanics should validate the accepted timing window

Do not create different buffering behavior because one device sends a button and another sends a touch button.

### Chords/modifiers

Use modifiers sparingly. They are natural on keyboard, possible on gamepad, and often poor on touch/VR. Every required chord needs a touch and accessibility alternative. Avoid hiding core actions behind simultaneous multi-button presses.

## Interaction systems

Use one target resolver that scores candidates by:

- eligibility and current game state
- line of sight/occlusion
- distance and facing
- screen/reticle proximity
- explicit priority
- stability/hysteresis to prevent flicker

All devices invoke the same `Interact` action. Presentation differs:

- mouse: click target or use key prompt
- gamepad: focused/current candidate plus action button
- touch: tap object or contextual button
- VR: direct grab/touch or ray interaction

The server resolves or revalidates the target. A client-provided candidate is a hint, not authority.

## Inventory and hotbars

### Hotbar

Support:

- direct numeric keys where available
- wheel/shoulder cycling
- touch buttons or horizontal swipe as optional enhancement
- gamepad selection with visible focus
- VR wrist/radial/physical inventory appropriate to the experience

Keep equip behavior in one controller. Cycling is a signed step action, not separate per-device equip logic.

### Inventory

Use a mode/context transition. On open:

- disable or sink conflicting gameplay actions
- focus a sensible gamepad item/control
- expose keyboard search shortcuts only while not typing
- support touch scroll and tap
- give drag-and-drop a confirm/move alternative
- restore previous selection and gameplay context on close

## Radial menus

A radial menu consumes a `Direction2D` selection vector plus confirm/cancel semantics.

- define an inner deadzone so releasing near center can cancel
- apply angular hysteresis so adjacent wedges do not flicker
- support mouse position, stick vector, touch drag, and VR ray/hand direction
- show both selected wedge and action outcome
- offer list navigation for users who cannot hold a direction
- decide whether release commits or a separate confirm commits; keep it consistent

## Vehicles

Vehicle controls should map to physical intent:

- steering: Direction1D or Direction2D
- throttle/brake: separate Direction1D values when analog control matters
- handbrake/boost/horn/exit: Bool
- camera/look: separate from steering unless the product deliberately couples them

Design differences:

- keyboard uses digital target values and vehicle dynamics provide ramping
- gamepad uses analog sticks/triggers with deadzones
- touch uses a steering wheel/joystick/buttons chosen for the vehicle and screen
- VR may use physical controls, controller pose, or conventional sticks with comfort restrictions

Server ownership depends on physics architecture, but rewards, races, damage, and impossible motion require server validation. Network ownership is not a trust boundary.

## Building and editor-like controls

Separate selection, transform intent, placement confirmation, and camera navigation.

- mouse: pointer ray, wheel, modifiers, drag handles
- keyboard: shortcuts and fine/coarse increments
- gamepad: reticle/ray, shoulders/triggers for axis or mode, clear focus state
- touch: direct manipulation with handles, pinch/rotate only when reliable, explicit buttons for precision
- VR: direct manipulation, ray grab, two-hand scale/rotate where comfortable

Provide an undo/cancel path on every device. The server validates placement volume, ownership, cost, collision, and rate.

## Rebinding

A scalable binding system stores semantic action-to-binding preferences, not code branches.

Requirements:

- keep essential cancel/menu/recovery actions reachable
- prevent or clearly resolve conflicts inside overlapping contexts
- identify reserved/Core bindings and unsupported inputs
- display the actual localized key/controller glyph after binding
- support reset-to-default per device
- save only serializable binding identifiers and validate on load
- migrate versioned settings when actions are renamed
- do not promise arbitrary touch rebinding unless the UI supports repositioning and conflict-safe layouts
- VR rebinding must distinguish left/right controller and handedness where applicable

## Action telemetry and diagnostics

Useful debug information includes:

- current enabled contexts and priorities
- latest preferred input and capability snapshot
- current action state values
- binding chosen for each prompt
- focus owner and selected GUI object
- device disconnect/focus-loss resets
- remote request rates by semantic action

Keep telemetry development-only or privacy-conscious. Do not log raw text entry, unnecessary pointer traces, or sensitive user behavior.

## Core-mechanic review checklist

- [ ] Action names describe intent.
- [ ] Correct action types preserve analog/pointer state.
- [ ] Default character controls are retained unless a complete replacement is justified.
- [ ] Deadzone and response shaping happen once.
- [ ] Sensitivity units and settings are device-appropriate.
- [ ] Camera smoothing is frame-rate independent and not applied to VR head tracking.
- [ ] Aim converts to one world-space contract.
- [ ] Aim assistance has bounded, testable components.
- [ ] Hold/repeat/buffering live in the controller, not in device scripts.
- [ ] Inventory, radial, vehicle, and build flows have complete device alternatives.
- [ ] Rebinding conflicts, recovery bindings, saving, and migration are defined.
- [ ] Server authority is explicit for every gameplay-affecting action.
