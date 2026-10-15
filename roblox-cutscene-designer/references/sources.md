# Sources and verification notes

Updated 2026-10-15. Use these primary sources to resolve uncertain behavior or
update the skill. Verify changing UI labels and permissions against the live
Studio version; do not treat this date as a guarantee of future behavior.

## Skill authoring

- [Agent Skills specification](https://agentskills.io/specification): skill folder,
  frontmatter, naming, and progressive disclosure.
- [Agent Skills creator guidance](https://agentskills.io/skill-creation/best-practices):
  task-specific procedures, calibrated constraints, concise entrypoints, and
  validation loops. Applied here by separating conditional authoring routes,
  publication, runtime integration and UI details.
- [Anthropic skill authoring guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices):
  concrete workflows and behavioral scenarios. The included scenario cases are
  a review aid, not a claim of independent or live execution testing.

## Roblox

- [Animation Editor](https://create.roblox.com/docs/animation/editor): authoring,
  local saving, and publishing with the owning group selected in Creator.
- [3D Importer](https://create.roblox.com/docs/studio/importer) and
  [export requirements](https://create.roblox.com/docs/art/modeling/export-requirements):
  supported external rig/animation workflows and Blender export settings. Verify
  the actual rig and installed version rather than assuming a universal preset.
- [Sharing animations](https://create.roblox.com/docs/education/build-it-play-it-island-of-move/sharing-animations):
  portable local animation files; exporting/importing a source file is distinct
  from cloud publication.
- [AssetService](https://create.roblox.com/docs/reference/engine/classes/AssetService)
  and [AssetCreatorType](https://create.roblox.com/docs/reference/engine/enums/AssetCreatorType):
  asset creation/version operations, creator parameters and returned result codes.
  Availability depends on the supported asset type and execution permissions;
  these APIs do not imply that every MCP or ordinary game script can publish clips.
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

## Blender MCP

- [Blender MCP upstream project](https://github.com/ahujasid/mcp-for-blender) and
  [server implementation](https://github.com/ahujasid/mcp-for-blender/blob/main/src/blender_mcp/server.py):
  one community implementation of live Blender scene inspection, Python execution
  and visual previews. It is an example, not a required package or an official
  Blender API. Discover the installed tool schemas and Blender version before use.

The Blender transfer guidance also incorporates this workflow's observed use of
an exported Roblox rig, MCP-driven posing, evaluated-frame export, target-rig
comparison, reviewer feedback and published playback checks. Those observations
do not guarantee support for other rigs, MCP versions or publication contexts.

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
that animation only rotates joints. Verify importer/API support in the current
environment rather than treating a prior project's successful route as universal.
