# Blender MCP authoring and transfer

Use this route when Blender is requested or provides a practical advantage for
poses, contact constraints, curves, mechanical props or repeated refinement.
It does not require computer use or Roblox Animation Editor authoring.

## Connect and preserve the working scene

Discover the available Blender MCP tools and read their schemas. Check addon
status, Blender version and current scene before writing. Tool names vary:
some implementations expose scene inspection, Python execution and viewport/frame
previews. Use the installed version's API rather than assuming an older Actions
or F-curves layout.

Use the user's live Blender through MCP. If launching it is needed and authorized,
find the actual executable and open the intended file by command; do not depend on
desktop clicking. Save a copy before replacing scene content. Keep scripts and
exports in the task workspace so work can resume from a saved `.blend`.

Do not install competing listeners or enable unrelated paid generators. A missing
MCP does not justify claiming that a headless mock or screenshot is the live app.

## Transfer the actual Roblox rig

Through Studio MCP, export the data needed to reconstruct the target:

- Part/bone names, hierarchy, rest transforms, dimensions and scale.
- Motor6D C0/C1 or AnimationConstraint attachment frames, as actually used.
- Mesh/skinning information when available, and relevant accessories/props.
- Existing clips or boundary poses that the new performance must join.
- Prop grip, stow and contact frames, plus mechanical joints such as a wheel.

Do not replace the target with an arbitrary generic skeleton. Preserve rest
attachments; animate relative transforms instead of changing rig offsets to force
a pose. Preserve reference geometry when prop contact depends on body proportions.

Define units and axis conversion once and apply them consistently to geometry,
rest transforms, animation and props. For example, a project may map Roblox
`(x,y,z)` to Blender `(x,-z,y)` with one Blender unit per stud; this is a chosen
convention, not an instruction to apply a second conversion to an FBX importer.

If mesh access is restricted, use explicitly documented, dimension-matched preview
proxies. A proxy can support blocking; verify the final motion with actual Roblox
geometry before claiming collision/contact quality.

## Author and review

Use Blender MCP to build the armature/actions, pose and keyframe joints, solve
contacts, and refine interpolation. Keep fixed grips attached to the relevant hand
or prop frame; track pickup/stow events separately from the prop's world path.

Inspect evaluated frames, not just keyed control values. Check elbow-plane flips,
hand sliding, intersections, planted feet, root drift, loop seams and joins between
clips. Review normal-speed playback or a rendered preview with props from useful
angles. Numerical contact/continuity checks supplement visual motion review.

Save the editable `.blend`, exact action/revision, frame rate, duration, looping,
markers and export script/settings. Record any proxy limitations. Follow the
user's review policy; if reviewer-agent review is authorized, give that reviewer
the actual motion and relevant contact evidence, then resolve findings.

## Choose and validate the transfer

Two useful routes:

- **FBX or another supported animation importer:** export using current Roblox
  requirements and the installed Blender version, with animation data included.
  Check axis/scale settings, baked constraints, hierarchy and unwanted extra bones.
  Use MCP/import APIs if supported; invoke the editor UI only for a step that
  actually requires it.
- **Explicit pose export:** sample the evaluated Blender rig, convert into the
  target's joint-local animation space, and construct a Roblox KeyframeSequence
  or supported clip through Studio MCP. Save a portable source such as `.rbxmx`
  plus a pose/marker manifest. This is appropriate for inspected rigid-part rigs;
  do not assume the same transform derivation fits every bone or constraint rig.

For either route, check:

1. Names and hierarchy, including intermediate/root poses, match the Animator rig.
2. Rest space, handedness, rotations and units round-trip correctly. Compare
   reconstructed part/bone transforms to evaluated Blender frames at contacts,
   transitions and representative in-between times, using a stated tolerance.
3. IK/constraints/drivers are baked or otherwise exported as intended. A viewport
   solution that is absent from the exported data will not survive import.
4. Duration, loop flag, priority and named markers survive import. Prefer named
   enum values; Roblox's numeric priority values are not their ordering.
5. Prop attachment transforms and attachment-switch times accompany the clip.
   Do not silently change the held/stowed offset after reviewing its contacts.

Import into a separate local save without overwriting other work. Preview it on the
actual target rig in Studio, then follow [publication](publication.md). Confirm the
published asset's playback, markers and contact again; export validation alone
does not prove upload success or runtime compatibility.

Keep reusable export code with the project that owns its rig assumptions. Do not
copy a prior game's IDs, poses, offsets, owner, machine paths or numerical
tolerances into an unrelated cutscene.
