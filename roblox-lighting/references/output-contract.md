# Output Contract and Machine-Actionable Workflow

## 1. Required input model

The agent should normalize available inputs into:

```json
{
  "mode": "FROM_SCRATCH | MATCH_SCREENSHOT | LINK_ASSISTED_MATCH | IMPROVE_OR_DEBUG | AUDIT_OR_OPTIMIZE",
  "user_goal": "string",
  "screenshots": [],
  "roblox_url": null,
  "genre": null,
  "map_metadata": {},
  "gameplay_metadata": {},
  "art_direction": {},
  "camera_metadata": {},
  "performance_target": {},
  "existing_settings": null,
  "studio_access": false,
  "available_tools": []
}
```

Missing values are allowed. Record assumptions instead of fabricating facts.

## 2. Observation output

Use `assets/observation.schema.json`. Required conceptual groups:

- source ledger;
- camera/composition;
- geometry/material confounders;
- global light direction/softness/fill;
- atmosphere/sky/clouds;
- local lights/emissive cues;
- post-processing/tone;
- gameplay/readability;
- uncertainty and high-information next views.

Every inference must contain evidence, confidence, and plausible alternatives.

## 3. Hypothesis output

Create 1–3 hypotheses:

```json
{
  "id": "H1",
  "summary": "Low warm sun, cool sky fill, medium haze, restrained grade",
  "explains": ["long parallel shadows", "warm lit faces", "blue distant terrain"],
  "assumptions": ["reference was not externally color graded"],
  "confidence": 0.72,
  "roblox_feasibility": 0.9,
  "gameplay_fit": 0.85,
  "performance_risk": "low",
  "rejected_if": ["additional view shows no directional shadows"]
}
```

Choose one preferred hypothesis and preserve one alternative when ambiguity matters.

## 4. Lighting plan

Create `lighting-plan.json` using `assets/lighting-plan.schema.json`. Include:

- identity/version/plan ID;
- intent, mode, thesis, genre, target state;
- source ledger references;
- assumptions and confidence;
- global Lighting properties;
- one Sky configuration;
- Atmosphere or legacy fog choice;
- Clouds;
- post-processing;
- local-light declarations with semantic target paths/attachments;
- material/geometry requirements;
- runtime profile/transition rules;
- quality tiers;
- validation cameras and metrics;
- unresolved ambiguities and stopping criteria.

Validate with `scripts/validate_plan.py`.

## 5. Studio implementation output

When direct Studio editing is unavailable, generate:

```bash
python scripts/generate_luau.py lighting-plan.json --output apply_roblox_lighting.lua
```

The output should:

- back up affected Lighting properties, Workspace wind, managed local lights, and affected Lighting/Terrain child instances;
- tag generated instances;
- preserve unmanaged conflicts by default and warn when they can alter the planned result;
- optionally back up and replace matching global conflicts only after explicit `--replace-conflicts` selection;
- update only managed instances by default;
- use guarded property writes;
- create missing managed Sky/Atmosphere/Clouds/post effects;
- create local lights only when a target path resolves;
- generate Camera-local script instructions/effects separately;
- print warnings/manual steps;
- include plan ID and timestamp.

Also supply `assets/restore-backup.lua`. Camera-local effects are generated separately and must be removed or disabled separately during rollback.

## 6. Human-readable final report

Use this structure:

### A. Result

- selected mode/hypothesis;
- one-paragraph creative and technical rationale;
- what the lighting enables for the player.

### B. Evidence and uncertainty

- strongest observations;
- confidence ranges;
- camera/material/geometry confounders;
- alternatives and what would disambiguate them.

### C. Implementation

- hierarchy and key settings;
- local light placement;
- material/geometry changes;
- runtime/transition logic;
- generated files.

### D. Performance and accessibility

- low/medium/high strategy;
- shadow/light activation plan;
- fairness/readability/comfort notes.

### E. Validation

- views/devices/quality tiers tested;
- image metrics and visual rubric;
- profiler findings;
- remaining mismatches and why.

### F. Rollback and maintenance

- backup/restore method;
- current-doc verification date;
- properties/endpoints that require future re-check.

## 7. Evaluation metrics

### Screenshot/style metrics

- camera/silhouette agreement;
- sun/shadow direction angular error;
- shadow area/softness agreement;
- mean/percentile luminance;
- clipped black/white percentages;
- regional color/histogram distance;
- atmospheric depth contrast;
- local light pool/cone placement;
- bloom mask agreement;
- perceptual rubric score.

### Gameplay metrics

- two-second route comprehension;
- hazard/enemy/interactable visibility;
- player silhouette fairness;
- UI contrast;
- motion comfort;
- indoor/outdoor transition comfort;
- low-quality resilience.

### Performance metrics

- frame-time median/p95/worst;
- MicroProfiler lighting/shadow/post scopes;
- active/overlapping/shadowed light counts;
- quality-tier differences.

## 8. Iteration state

Maintain an experiment log:

```json
{
  "iteration": 4,
  "change_family": "atmosphere",
  "changes": {"Density": [0.22, 0.27], "Offset": [0.05, 0.08]},
  "expected": "reduce far landmark contrast without changing foreground",
  "observed": "far contrast improved; horizon slightly ghosted",
  "metrics_delta": {"far_region_hist_l1": -0.08},
  "gameplay_delta": "landmark still readable",
  "decision": "keep density; revert offset to 0.06"
}
```

## 9. Stopping rules

Stop iterating when:

- all mandatory quality gates pass;
- the preferred hypothesis explains the strongest evidence;
- screenshot similarity is within agreed tolerance or limited by known non-lighting/engine differences;
- gameplay/readability/performance are acceptable;
- two consecutive fine iterations produce negligible perceptual improvement;
- remaining uncertainty is explicitly documented.

Do not continue by adding extreme post effects merely to improve a metric.

## 10. Failure output

When a step cannot be completed, do not silently omit it. Report:

- attempted action;
- exact failure/limitation;
- evidence still available;
- fallback performed;
- impact on confidence;
- next best action.
