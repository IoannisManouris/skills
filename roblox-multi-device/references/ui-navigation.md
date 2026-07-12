# Cross-Device UI, Focus, Prompts, and Layout

Read this reference for menus, HUDs, inventories, hotbars, shops, dialogs, radial menus, drag interactions, safe areas, controller navigation, prompt glyphs, and accessibility.

## UI is an input surface

A screen is not cross-device merely because it renders at every resolution. Every interactive path must support:

- pointer click/hover/scroll where appropriate
- touch tap/drag/scroll without hover dependence
- gamepad/keyboard focus navigation and activation
- VR ray/direct interaction or an immersive alternative
- consistent cancel/back and modal behavior
- readable layout at phone distance, desktop distance, and living-room distance when those targets are promised

Audit complete tasks, not individual widgets: open inventory, inspect item, change tab, equip, close; purchase, confirm, recover from error; type, submit, cancel; drag or move an item using every supported device.

## Activation contract

For ordinary buttons, use `GuiButton.Activated` as the shared activation signal. It can represent activation from different input methods. Keep `MouseButton1Click` only when behavior is intentionally mouse-specific.

```lua
button.Activated:Connect(function(inputObject, clickCount)
    controller:activateItem(button:GetAttribute("ItemId"))
end)
```

The UI callback should call the same semantic controller method used by input actions. Do not duplicate purchase, equip, cooldown, or interaction logic inside each device path.

Use `SecondaryActivated` only for a clearly designed secondary action. A right-click-only function needs a controller/keyboard/touch alternative.

## Focus ownership

`GuiService.SelectedObject` is global project UI state. One project service should own it.

The owner should:

- remember a valid selection per panel
- select a deliberate default when gamepad navigation enters a panel
- validate `Visible`, `Selectable`, `Interactable`, ancestry, and modal membership
- restore parent-panel selection after a nested dialog closes
- clear selection when the user returns to pointer/touch mode, if that matches the UX
- reacquire focus on the next gamepad navigation input
- prevent selection from landing in hidden, disabled, clipped, or off-panel controls
- clear stale references when UI is destroyed

Avoid unrelated scripts repeatedly assigning `SelectedObject`; they create focus ping-pong and modal escape bugs.

## Focus stack

Use a stack for nested UI:

```text
Gameplay
  └── Inventory (remember: ItemGrid/Slot7)
       └── ItemDetails (remember: EquipButton)
            └── ConfirmDiscard (default: CancelButton)
```

Opening a child stores the parent's selected object. Closing the child restores it if still valid, otherwise selects the parent's default. Closing the root clears or restores gameplay focus according to input mode.

`assets/ui-focus-controller.luau` provides a minimal implementation pattern.

## Selectability and navigation

For each focusable `GuiObject`:

- set `Selectable = true`
- set a clear, high-contrast selected style through `SelectionImageObject`, state styling, or both
- use `SelectionOrder` when automatic order needs help
- use `NextSelectionUp`, `NextSelectionDown`, `NextSelectionLeft`, and `NextSelectionRight` for non-geometric layouts, wrap rules, tabs, and virtualized grids
- set hidden/disabled items non-selectable or route around them

Automatic spatial navigation works for simple layouts, but verify it. It often fails with:

- two-column screens with sidebars
- overlapping/animated panels
- scrolling grids and recycled cells
- wrap-around hotbars
- tabs above lists
- controls whose visual and hierarchy order differ
- invisible placeholders

Do not build new navigation around deprecated `AddSelectionParent`, `AddSelectionTuple`, or `RemoveSelectionGroup` APIs.

### Directional graph review

Treat controller focus as a directed graph. For every node:

- each allowed direction reaches the intended neighbor
- no edge enters another modal or hidden panel
- there is a route to every required control
- there is a route back
- list/grid edges either stop, wrap, scroll, or move sections deliberately

A useful debug mode draws or logs the four neighbors of `SelectedObject` and highlights invalid targets.

## Scrolling and virtualized content

When selection moves into a scrolling list, ensure the selected object becomes visible. For virtualized cells:

- keep selection by stable item ID, not recycled instance identity
- recreate/select the visible cell after data or scroll changes
- avoid destroying the selected cell without moving focus first
- define behavior when filtering removes the selected item
- preserve scroll position when returning where practical

