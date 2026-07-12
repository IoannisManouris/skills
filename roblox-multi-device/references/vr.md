# VR Controls and Interaction

Read this reference when the experience supports VR headsets, tracked controllers/hands, world-space interaction, immersive locomotion, VR combat, wrist interfaces, recentering, or comfort settings.

VR is not desktop camera control with two extra tracked objects. Head pose belongs to the player, interaction occurs in three-dimensional reach space, and frame-time or camera mistakes can cause discomfort.

## 1. Detection and capability model

Use `VRService.VREnabled` for current VR state. Do not build new detection around deprecated `UserInputService.VREnabled`.

Track at least:

- whether VR is enabled
- which `UserCFrame` roles are enabled/tracked
- current controller or hand availability
- recenter/body-origin state
- seated/standing or user-selected locomotion preference
- the non-VR input capabilities that may coexist

VR state does not erase keyboard/gamepad capability. A player may use a gamepad for locomotion and tracked controllers for pointing. Bind semantic actions by role and make presentation follow the actual active path.

## 2. VRService responsibilities

Use `VRService` for VR-specific state and operations such as:

- `VREnabled`
- `GetUserCFrame()`
- `GetUserCFrameEnabled()`
- user CFrame enabled/changed events
- recentering through supported VR APIs
- navigation requests where appropriate
- controller models, laser-pointer, avatar gesture, and related VR presentation properties when the project deliberately configures them

Verify current API signatures and deprecation/security annotations before relying on a specific member.

### Tracked pose conversion

`GetUserCFrame()` returns tracked poses in VR tracking space. Convert through the current camera/world origin and account for head scale according to current Roblox guidance.

Keep pose conversion in one module. Do not duplicate subtly different world-pose calculations across weapons, hands, UI, and networking.

Conceptual flow:

```text
VRService tracked UserCFrame
            │
            ▼
VR origin / camera transform + head scale
            │
            ▼
world-space head/hand/controller pose
            │
            ├── local avatar/IK/presentation
            ├── ray/direct interaction candidates
            └── rate-limited cosmetic replication if required
```

Do not treat a temporary untracked pose as valid zero-space input. Check tracking availability and enter a recoverable state.

## 3. Headset camera rules

The headset orientation and position are controlled by the player and runtime. Never:

- overwrite the headset pose each frame as though it were a mouse camera
- smooth or delay real head rotation
- apply desktop recoil by rotating the entire camera
- force yaw snaps that are not initiated by the player
- attach large screen-space UI rigidly in front of the face
- use aggressive screen shake

Game camera systems may control the **world/body origin**, locomotion, vehicle frame, or cinematic environment, but must preserve the player's tracked head motion.

### Recoil and impact

Prefer:

- weapon/hand animation
- controller haptics
- world/object response
- audio
- restrained vignette or environmental effects when tested

Avoid manipulating the player's head transform.

### Recenter

Provide a clear recenter action and handle runtime recenter events. After recentering:

- update body/origin assumptions
- keep held objects stable or deliberately reconcile them
- reposition UI that is intended to follow the player's body or play-space origin
- avoid teleporting the avatar into invalid geometry

## 4. Locomotion architecture

Offer locomotion choices suitable for the experience. Common modes:

- smooth locomotion
- teleport locomotion
- snap turning
- smooth turning
- seated-friendly movement
- room-scale physical movement within the tracked play space

Do not force every player into the most intense option.

### Smooth locomotion

Define the movement frame explicitly:

- headset-forward movement is intuitive but can drift with looking
- controller/hand-forward movement preserves look independence
- body/avatar-forward movement can feel stable but requires body orientation logic

Expose a setting when the audience benefits. Movement should:

- preserve analog magnitude
- avoid sudden acceleration spikes
- stop cleanly on context changes or tracking loss
- respect collision and server-authoritative gameplay rules
- not translate the head independently from the avatar/world origin

### Teleport locomotion

A robust teleport system includes:

