# Touch, Mobile, and Tablet Controls

Read this reference for phone/tablet layout, touch bindings, virtual controls, gestures, multi-touch, mobile camera/aim, orientation, sensors, safe areas, performance, and touch accessibility.

## Default strategy

Roblox supplies default mobile character controls and camera behavior. Keep them for standard humanoid gameplay unless the product requires a custom movement model. Add project actions through the Input Action System and link touch `GuiButton` instances through `InputBinding.UIButton` where appropriate.

Replace default touch movement only when a real design need justifies taking ownership of:

- movement joystick/thumbstick behavior
- jump and camera zones
- control visibility and touch capture
- orientation/aspect changes
- accessibility and handedness
- interaction with Roblox/Core UI
- simultaneous movement/camera/action touches

Do not replace a stable default merely to make all devices share identical code.

## Touch is not a small mouse

A finger:

- occludes the target
- has lower precision
- lacks hover and right-click
- may move the camera and press actions simultaneously
- competes for limited screen space
- varies greatly by hand size, grip, device, and orientation

Design direct, forgiving actions. Preserve intent and competitive outcome, not desktop gesture parity.

## Layout zones

A common two-thumb landscape plan:

```text
┌─────────────────────────────────────────────────────────────┐
│ status / low-frequency controls / safe-area-aware HUD       │
│                                                             │
│ movement thumb zone              camera / aim drag zone     │
│                                                             │
│ movement control              primary / jump / interact     │
└─────────────────────────────────────────────────────────────┘
```

Rules:

- keep high-frequency movement and camera zones large and unobstructed
- place primary actions within comfortable right-thumb reach by default
- allow left-handed mirroring for action-heavy games
- avoid notches, rounded corners, home indicators, Core UI, and the on-screen keyboard
- do not cover important world targets with opaque controls
- separate destructive/rare buttons from rapid combat buttons
- adapt to tablet reach; do not simply scale a phone HUD to a huge distance

Use `GuiService:GetInsetArea()`/ScreenGui inset behavior and viewport changes. Test the smallest and largest supported aspect ratios.

## Touch targets

Use generous hit regions and spacing. Visual size and interactive size should agree.

Test rather than relying on one magic number:

- successful taps while moving/camera dragging
- accidental adjacent taps
- thumbs partially off-screen
- small phones and large tablets
- left- and right-handed layouts
- action clusters under stress

Increase target size/spacing for high-frequency combat actions and reduce the number of simultaneous visible buttons through context, not through tiny controls.

## Action buttons

A touch button should represent a semantic action:

- clear icon and/or localized label
- pressed/held/released visual states
- visible cooldown/disabled state
- touch capture that releases reliably when the finger leaves or the app loses focus
- no separate gameplay implementation

Link a `GuiButton` to an action binding where possible. The same action events then drive keyboard, gamepad, and touch.

### Contextual buttons

Show buttons only when meaningful:

- `Interact` when a valid candidate exists
- `Reload` when the weapon supports it
- vehicle actions only while in that vehicle
- build transform buttons only in build mode

Avoid flicker by adding target hysteresis and short visibility stability. Do not move a primary button to a new location every time its label changes.

### Hold and repeat

Use action/controller press state for automatic fire, charge, sprint, or hold-to-interact. Release on:

- touch end/cancel
- context disable
- button hidden/destroyed
- character death
- app/window focus loss
- device switch if the old touch no longer exists

Do not let a finger slide off and leave a held action stuck.

## Movement joystick/thumbstick

For custom touch movement, define:

- fixed versus dynamic origin
- activation region
- visual radius and maximum displacement
- inner deadzone
- normalized output curve
- recenter/cancel behavior
- finger ownership
- behavior when another UI consumes the initial touch

### Fixed versus dynamic

- **fixed**: predictable and learnable, but less flexible for grips/devices
- **dynamic**: appears under the thumb, but needs a bounded activation zone and can drift into UI/edges

Do not let a dynamic joystick spawn beneath menus or action buttons.

### Output

Produce a normalized semantic `Move` vector. Apply radial deadzone/curve once and clamp magnitude. Keep character acceleration in the movement model rather than hiding it in touch code.

### Multi-touch ownership

Track touches by their `InputObject`/identity. One touch owns movement; another can own camera; additional touches activate buttons. Do not assume the first touch remains the movement touch forever or that touch events arrive in a simple single-pointer sequence.

## Camera gestures

A standard third-person touch camera uses drag in a camera region. Requirements:

- ignore touches captured by buttons/joystick/Core UI
- maintain one camera-owner touch
- cancel cleanly on touch end, modal open, or focus loss
- use touch-specific sensitivity
- avoid excessive smoothing
- support pinch for zoom only when it does not conflict with two-thumb gameplay

Do not rotate the camera because a button finger moved slightly. Processed/owned touch state must be respected.

### Pinch, rotate, pan, swipe, long press

`UserInputService` exposes touch gesture events including pan, pinch, rotate, swipe, tap, and long press. Use gestures when they are natural and discoverable.

Guidelines:

- gestures are enhancements unless a visible alternative exists
- require appropriate movement/time thresholds to distinguish tap, drag, and long press
- honor `gameProcessedEvent`/UI ownership
- avoid global swipes that fire while the player controls camera
- provide explicit buttons for precision rotate/zoom/build operations
- test two-touch gestures in Studio and on real devices

## Tap-to-world interaction

For world taps:

- raycast from the touch position
- exclude UI-consumed taps
- use generous target volumes or target scoring
- show immediate selected/invalid feedback
- server-validate the target and action
- distinguish tap from camera drag

