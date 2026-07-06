# Server-Client Decision Matrix

Use this reference when deciding where each game system should live.

## Quick rule

- Server: truth, value, fairness, persistence, private logic, shared world decisions.
- Client: input, UI, camera, local feedback, visual smoothness, player-specific presentation.
- Shared: constants, public config, action names, harmless type definitions.
- Split: systems that need instant feel but must still be fair.

## Detailed matrix

| Feature | Server responsibility | Client responsibility | What crosses network | Never trust from client |
|---|---|---|---|---|
| Buttons/menu/shop UI | Validate action and mutate state | Render UI and send intent | `BuyItem {itemId}`; `InventoryPatch` | price, new balance, ownership |
| Hotbar/equip | Check ownership and equip rules | Render selected slot and animations | `EquipItem {itemId}`; `EquippedPatch` | claim that item is owned |
| Currency | Own balance and rewards | Display balance | balance patches | final balance, reward amount |
| Inventory | Own item table | Display and local sorting | inventory patches | full replacement table |
| Saves | Load/save profile | None except display | initial state/patches | profile object to save |
| Combat | Cooldowns, ammo, hit approval, damage | Input, aim UI, recoil, local animation | fire/attack command; combat result | damage, target validity, cooldown done |
| Melee | Range/angle/team checks | Swing animation and local effects | attack command; hit result | touched target as final truth |
| Hitscan guns | Server ray/sanity check and damage | Crosshair, recoil, muzzle flash, optional predicted tracer | origin/direction/shotId; result | hit player, damage, wall penetration |
| Projectile guns | Spawn/validate authoritative projectile or hit | Cosmetic predicted projectile | fire intent; spawn/hit event | client physics hit result alone |
| Abilities | Cooldown truth, resource cost, final effect | Input, cast bar, local anticipation | ability command; result/correction | ability available, final target list |
| Movement | Sanity validation, server-owned constraints when competitive | Character control feel, camera | occasional requests/state if custom movement | impossible positions/speeds |
| Vehicles | Ownership assignment and rules | Local driving feel if owner | input or seat state; result | race finish, collision damage, speed records |
| NPC AI | Targeting, pathing, damage | Render animations/effects | replicated NPC state or result events | client target/damage claims |
| Round system | Timer truth, state transitions, winners | HUD countdown and transitions | `RoundStatePatch` | winner, time remaining, score |
| Matchmaking/teleport | Queue truth and teleport decisions | Menu and queue status display | join/leave queue command; status | team assignment or destination |
| Leaderboards | Server stat updates | Display | stat patches/Roblox replication | stat increments from client |
| VFX/SFX | Broadcast effect descriptor if shared | Play actual effect locally | `{effectId, position, targetId}` | gameplay outcome from effect |
| Camera/screen shake | Usually none | Fully client-owned | maybe effect descriptor | camera state as proof of action |
| Aim/look cosmetics | Optional relay/rate validation | Send throttled angles | unreliable yaw/pitch | aim as proof of hit by itself |
| Building/placement | Validate ownership, bounds, cost, overlap | Preview ghost and placement UI | placement request; approved placement | final CFrame without bounds checks |

## Split-system pattern

Use split ownership for actions where waiting for the server would feel bad but trusting the client would be unsafe.

Example: weapon firing

1. Client detects input instantly.
2. Client plays local animation, sound, recoil, and predicted tracer.
3. Client sends `FireWeapon {weaponId, origin, direction, shotId, clientTime?}`.
4. Server validates equipped weapon, ammo, cooldown, alive state, range, direction sanity, and raycast/hit result.
5. Server applies damage and broadcasts result.
6. Client reconciles if server denied or adjusted the shot.

## Server-only containers

Use server-only containers for:

- economy rules
- combat rules
- anti-cheat thresholds
- secret configs/API keys
- server-only modules
- DataStore code
- authoritative templates that clients should not copy
- hidden map/objective logic

## Replicated/shared containers

Use replicated/shared containers only for:

- RemoteEvents/RemoteFunctions
- public constants
- public item display metadata
- client-safe config
- module types/helpers that contain no secrets and no authority

## Questions to ask during review

- Can the client create or destroy value here?
- Can the client hurt another player here?
- Can the client skip progression here?
- Can the client reveal private information here?
- Is this only visual/audio/UI for one player?
- Could this be sent as an ID/intent instead of a full state table?
- Does this need reliable delivery, or is latest-value-wins enough?
- Can Roblox automatic replication or StreamingEnabled solve this without custom remotes?
