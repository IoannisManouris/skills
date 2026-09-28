# Style system: observable grammar, not a fixed preset list

## Contents
Profile axes; environment inspection; input precedence; style families; temporal reference analysis; adaptation examples.

These are original operational design heuristics, not Roblox engine rules. A style family is a useful description, not a complete recipe. **Fire is a subject, fantasy is a genre, and painterly is a rendering treatment.** Combine independent axes rather than treating those labels as interchangeable or exhaustive.

## Record a profile before designing

| Axis | What to inspect / record | How it affects the effect |
|---|---|---|
| Shape language | Round vs angular; symmetry; broad masses vs filigree | Primary silhouette, shockwave form, debris outline |
| Edge treatment | Soft, sharp, stepped, inked, faceted | Texture masks, mesh edges, alpha ramps |
| Material language | Matte, metallic, emissive, translucent, painted | Lighting response and actual need for lights |
| Spatial detail | Large simplified forms vs fine irregular texture | Sprite frequency, density, mesh complexity |
| Palette roles | Base, accent, danger, ally, neutral, environment | Color choices with semantic constraints |
| Value range | Dark/light backgrounds and UI; exposure | Readability without universal white bloom |
| Saturation | Muted, narrow accents, broad saturation | Color budgets; avoid all layers competing |
| Temporal grammar | Snappy, elastic, stepped, flowing, weighty | Curves, pauses, stagger, residual movement |
| Physical plausibility | Realistic, exaggerated, abstract | Acceleration, scale, causal sequence |
| Density / negative space | Sparse/readable vs deliberately overwhelming | Layer count and overlap allowance |
| Scale / camera | Avatar, floor tiles, weapon length; FOV and distance | Stud dimensions, minimum readable shape |
| Perspective | Fixed side-view, top-down, orbit, first-person | Billboard suitability, mesh need, occlusion |
| Lighting | Authored global setup, local light sources, interiors | LightInfluence, emitter contrast, post effects |
| Accessibility | Motion reduction, flash limits, color-blind cues | Redundant shapes, camera settings, alternatives |

Use a short textual rationale per important axis, evidence paths/screenshots, and confidence (`observed`, `inferred`, `unknown`). Do not present sampled pixel colors as an objective style classifier. A tree-wide count of BasePart.Color can be dominated by hidden objects or many small parts and is not a screen-area palette.

## Environment mode

Inspect the actual gameplay camera, not only the default Studio view. Capture the target surface and representative adjacent locations, with existing characters, effects and UI where possible. Identify what must remain visually prominent. Derive scale from real instances or bounding boxes rather than guessing from perspective. Look for representative variation: an interior/night area may require different contrast treatment from a sunny outdoor hub.

Build a small primary-shape prototype in the target place. Examine it in color and, where tools permit, a grayscale/thumbnail view. First solve detection of the action and its footprint; only then harmonize texture noise and accent palette. **Matching a scene does not mean making the effect indistinguishable from it.** Set critical hit-area boundaries separately from decorative spill. Preserve any existing team/status color semantics.

## Input precedence

User-stated restrictions govern the requested aesthetic. The environment governs unrequested integration details. A reference governs only the axes the user asked to match. For a hybrid, explicitly assign axes: e.g. reference timing and silhouette, scene palette and surface response, existing combat system marker names and telegraph semantics. Resolve conflicts in a one-sentence design decision rather than silently selecting anime defaults.

## Practical style families

Each row is a starting grammar to adapt, **not a taxonomy boundary or an assurance that a label covers every aesthetic**. Element, genre and mood tags may apply to any row.

