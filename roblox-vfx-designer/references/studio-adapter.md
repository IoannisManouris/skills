# Studio capability adapter

Contents: discovery; safe live workflow; uploads; offline fallback.

## Discover, do not assume

Inspect the host's actual tool definitions. The current official
[Studio MCP documentation](https://create.roblox.com/docs/studio/mcp) describes data
model exploration, script editing, Luau execution, image handling, and playtests.
Providers and versions differ, so treat documented tool names as discovery hints,
not as a guaranteed schema. Never fabricate calls to tools absent from the host.

Required capabilities by task:

| Task | Minimum capability | Fallback |
|---|---|---|
| Match environment | Read relevant instances plus view images | User screenshots / project art metadata, with uncertainty |
| Patch live place | Authorized edit-model write | Luau files and explicit import paths |
| Trigger/render effect | Client play-mode execution and capture | Studio test instructions; no claim it was rendered |
| Import textures | Authorized image importer/upload | Local prepared files and manifest with null IDs |
| Inspect reference clip | Accessible playback/frames | Request accessible excerpt; don't infer exact motion from title |
| Verify multiplayer | Multiple test clients/server observation | Mark multiplayer verification not run |

## Safe editing transaction

Select the intended Studio/place. A remote code environment is not the same machine
as the user's Studio. Keep the actual place identifier in every tool call where the
schema requires it. If several places are open and context cannot resolve the target,
ask instead of modifying the first one returned.

Read first; checkpoint relevant scripts/properties using the existing source-control
or backup workflow. Inspect in bounded batches. Never recursively dump all script
source or enormous trees into context. Stage changes under an effect namespace.
Avoid executing untrusted asset scripts; inspect isolated assets before insertion.

Use Edit mode for persistent construction and Client play mode for cosmetics.
A runtime-created object may disappear when play mode ends; do not confuse that with
a saved asset. Run only necessary tests and restore test camera, selection, and
presentation settings. Don't publish the experience unless publishing was requested.

## Image transfer

Some Studio adapters accept public HTTP image URLs for upload; some accept only
local files or host-specific image handles. Consult the actual contract. A tool
that stores a reference-image handle is not necessarily a texture upload tool.
Preserve the returned mapping and owner/permissions; verify rendered use. For local
or transformed images, use a supported file uploader or ordinary Studio import.
Do not put a private image on a public host without separate authorization.

## No Studio connection

Continue with a code/artifact deliverable when useful. Record which evidence came
from project files versus screenshots versus assumptions. Supply creation/import
instructions and a smoke-test entry point. Do not silently choose a new art style
or claim environment matching from an unseen place.

The optional `SceneProbe.luau` is read-only and bounded, but its part-frequency
palette is only a diagnostic hint. Visible, lit screen area is what the player sees.
