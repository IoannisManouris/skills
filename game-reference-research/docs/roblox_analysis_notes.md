# Roblox-Specific Analysis Notes

Use this when the reference is a Roblox game.

## Roblox evidence to look for

- Game page title, description, age guidelines, max players, genre tags
- Badges
- Gamepasses
- Developer products if visible
- Social links/group ownership
- Update logs
- Thumbnails/icons
- In-game UI screenshots
- First-session flow
- Mobile control layout
- Loading screens
- Shop/reward screens
- Round/level/teleport behavior
- Save/progression behavior

## Roblox systems to consider

- ServerScriptService server logic
- ReplicatedStorage modules/remotes/assets
- StarterPlayerScripts client input/camera/UI control
- StarterGui screens
- Workspace map/physics/interactables
- CollectionService tags
- Attributes for state/config
- RemoteEvents and RemoteFunctions
- DataStores / OrderedDataStores
- MemoryStoreService for queues or temporary state
- MessagingService for cross-server announcements
- TeleportService for reserved/private server flows
- MarketplaceService for purchases
- TweenService for UI/polish
- RunService for per-frame client effects
- Physics constraints/network ownership for physics-heavy games

## Roblox client/server inference rules

Use **server-side likely** when:

- Currency changes persist.
- Purchases or rewards are validated.
- Damage, wins, level clears, or inventory persist.
- Anti-exploit integrity matters.

Use **client-side likely** when:

- The effect is purely visual.
- Camera shake, UI animation, local particles, trails, or input display are involved.
- Responsiveness matters but server authority is not required.

Use **shared/replicated likely** when:

- State must be visible to all players.
- Modules/configs are probably shared by server and client.
- UI needs replicated data from the server.

Never claim exact script names or folder structures unless supplied or visible.

## Roblox report additions

For Roblox full reports, include:

- Mobile UX/readability
- Gamepass/developer-product surface if visible
- Save/progression assumptions
- Anti-exploit risk notes
- Physics/network ownership notes if relevant
- Retention loop and replayability
- Social loop and multiplayer role structure
