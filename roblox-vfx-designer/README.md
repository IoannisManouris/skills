# roblox-vfx-designer

An installable Agent Skill for designing and implementing Roblox VFX from a written
style, an existing Studio environment, an image/video reference, or a documented
combination of these inputs. Version 1.0.0; sources checked 2026-09-28.

This is an agent instruction/toolkit package, not a trained model, a Roblox Studio
plugin, an MCP server, or a collection of finished Roblox effects. It does not grant
Studio, network, filesystem, or upload permissions by itself.

## Install

Extract the ZIP. Keep the `roblox-vfx-designer` directory intact; `SKILL.md` must be
at that directory's root, not nested inside a second same-named directory.

**Codex, current local discovery locations:** put the directory at
`~/.agents/skills/roblox-vfx-designer/` for your user, or
`<repo>/.agents/skills/roblox-vfx-designer/` for a project. On Windows the user path
is typically `%USERPROFILE%\.agents\skills\roblox-vfx-designer\`.

**Claude Code:** use `~/.claude/skills/roblox-vfx-designer/` or
`<repo>/.claude/skills/roblox-vfx-designer/`.

Other Agent Skills hosts: use that host's documented skill import/location. Do not
assume all hosts import ZIPs or use the same directory. Reload/restart the host if
it does not discover the new directory. Verify it appears in the host's skill list.
Avoid installing multiple copies with the same name in overlapping discovery paths.

The frontmatter description advertises Roblox VFX tasks. Codex's
`agents/openai.yaml` explicitly permits implicit invocation. Host/model routing is
still probabilistic; it cannot be guaranteed for every agent. Test the supplied
trigger cases. An explicit Codex fallback is `$roblox-vfx-designer`.

Sources: [Agent Skills spec](https://agentskills.io/specification),
[OpenAI skill discovery](https://learn.chatgpt.com/docs/build-skills),
[Claude Code skills](https://code.claude.com/docs/en/skills).

## Live Studio connection

Use an authorized Studio integration already available to the agent. Current
[official Studio MCP instructions](https://create.roblox.com/docs/studio/mcp)
describe enabling the server and connecting supported clients. This ZIP deliberately
does not install servers, change account permissions, or hardcode a third-party tool
schema. An agent running on a remote Linux/SSH machine is not automatically
connected to Studio on your Windows computer; an explicitly configured, trusted
bridge/host connection is still needed. Do not expose a local Studio control port
publicly just to make the skill work.

Without Studio tools the skill can create Luau and integration files, but cannot
truthfully inspect a live place, upload art, or confirm a rendered result.

## Example requests

“Create a restrained dusty landing impact matching this place.”

“Make an icy shield with clean geometric edges, no bloom, readable on mobile.”

“Use this clip's spiral timing and silhouette, but match our forest's materials.”

“Fix this beam's orientation and make the particles stop cleanly when cancelled.”

“Create a low-poly blocky explosion, not an anime shockwave.”

## What's included

`SKILL.md` is the lean entry point. `references/` contains targeted implementation
and artistic guides, a media reference index, and source/provenance records.
`templates/luau/` contains original client-effect building blocks.
`templates/specs/` supplies structured planning and asset schemas.
`assets/library-catalog.json` describes reusable texture sources.
`scripts/` contains optional acquisition, image-preparation, and validation helpers.
`evals/` supplies positive/negative routing cases and behavior/test cases.

No copyrighted reference clips, proprietary game assets, or unverified asset IDs
are redistributed. No third-party texture binaries are bundled: source pages were
verified, but binary downloading in the build environment failed. The catalog and
fetch helper allow an agent with authorized internet access to obtain them later.
This distinction is deliberate and is recorded in the build provenance.

## Optional Python tools

The skill itself does not require Python. The fetch helper uses the standard
library. Image preparation needs Pillow; the package validator needs PyYAML and
jsonschema. Install dependencies only with the host's normal user authorization:

```bash
python -m pip install -r scripts/requirements.txt
python scripts/validate_package.py
python -m unittest discover -s evals -p 'test_*.py' -v
python scripts/asset_fetch.py list
```

The fetch helper can discover download links without downloading images. Download
requires a CC0/public-domain evidence file written after reviewing the original
asset page. It never uploads to Roblox. Review external files before any import.

## Verification and research provenance

See `evals/build-validation.json` for checks actually run. Luau templates require
Roblox Studio testing: this package was not executed inside Studio and carries no
claim of visual, device-performance, or multi-agent routing certification.

The conversation contains the requested Deep Research brief but no accessible
completed report or attachment. This version therefore uses separately verified
primary sources; it does not claim the missing report was incorporated. The
`references/research-provenance.md` procedure explains how to merge that report
when its actual contents are available, without overwriting verified API facts.

## Rights

Original package instructions and code are provided under MIT (`LICENSE`). External
assets keep their original licenses. Default texture acquisition is CC0/public
domain only; CC-BY, royalty-free, marketplace, and custom-license material require a
separate explicit decision and are not silently substituted. CC0 is not a guarantee
that an uploader owned everything or that trademark/privacy rights disappear.
