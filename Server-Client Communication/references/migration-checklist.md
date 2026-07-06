# Migration Checklist for Mixed Server/Client Projects

Use this when an existing Roblox project has scripts in the wrong place or remotes that trust the client.

## Phase 0: Audit

Create a table with these columns:

| System | Current location | Current remote(s) | Current trust issue | Correct owner | Migration action |
|---|---|---|---|---|---|

Look for:

- LocalScripts changing currency, inventory, XP, wins, damage, cooldowns, or saved data.
- Server scripts waiting on `InvokeClient()` for gameplay decisions.
- Remotes named broadly like `UpdateData`, `SetValue`, `Damage`, `GiveReward`, or `AdminAction`.
- Client sending full state tables instead of small intents.
- Server accepting client-sent prices, damage, CFrames, or target lists without checks.
- Server-only logic stored in `ReplicatedStorage`.
- Per-frame RemoteEvent firing.

## Phase 1: Persistence and economy first

Move these to server services:

- profile loading/saving
- currency mutation
- item grants/removals
- purchase receipt processing
- XP/level progression
- reward grants

Delete or disable client code that directly edits these values.

Correct pattern:

1. Client sends request: `BuyItem { itemId }`.
2. Server loads server item config and profile.
3. Server validates price, ownership, distance/context if relevant.
4. Server mutates profile.
5. Server sends patch to client.

## Phase 2: Inventory and equipment

Server owns:

- actual inventory table
- equip rules
- item ownership
- stack counts
- loadout validity

Client owns:

- hotbar UI
- drag/drop visuals
- selection highlight
- local equip animations after approval or optimistic display with correction

## Phase 3: Combat and interactions

Replace client-authored results with server-approved results.

Bad:

```lua
DamageRemote:FireServer(targetHumanoid, 50)
```

Better:

```lua
ActionRequest:FireServer("FireWeapon", {
    weaponId = "blaster",
    origin = muzzleWorldPosition,
    direction = cameraDirection,
    shotId = shotId,
})
```

Server validates and computes the hit.

For interactions:

- Check the target instance is in the expected collection/folder/tag.
- Check the player is near enough.
- Check the player is in a valid state.
- Check cooldowns and ownership.
- Apply server result.

## Phase 4: Physics and network ownership

Inventory all unanchored parts that matter to gameplay.

Set server ownership (`SetNetworkOwner(nil)`) when:

- physics affects damage, wins, currency, or progression
- object is shared/competitive
- object can be used to grief or exploit
- accurate server collision is more important than local smoothness

Allow client/network ownership when:

- object is cosmetic or low impact
- object is controlled by one player and server validates final outcomes
- responsiveness matters and cheating impact is limited

## Phase 5: Presentation cleanup

Move to client:

- UI animations
- hover/click effects
- camera shake
- recoil visuals
- local-only sounds
- local particles
- mobile button display/positioning
- local prediction/tracers
- cutscenes that do not change server truth

The server should send only compact descriptors for shared effects:

```lua
StateChanged:FireAllClients("PlayEffect", {
    effectId = "ExplosionSmall",
    position = position,
})
```

## Phase 6: Network usage pass

Reduce bandwidth by:

- removing per-frame remotes
- batching small patches
- sending IDs instead of large objects/tables
- using deltas instead of full state
- using `UnreliableRemoteEvent` for latest-value-wins cosmetic streams
- relying on Roblox replication for Instances where appropriate
- enabling/tuning StreamingEnabled for large worlds
- avoiding `FireAllClients` when only one player needs the data

## Phase 7: Security pass

For every remote, answer:

- What is the action allowlist?
- What exact schema is accepted?
- What is the per-player rate limit?
- What context must be true?
- What server state is checked?
- What server state is mutated?
- What patch/result is sent back?
- What exploit would happen if this remote accepted lies?

## Phase 8: Testing

Test with Studio server/client mode:

- Confirm client-only UI/VFX does not appear on server unless intended.
- Confirm server-owned state changes replicate correctly.
- Call remotes manually with bad payloads and confirm rejection.
- Simulate spam and confirm rate limiting.
- Test high ping by delaying local prediction/correction logic if possible.
- Test StreamingEnabled areas where instances may not exist on the client yet.
- Test leaving/rejoining for save correctness.

## Final report template

When reporting the refactor, use this template:

```markdown
## Server/client ownership changes

| System | Before | After | Why |
|---|---|---|---|

## Remote contract

| Remote | Direction | Payload | Validation | Result |
|---|---|---|---|---|

## Security improvements

- ...

## Network usage improvements

- ...

## Testing performed

- ...

## Remaining risks

- ...
```
