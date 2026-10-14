# Runtime integration and verification

Read after the required clips have completed review and publication. Adapt these
constraints to the game's existing cutscene architecture rather than installing a
second framework or hardcoding a new folder layout.

## Separate ownership of presentation and gameplay

- Drive each player's camera, HUD, and optional dialogue from the client. Obtain
  `workspace.CurrentCamera` in client code and use `Enum.CameraType.Scriptable`
  during direct camera control. `Custom` does not disable the default camera.
- Snapshot the prior camera type, subject, CFrame, Focus, FOV, and any input/HUD
  state you change. Cooperate with existing camera/control ownership mechanisms.
- Load animation tracks through `Animator:LoadAnimation()`. For replicated motion,
  the Animator must originate on the server. Player-character animations can
  replicate from that player's client; shared NPC animations must be loaded and
  started on the server. Use local actor clones for a private scene when that fits
  the design, instead of moving a shared NPC differently for every viewer.
- Gameplay consequences remain server-authoritative. Validate cutscene triggers
  and completion/skip requests against the player's actual state. A local animation
  marker or client "finished" message is not proof that a reward was earned.
- For synchronized playback, use a shared server start time and elapsed-time
  scheduling, accounting for clients that load late. Sending a RemoteEvent to
  everyone does not guarantee simultaneous arrival. Avoid synchronizing scenes
  that are intended to be private to one player.

## Coordinate camera, motion, and cues

Represent the scene as a timeline or the project's existing sequence abstraction:
shot duration, camera transform/path, actor/world path, verified animation ID,
markers, and requested audio/VFX/UI cues. Express positions relative to stable
scene anchors when reuse matters. Keep spatial continuity between clips and shots.

Use TweenService for simple camera moves, or the project's render-step camera
update for paths and tracking. Compute progress from elapsed time with clamped
interpolation. Do not use fixed per-frame increments. Update Camera.Focus along
with the Scriptable camera. Avoid two independent systems writing the camera.
Verify framing at the intended aspect ratios, and prevent paths through geometry.

Use `AnimationTrack:GetMarkerReachedSignal("MarkerName")` for animation contacts
and effects, connecting before `Play()`. Disconnect callbacks during cleanup.
Missing markers, interrupted tracks, and failed asset loads must not trap the
sequence in an infinite wait. Use bounded waits and cancellation-aware scheduling.
Check completion/cancellation state before firing gameplay effects or delayed cues.

Set track priority intentionally. From highest to lowest the order is Action4,
Action3, Action2, Action, Movement, Idle, Core; numeric enum values do not express
this ordering. Start with Action for full-body cinematic performances when it
fits the game, and use a higher Action level only for a demonstrated conflict.
Stop/fade tracks owned by the scene without indiscriminately stopping other systems.

Coordinate physical travel through the game's movement authority or a deliberate
staged-actor mechanism. Match foot contacts and prop attachments to the world path.
Neither a Scriptable camera nor a pose animation by itself locks player movement.
Use the existing input/control system; do not default to ragdolling the character
with PlatformStand or permanently anchoring a live player.

Preload the required published animation/sound assets before taking control where
practical. Surface load failures; avoid indefinite waits for an AnimationTrack
length that is still zero. Handle streamed-out actors and scene locations using
the project's streaming/readiness conventions and a timeout. Never confuse an
editor preview with runtime asset availability.

## One cleanup path for every exit

Use the same idempotent cleanup for completion, skip, failure, respawn/death,
cancellation, or scene replacement. Track the resources and state this playback
owns; guard delayed work with a playback token or equivalent. On cleanup:

1. Cancel tweens, timers/tasks, render bindings, and event connections owned by this
   playback; stop its animation tracks and temporary sounds/effects.
2. Release temporary actors, props, UI, and input locks. Restore saved HUD visibility
   and control state rather than enabling everything blindly.
3. Restore camera ownership and saved state. If the old subject was destroyed on
   respawn, bind to the new character or the game's camera controller. Do not let
   an older scene's cleanup overwrite a newer scene that now owns the camera.
4. Restore temporary character/physics settings, and apply only the intended final
   gameplay position/state. Clear busy flags so a supported replay works.

## Verify in the actual game

Use focused Studio playtests and output logs. Confirm:

- Normal completion: correct published clips, readable composition, intended
  timing, no errors, and a clean return to gameplay.
- Replay/retrigger: no doubled markers, accumulated connections, or stuck locks.
- Skip/cancel/death mid-shot: no later cue fires and camera/input/HUD recover.
- Missing or restricted asset/actor: bounded failure and recovery, not a hang.
- Shared scene, when applicable: two clients observe the intended actors/timing;
  a private scene does not unexpectedly move other players' shared world.
- Requested dialogue UI: readable on the target devices with correct progression
  and cleanup. Without a text request, no dialogue text/UI was introduced.

If a playtest is unavailable, report the unverified cases. Do not claim code
inspection establishes that published assets play or that cleanup works in Studio.