| Family | Shape / texture / palette | Motion and construction | Avoid / reference-search phrases |
|---|---|---|---|
| Naturalistic / realistic | Irregular material-specific breakup; restrained hot cores; variable edges | Causal ignition/expansion/cooling; flipbook smoke, few fragments, scale-correct gravity | Uniform circles, identical puffs; search soot plume, splash crown, dust impact |
| Semi-realistic game VFX | Real-world material cues with simplified strong silhouette | Compress dead time, separate contact and tail, more readable sparks | Realistic simulation so dense it hides gameplay |
| Cinematic naturalism | Large coherent masses with camera-aware detail | Shot-specific layers and controlled exposure; mesh volume plus sprite detail | Shipping cinematic budget to every gameplay cast |
| Rounded cartoon / toy-like | Puffy clumps, clean accents, simple gradients | Quick squash/overshoot, few large readable sprites or meshes | Tiny gritty noise; search cartoon smoke puff, toy explosion |
| Anime / manga | Sharp crescents, starbursts, ink/speed shapes, intentional high contrast | Held anticipation, fast release, angular trails; optional restrained impact frames | Constant strobing, generic huge neon spheres |
| Cel-shaded | Discrete value bands, hard shade boundaries | Graphic meshes and masks; coherent limited shade palette | Soft photoreal smoke pasted into hard-edged world |
| Comic-book / inked | Outlines, hatching, halftones, lettering where appropriate | Bold pose-like beats; layer graphic stamp with physical contact | Text illegible in perspective; unlicensed lettering art |
| Hand-drawn 2D hybrid | Variable line, silhouette-changing frames, intentional imperfection | Flipbook-driven shapes on world cards or UI; stepped timing | Treating every shape as a smoothly scaled stock sprite |
| Painterly | Brush edges, broad strokes, grouped values | Flow in large strokes; carefully limited soft secondary texture | High-frequency photographic detail; search brush stroke smoke |
| Low-poly / faceted | Flat polygon masses, planar highlights | Mesh fragments, faceted shock front, sparse particles | Unnecessary alpha clouds hiding geometry |
| Voxel / blocky | Grid-aligned volumes, block fragments | Quantized spatial changes, chunked expansion | Misaligned scale and rounded texture noise |
| Pixel-art / retro sprite | Intentional pixel size, limited ramps | Nearest-neighbor authoring, discrete frames; test on actual screen | Claiming perfect nearest sampling for world particles without testing |
| Retro console / low-fidelity | Low-resolution texture vocabulary, dither/vertex-like treatment | Simple cards and low-poly meshes, limited color bands | Accidental low quality masquerading as consistent direction |
| Minimalist / clean | Few geometric shapes; large negative spaces | One strong directional sweep, concise release | Micro-particles added just to inflate complexity |
| Abstract / geometric | Rings, planes, lattices, mathematical rhythm | Coordinated meshes, beams and transforms | All geometry rotating at the same speed without hierarchy |
| Ornamental fantasy | Motifs, sigils, glyph shapes, controlled glows | Motif establishes identity; energy converges then releases | Random unreadable runes, borrowed copyrighted emblems |
| Organic magic / nature | Branching/leaf/vein shapes; irregular flow | Growth, spirals, stagger; meshes plus soft spores | Mechanical symmetric rings unless deliberately hybrid |
| Sci-fi / engineered energy | Precise alignment, panels, cores, functional segmentation | Measured charge, directional beam, engineered shutdown | Random lightning clutter inconsistent with machinery |
| Holographic / digital | Scan bands, grids, broken contours | Layered meshes/images, stepped opacity, controlled slice offsets | Assuming a global programmable distortion shader exists |
| Glitch / corrupted signal | Discontinuity and constrained channel offsets | Short bursts of controlled displacement, not constant random shake | Unreadable objectives, gratuitous full-screen flashes |
| Neon / cyberpunk | Dark support, localized luminous accents | Emissive trails against structured dark masses | Everything neon, bloom erasing edge detail |
| Cute / chibi | Rounded hearts/stars/puffs, friendly scale | Bouncy cadence, sparse confetti, soft tails | Tiny noisy effects or aggressive flashing |
| Dark / horror / occult | Negative shapes, smoke stains, unstable restrained accents | Slow pressure then brief rupture; light used intentionally | Blacks invisible against darkness; constant blur |
| Gritty / industrial / tactical | Material grit, hot metal sparks, small smoke masses | Fast mechanical impulse, heavy settling debris | Huge bright gamey rings for ordinary contact |
| UI / motion-graphic integrated | Typography/icon language and screen-space spacing | UI tweens plus world anchor; feedback tied to actual state | World effects always on top, covering menus and targets |

For an unlisted style (paper cutout, clay, chalk, stained glass, watercolor, mixed media), describe it along the same axes and construct a new profile. Do not force it into the nearest row. Keep borrowed reference **principles** separate from reusing protected images or texture files.

## Video and image analysis protocol

Open the actual reference and record access status. A thumbnail or title is not the clip. With permitted video tools, inspect normal speed and frames around anticipation, maximal silhouette, contact, and dissipation. Record relative beat positions only when observed; do not fabricate timestamps. Separate camera shake from object movement; lighting bloom from the emitter shape; occluding geometry from the effect. Seek another angle for ambiguous 3D structure.

For an image-only reference, record geometry and palette evidence but leave timing provisional. Build a plausible motion interpretation and label it as original. Avoid extracting textures from proprietary game footage. Rebuild motifs with original shapes or separately licensed art.

## Same event, different style: grounded landing

Naturalistic: a compact surface-matched dust plume with asymmetric small fragments and a fast, low flash only when justified. Low-poly: a handful of faceted wedges with brief scale expansion; little smoke. Anime: a crisp radial impact form, directional streaks and quick displaced ground dust; motion can be exaggerated without enlarging the damaging radius. Painterly: broad irregular contact strokes with brush-edged dissipation. Holographic: precisely aligned contact scan, segmented ring and short data fragments. All share the same authoritative event and footprint; they do not need the same textures or number of layers.

## Source basis

The profile, family table and adaptation rules are original design synthesis. Gameplay hierarchy and restraint are informed by the primary practitioner discussions at [Riot Art Education: VFX](https://www.riotgames.com/en/artedu/visual-effects) and [Clarity in League](https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/). These are transferable design principles, not Roblox API specifications.
