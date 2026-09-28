# Performance and accessibility

## Contents
Documented tool use; budget reasoning; tier design; profiling protocol; failure remedies.

Roblox documents profiling and optimization tools, but **there is no universal “safe 500 particles” budget for every phone, camera and scene**. Use [performance optimization](https://create.roblox.com/docs/performance-optimization/improve) and [MicroProfiler](https://create.roblox.com/docs/performance-optimization/microprofiler) in the target project. Recommendations below are testable heuristics, not platform limits.

## Cost dimensions

Transparent **screen coverage and overlap** matter: a few enormous overlapping smoke cards can cost more than many tiny sparks. Inspect near-camera views, translucent shells, wide beams and dense flipbooks. Reduce overlap and empty alpha space, select purposeful texture resolution, and avoid making one light per particle. Texture memory, uploaded resolution and rendered resolution are different; don't freeze an old upload limit into the skill.

CPU costs include instance churn, per-frame callbacks, physics, redundant asset searches and garbage collection. Use shared controllers and cache resolved assets/configs. Pool frequent inert effects when reuse is correct; allocating an unbounded pool only moves the leak. Update far-away optional details less often. Cosmetic fragments can follow simple client arcs instead of full replicated physics.

An emitter occupancy estimate at ordinary time scale is rate times mean lifetime plus active bursts. It is a planning estimate, not visibility assurance. Validate spikes from concurrent actions, not just one isolated effect. Beams/trails trade geometry/history detail against smoothness. Screen-space post effects and camera changes affect the whole view; do not use them to conceal weak base art.

## Tier policy

Use a project-owned quality setting and observed performance, not a brittle device-name whitelist. Preserve the primary silhouette, direction and gameplay footprint at all tiers. Then reduce optional wisps, micro-sparks, layered smoke, shadows and fragments. A low tier may use a simpler graphic cue rather than fewer unreadable parts of the high tier.

Suggested priority order: essential telegraph/status -> clear contact shape -> directional support -> material tail -> secondary ornament. Define distance culling by role. A distant cosmetic smoke plume may disappear; an imminent damaging area needs a readable substitute. Keep audio and accessibility semantics when simplifying visual detail.

## Measure rather than declare

Capture a comparable scene baseline; then one cast; then the expected worst overlap; then cancellation/replay and sustained stress. Record place/build, device, resolution, graphics settings, camera distance, concurrent count, frame-time distribution and memory/instance trends. Where available, inspect CPU/GPU profiling categories and network traffic separately. Run both editor preview and actual client/device tests when relevant; Studio on a strong desktop is not evidence of mobile performance.

Change one dominant cost at a time and compare. Count-before/after tests should allow known persistent pool capacity but not unbounded live effects or connections. Test leaving/returning to the area, respawn, interrupted abilities, and asset-load failures.

## Accessibility / clarity

Honor reduced camera motion. Avoid rapid high-contrast full-screen flash sequences and repeating strobe; use localized shape or audio alternatives. Color should not be the only indicator of danger/team/status. Preserve interface legibility and important silhouettes. Don't silently lower the visual footprint of damaging effects under “optimization.” Select flash/motion limits with the project's accessibility requirements and current applicable guidance, not an invented medically safe numeric threshold.

## Common anti-patterns

| Failure | Better intervention |
|---|---|
| Every effect has 20 emitters | Build a primary shape, remove redundant roles, test whether each layer contributes |
| Smoke becomes opaque soup | Reduce overlaps/opacity, stagger lifetime, add negative space, separate depth |
| Bloom turns everything white | Fix value hierarchy and source shape; lower scene-wide contribution |
| Server spawns hundreds of physical shards | Client visual simulation, bounded reusable pieces, authority only where required |
| Constant hard-coded FOV resets | Owned presentation contributions and exact cancellation |
| Pool grows forever | Capacity, overflow policy, counted leases, stress test |
| Detail disappears on low settings | Deliberate cheap silhouette, not a critical particle-only boundary |
| “Optimized” based on particle count only | Measure frame time, screen coverage, memory, CPU, physics and network |