1. Begin aim on a semantic action.
2. Render an arc/ray and destination marker locally.
3. Validate slope, surface, clearance, bounds, cooldown, and game state.
4. Show invalid destinations distinctly.
5. Confirm on release or a dedicated action.
6. Optionally fade/vignette during relocation.
7. Request the semantic teleport from the server when position is authoritative.
8. Server revalidates and applies the approved destination.

Never let the client send “set my CFrame here” without validation.

### Snap turning

- expose angle options, commonly a small set of comfortable increments
- add a short repeat lockout so one stick deflection does not produce multiple accidental turns
- require the stick to return toward center before another snap when using edge-trigger behavior
- rotate the body/world origin around an appropriate pivot, not the tracked head pose in isolation

### Smooth turning

- expose speed and inversion/direction settings where appropriate
- integrate by time
- offer comfort vignette independently from movement vignette
- avoid acceleration curves that surprise the player

### Comfort vignette and fade

Use comfort effects as optional assistance:

- scale with locomotion/turn intensity rather than appearing randomly
- keep the center of vision clear
- do not hide critical hazards or UI
- expose strength or off setting
- avoid abrupt opacity changes

## 5. Body, hands, and controller presence

### Body orientation

Decide how avatar body yaw follows:

- headset yaw
- locomotion direction
- dominant controller/aim direction
- a blended rule

Avoid rapid body spinning when the player glances sideways. Keep body-follow logic separate from head tracking.

### Hand/controller models

Use the appropriate runtime/controller model behavior or project-owned hands. Ensure:

- models appear only when their tracking role is valid
- dominant-hand settings are respected
- hand scale matches the avatar/world
- collisions do not push the player unexpectedly
- visual hands do not become authoritative physics by accident
- controller model changes are handled without stale references

### Inverse kinematics

Tracked poses are local presentation inputs. For networked avatars:

- compress and throttle cosmetic pose data
- interpolate remote poses
- tolerate packet loss and out-of-order transient updates
- do not base damage, ownership, or rewards solely on unverified client poses
- keep critical interaction validation in server-understood world terms

## 6. Interaction model

Use a shared interaction state machine rather than separate one-off grab scripts:

```text
Idle
 ├── HoverCandidate
 ├── RayCandidate
 └── Held
      ├── PrimaryUse
      ├── SecondaryUse
      ├── TwoHanded
      └── Released / Cancelled
```

Each interactable should declare supported modes and constraints, such as direct grab, ray select, use, hold, two-hand attach, distance, ownership, and accessibility alternative.

### Direct interaction

For near-hand interactions:

- use an explicit proximity/overlap candidate system
- visibly highlight or subtly respond to the current candidate
- prioritize candidates deterministically
- require a semantic grab/use action
- maintain a stable hold transform
- release on input release, tracking loss, object invalidation, death, or context change

Do not attach every touched physics part automatically.

### Ray interaction

A controller ray is useful for UI and distant objects:

- show origin, direction, hit target, and maximum range clearly
- use stable target filtering and occlusion
- avoid ray jitter by smoothing only the pointer/target presentation, not the hand pose itself
- provide a confirm action and optional dwell accessibility mode
- make hit targets sufficiently large in angular size
- distinguish UI, gameplay, and teleport rays by state and visuals

### Grabbing physics objects

Choose the hold model deliberately:

- kinematic/constraint follow for stable held objects
- physics spring/constraint for weight and lag
- server-owned or validated state for competitive objects

Handle:

- network ownership changes
- collision groups while held
- maximum stretch/distance
- obstruction
- throw velocity estimation
- mass/weight feedback
- object deletion or streaming
- simultaneous grab contention

The client may animate immediately, but the server validates ownership, range, inventory rules, and authoritative outcomes.

### Throwing

Estimate release velocity from a short time window rather than one noisy sample. Clamp implausible linear/angular velocity and validate important throws server-side. Do not reward or damage from a client-reported throw result alone.

### Two-handed objects

For rifles, tools, bows, or large objects:

- identify primary and secondary attachment roles
- preserve the primary ownership/action hand
- calculate orientation from both tracked points without sudden flips
- define what happens when one hand releases or loses tracking
- support handedness changes where the mechanic allows it
- avoid forcing arms beyond reasonable reach

