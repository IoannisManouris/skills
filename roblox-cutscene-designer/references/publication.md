# Animation publication and verification

Applies to Blender-authored, editor-authored and other supported local clips.
Authoring, importing, animation publication and experience publication are
separate operations.

## Review and authorization

Before upload, match the exact revision, verified experience owner, create/update
operation, review outcome and user's authorization. Honor an existing instruction
such as "publish after reviewer-agent approval" without asking the user again for
each clip. The agent's review does not independently grant publication permission.

When authorization is missing, show the concrete playable preview and ask one
question about publishing that revision to the verified owner. Changes requested
by the user require revision and appropriate re-review; silence is not approval.
For reused published assets, assess fit and access without duplicating uploads.

## Select a supported publication route

Prefer a callable Studio MCP/API operation that supports the clip type and
destination. Discover its actual schema, capability and permission requirements;
do not assume every Studio MCP exposes upload or that ordinary game scripts may
perform authoring operations.

Where available, `AssetService:CreateAssetAsync` can provide an authoring route:
use the reviewed clip, the correct supported asset type, and explicit
`CreatorId`/`CreatorType` request parameters for the verified owner. Check current
documentation and the live tool context for support for that clip type, rather
than probing by uploading unreviewed drafts. Handle both thrown errors and a
returned non-success result; a successful `pcall` alone is not upload success.
Capture the ID from the actual successful result.

Use a version/update operation only when the identified existing asset update is
authorized. Do not guess private endpoints or weaken permissions to avoid a UI
step. If the API route is unavailable, use the Animation Editor's native
publication flow when accessible. Missing computer use blocks only UI-dependent
operations, not a supported MCP/API route.

## Native publication fallback

Read the installed computer-use skill before UI operations. Reopen/select the
reviewed local or imported clip, choose the observed **Publish to Roblox** action,
and verify the **Creator** selector matches the owner. Preserve the user's window
layout; inspect controls instead of replaying fixed coordinates.

If the intended owner is unavailable or access is denied, retain the local clip
and report the actual access problem. Do not choose another creator or publish the
experience to manufacture a destination.

## Observe, verify and recover

Submit once. Obtain the actual result/ID; a closed dialog or finished tool call is
not proof of publication. On an unclear outcome, inspect the owner's inventory or
the reported operation before retrying. Avoid duplicate uploads.

Verify the asset's creator and correspondence to the reviewed revision. Where
available, inspect the downloaded clip's duration, loop flag, markers and priority.
Then load the published ID with the correct Animator in the target experience and
observe actual motion and prop behavior. Loading length zero in an unsuitable
Edit context is not conclusive; test in a running client/server as appropriate.

Record verified IDs/links, source revision, owner and observed playback evidence.
Keep moderation/access failures explicit. A saved clip, imported file or temporary
preview registration ID is not a published Roblox animation.

Track `planned -> editing -> awaiting-review -> approved -> published -> verified`
with blockers separately. Preserve prior versions and IDs. Reconcile an interrupted
upload before submitting again. Publishing the experience itself requires its own
authorization; animation approval does not authorize that action.
