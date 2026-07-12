# Keyboard and Mouse Controls

Read this reference when implementing PC controls, raw mouse/pointer behavior, keyboard shortcuts, text entry, editor-like mechanics, rebinding, international layouts, or focus-loss handling.

## Default strategy

Use semantic `InputAction` instances and keyboard/mouse `InputBinding` children for gameplay actions. Use `UserInputService` directly only for cases such as:

- mouse delta/location and pointer capture
- scroll/pinch-like pointer actions not represented cleanly by the current action map
- raw hover or drag support
- text focus and on-screen keyboard awareness
- window focus changes
- low-level diagnostics

If using `InputBegan`, `InputChanged`, or `InputEnded`, honor `gameProcessedEvent` unless the action intentionally overrides processed input. A key typed into chat or a TextBox must not fire gameplay by default.

## Keyboard action design

### Movement

Standard humanoid movement should normally remain on Roblox default controls. For custom movement, combine direction inputs into one normalized `Move` vector. Clamp diagonal magnitude.

Support arrow keys or alternate layouts only when product requirements justify them; a configurable binding system is better than hard-coding many duplicates.

### Shortcuts

Keep shortcuts contextual and discoverable:

- one semantic action per shortcut
- disable gameplay shortcuts during text entry
- avoid collision with Core/experience menus and mouse-lock behavior
- show the current key in prompts/settings
- provide controller/touch/VR equivalents for required functions
- do not require obscure multi-key chords for core play

### Modifiers

The Input Action System supports primary/secondary modifier properties on bindings. Use them for intentional commands such as editor shortcuts, not as a substitute for contexts. A menu-only `Ctrl+F` belongs in the menu context; it should not be globally active and then ignored by gameplay code.

Define left/right modifier equivalence deliberately. Test sticky keys and accessibility input behavior where relevant.

## International keyboard layouts

`Enum.KeyCode` identifies physical/logical keys according to Roblox's input model, but the displayed label should use current Roblox key-code string APIs where possible.

Rules:

- use `UserInputService:GetStringForKeyCode()` for displayed keyboard names
- use the selected binding, not the default binding, in prompts
- do not render “Z” or “Y” from an English asset and assume all layouts match
- keep action labels localized separately from key labels
- test common non-US layouts and keys that may be unavailable or moved
- avoid basing gameplay on typed character text when a physical action binding is intended
- validate saved keycodes after game updates and setting migrations

For text entry, let TextBox/IME composition handle characters. Do not implement chat-like text through gameplay key events.

## Mouse look and pointer lock

`UserInputService.MouseBehavior` and mouse delta are client presentation/control state. Establish an owner—usually the camera controller.

### Gameplay mode

- capture/lock only when the camera needs relative motion
- process delta in one camera path
- apply sensitivity once
- avoid heavy work in input/render callbacks
- restore a valid cursor state after respawn or focus regain

### Menu mode

- release capture for pointer-driven UI
- show the cursor unless a deliberate virtual-cursor design is active
- preserve the previous camera/cursor mode and restore it on close
- clear held mouse buttons/actions when the window loses focus

### Hybrid mode

Some games keep camera look while showing a centered reticle and use keyboard focus for menus. Document the mode transition explicitly; do not allow a hidden cursor to click UI unintentionally.

## Mouse sensitivity and precision

Mouse delta is not the same control quantity as stick displacement. Keep a mouse-specific sensitivity setting and avoid gamepad response curves/deadzones on mouse input.

For precision interactions:

- use viewport rays from the current cursor/reticle
- maintain stable hover target selection with hysteresis when objects overlap
- separate visual hover from server-authoritative interaction
- avoid snapping the physical cursor for aim assistance
- provide a reduced sensitivity/fine-adjust modifier only when discoverable and useful

High polling-rate mice can generate frequent changes. Process only the latest/accumulated delta in the camera's update loop and keep event callbacks lightweight.

## Buttons and wheel

Map:

- primary click to the semantic primary action or GUI activation
- secondary click to an explicit secondary action with alternatives
- middle click only for optional/advanced behavior
- wheel to zoom, cycle, or scroll according to context

Do not let one wheel event both scroll a menu and switch weapons. Context and processed-input handling should make ownership unambiguous.

Wheel repeat/step behavior should be rate-limited by the controller, not by several raw listeners.

## Hover, context menus, and drag

Mouse affordances can be richer but must remain optional for cross-device support.

