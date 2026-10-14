# Animation Editor and publishing

Read when creating, revising, reviewing, or publishing a clip. Menu labels vary
across Studio versions: inspect the live UI instead of replaying fixed coordinates.

## Prepare and animate

Use the native computer-use surface documented by the installed computer-use
skill. Discover actual windows, capture the current state, act on an observed
control, then verify the result. Roblox MCP inspection and a render screenshot
alone cannot operate the editor's native upload dialog.

1. Confirm the target Studio, place, rig, and clip ID. Preserve any existing work;
   use a separate local save when revising someone else's animation.
2. Open Animation Editor from the observed Avatar toolbar or Window > Avatar menu.
   Select the correct rig. Check its joints/bones and Humanoid or AnimationController
   with Animator. Match rig type and hierarchy; do not assume R6 and R15 interchange.
3. Name the clip clearly and set its duration. Check the displayed timeline units
   and frame rate before entering times. Block the initial pose, anticipation,
   action/contact, follow-through, and final pose by moving/rotating the rig's
   joints in the editor. Key the required joints, including a deliberate start pose.
4. Refine timing, arcs, balance, planted contacts, hand/prop alignment, and easing.
   Use the curve editor when it improves the motion. Recheck the visual result
   after converting or optimizing curves. Do not add keys merely to increase count.
5. Set looping deliberately. Match both pose and motion across a loop boundary;
   align entry/exit poses for nonloops. Choose animation priority to override the
   intended tracks without needlessly suppressing all animation layers.
6. Add named event markers for exact contacts or cues. Record their case-sensitive
   names and parameters in the plan, so runtime code can subscribe before playback.
7. Save locally through the editor and record where it can be reopened. Local
   animation saves preserve authoring work; they are not cloud asset IDs. Ensure
   project work is persisted using the project's established local-save workflow.
8. Preview at normal speed and slow speed from useful angles. Correct foot sliding,
   mesh intersections, awkward holds, abrupt easing, and mismatched final poses.
   Preview with relevant props and blocking, not only in an empty space.

Joint animation and an actor's physical world movement are different concerns.
Plan the world path separately and verify root behavior with the actual rig and
current engine features. Do not assume visible root movement in the editor will
move the gameplay character as required, or claim animations can only rotate joints.

## Present one concrete approval item

Provide the user an actual playable preview of the saved revision. Include:

- Clip ID, name, revision, rig, action, and duration/loop status.
- Where to play it, or an actual preview recording when capture is supported.
- The verified publisher type, name, and ID, and whether this creates a new asset
  or updates a specifically identified existing asset.
- One question asking for changes or approval to publish that exact clip.

Record the user's response and the previewed revision. A request such as
"slow down the turn" means revise and show it again. No response means waiting.
An affirmative response to this specific publication question can authorize the
upload; do not demand ritual wording or a second redundant confirmation.

## Publish the approved clip through computer use

Before submitting, verify all four match: **clip revision, destination owner,
create/update operation, and user approval**.

1. Reopen the approved local clip if necessary and confirm the current editor
   selection. Use the editor's observed menu to choose **Publish to Roblox**.
2. Fill in its title and optional description. Inspect the **Creator** selector.
   For a group-owned experience, select the exact owning group. For a user-owned
   experience, select the owning user's account. Match IDs through trustworthy
   Studio/Creator Dashboard evidence when names are ambiguous.
3. If the owner is missing, the account is wrong, or permissions are insufficient,
   stop before submission. Retain the local clip and identify the access problem.
   Do not choose a different creator, change group roles, or publish the game to
   manufacture a destination.
4. Submit once. Observe the success or error state and obtain the actual animation
   asset ID from the result, Toolbox, or Creator Dashboard. A closed dialog alone
   is not success. For timeouts or unclear results, inspect the intended owner's
   inventory first; retry only after establishing the previous upload did not land.
5. Verify the asset's creator, ID, and correspondence to the approved clip. Record
   an actual link/ID and observed evidence, not a guessed numeric value. Check
   moderation/access status if Roblox reports a restriction.
6. Run a focused playback check in the target experience with the correct Animator
   and published ID. Record whether loading and visible motion succeed. If access
   is still pending or failed, retain that status rather than marking it verified.
   Resolve the issue before completing this clip's cycle.

Saving locally, publishing an animation, and publishing the experience are three
different actions. The per-clip approval covers the specified animation upload.

## Recovery

Maintain `planned -> editing -> awaiting-review -> approved -> published -> verified`
for each clip, with the actual blocker recorded separately. Revisions return to
`editing`; preserve prior IDs/history rather than overwriting evidence. On resume,
compare the editor revision and observed asset state against the user's actual
decision. Complete the unfinished clip before starting the next one.
