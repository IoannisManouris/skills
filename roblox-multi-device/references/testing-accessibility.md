# Cross-Device Testing and Accessibility

Read this reference before declaring keyboard/mouse, touch, gamepad/TV, or VR support complete. Code review and emulation are necessary but not sufficient. The final report must distinguish what was inspected, emulated, automated, and physically tested.

## 1. Define the support contract

Before testing, write the promised matrix. Do not use “all devices” as an unbounded claim.

Example:

| Family | Target configurations | Required for release |
|---|---|---:|
| Keyboard/mouse | Windows/macOS desktop, common layouts, high/low sensitivity | Yes |
| Touch | Small phone, large phone, tablet, landscape; portrait only if supported | Yes |
| Gamepad | Controller Emulator plus supported physical controller families | Yes |
| TV/large display | Gamepad-first UI at several large-display presets and real viewing distance | Yes |
| VR | Quest emulation, physical target headset, seated and standing | Product-dependent |

Record explicit exclusions such as portrait play, mouse-only editor mode, local multiplayer, hand tracking, or a particular vehicle mechanic in VR. Exclusions must be visible to the user and must not leave a broken path.

## 2. Evidence levels

Use these labels in the implementation report:

- **Code-inspected** — structure and logic reviewed; no runtime proof.
- **Automated** — repeatable scripted test passed.
- **Studio-emulated** — tested in a Studio emulator/simulator.
- **Physical-device** — tested on named hardware.
- **Live-session** — tested in a published/multiplayer environment.
- **Not tested** — remaining manual requirement.

Never upgrade one evidence level into another. “Works in Device Emulator” is not “tested on mobile.”

## 3. Release gates

A device family is release-ready only when:

1. Every required gameplay action has a usable binding or intentional exclusion.
2. Every required UI task is completable with that family.
3. Input can hot-swap without stale prompts, stuck states, or lost focus.
4. Text entry and overlays return to the correct state.
5. safe areas, aspect ratios, and accessibility preferences do not hide critical content.
6. authority boundaries remain correct under latency and malicious/invalid requests.
7. frame time, memory, networking, and battery/thermal concerns are acceptable on target hardware.
8. critical and high-severity defects are resolved or the feature is removed from the support claim.
9. physical testing is complete for input feel or comfort-sensitive targets.

## 4. Test environments

### Studio tools

Use the current Studio tools appropriate to the path:

- Device Emulator for resolutions, aspect ratios, orientation, lower-memory presets, mobile, console, and VR profiles.
- Touch simulation for single-touch and two-touch gestures.
- Controller Emulator for generic and supported controller mappings.
- VR emulation for headset and controller flow.
- multi-client/server test modes for authority and replication.
- network simulation for latency, packet loss, and jitter.
- scripted testing services and virtual input where available and appropriate.

### Physical hardware

Maintain a small named test pool, for example:

```text
Phone A — compact screen, current OS, touch only
Phone B — tall aspect ratio, current OS, Bluetooth controller
Tablet A — large touch screen, hardware keyboard
Controller A — Xbox-family
Controller B — PlayStation-family
Large display — couch viewing distance
Headset A — standalone Quest target
Desktop — high-polling mouse, alternate keyboard layout
```

Do not invent coverage. List unavailable hardware in remaining risks.

## 5. Core state-transition suite

Run these transitions for each supported family:

- join → load → spawn
- spawn → gameplay
- gameplay → pause/menu → gameplay
- gameplay → inventory/shop/map → gameplay
- gameplay → text entry → gameplay
- gameplay → vehicle/build/spectator context → gameplay
- death/reset → respawn
- round end → lobby → next round
- teleport/server transfer when applicable
- window focus lost/restored
- device/controller disconnected/reconnected
- orientation/resolution change
- accessibility setting changed while a screen is open
- streamed object appears/disappears

At every transition check:

- enabled input contexts
- held actions and repeat timers
- mouse lock/cursor state
- selected/focused UI object
- touch controls and prompts
- camera mode
- interaction target/highlight
- local prediction or held objects
- server-side state and cooldowns

## 6. Hot-swap matrix

Test switching input while performing real tasks, not only on an empty screen.

| From | To | Required checks |
|---|---|---|
| Keyboard/mouse | Gamepad | prompt glyphs, focus entry, cursor/mouse lock, held key cleanup |
| Gamepad | Keyboard/mouse | clear/retain selection policy, cursor visibility, prompt update |
| Touch | Gamepad | touch button visibility, virtual thumbstick state, focus entry |
| Gamepad | Touch | selection clearing, tap activation, camera touch zones |
| Touch | Keyboard/mouse | hardware keyboard prompts, pointer/hover behavior |
| Non-VR | VR | only when runtime/product flow supports it; camera/origin/UI reinitialization |

Scenarios:

