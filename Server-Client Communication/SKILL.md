---
name: server-client-communication
description: Use this skill when designing, auditing, refactoring, or coding Roblox server-client communication, RemoteEvents, RemoteFunctions, UnreliableRemoteEvents, client/server responsibility splits, server authority, replication, network ownership, hit validation, UI/VFX/client prediction, or when moving game systems into the correct server or client layer.
compatibility: Agent Skills-compatible coding agents. Optimized for Roblox Luau projects, but includes general multiplayer networking principles.
metadata:
  display_name: Server-Client Communication
  version: "1.0.0"
  domain: roblox-networking
---

# Server-Client Communication Skill

Use this skill to design, review, or rewrite Roblox networking so the server owns truth and the client owns responsiveness. The default architecture is:

> Clients request, predict, and render. Servers validate, decide, persist, and replicate approved results.

## Activation examples

Use this skill for requests such as:

- "set up proper remotes"
- "move this to the server/client"
- "secure this RemoteEvent"
- "reduce network usage"
- "make hit detection safe"
- "why is this exploitable?"
- "restructure my Roblox project"
- "should this run on the client or server?"
- "make this smoother without trusting the client"

Do not use this skill for unrelated Roblox work unless the task involves networking, replication, RemoteEvents, server authority, client prediction, or ownership boundaries.

## Core decision rule

Before writing code, classify every feature using this test:

1. If a malicious client could create value, bypass rules, damage fairness, reveal secrets, save fake data, or affect other players by lying, the server must own the result.
2. If the feature only changes how one player sees, hears, aims, animates, or feels the game, the client should usually own it.
3. If the feature needs both responsiveness and fairness, split it: client predicts/renders immediately, server validates and corrects/replicates the authoritative outcome.

When uncertain, prefer server authority for gameplay truth and client-side rendering for presentation.

## Required workflow

For any Roblox server-client task, follow this workflow:

1. Inventory the involved systems: UI, input, camera, VFX, SFX, animation, combat, inventory, economy, saving, physics, NPCs, matchmaking, leaderboards, projectiles, abilities, round state, or map state.
2. Decide the owner for each system: server, client, shared constants, or split.
3. Define the network contract using compact messages:
   - Client -> Server: command/intent only.
   - Server -> Client(s): approved result, state patch, or replicated event.
   - Client <-> Server high-rate cosmetic stream: only if noncritical, throttled, and preferably unreliable.
4. Add validation at every public remote boundary:
   - type/schema
   - action allowlist
   - rate limit
   - ownership/entitlement
   - distance/context
   - cooldown/state preconditions
   - server-derived cost/damage/reward
   - replay/duplicate protection when needed
5. Keep private logic and templates server-only.
6. Test in Studio with separate server/client views and confirm no client can author authoritative results.
7. Report exactly what moved, why it moved, what crosses the network, and what validation was added.

Read `references/decision-matrix.md` when deciding ownership across many systems.
Read `references/code-patterns.md` when implementing Roblox Luau modules/remotes.
Read `references/migration-checklist.md` when refactoring an existing mixed-up project.

## Ownership model

Use this split unless project-specific constraints prove otherwise:

| System | Owner | Network payload |
|---|---|---|
| UI, HUD, menus, shop screens | Client | Server sends state patches; client sends purchase/use commands |
| Camera, crosshair, input, mobile buttons | Client | Usually none; send only gameplay commands |
| Local VFX/SFX, tweening, screen shake | Client | Server broadcasts small effect descriptors only when other players must see it |
| Currency, inventory, purchases, rewards | Server | Client sends intent; server sends approved patch |
| DataStore/profile saving | Server | No client-authored save state |
| Damage, cooldown truth, ammo truth, team checks | Server | Client sends attack/fire intent; server computes result |
| NPC AI/pathfinding/game mode rules | Server | Server replicates state or result events |
| Cosmetic aim/look stream | Client-originated, server-relayed if needed | Throttled angles/IDs, not critical state |
| Character movement feel | Client/Roblox replication with server validation | Server sanity checks impossible movement |
| Competitive physics/projectiles | Server or split | Client may predict visuals; server confirms hit/result |
| Noncritical physics cosmetics | Client/network ownership acceptable | Do not base rewards/damage on unverified client physics |

## Remote design rules

Prefer a small, explicit remote surface instead of many ad-hoc remotes with inconsistent validation.

Recommended remote classes:

- `ActionRequest` (`RemoteEvent`): client commands to server.
- `StateChanged` (`RemoteEvent`): server-approved patches/events to client(s).
- `GetInitialState` (`RemoteFunction`): low-frequency client -> server initial snapshot only.
- `AimUpdate` or `CosmeticStream` (`UnreliableRemoteEvent`): noncritical, high-rate, latest-value-wins data.

Avoid `RemoteFunction:InvokeClient()` from the server for gameplay because the server can yield or fail if the client does not return correctly. Use asynchronous RemoteEvents instead.

## Payload rules

Send the smallest payload that preserves meaning.

Good payloads:

```lua
ActionRequest:FireServer("BuyItem", { itemId = "speed_boost" })
ActionRequest:FireServer("FireWeapon", { origin = origin, direction = direction, shotId = shotId })
StateChanged:FireClient(player, "InventoryPatch", { coins = 120, itemId = "speed_boost", count = 1 })
```

Bad payloads:

```lua
ActionRequest:FireServer("SetCoins", 999999)
ActionRequest:FireServer("DealDamage", targetPlayer, 100)
ActionRequest:FireServer("ReplaceInventory", entireClientInventoryTable)
ActionRequest:FireServer("IAmAllowedToBuy", itemId, price, newBalance)
```

Never let the client send final truth for money, inventory, damage, XP, cooldown completion, ownership, round wins, or save data.