Touch and mouse wheel scrolling should not leave a hidden selected object that later receives controller activation.

## Cancel/back policy

Define one back stack:

1. close the top confirmation/popover
2. close item details/submenu
3. close the root menu
4. return to gameplay

Do not make the same button close all layers at once. The gamepad cancel button, keyboard escape/back shortcut, touch close button, and VR back action call the same top-level `requestBack()` behavior.

Reserve a reliable recovery route if the UI loses selection. The user should never need a pointer to escape a controller-only screen.

## Text entry and IME

TextBoxes introduce a separate input state.

On focus:

- enable/push `TextEntryContext`
- suppress gameplay hotkeys that overlap typing
- preserve the selected/focused TextBox
- account for the on-screen keyboard covering content on touch devices
- avoid stealing focus due to prompt/device changes

On focus release:

- validate/submit or cancel according to the screen contract
- restore the previous context and focus target
- clear held gameplay state before re-enabling it

Use `UserInputService:GetFocusedTextBox()`, TextBox events, or centralized focus signals as appropriate. Do not infer text entry solely from the last key pressed. Test international input methods, composition, paste, and controller on-screen keyboard flows on target platforms.

## Pointer and hover

Hover may enhance but cannot contain required information.

For any hover tooltip or reveal:

- show it on keyboard/gamepad focus
- offer tap-to-select or an information button on touch
- provide a VR focus/ray equivalent
- ensure the tooltip itself does not trap focus

Cursor appearance should reflect interactable state. When a camera captures the mouse, release or adapt capture for pointer-driven menus and restore the prior mode on close.

## Drag and drop

`UIDragDetector` can unify drag interactions, but drag is not universally accessible.

Every required drag operation should have one or more alternatives:

- select source, then select destination
- “Move” action followed by directional navigation
- context menu with equip/swap/drop
- increment/decrement buttons for sliders or ordering
- direct transform controls in VR

During drag:

- capture one owner pointer/touch
- distinguish tap from drag with a movement threshold
- show valid/invalid destinations
- auto-scroll cautiously near edges
- cancel on focus loss, context change, owner destruction, or modal opening
- server-validate consequential moves

Do not use the deprecated `GuiObject.Draggable` path as the basis for a new system.

## Prompts and glyphs

Prompts should be generated from semantic action metadata and current presentation mode.

Recommended prompt model:

```lua
{
    actionId = "Interact",
    label = "Interact", -- localize this
    keyCode = Enum.KeyCode.E, -- current binding
    image = UserInputService:GetImageForKeyCode(Enum.KeyCode.ButtonX),
    text = UserInputService:GetStringForKeyCode(Enum.KeyCode.E),
}
```

Rules:

- listen to `PreferredInput` changes
- also refresh after rebinding, controller connection changes, handedness changes, or UI context changes
- use Roblox key-code image/string methods where possible
- provide text fallback when an image is unavailable
- do not hard-code Xbox letters for all controllers
- localize action labels; do not embed English in glyph images
- show hold/repeat/toggle semantics visually or in text
- avoid prompt flicker from noisy input changes; `PreferredInput` is the primary presentation signal
- keep touch buttons labeled by action meaning, not by keyboard key
- VR prompts should identify hand/controller and interaction motion when a flat glyph is insufficient

Use `assets/prompt-glyphs.luau` as a small resolver, not as a complete localization system.

## Responsive layout

Use relative layout, constraints, and breakpoints based on available space—not guessed platform names.

Consider:

- camera viewport size and aspect ratio
- `GuiService.ViewportDisplaySize` (`Small`, `Medium`, `Large`)
- device/Core UI/topbar safe insets through `GuiService:GetInsetArea()` and related properties
- `ScreenGui` inset configuration
- orientation changes
- touch-control reservations
- text expansion from localization and preferred text size
- on-screen keyboard position/size
- TV viewing distance
- VR world-space scale and distance

### Safe areas

Critical controls, prompts, currency, health, and navigation should remain within the appropriate safe region. Decorative backgrounds may bleed outward. Test notches, rounded corners, Core UI overlap, TV edge cropping, and emulator aspect-ratio extremes.

Do not assume a fixed topbar height or hard-code one phone notch. Recalculate on relevant property/viewport changes, not every frame.

### Breakpoint strategy

A robust pattern:

- **small**: simplify chrome, stack panels, prioritize thumb reach, larger relative touch targets
- **medium**: standard desktop/tablet layout
- **large**: increase text/control scale and spacing for distance; preserve focus clarity

`ViewportDisplaySize` is a layout hint, not proof of console or TV hardware.

### Scale and offset

Use scale for overall responsive placement and constraints/offsets for minimum usable sizes. Pure scale can make controls tiny on high-aspect phones; pure offsets can overflow. Combine `UIListLayout`/`UIGridLayout`, `UIPadding`, `UISizeConstraint`, `UIAspectRatioConstraint`, and `UIScale` where appropriate.

## Touch target and spacing heuristics

Roblox does not supply one universal target size for every game. As a design starting point, favor comfortably large targets with spacing that prevents accidental activation, then test with real thumbs on the smallest supported screens. Critical combat buttons usually need more separation than infrequent menu buttons.

Measure:

- hit rate and accidental taps
- reach while the other thumb moves/cameras
- overlap with default thumbstick/jump controls
- landscape and portrait layouts if both are supported
- hands of different sizes and left-handed configurations

Do not hide a tiny hitbox inside a larger-looking image; the interactive area should match visual affordance.

## TV and distance readability

For large-display/gamepad-first presentation:

- increase effective text size and line spacing
- increase focus ring thickness and contrast
- reduce dense multi-column text
- keep essential UI within generous edge margins
- avoid instructions that depend on reading tiny key labels
- present one clear primary action per modal
- minimize pointer-like precision tasks
- ensure notifications remain long enough to read from distance

## VR UI placement

Flat ScreenGui menus may be inappropriate or uncomfortable in VR. Prefer:

- world-space panels at a comfortable distance and scale
- wrist/hand UI for frequent small controls
- controller ray/laser for distant panels
- direct touch/grab for near controls
- curved or spatial layouts only when they improve comfort

Avoid attaching large opaque panels rigidly to the head. Do not place required UI behind the player without clear cues. See `references/vr.md`.

## Accessibility

Design for alternatives rather than one “accessible mode.”

Support where relevant:

- remapping and reset defaults
- hold/toggle choices for sprint, crouch, aim, and repeated actions
- adjustable sensitivity and invert axes
- aim/interaction assistance settings
- readable selected, hovered, pressed, disabled, success, and error states that do not rely on color alone
- captions/visual equivalents for audio cues
- haptic plus visual/audio feedback, never haptic-only meaning
- preferred text size and layouts that can expand
- reduced-motion behavior for menu transitions, camera shake, flashes, and repeated animations
- transparency preference where exposed and useful
- left-handed touch/VR layouts
- sufficient timeouts or user-controlled dismissal

When Roblox exposes a preference through `GuiService`, observe property changes and test fallback behavior. Project-specific settings should be saved and versioned.

## State styling matrix

Every interactive control should have discernible states:

| State | Required signal |
|---|---|
| default | label/icon and affordance |
| hover | optional pointer enhancement |
| selected/focused | strong outline/scale/background; not color alone |
| pressed | immediate visual/audio/haptic response |
| disabled | visibly unavailable and non-selectable/non-interactable |
| loading | progress/busy state that blocks duplicate activation |
| success/error | clear result with text/icon where important |

Do not animate focus so aggressively that selection feels delayed or causes motion discomfort.

## UI acceptance checklist

- [ ] Every ordinary action uses `Activated` or the shared semantic path.
- [ ] Every required screen is finishable with mouse, touch, gamepad/keyboard focus, and VR interaction where promised.
- [ ] Focus entry, restore, and cancel behavior are defined for every modal.
- [ ] Hidden/disabled elements cannot receive selection.
- [ ] Directional navigation graph is deterministic.
- [ ] Scrolling/virtualized lists keep selection visible and stable.
- [ ] Text entry suppresses gameplay and handles the on-screen keyboard.
- [ ] Required information is not hover-only.
- [ ] Drag operations have a non-drag alternative.
- [ ] Prompts update on input hot-swap and rebinding.
- [ ] Safe insets, aspect ratios, orientation, localization, and preferred text size are tested.
- [ ] Selected state is readable from TV distance and in VR where relevant.
- [ ] Reduced-motion, visual/audio/haptic alternatives, and left-handed needs are considered.
