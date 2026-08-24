# Roblox Experience Link Research

## Goal

When the user supplies a Roblox experience/place URL, improve lighting inference by collecting **public** metadata and gameplay media, then selecting references that show the same lighting state as the user's snapshot.

A Roblox link is evidence, not permission to access private source settings.

## 1. Parse and normalize the URL

Common patterns include:

- `https://www.roblox.com/games/<placeId>/<slug>`
- regional or share URLs that redirect to a games page;
- a bare place ID supplied with an experience name.

Extract the numeric place ID. Follow public redirects only. Record the canonical URL.

Use:

```bash
python scripts/research_roblox_game.py "<roblox-url>" --output research.json --download-dir media
```

The script attempts current public Roblox metadata/media endpoints, records failures, and creates suggested web/image-search queries. Endpoints can change; verify against current official Roblox documentation.

## 2. Resolve place to universe/experience

Preferred sequence:

1. Resolve place ID to universe ID using a current public Roblox endpoint when available.
2. Query current game metadata using the universe ID.
3. Query official experience media/thumbnails.
4. Preserve IDs, URLs, timestamps/status, and endpoint response metadata in a source ledger.

Do not use user cookies, session tokens, undocumented authentication bypasses, or private APIs. If a public endpoint fails, use the experience page and web/image search rather than escalating access.

## 3. Collect public reference classes

In descending initial trust:

1. User-provided raw gameplay images/video.
2. Official Roblox experience media and thumbnails.
3. Creator/group-owned trailers, social posts, devlogs, and update videos.
4. Recent gameplay videos/screenshots from reputable creators or players.
5. Search-engine image results and wiki/community pages.

Official thumbnails are not guaranteed to be raw gameplay. They may be staged, edited, old, or captured under a special event state. Record authenticity confidence.

## 4. Search query generation

Use the official title, creator/group, place ID, universe ID, and recognizable map/level terms. Generate several targeted queries, for example:

- `"<experience title>" Roblox gameplay <map/level>`
- `"<experience title>" Roblox night gameplay`
- `"<experience title>" Roblox update <year>`
- `site:youtube.com "<experience title>" gameplay`
- `site:roblox.com/games/<placeId>`
- `"<experience title>" screenshot Roblox`

Use image search when available. For videos, inspect representative frames rather than trusting the thumbnail.

## 5. Filter for relevance

Reject or down-weight media that is:

- clearly fan art or unrelated UGC;
- heavily edited with text/glow/grade obscuring the scene;
- from a different map, season, event, or time of day;
- too old relative to a major visual update;
- low resolution or dominated by UI;
- captured in a lobby when the target is gameplay;
- a copycat experience with a similar title;
- using a custom cinematic camera/grade not seen in normal gameplay.

Verify the experience identity through title, creator, URL/ID, recognizable geometry/UI, and publication context.

## 6. Cluster by lighting condition

Do not combine incompatible images. Create clusters using visible features:

- outdoor day / golden hour / night;
- clear / overcast / foggy / storm/event;
- interior biome/room;
- lobby vs round/gameplay;
- low vs high graphics;
- normal gameplay vs thumbnail/cinematic grade;
- map version/update period.

For each image compute or estimate:

- average sky hue/value;
- global luminance and clipping;
- shadow direction/length/softness;
- atmosphere/fog depth;
- dominant local-light colors;
- bloom/saturation/contrast;
- recognizable location.

Use visual embeddings if the agent has them; otherwise use a structured vision rubric. After downloading candidate images, run:

```bash
python scripts/cluster_images.py media \
  --reference user-snapshot.png \
  --recursive \
  --output lighting-clusters.json
```

The clustering helper uses broad color, luminance, sky/ground, saturation, and percentile features as triage. It cannot establish semantic identity, map version, authenticity, or exact illumination, so visually verify every selected candidate. `scripts/image_metrics.py` can provide aligned pair diagnostics after camera/map matching.

## 7. Match the user's snapshot to a cluster

Score each candidate:

```text
cluster_score =
  0.25 * map_or_location_match +
  0.20 * sun_shadow_match +
  0.15 * sky_weather_match +
  0.15 * luminance_tone_match +
  0.10 * atmosphere_depth_match +
  0.10 * local_light_palette_match +
  0.05 * recency_authenticity
```

Weights are a starting heuristic. Increase location weight when multiple maps exist; increase authenticity when thumbnails conflict with gameplay.

Keep the best coherent cluster and at most one plausible alternative. Never average the title thumbnail's golden-hour grade with normal noon gameplay merely because both are official.

## 8. Build a source ledger

Use entries like:

```json
{
  "source_id": "official-media-03",
  "url": "...",
  "source_type": "official_experience_media",
  "experience_identity_confidence": 0.99,
  "raw_gameplay_confidence": 0.62,
  "capture_or_publish_date": null,
  "map_cluster": "main-map-v4",
  "lighting_cluster": "clear-late-afternoon",
  "similarity_to_user_snapshot": 0.81,
  "included": true,
  "notes": ["same landmark", "thumbnail may have extra bloom"]
}
```

Cite the ledger in the final report. Distinguish fact (title, creator, IDs, media URL) from visual inference (time, grade, similarity).

## 9. Use multiple views to reduce ambiguity

From the selected cluster, seek:

- a view 90° around the same landmark to triangulate sun direction;
- a view toward the horizon/sun;
- a clear contact shadow;
- indoor and outdoor views;
- reflective surfaces;
- footage showing dynamic day/night or event transitions.

Update observation confidence rather than simply adding more settings.

## 10. Handle dynamic or multiple lighting states

If the experience changes time, weather, biome, round, or event state:

- identify the state shown in the user's snapshot;
- build a named lighting profile per state;
- define transition rules and runtime ownership;
- avoid presenting one state as the entire game's settings;
- ensure generated scripts do not globally switch every player for a camera-local effect.

## 11. Legal/ethical boundaries

- Reproduce a visual style/lighting relationship, not copyrighted skybox textures or stolen assets.
- Use publicly accessible media and respect platform/source terms.
- Do not claim private source extraction.
- Do not impersonate the original creator or present the result as official.
- Record uncertainty when a media item appears edited.

## 12. Failure fallback

If the URL cannot be resolved or media is unavailable:

1. keep the user snapshot as primary evidence;
2. search the exact title/creator/place ID on the public web;
3. use any reliable matching gameplay media;
4. proceed with a single-image hypothesis;
5. state which link-derived facts could not be verified.