- hover tooltips also appear on focus/tap
- context menus have gamepad/touch/keyboard activation paths
- drag-and-drop has select/move or action-menu alternatives
- double-click behavior has a single-activation alternative
- edge scrolling during drag is bounded and cancellable
- the server validates consequential drops, placements, trades, and purchases

Use `UIDragDetector` for a modern UI drag primitive where it fits, but keep semantic fallback operations.

## Keyboard navigation of UI

Controller-style focus navigation can also support arrow keys. Avoid intercepting arrow keys while a TextBox or scrolling text editor needs them.

Common mappings:

- arrows/WASD: directional navigation only when not consumed by gameplay/text
- Enter/Space: confirm/activate
- Escape/Backspace: cancel/back according to context
- Tab/Shift+Tab: ordered focus where appropriate
- Q/E or bracket keys: tab/page switching, with visible prompts

Do not create two independent focus systems for keyboard and gamepad. Use one selection owner and configure which keys drive it.

## Text entry

On TextBox focus:

- enter `TextEntryContext`
- stop movement/fire/repeat actions that are currently held
- release mouse capture if necessary
- keep escape/submit semantics clear
- do not mutate focus because `PreferredInput` changes while typing

On release:

- sanitize/validate data at the appropriate layer
- restore prior input context and pointer mode
- avoid immediately firing the key that closed/submitted the TextBox as a gameplay action

Test:

- composition/IME
- paste and selection
- enter versus multiline behavior
- escape/cancel
- focus switching between fields
- chat/Core UI overlap
- alt-tab during typing

## Focus loss and alt-tab

Listen to window focus events when held state or pointer capture can become stale.

On focus release:

- clear held semantic actions/repeat loops
- stop drag operations
- pause or neutralize custom camera/movement input as appropriate
- release temporary pointer capture if the engine does not do so safely
- do not tell the server the player completed an action merely because input ended abnormally

On focus regain:

- sample current action/context state carefully
- restore the intended cursor/camera mode
- avoid treating still-held keys as fresh presses unless designed

## Rebinding UI

A keyboard/mouse binding screen should:

1. enter a capture context that blocks gameplay
2. wait for one allowed input
3. reject reserved/unsupported keys with a helpful message
4. detect conflicts in overlapping contexts
5. offer swap, unbind, or cancel according to policy
6. display the resolved key string
7. save a versioned identifier
8. provide reset-to-default

Do not bind on key release if the UI instruction says “press a key” unless modifier capture requires it. Time out or provide a visible cancel path.

Mouse buttons and wheel bindings need explicit representation; do not coerce them into fake keyboard strings.

## Core mechanic patterns

### Shooter

- mouse drives direct camera delta
- primary/secondary buttons trigger semantic actions
- reticle ray defines aim descriptor
- recoil is camera/weapon feedback, not input mutation
- server owns fire rate, ammo, hit acceptance, and damage

### Top-down/RTS

- pointer viewport position drives selection/commands
- keyboard controls camera pan/shortcuts
- selection rectangle and drag are local presentation
- server validates commands and ownership
- controller/touch require cursor or focus alternatives if supported

### Builder/editor

- pointer ray selects handles/objects
- modifiers choose axis/mode
- wheel adjusts depth/scale if appropriate
- keyboard provides discrete precise steps
- all transformations are previews until server validation/commit

### Driving

Keyboard synthesizes digital steering/throttle targets; vehicle dynamics provide acceleration. Do not apply a stick deadzone to keyboard values.

## Keyboard/mouse anti-patterns

- dozens of unrelated `InputBegan` listeners checking the same keys
- ignoring `gameProcessedEvent`
- firing gameplay while chat/TextBox is focused
- hard-coded English key names in prompts
- treating mouse delta like a gamepad stick
- smoothing mouse twice
- permanent mouse lock after opening menus
- required right-click, hover, wheel, or drag behavior with no alternative
- reconnecting global input on every respawn
- continuing held actions after alt-tab/focus loss
- sending mouse delta every frame to the server without a clear need

## Acceptance checklist

- [ ] Semantic actions own keyboard/mouse bindings.
- [ ] Default movement/camera are preserved or intentionally replaced.
- [ ] Processed UI/text input does not trigger gameplay.
- [ ] Displayed keys use current binding and key-string/glyph APIs.
- [ ] Mouse look, pointer mode, and menu transitions have one owner.
- [ ] Text focus and focus loss clear held actions safely.
- [ ] Wheel/context/drag behavior is context-exclusive.
- [ ] International layouts and IME have test coverage.
- [ ] Every required pointer-only affordance has a non-pointer path for promised devices.
