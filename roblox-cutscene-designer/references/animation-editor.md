# Animation Editor authoring

Use when native Studio editing is requested or well suited to the work, such as
revising an existing editor clip or making a straightforward native animation.
This is an optional route; Blender MCP authoring is covered in
[blender-workflow.md](blender-workflow.md).

For UI-dependent steps, use the native surface documented by the installed
computer-use skill. Inspect the actual Studio window and controls; menu labels
vary. A browser or viewport screenshot alone does not establish native UI control.
Preserve docking and window placement.

## Prepare and animate

1. Confirm Studio, place, rig and clip ID. Preserve existing work and use a
   separate local save when revising someone else's clip.
2. Open Animation Editor through the observed Avatar toolbar or Window menu.
   Select the rig, inspect its joints/bones and Animator, and match its hierarchy;
   do not assume R6 and R15 interchange.
3. Set a clear clip name and duration. Check timeline units/frame rate. Key the
   initial pose, anticipation, contact/action, follow-through and final pose.
4. Refine arcs, balance, planted contacts, hand/prop alignment and easing. Check
   the visual result after curve conversion or optimization.
5. Set looping and priority deliberately. Match pose and motion across loop
   boundaries, and join nonloop entry/exit poses to neighboring clips.
6. Add case-sensitive event markers and record their times/parameters for runtime.
7. Save an editable local revision. Local saves preserve work; they are not cloud
   asset IDs. Persist the project using its established local-save workflow.
8. Review normal-speed and slow playback with props from useful angles. Correct
   sliding, intersections, awkward holds and abrupt transitions.

Joint animation and physical world travel are separate concerns. Verify root
behavior on the actual rig rather than assuming editor movement drives gameplay.

Apply the review/publication policy in [publication.md](publication.md). Use a
supported MCP/API publishing route if available, or the observed native dialog
when needed; choosing Animation Editor for authoring does not force UI publishing.

If native control is unavailable, preserve the local work. Continue with a suitable
MCP/Blender route when allowed by the user; do not silently disregard an explicit
"Animation Editor only" requirement.
