# Migration and Audit Guide

Read this reference when converting an existing Roblox project from scattered key checks, ContextActionService bindings, custom touch buttons, mouse-only UI, or device branches into the multi-device architecture.

The migration goal is behavioral equivalence first, then device completion. Do not replace every control at once without a rollback path.

## 1. Audit deliverables

Produce these artifacts before major edits:

1. current input/API inventory
2. semantic action inventory
3. context/state map
4. UI task/navigation inventory
5. device support gap matrix
6. client/server authority findings
7. migration stages and rollback points
8. test plan

Use `assets/action-map.template.json`, `assets/project-layout.template.md`, and `assets/implementation-report.template.md`.

## 2. Repository discovery

Search client, shared, and server code for:

```text
UserInputService
ContextActionService
InputBegan
InputChanged
InputEnded
TouchStarted
TouchMoved
TouchEnded
MouseButton1Click
MouseButton2Click
MouseEnter
MouseLeave
KeyCode
UserInputType
GetMouse
MouseBehavior
MouseDeltaSensitivity
GuiService.SelectedObject
NextSelection
Selectable
Activated
VRService
VREnabled
RemoteEvent
RemoteFunction
FireServer
InvokeServer
```

Also inspect instances/configuration in Studio or serialized project files:

- `InputContext`, `InputAction`, `InputBinding`
- `StarterPlayer` movement/camera modes
- `ScreenGui.ScreenInsets` and safe-area settings
- touch buttons and default `TouchGui` interactions
- custom PlayerModule/camera/control forks
- selection properties and focus visuals
- prompt/glyph asset tables
- controller/VR model scripts

Search is discovery, not proof. Read each call site in context.

## 3. Build the current-control table

For every existing binding or gesture, record:

| File/object | Hardware input | Behavior | State/context | UI/gameplay | Server message | Cleanup |
|---|---|---|---|---|---|---|
| Combat.client.lua | MouseButton1 | fire | alive/gameplay | gameplay | FireWeapon | InputEnded |
| MobileButtons.Fire | Activated | fire | touch HUD | gameplay | FireWeapon | button release |
| Inventory | ButtonB | close | menu | UI | none | context disable |

Look for duplicate implementations of the same intent. Duplicates often disagree on cooldown, targeting, animation, or server payload.

## 4. Classify findings

### Direct hardware coupling

Examples:

- gameplay module checks `Enum.KeyCode.E`
- inventory module checks `ButtonB`
- mobile button directly calls a remote

Target: one semantic `Interact`, `Cancel`, or `Fire` action routed to one controller path.

### Presentation coupling

Examples:

- HUD displays keyboard prompt at spawn only
- `TouchEnabled` hides gamepad UI permanently
- selected focus is set only when a console flag is true

Target: presentation listens to `PreferredInput` and capability/profile changes.

### Context leakage

Examples:

- firing while typing
- jump/dodge while inventory is open
- menu cancel triggers crouch
- vehicle controls remain enabled after exit

Target: explicit input contexts and centralized transitions.

### UI incompleteness

Examples:

- mouse click is the only activation path
- hover contains essential information
- drag-only inventory
- hidden objects stay selectable
- no default selected object

Target: `Activated`, focus map, alternatives, and lifecycle cleanup.

### Authority flaw

Examples:

- mobile button tells server final damage
- client sends purchase price/balance
- VR client sets authoritative teleport position

Target: semantic intent and server revalidation.

## 5. Choose the migration boundary

Recommended boundary:

```text
legacy hardware adapters ──┐
new InputAction events ────┼──► semantic action router ─► existing mechanic controller
UI Activated events ───────┘
```

During migration, adapt old sources into the same semantic entry point. Do not keep separate mechanic implementations by device.

### One binding owner

For each semantic action, name exactly one active input owner per context. If IAS and CAS coexist temporarily:

- IAS should be the target for new cross-platform maps
- legacy CAS may remain behind a compatibility adapter
- disable/remove old direct listeners as their actions migrate
- never bind the same hardware/action pair in both stacks without a documented precedence reason
- add temporary diagnostics to detect duplicate invocation

## 6. Staged migration

### Stage 0 — Baseline and rollback

- capture current behavior and defects
- create a branch/commit checkpoint
- record input settings and instance hierarchy
- add lightweight action invocation logging in development
- define support scope and critical user journeys

Exit gate: current behavior can be reproduced and rollback is possible.

### Stage 1 — Semantic action catalog

- name actions by intent
- assign contexts and `InputActionType`
- identify analog versus boolean semantics
- record device bindings, prompts, authority, and exclusions
- validate the JSON action map

