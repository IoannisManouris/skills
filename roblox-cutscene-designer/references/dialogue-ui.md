# Dialogue and UI integration

Read only when the user asks for on-screen dialogue, subtitles, speech text, or
equivalent narrative text. Keep `text_dialogue_requested` false otherwise. A
voice-only request should not silently acquire subtitles. If "dialogue" is
ambiguous about its medium, resolve that narrow choice before adding visible text.

## Reuse the existing dialogue presentation

Search relevant UI instances, scripts/modules, and templates for the game's
dialogue system. Inspect StarterGui, the runtime PlayerGui when available, and
relevant shared UI/controller locations. Look for dialogue, dialog, conversation,
subtitle, speaker, and typewriter behavior, not just a particular instance name.
Read how the UI is opened, populated, advanced, and closed; view it when possible.

Use its supported controller or component interface. Reuse its speaker styling,
line progression, localization, input prompts, and accessibility conventions.
Avoid cloning another dialogue stack or changing the UI for unrelated scenes.
If the existing system is temporarily inaccessible, report what must be checked
instead of declaring it absent and replacing it.

## If no dialogue UI exists, match the observed game UI

Inspect representative visible menus, HUD, panels, and buttons. Record the useful
style properties: fonts and text hierarchy, palette, contrast, spacing, corners,
borders, shadows, icon treatment, panel placement, and transition timing.

Build a small dialogue component consistent with those observations. Support the
needed speaker/line data, wrapping, progression, and cancellation, with adequate
contrast and screen-safe placement. Match the game's keyboard, touch, and gamepad
conventions where those devices are supported. Keep reading speed appropriate to
the scene and respect existing text scaling/localization choices.

If the game has no usable UI reference, choose a restrained style fitting the
scene and state that assumption. Do not claim it matches a style you did not see.

## Integrate and inspect

Use supplied lines faithfully or write lines only within the requested creative
scope. Time them to the scene beats and approved animation markers. Do not add
voice generation just because text dialogue was requested.

Verify readability, long-line wrapping, input progression, layer ordering, and
cleanup when skipping or cancelling. Restore any UI state the cutscene changed.