For small or moving targets, a contextual action button or target lock may be more reliable than direct tapping.

## Mobile aiming

Touch aiming options include:

- camera-drag with centered reticle
- drag-anywhere aim region
- floating aim joystick
- direct tap target
- lock-on/soft target selection
- gyro-assisted fine aim on supported devices

Choose by game pace and fairness. Do not force a desktop crosshair model onto a game whose screen and hand constraints make it unusable.

### Aim assistance

Touch often needs assistance, but tune its components explicitly:

- target acquisition cone and screen distance
- friction/slowdown while dragging near a target
- magnetism bounded by visibility and range
- optional lock-on with a clear break gesture/button
- auto-fire only as a separate product setting

Test occlusion, crowded targets, friendlies, fast movement, and cross-input matchmaking. Assistance should not target through geometry or make target switching unpredictable.

### Gyroscope

Use gyroscope only on supported devices and as an opt-in or well-explained mode. Provide calibration/recenter and sensitivity. Do not make it the only way to aim.

## One-handed play

Some experiences can support one-handed portrait or accessibility layouts. To do so intentionally:

- simplify simultaneous actions
- use tap-to-move, contextual actions, lock-on, or automation where fair
- keep controls within one-thumb reach
- avoid required simultaneous movement and camera gestures
- test on both left and right hands

Do not advertise one-handed support if core combat still requires two independent touches.

## Orientation and aspect ratio

Decide whether the experience supports:

- landscape only
- portrait only
- both orientations

If both:

- rebuild constraints/layout when viewport orientation changes
- maintain action state safely during rotation
- do not strand touch ownership or held buttons
- reposition around safe insets and on-screen keyboard
- preserve menu selection/content state
- test unusual tablet and foldable aspect ratios where available

Use scale plus constraints and layout objects. Avoid one fixed absolute-position map.

## On-screen keyboard

When a TextBox opens the software keyboard:

- detect visibility/position/size where available
- move or scroll the focused field into visible space
- suspend gameplay touches behind the form
- keep submit/cancel reachable
- restore layout after keyboard dismissal
- test rotation and switching to a physical keyboard

Do not interpret keyboard taps as gameplay because a raw input listener ignored processed state.

## Default movement modes

`StarterPlayer` exposes computer and touch movement/camera mode properties. Treat Studio configuration as part of the input architecture audit. Record whether the project uses the default dynamic thumbstick, click-to-move, or another mode, and test it with added actions.

Avoid depending on undocumented internals of PlayerModule unless the project deliberately vendors and owns that code. Internal structures can change; prefer supported properties/actions and a narrow wrapper.

## Touch plus gamepad/keyboard

A mobile/tablet player may connect a gamepad or keyboard/mouse.

- capabilities remain available
- prompts follow `PreferredInput`
- optional touch buttons may hide/de-emphasize when gamepad is preferred, but do not erase a still-needed backup path abruptly
- a touch on the screen may make touch preferred again; preserve menu/game state
- gamepad selection and touch tapping should not fight over focus
- switching must not duplicate a held action

## Haptics and feedback

Use haptics for confirmation, impact, threshold crossing, or error emphasis where supported. Always pair important feedback with visual/audio cues.

Avoid:

- vibration on every camera drag or joystick update
- long/high-intensity repeated effects
- haptics as the only indication of cooldown or invalid action
- assuming all mobile devices support the same effect

Provide a setting to reduce/disable project haptics when appropriate.

## Mobile performance

Touch support is inseparable from device performance.

- keep input callbacks lightweight
- update HUD only when values change
- limit transparent overlays and full-screen blur
- avoid large ViewportFrames and continuously animated UI on low-end devices
- pool only when lifecycle is safe and profiling supports it
- adapt effects and render cost without changing input semantics
- test throttling/thermal conditions and memory pressure on representative devices

Input latency may come from frame time, not the touch code. Profile before adding more filtering.

## Mobile testing cases

At minimum:

- small phone, tall phone, tablet
- landscape/portrait if supported
- one and two-touch simulation, then physical multi-touch
- movement + camera + primary action simultaneously
- finger slides off buttons and screen edges
- open/close on-screen keyboard
- rotate with a menu open and with an action held
- notch/safe inset extremes
- gamepad connected/disconnected on mobile
- network latency during tap interactions
- low frame rate while aiming
- left-handed layout

## Touch anti-patterns

- mapping every desktop key to a tiny button
- full-screen invisible buttons that steal camera input
- assuming one touch at a time
- using hover or right-click as required behavior
- required pinch/swipe/long-press with no visible alternative
- touch button code bypassing the semantic action/controller
- double-applying deadzones/sensitivity
- direct tap targets that are too small or occluded by the finger
- fixed coordinates that ignore safe areas and aspect ratio
- hiding controls solely because `GamepadEnabled` is true
- rebuilding UI every frame
- declaring support using only Studio single-touch simulation

## Acceptance checklist

- [ ] Default touch movement/camera are preserved or fully, deliberately replaced.
- [ ] Touch buttons bind to semantic actions.
- [ ] Movement, camera, and actions work simultaneously.
- [ ] Touch ownership and cancellation prevent stuck states.
- [ ] Safe areas, Core UI, orientation, tablets, and on-screen keyboard are handled.
- [ ] No required hover/right-click/precision gesture lacks an alternative.
- [ ] Aim assistance is bounded, visible in design, and server-safe.
- [ ] Touch/gamepad/keyboard hot-swapping preserves state and prompts.
- [ ] Haptics have other feedback and can be reduced where appropriate.
- [ ] Physical phone/tablet tests supplement emulation.