- hold movement, then switch
- hold aim/fire/grab, then switch or disconnect
- switch while a modal is open
- switch during text entry
- switch inside a vehicle/build mode
- switch during loading or respawn

No action may remain logically pressed after its source disappears.

## 7. Gameplay action matrix

Create one row per semantic action:

| Context | Action | KBM | Touch | Gamepad | VR | Hold/release verified | Server validation |
|---|---|---:|---:|---:|---:|---:|---:|
| Gameplay | Interact | E | button | face button | grip/ray confirm | Yes | range/state |
| Gameplay | Fire | mouse | fire button | trigger | trigger | Yes | ammo/rate/hit |
| Menu | Cancel | Esc | back button | cancel | controller/back UI | Yes | Local |

For analog actions record:

- neutral value
- minimum useful value
- full-scale value
- diagonal magnitude
- deadzone and drift behavior
- response curve
- frame-rate dependence
- device-specific sensitivity

For button actions record:

- press
- hold
- release
- repeat
- double activation if used
- cancellation when context closes

## 8. UI task suite

Test tasks rather than individual buttons. Typical tasks:

- open and close every top-level screen
- select a tab
- scroll to an off-screen item
- open an item detail/context menu
- equip/use/buy/sell with confirmation
- change a setting and restore it
- rebind a control and resolve conflict
- enter/cancel/submit text
- navigate an empty list and a long/virtualized list
- dismiss notifications/dialogs
- recover after a selected item is removed
- complete onboarding/tutorial prompts
- access help/accessibility options

For each task verify:

- keyboard-only path
- pointer path
- touch path
- gamepad path without a virtual cursor unless deliberately designed
- VR path where the UI is available in VR
- visible focus/hover/pressed/disabled/error/loading states
- cancel/back behavior
- focus restoration
- safe-area and localization resilience

## 9. Screen and layout matrix

Test at least:

- compact phone landscape
- tall/narrow phone landscape
- tablet landscape
- common desktop aspect ratios
- ultrawide if supported
- large-display/TV preset
- VR headset emulation/physical optical view

Also test:

- orientation changes if the product supports them
- device safe insets and top-bar/Core UI insets
- maximum preferred text size supported by the design
- reduced transparency/high-contrast behavior where available
- reduced-motion setting
- pseudolocalization and elongated strings
- lower resolution/DPI and UI scale extremes

Watch for:

- controls under system gestures/notches
- clipped selected rings
- prompt overlap
- touch buttons covering movement/camera zones
- unreadably small TV text
- text truncation that hides action meaning
- modal content outside the usable viewport
- world-space VR UI at uncomfortable depth/scale

## 10. Touch-specific suite

Test real multi-touch combinations:

- movement + camera
- movement + primary action
- movement + camera + action when required
- hold/charge + movement
- pinch/rotate/pan gestures without stealing unrelated touches
- one touch leaving the screen or being cancelled
- rapid taps and accidental edge touches
- drag beginning on child UI and ending outside bounds
- phone call/notification/app focus interruption where feasible

Test target size, reach, hand occlusion, heat/battery, and touch latency on hardware. Studio mouse simulation does not reproduce fingers covering the screen.

## 11. Gamepad/TV-specific suite

Test:

- slight stick drift and noisy triggers
- stick held through context change
- rapid diagonal navigation
- long hold/repeat in lists
- irregular selection graphs
- disabled/hidden/destroyed selected objects
- scrolling and virtualized grids
- controller disconnect and alternate-input recovery
- multiple connected controllers
- haptic availability/off state
- all tasks from realistic couch distance
- platform keyboard overlays/text entry

Check that no prompt assumes the wrong controller family and every glyph has a textual/accessibility fallback.

## 12. Keyboard/mouse-specific suite

Test:

- layout-aware displayed key names
- modifier combinations and left/right variants where meaningful
- simultaneous key rollover for common movement/action combinations
- high and low mouse sensitivity
- high-polling-rate mouse for per-event allocation/performance problems
- pointer lock entering and leaving menus
- wheel/trackpad behavior
- focus loss, alt-tab, and mouse capture recovery
- TextBox/IME/composition input
- keyboard-only menu completion
- no required hover-only information

Do not bind essential actions only to a key unavailable on common compact or international layouts without rebinding.

## 13. VR-specific suite

Emulation checks logic; physical testing checks comfort and tracking. Test:

- seated and standing heights
- left/right dominant hand
- one controller missing/untracked
- recenter in every major state
- smooth/teleport locomotion
- snap/smooth turn settings
- small/large play spaces
- direct and ray interactions
- two-handed item release/tracking loss
- reach and limited-mobility alternatives
- world-space UI readability and target acquisition
- haptics and audio alternatives
- sustained headset frame-time/thermal behavior
- network latency for grab/use/teleport validation

Run a comfort review with more than the implementer when possible. Record duration and symptoms rather than saying “felt fine.”

## 14. Accessibility review

Accessibility is a set of usable alternatives, not one checkbox.

