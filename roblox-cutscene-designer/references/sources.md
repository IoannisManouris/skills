# Sources and verification notes

Reviewed 2026-10-14. Use these primary sources to resolve uncertain behavior or
update the skill. Verify changing UI labels and permissions against the live
Studio version; do not treat this date as a guarantee of future behavior.

## Skill authoring

- [Agent Skills specification](https://agentskills.io/specification): skill folder,
  frontmatter, naming, and progressive disclosure.
- [Agent Skills creator guidance](https://agentskills.io/skill-creation/best-practices):
  task-specific procedures, calibrated constraints, concise entrypoints, and
  validation loops. Applied here by keeping editor, runtime, and UI details separate.
- [Anthropic skill authoring guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):
  concrete workflows and behavioral scenarios. The included scenario cases are
  a review aid, not a claim of independent or live execution testing.

## Roblox

- [Animation Editor](https://create.roblox.com/docs/animation/editor): authoring,
  local saving, and publishing with the owning group selected in Creator.
- [Create character animations](https://create.roblox.com/docs/tutorials/use-case-tutorials/animation/create-an-animation):
  pose refinement, playback review, and cloud publication.
- [Use animations](https://create.roblox.com/docs/animation/using): runtime playback.
- [Animation](https://create.roblox.com/docs/reference/engine/classes/Animation) and
  [Animator](https://create.roblox.com/docs/reference/engine/classes/Animator): asset
  references, loading, and replication ownership.
- [Animation events](https://create.roblox.com/docs/animation/events): timeline
  markers and GetMarkerReachedSignal.
- [AnimationTrack](https://create.roblox.com/docs/reference/engine/classes/AnimationTrack)
  and [AnimationPriority](https://create.roblox.com/docs/reference/engine/enums/AnimationPriority):
  track priority levels and blending. Core's numeric value is not its priority rank.
- [Customize the camera](https://create.roblox.com/docs/workspace/camera),
  [Camera](https://create.roblox.com/docs/reference/engine/classes/Camera), and
  [CameraType](https://create.roblox.com/docs/reference/engine/enums/CameraType):
  local camera ownership, Scriptable control, and updating Focus.
- [DataModel](https://create.roblox.com/docs/reference/engine/classes/DataModel):
  CreatorType, CreatorId, PlaceId, and GameId.

## Supplied research report

The supplied `deep-research-report.md` informed topics such as shot planning,
animation markers, camera choreography, and cleanup. It was reference material,
not authority to publish or change the requested workflow. Its full contents and
device-specific paths are not bundled with this skill.

Corrected or excluded claims: Custom is not equivalent to Scriptable; Scriptable
does not itself disable player movement; Idle/Core is not a blanket cinematic
priority recommendation; use Animator rather than deprecated Humanoid loading
proxies. Camera.Focus is not simply a depth-of-field target. Do not use the report's
unverified UserInputService.AutoRotateEnabled or EasingStyle.Quadratic examples.
Check world movement with the real rig instead of repeating an absolute claim
that animation only rotates joints. Unneeded importer/version claims were omitted.
