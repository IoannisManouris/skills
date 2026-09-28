# Effect recipe library

## How to use

These **36 original layer/timeline patterns** are design starting points, not measured optimums or universal numeric limits. Read only relevant entries. Times are illustrative seconds relative to an event; adapt to avatar scale, animation, gameplay, camera and style. Every stack can be reduced. The engine mappings are grounded in the [official effects guides](https://create.roblox.com/docs/effects); detailed methods are in the particle and instance guides. None of these entries claims the missing Deep Research report was imported.

## Index

1. Explosion; 2. Muzzle flash; 3. Bullet impact; 4. Projectile flight; 5. Laser / sustained beam; 6. Sword slash; 7. Hit spark / parry; 8. Shockwave; 9. Ground crack / earth spike; 10. Dust / smoke plume; 11. Fire / burning; 12. Water splash; 13. Waterfall / fountain; 14. Ice / freeze; 15. Lightning / electric arc; 16. Wind / gust / tornado; 17. Magic cast; 18. Portal; 19. Aura; 20. Charge / power-up; 21. Healing / buff; 22. Poison / debuff; 23. Shield / block; 24. Teleport / dash; 25. Spawn / despawn / dissolve; 26. Footsteps / landing; 27. Rain / snow; 28. Ambient motes / embers / insects; 29. Destruction / debris; 30. UI reward / level-up; 31. Cinematic impact / ultimate; 32. Glitch / hologram reveal; 33. Sand / mud / ink splatter; 34. Black hole / gravity well; 35. Meteor / falling strike; 36. Plant growth / vine attack

## 1. Explosion

**Layer plan:** A fast contact flash; expanding fire/smoke flipbook or shaped mesh; directed fragments; delayed dust and optional single light.

**Timeline:** Contact 0; flash fades ~0.05–0.12 s; expanding body ~0.1–0.45 s; smoke ~0.5–2 s.

**Style adaptation:** Cartoon puffs vs naturalistic irregular plume vs faceted chunks; do not simply recolor one stock explosion.

**Fallback / failure check:** Keep primary expansion/contact; remove extra embers and lights. Avoid physical Explosion for pure cosmetics.

## 2. Muzzle flash

**Layer plan:** Weapon-tip attachment; directional flash card/mesh; tiny brief light if justified; sparse smoke.

**Timeline:** At shot; flash ~0.03–0.08 s; smoke ~0.1–0.4 s.

**Style adaptation:** Tactical compact hot flash vs stylized graphic wedge; alternate authored variants subtly.

**Fallback / failure check:** Keep direction/contact. Check first-person clipping and accidental persistent enabled Rate.

## 3. Bullet impact

**Layer plan:** Surface-normal flash or material chip; dust puff; brief fragment spray.

**Timeline:** At validated impact; sparkle ~0.05–0.15 s; dust ~0.2–0.8 s.

**Style adaptation:** Metal sparks, wood chips, stone dust, wet splash need different material vocabulary.

**Fallback / failure check:** One impact shape and material tail; never use cosmetic raycast misses as gameplay truth.

## 4. Projectile flight

**Layer plan:** Mesh/core for readable position; short Trail or emitter tail; optional sparse air wisps.

**Timeline:** Launch impulse -> moving flight -> stop trail -> separate contact effect.

**Style adaptation:** Physical tracer vs glyph orb vs square pixel bolt.

**Fallback / failure check:** Simplify tail; preserve critical projectile location/direction; clear history on correction/teleport.

## 5. Laser / sustained beam

**Layer plan:** Two anchors with Beam core; wider low-opacity support; endpoint impact and optional local light.

**Timeline:** Fast activation, stable controlled sustain, short shutoff; endpoint tracks hit state.

**Style adaptation:** Engineered straight beam vs organic curved channel; use few distinct widths.

**Fallback / failure check:** Core and endpoint survive; no assumption ribbon looks round from every angle.

## 6. Sword slash

**Layer plan:** Trail along blade width during swing; mesh crescent or ordered flipbook for primary arc; hit effect separately.

**Timeline:** Windup optional; enable around active swing; contact on actual hit; tail ~0.1–0.3 s.

**Style adaptation:** Inked crescent, clean low-poly arc or restrained metal motion.

**Fallback / failure check:** Keep arc shape; remove spark fringe; a stationary Trail is not a slash.

## 7. Hit spark / parry

**Layer plan:** Directional star/diamond flash; a handful of streaks; optional short ring for parry distinction.

**Timeline:** Very brief contact peak; streaks decay ~0.1–0.3 s.

**Style adaptation:** Sharp anime rays vs mechanical sparks vs cute four-point gleam.

**Fallback / failure check:** Preserve parry identity without intense screen flash; do not spawn before hit confirmation.

## 8. Shockwave

**Layer plan:** Expanding ring mesh/ground card or deliberate radial stack; restrained trailing dust.

**Timeline:** Fast outward onset with deceleration; fade before it stalls; illustrative ~0.2–0.6 s.

**Style adaptation:** Faceted ring, smooth pressure sweep or broken brush circle.

**Fallback / failure check:** Simple readable ring; distinguish decorative radius from damage radius.

## 9. Ground crack / earth spike

**Layer plan:** Surface-aligned crack art or segmented meshes; lifted stones; sparse dust and contact accent.

**Timeline:** Crack propagates in a chosen path; spikes rise staggered; settle/fade after ability window.

**Style adaptation:** Graphic branching fissure vs rough displaced plates.

**Fallback / failure check:** Reduce small stones, retain hazard footprint. No terrain destruction by accident.

## 10. Dust / smoke plume

**Layer plan:** A few irregular sprites/flipbook clumps with coherent impulse and drag; wisps later.

**Timeline:** Opacity rises as volume forms then falls; tail outlasts contact.

**Style adaptation:** Soft physical turbulence vs broad cartoon circles vs brush masses.

**Fallback / failure check:** Reduce screen overlap before count alone; avoid identical dense billboards.

## 11. Fire / burning

**Layer plan:** Layered flame shapes/flipbook; limited ember trail; smoke if material demands; controlled light.

**Timeline:** Ignition -> lively sustained flow -> extinguish tail.

**Style adaptation:** Naturalistic hot-to-cool breakup, cel-shaded flame bands, pixel steps.

**Fallback / failure check:** One readable flame body; stop owner on despawn; no light per particle.

## 12. Water splash

**Layer plan:** Crown/arc meshes or flipbook body; droplets with ballistic arcs; surface ripple.

**Timeline:** Contact sheet/crown first; droplets separate and fall; ripple persists.

**Style adaptation:** Graphic blue-white shapes vs nearly neutral water with bright foam.

**Fallback / failure check:** Keep crown/ripple; translucent shells are not a free refraction shader.

## 13. Waterfall / fountain

**Layer plan:** Continuous mesh or Beam sheets; impact foam sprites; local mist and ripples.

**Timeline:** Loop with steady direction and entry/exit.

**Style adaptation:** Faceted ribbons vs smooth stylized sheets vs textured natural flow.

**Fallback / failure check:** Keep large flow shape; reduce broad mist overdraw and repeated lights.

## 14. Ice / freeze

**Layer plan:** Crystal meshes, frost mask/overlay and sparse cold motes; shatter separate.

**Timeline:** Growth in directed stages; quiet sustained state; break or thaw on actual state end.

**Style adaptation:** Faceted crystals, flat stylized frost, pixel blocks.

**Fallback / failure check:** Keep freeze status readable; do not add gameplay immobility from visual code.

## 15. Lightning / electric arc

**Layer plan:** Connected Beam segments or authored bolt mesh; thin hot core, restrained branch accents, contact sparks.

**Timeline:** Short strike, brief discontinuous rebranch, quick decay; not constant global strobe.

**Style adaptation:** Angular graphic bolt vs noisy natural forks vs clean engineered arcs.

**Fallback / failure check:** Fewer branches; maintain source/target; no native arbitrary lightning API assumed.

## 16. Wind / gust / tornado

**Layer plan:** Curved mesh ribbons/Beams; sparse dust/leaves with directional flow; visible base if hazardous.

**Timeline:** Acceleration into sweep/spiral; uneven secondary motion; taper exit.

**Style adaptation:** Graphic crescents, painterly sweeps or near-invisible natural dust cues.

**Fallback / failure check:** Retain path/hazard outline; do not fill the whole cone with opaque particles.

## 17. Magic cast

**Layer plan:** Identity motif at source; converging motes/ribbons; release core; separate impact.

**Timeline:** Anticipation -> compression -> release; phases use ability markers/state.

**Style adaptation:** Glyph ornament vs organic vines vs minimalist geometry.

**Fallback / failure check:** Keep motif plus release; avoid random runes unrelated to style.

## 18. Portal

**Layer plan:** Rim mesh/segmented rings; surface art; controlled inward/outward wisps; entry/exit accent.

**Timeline:** Open establishment -> quiet loop -> collapse; handle cancel during opening.

**Style adaptation:** Stone/organic threshold, clean sci-fi aperture or inked tear.

**Fallback / failure check:** Keep boundary; do not promise real alternate-world rendering without a dedicated system.

## 19. Aura

**Layer plan:** Body-following low-density motif with spacing; subtle orbit meshes/trails; readable status marker.

**Timeline:** Entry accent -> restrained loop -> fade on removal/respawn.

**Style adaptation:** Holy rays, occult smoke, technological lattice or cute hearts.

**Fallback / failure check:** Reduce constant clutter; locked particles versus world trails must be intentional.

## 20. Charge / power-up

**Layer plan:** Inward paths, growing core, tension accents and timed release.

**Timeline:** Change rhythm/density across charge rather than linearly scaling everything; cancel reverses or dissipates.

**Style adaptation:** Mechanical capacitors, magical spiral, angular anime compression.

**Fallback / failure check:** Keep progress/phase cue; do not fire release after cancellation.

## 21. Healing / buff

**Layer plan:** Upward soft motes plus distinctive icon/motif; local low-opacity pulse; optional body highlight.

**Timeline:** At successful state application; one accent plus sparse periodic loop.

**Style adaptation:** Leaves, clean UI rings, stars or warm ritual shapes; not automatically green.

**Fallback / failure check:** Preserve status identity/color semantics; avoid obscuring the avatar.

## 22. Poison / debuff

**Layer plan:** Low drifting wisps, droplets/marks and status icon; restrained negative-space halo.

**Timeline:** Application hit -> restrained persistent cue -> remove on authoritative end.

**Style adaptation:** Organic murk, industrial chemical vapor or clean symbolic indicator.

**Fallback / failure check:** Keep icon/shape; do not rely solely on green vs red.

## 23. Shield / block

**Layer plan:** Mesh boundary or segmented panels; contact-local ripple/flash; sparse fracture on break.

**Timeline:** Activation establishes boundary; hits localize; break releases fragments then clears.

**Style adaptation:** Energy hex panels, faceted ice, organic bark or graphic outline.

**Fallback / failure check:** One boundary and local hit; no gameplay ForceField inserted for looks.

## 24. Teleport / dash

**Layer plan:** Source contraction/afterimage; short directional trace; destination burst; owner-safe visibility restoration.

**Timeline:** Source cue -> authoritative relocation -> arrival; interrupted states restore.

**Style adaptation:** Digital slices, smoke vanish, geometric blink or brush smear.

**Fallback / failure check:** Preserve destination readability; clear Trails to avoid bridging the entire teleport.

## 25. Spawn / despawn / dissolve

**Layer plan:** Staged transparency/mesh scale with particles; silhouette retained until handoff; original dissolve-like texture sequence if needed.

**Timeline:** Finite entry or exit with synchronized visibility handoff.

**Style adaptation:** Pixel assembly, faceted shards, smoke or holographic scan.

**Fallback / failure check:** Simple fade/shape fallback; no claim of general programmable dissolve shader.

## 26. Footsteps / landing

**Layer plan:** Surface-appropriate dust/splash/chips at contact anchors; landing increases coherent impulse, not random density.

**Timeline:** Foot marker/contact event; tiny trail-free tail; landing as larger single event.

**Style adaptation:** Toy puffs, realistic fine dust, pixel stamps.

**Fallback / failure check:** Distance-cull optional steps; do not spawn a full explosion at every foot.

## 27. Rain / snow

**Layer plan:** Camera/region-local bounded emit volume; optional nearby collision accents; indoor suppression policy.

**Timeline:** Continuous ambience with smooth entry/exit and drift.

**Style adaptation:** Graphic streaks, chunky snowflakes or subdued natural precipitation.

**Fallback / failure check:** Reduce local density; do not simulate a physical raindrop per particle or rain indoors accidentally.

## 28. Ambient motes / embers / insects

**Layer plan:** Sparse point/region emission; slow varied movement; limited glow.

**Timeline:** Long calm loop with randomized but coherent cadence.

**Style adaptation:** Dust in light shafts, magical motes or firefly dots.

**Fallback / failure check:** Cull by area/distance; avoid thousands of invisible long-lived instances.

## 29. Destruction / debris

**Layer plan:** Primary breakup silhouette using a few mesh chunks; dust and directional secondary fragments.

**Timeline:** Fracture impulse -> ballistic settling -> quiet cleanup.

**Style adaptation:** Faceted blocks vs material fragments; match actual object scale.

**Fallback / failure check:** Client arcs instead of mass physics; no unbounded chunk pool.

## 30. UI reward / level-up

**Layer plan:** World accent plus ScreenGui icon/number motion; clear focal hierarchy; brief optional confetti.

**Timeline:** Event confirmation -> accent -> count/update -> settle.

**Style adaptation:** Cute sparkle, clean motion-graphic or ornate fantasy treatment.

**Fallback / failure check:** Preserve readable number/confirmation; respect safe areas and reduced motion.

## 31. Cinematic impact / ultimate

**Layer plan:** Purposeful staged large silhouette; controlled local camera/audio contributions; gameplay-safe visibility.

**Timeline:** Anticipation, brief dominant beat, fast return of visibility, long sparse tail.

**Style adaptation:** Any chosen style amplified coherently, not necessarily anime.

**Fallback / failure check:** Lower tiers keep critical state; restore camera exactly and suppress flashes per settings.

## 32. Glitch / hologram reveal

**Layer plan:** Original scan-line image/mesh layers; segmented appearance and brief offset fragments.

**Timeline:** Discrete controlled interruptions, then stable resolved state.

**Style adaptation:** Digital cyan is optional; use the scene accent roles.

**Fallback / failure check:** One readable scan/outline; no arbitrary framebuffer sampling assumed.

## 33. Sand / mud / ink splatter

**Layer plan:** Surface-aligned splat art or mesh; directed droplets; material dust/sheen as needed.

**Timeline:** Contact fan -> secondary drops -> footprint fade.

**Style adaptation:** Comic ink, chunky mud or dry natural grit.

**Fallback / failure check:** Keep contact/material cue; no universal projection across uneven meshes.

## 34. Black hole / gravity well

**Layer plan:** Readable core/boundary; curved converging paths and sparse orbit debris; explicit hazard outline.

**Timeline:** Formation -> controlled inward flow -> collapse/ejection.

**Style adaptation:** Graphic void, sci-fi lens motif or occult smoke.

**Fallback / failure check:** No genuine spacetime/refraction promise; preserve visibility and damaging boundary.

## 35. Meteor / falling strike

**Layer plan:** Readable moving body, trailing fire/smoke, ground telegraph, surface-normal impact stack.

**Timeline:** Telegraph first -> falling motion -> validated impact -> tail.

**Style adaptation:** Faceted flaming rock, realistic plume or glyph projectile.

**Fallback / failure check:** Telegraph cannot be removed to save particles; synchronize impact, not launch timestamp alone.

## 36. Plant growth / vine attack

**Layer plan:** Segmented/skinned meshes or sequential pieces; sparse leaf motes and soil contact.

**Timeline:** Directed growth with stagger; hold if state persists; retract/decay.

**Style adaptation:** Organic curling, polygonal branches or paper-cut leaves.

**Fallback / failure check:** Fewer segments/motes; do not use particles as the only meaningful vine body.