### Motor/input

Consider:

- full control rebinding where feasible
- hold/toggle alternatives for sprint, aim, crouch, grab
- reduced simultaneous-button/chord requirements
- configurable double-tap/hold timings
- larger touch targets
- lower precision alternatives, aim assist, snapping, or lock-on
- one-handed modes where product scope permits
- seated VR and reach alternatives
- controller sensitivity/deadzone settings

### Vision

Consider:

- sufficient contrast and non-color-only state
- scalable readable text
- clear focus indicator
- high-visibility reticle/interaction highlight options
- reduced transparency
- prompt text fallback for glyphs
- UI safe from clipping at larger text sizes

### Motion/vestibular

Consider:

- reduced camera shake
- reduced motion/tweening
- field-of-view and motion effects where appropriate
- VR snap turn, teleport, vignette/fade, seated mode
- avoiding forced camera/head movement

### Hearing

Consider:

- subtitles/captions
- visual or haptic alternatives for gameplay-critical audio
- directional indicators where spatial sound conveys essential information
- independent volume categories when feasible

### Cognitive

Consider:

- consistent confirm/cancel behavior
- plain action labels
- remappable/repeatable tutorials
- adjustable timing for QTEs or time-limited interactions
- clear error recovery
- avoiding unexplained gesture-only controls

### Photosensitivity and fatigue

- avoid rapid flashing and provide reduced-effects modes
- avoid excessive haptics
- limit repetitive high-force controller/VR gestures
- support pauses/breaks where the game mode permits

## 15. Security and network tests

For each input-triggered remote, test invalid requests:

- unknown action or item ID
- wrong type, missing field, oversized string/table
- NaN/infinite/out-of-range number
- spam above intended rate
- action while dead, stunned, in menu, or wrong context
- impossible target/destination/range
- item not owned/equipped
- cooldown/ammo/currency mismatch
- replayed request/duplicate transaction
- client-provided reward/damage/price

Under network simulation, test:

- delayed approval after local prediction
- duplicate/out-of-order transient updates
- disconnect during pending interaction
- stale UI state
- correction/reconciliation that does not trap controls

## 16. Performance checks

Measure by device family where possible:

- client frame time/FPS and spikes
- server frame time for input-triggered systems
- memory growth after repeated menu/open/respawn cycles
- event connection/task count lifecycle
- remote calls/sec and payload size
- touch/VR thermal and battery behavior
- UI rebuild frequency on `PreferredInput` changes
- per-frame allocations in camera, aim, cursor, hand, or focus systems

Do not fabricate improvements. Mark unmeasured metrics as unmeasured and explain the expected direction.

## 17. Defect severity

Suggested classification:

- **Critical** — exploit/security issue, crash, unrecoverable control loss, severe VR safety/comfort issue.
- **High** — required action or screen cannot be completed on a promised family; stuck input; hidden critical UI.
- **Medium** — degraded navigation, misleading prompt, poor safe-area/readability, configuration not respected.
- **Low** — polish issue with a usable alternative.

Do not call a family supported while a critical or high defect remains in its required path.

## 18. Test report format

Use a table like:

| ID | Family/configuration | Scenario | Evidence | Result | Issue/notes |
|---|---|---|---|---|---|
| GP-UI-01 | Generic controller emulator | Complete inventory flow | Studio-emulated | Pass | Explicit grid links |
| TO-MT-02 | Compact phone | Move + camera + fire | Physical-device | Fail | Fire overlaps camera zone |
| VR-CF-03 | Quest target | Snap turn + recenter | Physical-device | Not tested | Hardware unavailable |

Then summarize:

- release-ready families
- conditional/experimental families
- unsupported paths
- critical/high defects
- physical hardware tested
- remaining manual tests

## 19. Automation guidance

Automate stable, deterministic paths such as:

- action-map schema and binding coverage
- context state transitions
- prompt selection for `PreferredInput`
- focus graph reachability for known screens
- hidden/disabled selection cleanup
- server validator unit tests
- cooldown and duplicate-request behavior
- layout bounds/inset assertions for fixed test sizes

Do not pretend virtual input fully replaces human testing for analog feel, hand occlusion, couch readability, motion comfort, haptics, tracking, or physical reach.

## 20. Final checklist

- [ ] A named support matrix and explicit exclusions exist.
- [ ] Every action and UI task has per-family evidence.
- [ ] Hot-swap and disconnect are tested in real states.
- [ ] safe areas, aspect ratios, text size, localization, and reduced motion are covered.
- [ ] invalid remote requests and adverse network conditions are tested.
- [ ] physical touch/controller/TV/VR testing is distinguished from emulation.
- [ ] performance evidence does not invent numbers.
- [ ] critical/high defects block the support claim.
- [ ] accessibility alternatives are verified, not only present in settings.
- [ ] remaining manual checks and unavailable hardware are disclosed.