Exit gate: every existing behavior maps to an action or is intentionally removed.

### Stage 2 — Action router

- introduce one action router/controller interface
- redirect existing keyboard/mouse path first or the best-understood path
- preserve public mechanic APIs
- ensure press/hold/release behavior matches baseline
- centralize cleanup

Exit gate: one device path works through semantic actions without duplicate invocation.

### Stage 3 — Context controller

- define gameplay/menu/text/vehicle/build/spectator contexts
- centralize enable/disable operations
- add LIFO modal/overlay behavior
- sink only required keys
- test default Roblox movement/camera interactions

Exit gate: state transitions do not leak actions.

### Stage 4 — Device completion

Add bindings and adaptations in a controlled order:

1. keyboard/mouse parity and text focus
2. gamepad mechanics and focus navigation
3. touch layout/multi-touch and gesture alternatives
4. TV/large-display presentation
5. VR locomotion/interactions if in scope

Exit gate: action-map coverage and UI task matrix pass per family.

### Stage 5 — Prompt/device profile

- centralize capabilities and `PreferredInput`
- make prompts action-based
- update touch visibility, cursor, selection, and layout on change
- test hot-swap in all major states

Exit gate: no spawn-only input assumptions remain.

### Stage 6 — Authority and performance

- replace device-specific remote payloads with semantic contracts
- validate rate/state/ownership/range/server-derived values
- remove per-frame remote/input allocations
- throttle only justified transient streams
- profile target hardware

Exit gate: invalid requests fail safely and performance evidence is recorded.

### Stage 7 — Remove legacy paths

- delete migrated direct listeners/CAS bindings/adapters
- remove obsolete prompt tables/device booleans
- remove dead touch buttons or duplicate UI code
- remove deprecated API calls
- run repository-wide search again

Exit gate: each action has one maintained path and no required legacy fallback remains.

## 7. Refactoring patterns

### Direct key check → semantic action

Before:

```lua
UserInputService.InputBegan:Connect(function(input, processed)
    if not processed and input.KeyCode == Enum.KeyCode.E then
        interact()
    end
end)
```

After conceptually:

```lua
actionRouter:bind("Interact", {
    pressed = function()
        interactionController:tryInteract()
    end,
})
```

The `Interact` `InputAction` owns keyboard, gamepad, touch, and VR bindings.

### Separate mobile mechanic → shared action

Before:

```lua
mobileFireButton.Activated:Connect(function()
    fireRemote:FireServer(target, damage)
end)
```

After:

```lua
-- The touch binding links to the same Fire InputAction/UIButton.
actionRouter:bind("Fire", {
    pressed = function()
        weaponController:beginFire()
    end,
    released = function()
        weaponController:endFire()
    end,
})
```

The weapon controller builds a semantic request; the server derives damage.

### Spawn-only prompt → device profile

Before:

```lua
prompt.Text = UserInputService.TouchEnabled and "Tap" or "Press E"
```

After:

```lua
local function renderPrompt(snapshot)
    promptRenderer:render("Interact", snapshot.preferredInput)
end

deviceProfile.Changed:Connect(renderPrompt)
renderPrompt(deviceProfile:getSnapshot())
```

### Mouse-only button → cross-input button

Before:

```lua
button.MouseButton1Click:Connect(activate)
```

After:

```lua
button.Activated:Connect(activate)
```

Then add selection/navigation and touch target checks.

### Scattered context flags → centralized context stack

Before:

```lua
isInMenu = true
canShoot = false
UserInputService.MouseBehavior = Enum.MouseBehavior.Default
-- several unrelated scripts change their own booleans
```

After:

```lua
contextController:pushLayer("Inventory", { "MenuContext" })
uiFocusController:open(inventoryRoot, defaultItem)
```

The screen's close path pops the same layer and restores focus/cursor policy.

## 8. Custom PlayerModule and camera forks

Treat custom control/camera forks as high-risk migration areas:

- determine why the fork exists
- compare against current Roblox default behavior/APIs
- identify changes to movement, camera, shift lock, touch controls, VR, and respawn lifecycle
- preserve only product-required differences
- avoid copying a current default module unless the project accepts ongoing maintenance
- test reserved/default controls and CoreGui interactions

Do not replace default movement/camera simply to unify inputs. Roblox already supplies familiar cross-device defaults for standard character control.

## 9. UI audit procedure

For each `ScreenGui` or world-space UI:

1. List every user task.
2. Identify entry/exit and modal hierarchy.
3. Mark interactive, disabled, hidden, and dynamic objects.
4. Verify `Activated` or semantic action path.
5. Build/fix focus graph.
6. add non-hover and non-drag alternatives.
7. verify scrolling/virtualization.
8. verify safe insets/aspect ratios/text size/localization.
9. test pointer, keyboard, gamepad, touch, and VR paths in scope.
10. document remaining exclusions.

Do not mark a screen complete because its first button can receive selection.

## 10. Prompt migration

Inventory all prompt sources:

- text such as `[E]`
- image IDs for controller buttons
- touch labels/icons
- tutorial screenshots
- world prompts
- tooltips and loading hints

Replace with action IDs and a centralized renderer. Handle:

- active `PreferredInput`
- rebind updates
- controller glyph/string lookup
- touch short labels
- VR role labels
- localized action text
- missing image fallback

Tutorial imagery may need device-neutral diagrams or multiple variants.

## 11. Rebinding migration

Do not expose rebinding until the action layer can safely handle it. Define:

- rebindable actions
- reserved/system inputs
- per-context conflicts
- modifier/chord rules
- gamepad and keyboard schemes
- persistence version/schema
- reset-to-default
- inaccessible/unbound prevention
- prompt invalidation

The server may save settings, but the client owns local binding presentation and input response. Validate saved data and migrate old versions.

## 12. Server contract audit

For each input-triggered remote, record:

| Remote/action | Client sends | Server derives/checks | Response |
|---|---|---|---|
| FireWeapon | weapon ID, origin/aim descriptor, sequence ID | equipped state, ammo, rate, origin bounds, hit/damage | approved shot/hit/state patch |
| Interact | interactable ID, kind | existence, range, LOS, state, permission | result/state patch |
| Teleport | destination descriptor | surface, clearance, bounds, cooldown | approved relocation/error |

Replace hardware-specific remotes such as `MobileFire` and `ControllerInteract` with semantic contracts when possible.

## 13. Diagnostics during migration

Useful development-only instrumentation:

- log semantic action name, state, value, context, and source binding
- count invocation per frame/action to catch duplicates
- display enabled context stack
- display `PreferredInput` and capabilities
- draw selected UI object and explicit navigation links
- display touch IDs/owners for multi-touch debugging
- display VR tracking availability and interaction candidate
- count remote frequency/payload estimates

Remove or gate verbose diagnostics before release.

## 14. Regression strategy

Build a small “golden journey” set before migration:

- spawn and move/camera
- interact with a world object
- use core combat/action loop
- open/operate/close inventory
- enter/exit vehicle/build mode
- pause/settings/text entry
- death/respawn

Run after every stage on at least the primary device path. Add the new family to the journey once its bindings/UI are implemented.

## 15. Audit severity guide

- **Critical** — client-authoritative reward/damage/purchase/teleport; unrecoverable input; dangerous VR camera behavior.
- **High** — promised family cannot complete a core mechanic/screen; input leaks through modal/text; stuck held action.
- **Medium** — misleading prompt, broken focus edge, poor safe-area/readability, duplicate low-impact invocation.
- **Low** — polish inconsistency with a complete alternative.

Prioritize authority and blocked paths before visual polish.

## 16. Rollback design

Each stage should be reversible:

- keep commits small and scoped
- put adapters behind configuration during transition
- avoid data-schema destruction until new settings migration is proven
- preserve old bindings long enough for parity testing, but never enable duplicate paths simultaneously
- document which instances/scripts must be restored
- keep server remote compatibility only as long as required and validate both versions

Remove rollback code after the new path is stable; permanent dual stacks become defects.

## 17. Audit report outline

```markdown
# Multi-device migration audit

## Scope and support contract
## Current architecture
## Action inventory and duplicates
## Context/state findings
## UI navigation findings
## Device gaps
## Server-authority findings
## Deprecated/stale API findings
## Migration stages
## Files to add/change/remove
## Test matrix
## Risks, rollback, and exclusions
```

## 18. Completion checklist

- [ ] Repository and Studio instance searches are complete.
- [ ] Existing controls are mapped to semantic actions.
- [ ] Duplicate device-specific mechanic paths are identified.
- [ ] Context leaks, UI gaps, and authority flaws are ranked.
- [ ] A staged migration with rollback gates exists.
- [ ] One semantic router and one context owner are the target.
- [ ] Default Roblox controls are preserved unless replacement is justified.
- [ ] Prompts and device presentation are centralized.
- [ ] Legacy listeners/adapters are removed after parity.
- [ ] Cross-device tests and physical-device gaps are reported honestly.
