# Roblox Multi-Device Project Layout

Adapt this layout to the project's package manager and conventions. Preserve existing architecture when it is coherent; the important boundary is semantic actions → controllers, not exact folder names.

```text
ReplicatedStorage
├── Inputs
│   ├── GameplayContext                 -- InputContext
│   │   ├── Interact                    -- InputAction (Bool)
│   │   │   ├── KeyboardInteract       -- InputBinding
│   │   │   ├── GamepadInteract        -- InputBinding
│   │   │   ├── TouchInteract          -- InputBinding linked to UIButton
│   │   │   └── VRInteract             -- InputBinding when applicable
│   │   ├── PrimaryAction               -- InputAction (Bool)
│   │   └── OpenInventory               -- InputAction (Bool)
│   ├── MenuContext                     -- InputContext, higher priority/sink as needed
│   │   ├── MenuConfirm                 -- InputAction (Bool)
│   │   └── MenuCancel                  -- InputAction (Bool)
│   ├── TextEntryContext                -- InputContext
│   ├── VehicleContext                  -- InputContext, optional
│   ├── BuildContext                    -- InputContext, optional
│   └── VRContext                       -- InputContext, optional
│
├── Shared
│   ├── Input
│   │   ├── ActionIds.lua               -- semantic IDs only
│   │   ├── ActionCatalog.lua           -- public binding/prompt metadata
│   │   └── DeviceConstants.lua         -- non-secret constants
│   └── Net
│       └── ActionContract.lua          -- public semantic request schema
│
└── Remotes
    ├── ActionRequest                    -- RemoteEvent
    └── StateChanged                     -- RemoteEvent

StarterPlayer
└── StarterPlayerScripts
    ├── Main.client.lua
    └── Client
        ├── Input
        │   ├── ActionRouter.lua
        │   ├── ContextController.lua
        │   ├── DeviceProfile.lua
        │   ├── PromptGlyphs.lua
        │   └── RawAdapters
        │       ├── PointerAdapter.lua   -- only when actions do not model the need
        │       ├── GestureAdapter.lua
        │       └── VRPoseAdapter.lua
        ├── Controllers
        │   ├── CharacterActionController.lua
        │   ├── InteractionController.lua
        │   ├── CombatController.lua
        │   ├── InventoryController.lua
        │   ├── VehicleController.lua
        │   ├── BuildController.lua
        │   ├── CameraController.lua
        │   └── VRController.lua
        ├── UI
        │   ├── UIFocusController.lua
        │   ├── PromptRenderer.lua
        │   ├── ResponsiveLayoutController.lua
        │   ├── TouchControlsController.lua
        │   └── ModalStack.lua
        └── Accessibility
            └── InputSettingsController.lua

StarterGui
└── MainUI
    ├── HUD
    │   ├── Prompts
    │   └── Actions                    -- touch buttons live in known, safe regions
    ├── Inventory
    ├── Settings
    └── Shared
        └── SelectionImage             -- project focus style

ServerScriptService
├── Main.server.lua
└── Server
    ├── Net
    │   ├── ActionRouter.lua
    │   ├── Validators.lua
    │   └── RateLimiter.lua
    └── Services
        ├── InteractionService.lua
        ├── CombatService.lua
        ├── InventoryService.lua
        ├── VehicleService.lua
        └── PlayerSettingsService.lua
```

## Dependency rules

```text
InputBindings / raw adapters
          │
          ▼
InputActions + ContextController
          │
          ▼
ActionRouter
          │
          ▼
Client controllers
    ├── local camera/UI/VFX/haptics
    └── semantic server requests
                    │
                    ▼
            server validators/services
```

- Mechanics import action IDs or subscribe through the router; they do not inspect hardware keys.
- UI imports prompt/focus/layout services; it does not call combat/economy remotes directly.
- `DeviceProfile` affects presentation and alternatives, not authoritative rules.
- Server code never needs to know whether a valid semantic action came from touch, gamepad, keyboard, or VR unless the product has a carefully justified device-specific rule.
- Shared code contains no secret prices, anti-cheat thresholds, private templates, or authoritative state.
- Default Roblox character controls/camera remain untouched unless the mechanic requires replacement.

## Context state example

```text
Gameplay                    Base: GameplayContext
Inventory open              Base: GameplayContext; overlay: MenuContext (sinks selected inputs)
Text field focused          Base: GameplayContext; overlays: MenuContext, TextEntryContext
Vehicle entered             Base: VehicleContext; optional shared global actions
Pause/settings modal        Highest overlay: MenuContext/PauseContext
VR enabled                  Add VRContext only for VR-specific actions; generic gameplay remains semantic
```

Do not scatter context writes. One controller owns transitions and applies them atomically.

## Installation mapping

The `.luau` files in this skill's `assets/` directory are templates, not a Rojo package. Copy/rename them into the project's chosen locations, update require paths, connect the project's actual UI/actions, and remove demonstration callbacks before release.