### Gestures

Use gestures only when:

- tracking reliability is sufficient
- false positives are safe
- an alternative action exists
- the gesture is culturally and physically accessible
- the detection window, threshold, and cancellation behavior are documented

Do not make an unannounced motion gesture the only way to perform a critical action.

## 7. Combat and aiming

### Weapons

For tracked weapons:

- derive local visual aim from the held model/controller pose
- display muzzle, sights, and reticle in world space
- stabilize only the weapon/reticle presentation when needed
- validate fire rate, ammo, origin bounds, direction, line of sight, and hit on the server
- keep recoil on the weapon/hands and haptics, not forced head motion

### Melee

Melee requires anti-exploit design. Server validation may consider:

- equipped weapon and attack state
- recent, plausible hand/weapon trajectory
- maximum reach from an authoritative body root
- target range and line of sight
- cooldown and repeated-hit suppression
- speed/energy clamps

Do not accept a single client message claiming a target and damage amount.

### Aim assistance

VR aim assistance should usually be subtler than gamepad assistance because the tracked device directly represents pointing. Consider larger interactable volumes, mild ray magnetism, forgiving grab candidates, or accessibility modes rather than silently rotating the hand aim.

## 8. VR UI

Prefer world-space or body-attached interfaces that are comfortable and context appropriate.

Common patterns:

- **world panel** for menus, shops, or terminals
- **wrist/hand panel** for compact status and quick actions
- **controller ray panel** for distant selection
- **diegetic object** for tools, maps, and inventory
- **gaze plus confirm** as an accessibility/fallback mode

### Placement

- keep panels at a comfortable distance and scale
- avoid attaching content rigidly to the head unless it is a small, brief status indicator
- place body-follow UI with damping that does not lag during selection
- prevent panels from spawning inside geometry
- keep important text readable at headset resolution
- account for seated reach and limited mobility

### Targets

VR target usability is angular, not merely pixel-based. Make controls easy to point at, leave spacing, and provide hover/selection feedback before activation.

### Text and keyboard

Minimize typing. Offer presets, voice-independent options, favorites, and recent values. When text entry is necessary:

- enter a dedicated text context
- suspend locomotion/weapon actions as appropriate
- preserve focus through platform keyboard overlays
- restore the previous panel and context afterward

### Focus and rays

Do not let two hands fight over one UI focus. Define:

- dominant pointer or last-intent pointer
- how the other hand becomes active
- visual ownership
- cancel/back behavior
- what happens when the active controller loses tracking

## 9. VR inventory and radial systems

### Inventory

Possible modes:

- wrist list/grid
- world panel
- physical slots/holsters
- backpack/quick-access volume
- radial menu

Every physical-slot design needs a seated/limited-reach alternative. Important inventory changes remain server-authoritative.

### Radial menu

A VR radial can use thumbstick direction, controller direction, or direct pointing. Provide:

- neutral/cancel center
- stable angular selection
- clear labels and icons
- release-to-confirm only when intentional
- a non-gesture fallback

## 10. Vehicles and moving frames

Vehicles increase discomfort risk. Define:

- cockpit/body frame and head freedom
- horizon policy
- acceleration/turn comfort options
- camera collision behavior
- entry/exit recentering
- seated controls and controller roles
- emergency exit/fallback input

Never lock the player's head to a vehicle camera orientation. Reduce forced roll and rapid acceleration where the genre allows.

## 11. Accessibility and comfort settings

Consider exposing:

- teleport versus smooth locomotion
- snap versus smooth turning
- snap angle and turn speed
- movement direction source
- vignette/fade strength
- dominant hand
- seated/standing mode
- height/recenter control
- hold versus toggle for grab/aim
- ray versus direct interaction preference
- haptic intensity/off
- subtitles and spatial-audio alternatives
- reduced motion/effects
- larger UI or longer dwell timing

Do not bury comfort options behind an interaction that itself causes discomfort.

## 12. Performance

VR needs stable frame time and low latency. Prioritize:

- reducing expensive per-frame scripts
- limiting transparent layered world UI
- pooling only where lifecycle is safe and profiling supports it
- controlling dynamic lights, particles, beams, trails, and post effects
- reducing physics assemblies/constraints and collision complexity
- avoiding full-world scans for hand candidates
- spatially querying only nearby interactables
- throttling cosmetic network pose streams
- using level-of-detail and streaming carefully
- testing on headset-class standalone hardware, not only a development PC

A high average frame rate with frequent spikes can still be uncomfortable. Profile frame-time consistency.

## 13. Network contract

Recommended semantic messages include:

```text
RequestTeleport(destinationDescriptor)
RequestGrab(interactableId, handRole)
ReleaseGrab(interactableId, releaseDescriptor)
UseHeldItem(itemId, useMode, aimDescriptor)
Interact(interactableId, interactionKind)
```

Server validation should derive or check:

- player state and permissions
- authoritative body position
- maximum reach/range
- line of sight and obstruction
- ownership/contention
- cooldown and item state
- destination clearance
- plausible pose/velocity bounds

Raw headset or hand poses, when replicated for remote-avatar presentation, are transient cosmetic streams. Keep them compact, rate-limited, and independent from authoritative results.

## 14. Tracking loss and lifecycle

Handle:

- one controller becoming untracked
- both controllers disconnecting
- headset recenter
- leaving and re-entering VR state when supported
- character respawn/death
- held object deletion or streaming out
- menu opened during a grab
- teleport interrupted by state change
- dominant-hand setting change
- player leaving while owning a physics interaction

On tracking loss, cancel or safely freeze actions; never continue firing, grabbing, or moving from stale state.

## 15. Testing

Use Studio VR emulation to verify flows without hardware. Current Studio testing supports Quest 2/Quest 3 emulation with headset/controller switching. Also test physical hardware:

- compatible OpenXR headsets through Studio on supported desktop systems
- standalone Roblox Quest app for target-device performance and behavior
- all intended controller families and handedness settings available to the team

Test:

- standing and seated height
- small and large play spaces
- one-hand mode or controller loss
- recenter during menus, locomotion, grab, and vehicle use
- smooth/teleport and snap/smooth settings
- left/right dominant hand
- reach limits and accessibility alternatives
- UI readability, ray accuracy, and text entry
- network latency on grab/use/teleport validation
- long sessions for comfort and fatigue
- headset thermal/performance behavior

Emulation does not validate motion comfort, real tracking, reach, controller ergonomics, haptics, optical readability, or standalone performance.

## 16. Anti-patterns

Reject or repair:

- checking deprecated `UserInputService.VREnabled`
- treating the headset as a mouse camera
- smoothing/delaying the actual head pose
- forced head recoil, shake, or rotation
- client-authoritative teleport, melee, grab, or damage
- streaming raw poses every render frame without need or limits
- required physical reaches with no seated alternative
- tiny screen-space UI locked to the face
- two controller rays controlling focus simultaneously without ownership
- no behavior for tracking loss or recentering
- declaring VR support after emulator-only testing
- applying desktop aim-assist rotation directly to tracked hands

## 17. Completion checklist

- [ ] VR is detected through `VRService` and tracking roles are checked.
- [ ] Head pose is never overridden or delayed by desktop camera logic.
- [ ] Body/world-origin, recenter, and pose conversion are centralized.
- [ ] Locomotion and turn modes include suitable comfort alternatives.
- [ ] Teleport and authoritative movement are server-validated.
- [ ] Grab, use, throw, melee, and two-hand states clean up on every lifecycle path.
- [ ] UI is world/body/wrist placed comfortably with accessible target sizes.
- [ ] Dominant hand, seated play, tracking loss, and controller disconnect are covered.
- [ ] Haptics and motion effects have fallbacks/settings.
- [ ] Pose networking is cosmetic, compact, throttled, and not authoritative.
- [ ] Frame-time consistency is profiled on target headset hardware.
- [ ] Studio emulation and physical headset results are both in the final report.
