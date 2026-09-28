# Production workflow

Contents: intake; evidence; design; implementation; iteration; handoff.

## Intake and evidence

Record effect intent separately from appearance. A stun, a heal, and an attack may
all be blue, but cannot share indistinguishable visual meanings. Determine whether
this is first-person, shoulder-camera, top-down, isometric, side-scrolling, or
cinematic work. Establish the ordinary gameplay viewing distance, character scale,
critical on-screen regions, trigger owner, and maximum likely concurrency.

Read the existing game code before proposing a new VFX network layer. Find where
attacks are confirmed, effects are spawned, animation tracks are loaded, projectiles
are simulated, and respawns clean up. Identify the shared texture library, camera
mixer, pooling utility, names/tags, and accessibility settings. Reuse those seams.

Save a minimal evidence record: input paths/URLs; chosen Studio/place; screenshots
or unavailable status; relevant existing scripts; style mode; assumptions; unknowns.
Do not read unrelated private files or upload a place/reference to third parties.

## Design deliverables

Produce a short style profile and a layer plan. Give every layer a role: primary
silhouette, action cue, directional motion, environmental response, or residual
state. Layers without a purpose are candidates for deletion.

For a one-shot, mark windup/anticipation, impact/contact, and dissipation relative
to the real gameplay event. For a loop, mark start, sustain, stop, and cancellation.
For a projectile, separate launch, travel, confirmed hit, and timeout. A travel
trail should not imply a collision before the authority reports one.

Design the low tier first. The effect must communicate with its primary layer
alone; richer tiers add subordinate detail, not additional gameplay information.
For ambient visuals, set a lower visual priority and avoid competing with hazards.

Example: a dusty stone landing should show a surface-normal dust fan, short impact
accent, a few local chips only when appropriate, and a tail low enough to leave the
avatar readable. An identical action in a clean digital arena might instead use a
thin geometric pulse with no soil, smoke, or rubble. This is an original adaptation
example, not a required universal recipe.

## Build sequence

1. Block out the primary read using a verified existing texture or an explicitly
   labelled temporary primitive. Make its size, orientation, timing, and stop work.
2. Integrate the actual animation/gameplay trigger. Do not polish a preview that
   fires at a different moment from the shipped ability.
3. Replace temporary art through the license/import pipeline. Verify real target
   experience permissions before relying on a texture.
4. Add directional and material response layers. Tune from the game camera.
5. Add local sound/camera feedback only if supported by the game's presentation
   architecture and player settings.
6. Exercise interruption, simultaneous casts, LOD, cleanup, and load failure.
7. Capture comparisons; remove expensive layers that do not improve communication.

## Iteration log

Keep observations separate from interpretations. Example: “At 30 studs the debris
outline is invisible on the floor” is an observation; “increase its size by 20%” is
a proposed fix. Change one major axis at a time. Compare the same camera, scene,
quality, trigger, and timing before/after. Never compare a reference shot with bloom
to a test with different exposure and conclude the texture alone is wrong.

## Handoff

Provide an entry-point example, parameter meanings/units, owner of start/stop,
quality policy, asset manifest, changed paths, screenshot/clip evidence, and test
status. Document any approximation such as mesh-based ripple instead of unavailable
screen-space refraction. Keep networking/damage configuration separate from art.

Source principles: [Riot visual-effects discipline](https://www.riotgames.com/en/artedu/visual-effects)
and [gameplay clarity](https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/).
The workflow, sample choices, and acceptance gates above are this package's design
heuristics, not official Roblox requirements.