## Standard project layout

Use this as the default target structure:

```text
ReplicatedStorage
  Remotes
    ActionRequest          -- RemoteEvent
    StateChanged           -- RemoteEvent
    AimUpdate              -- UnreliableRemoteEvent, optional
    GetInitialState        -- RemoteFunction, low frequency only
  Shared
    NetSchema              -- action names, payload shape comments, shared constants only
    PublicConfig           -- non-secret config only

ServerScriptService
  Main.server.lua
  Server
    Net
      ActionRouter.lua
      RateLimiter.lua
      Validators.lua
    Services
      PlayerStateService.lua
      CombatService.lua
      EconomyService.lua
      InventoryService.lua
      RoundService.lua
      SaveService.lua

ServerStorage
  PrivateModules
  Templates
  SecretConfig

StarterPlayer
  StarterPlayerScripts
    Main.client.lua
    Client
      InputController.lua
      UIController.lua
      EffectsController.lua
      CameraController.lua
      PredictionController.lua
```

Do not put secret logic, private server modules, economy authority, combat authority, anti-cheat rules, DataStore code, or hidden templates in `ReplicatedStorage`.

## Implementation rules

When writing or refactoring code:

- Put authoritative state mutations in server services, not in LocalScripts.
- Put input collection, UI rendering, camera, screen shake, and immediate local feedback in client controllers.
- Put shared action names and non-secret config in shared modules.
- Validate every remote call even if the UI "should never" send invalid data.
- Use allowlisted action names instead of executing arbitrary strings or paths from the client.
- Rate-limit by player and action, not globally only.
- Never trust client-provided prices, damage, positions, cooldown completion, or ownership claims without server recomputation/sanity checks.
- For high-frequency updates, throttle manually. Do not fire remotes every frame.
- Use server-to-client result events instead of synchronous server waits.
- Prefer patches/deltas over full-state replication when possible.
- Clean up per-player rate-limit/profile state on `Players.PlayerRemoving`.

## Feature-specific guidance

### UI and menus

Client owns layout, buttons, animations, hover states, local sorting/filtering, and screen transitions. Server owns whether an action is allowed and the resulting state.

Pattern: button click -> `ActionRequest("BuyItem", {itemId})` -> server validates -> `StateChanged("InventoryPatch", patch)`.

### Combat and abilities

Client may show immediate animation, recoil, sound, cooldown ghost, and predicted projectile trail. Server owns cooldown truth, ammo truth, hit approval, damage, team checks, range checks, and final result broadcast.

Pattern: input -> local feedback -> command to server -> server validates -> result broadcast -> client reconciles if needed.

### Projectiles

For competitive projectiles, server owns hit results. Client can spawn cosmetic local projectiles immediately, then server sends the approved projectile/hit event. If using physical projectiles with network ownership, do not grant rewards or damage solely from client-owned physics without server checks.

### Inventory/economy/purchases

Server owns all balances, item grants, ownership checks, and purchase receipts. Client owns only display and requests.

### Data saving

Server-only. The client never sends the profile to save. The client can request an action that mutates server profile state; the server saves its own profile object.

### NPCs and round state

Server owns NPC AI, target selection, round timers, win/loss conditions, map objective truth, and match state. Clients render UI, VFX, SFX, and local effects from replicated state.

### Network ownership and physics

Use network ownership for responsiveness/performance, not as a trust boundary. If physics affects scoring, damage, currency, progression, or PvP, the server must validate the result or own the object.

### StreamingEnabled

When large worlds or many instances create replication pressure, prefer Roblox instance streaming and careful model streaming settings over custom remote spam. Code must tolerate objects being unavailable on the client and use `WaitForChild`, tags, or streaming-aware discovery where appropriate.

## Security checklist

For every public RemoteEvent or RemoteFunction, ensure:

- [ ] Unknown action names are rejected.
- [ ] Payload type and required fields are checked.
- [ ] Strings are length-limited and IDs are allowlisted.
- [ ] Numbers are finite and within reasonable bounds.
- [ ] Instances sent by client are checked for ancestry, ownership, and relevance.
- [ ] Player is alive/in correct state/near enough when required.
- [ ] Cooldowns and rates are enforced server-side.
- [ ] Cost/damage/reward is computed from server config.
- [ ] Result is applied only on the server.
- [ ] Client receives only the minimum patch/result it needs.

## Output requirements for the agent

When responding to a user with a networking refactor or setup, include:

1. A short ownership summary: what belongs on server, client, and shared.
2. The remote contract: remote names, direction, payloads, and validation.
3. Full code modules when the user asks for code, not tiny disconnected snippets.
4. Notes on what was intentionally not replicated.
5. Security and network-usage tradeoffs.
6. Testing steps for Studio server/client mode.

For large refactors, propose or apply a staged migration:

1. Persistence/economy.
2. Inventory/entitlements.
3. Combat/interactions.
4. Physics/network ownership.
5. UI/VFX/SFX/camera cleanup.

## Gotchas

- A LocalScript can call a RemoteEvent with any payload. UI restrictions do not protect the server.
- Anything in `ReplicatedStorage`, `StarterPlayer`, `StarterGui`, `Workspace`, or other replicated containers should be treated as visible to exploiters.
- Remote names are not secrets. Security comes from server validation, not obscurity.
- Server-side `InvokeClient()` is fragile for gameplay. Prefer async result events.
- Client-side cooldown UI is only presentation. Server cooldown is the real gate.
- Client raycasts can be useful for feel, but server must confirm important hits.
- Full-state updates are easier but often waste bandwidth. Prefer small patches.
- Unreliable remotes are for latest-value-wins data, never purchases, damage, saves, or inventory.
- Network ownership improves physics responsiveness but expands the cheat surface if trusted.
