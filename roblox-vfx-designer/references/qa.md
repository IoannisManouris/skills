# QA gates and truthful validation

## Contents
Acceptance; visual inspection; runtime/device cases; evidence; skill evaluation.

## Required gates

1. **Intent:** effect tells the right event, at the right place/time. Hit/telegraph bounds are accurate and status meanings preserved.
2. **Style:** observable shape, edges, palette roles and rhythm match the chosen description/environment/reference axes. No unexplained generic neon/anime fallback.
3. **Assets:** original/downloaded source, author, exact rights and modifications recorded. No screenshots used as unlicensed textures. Imported content IDs actually resolve in the target experience.
4. **Isolation:** cosmetic instances cannot collide, alter terrain, provide ForceField protection, change damage or permanently overwrite camera/Lighting.
5. **Lifecycle:** finite stop owner; delayed work canceled; tails handled; repeated stop/release idempotent; reuse restores state; missing assets fail clearly.
6. **Experience:** view at gameplay distance, overlapping casts, low/high graphics, representative light/dark surfaces. Essential cue remains on reduced tier.

A passed static check cannot satisfy gates requiring an actual runtime or visual observation. Record `passed`, `failed`, `not_run`, or `blocked`, with evidence and cause. Never describe a generated test file as a test already executed.

## Visual inspection procedure

Review onset, dominant silhouette, contact and tail, not only the most flattering frame. Compare normal-speed motion to the reference when accessible. Check floor/wall/slope, near/far view, front/back of transparent cards, first-person camera penetration and interference with UI. Remove optional layers one at a time to discover which are redundant. Confirm the strongest accent occurs on the important beat. Record any artistically subjective choice as a rationale rather than a fake objective score.

## Runtime scenarios

Run play -> stop -> replay; hard cancel before the first delayed burst; graceful cancel mid-tail; stop twice; release old lease after a new acquire; rapid capacity exhaustion; destroy/respawn owner; teleport with an active trail; missing/denied texture; high-latency predicted attack and server rejection; multi-client duplicate event; join during persistent ambience. Not every effect needs every test, but explicitly mark irrelevant cases rather than pretending they ran.

The packaged Studio smoke test is an **execution fixture**, not runtime certification. Its proxy-texture use is intentional and cannot establish final texture/style quality.

## Evidence record

Return changed instances/files, selected Studio and datamodel, screenshot/video paths (only real captures), test date, counters/timing, quality settings, asset manifest and remaining limitations. Keep private place imagery local unless the user authorizes disclosure. A console with no errors is useful but not proof that an effect looks good.

## Evaluating the skill itself

Use `evals/trigger-cases.json` and `evals/behavior-cases.json` with actual host/model versions. Test positive, negative and contextual prompts; track missed triggers and unwanted invocation. Compare the same tasks without the skill, then with it. Have an appropriate reviewer examine rendered outputs; use hard gates for safety/lifecycle and a separate design assessment for style/readability. Test again after changing discovery metadata. These fixtures do not claim measured success rates. Method basis: [Anthropic skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
