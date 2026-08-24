# Roblox Luau Code Patterns

Use these patterns when implementing a proper server-client communication layer.

## Remote folder bootstrap

Create remotes in Studio or from a server bootstrap. Remotes must live somewhere both client and server can see, usually `ReplicatedStorage/Remotes`.

```lua
-- ServerScriptService/Server/Net/CreateRemotes.server.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local remotes = ReplicatedStorage:FindFirstChild("Remotes")
if not remotes then
    remotes = Instance.new("Folder")
    remotes.Name = "Remotes"
    remotes.Parent = ReplicatedStorage
end

local function ensure(className: string, name: string)
    local existing = remotes:FindFirstChild(name)
    if existing then
        assert(existing.ClassName == className, (`{name} must be a {className}`))
        return existing
    end

    local instance = Instance.new(className)
    instance.Name = name
    instance.Parent = remotes
    return instance
end

ensure("RemoteEvent", "ActionRequest")
ensure("RemoteEvent", "StateChanged")
ensure("RemoteFunction", "GetInitialState")
ensure("UnreliableRemoteEvent", "AimUpdate")
```

## Shared schema module

Keep this client-safe. Do not put secret prices, hidden damage multipliers, or anti-cheat thresholds here if they should not be public.

```lua
-- ReplicatedStorage/Shared/NetSchema.lua
local NetSchema = {}

NetSchema.Actions = {
    BuyItem = "BuyItem",
    EquipItem = "EquipItem",
    FireWeapon = "FireWeapon",
    UseAbility = "UseAbility",
    Interact = "Interact",
}

NetSchema.StateEvents = {
    InventoryPatch = "InventoryPatch",
    CombatEvent = "CombatEvent",
    RoundState = "RoundState",
    Error = "Error",
}

return NetSchema
```

## Server action router

```lua
-- ServerScriptService/Server/Net/ActionRouter.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local NetSchema = require(ReplicatedStorage.Shared.NetSchema)
local ActionRequest = ReplicatedStorage.Remotes.ActionRequest
local StateChanged = ReplicatedStorage.Remotes.StateChanged

local RateLimiter = require(script.Parent.RateLimiter)
local Validators = require(script.Parent.Validators)

local EconomyService = require(script.Parent.Parent.Services.EconomyService)
local InventoryService = require(script.Parent.Parent.Services.InventoryService)
local CombatService = require(script.Parent.Parent.Services.CombatService)

local handlers = {}

handlers[NetSchema.Actions.BuyItem] = function(player, payload)
    local ok, result = EconomyService:BuyItem(player, payload.itemId)
    if ok then
        StateChanged:FireClient(player, NetSchema.StateEvents.InventoryPatch, result)
    else
        StateChanged:FireClient(player, NetSchema.StateEvents.Error, { code = result })
    end
end

handlers[NetSchema.Actions.EquipItem] = function(player, payload)
    local ok, result = InventoryService:EquipItem(player, payload.itemId)
    if ok then
        StateChanged:FireClient(player, NetSchema.StateEvents.InventoryPatch, result)
    end
end

handlers[NetSchema.Actions.FireWeapon] = function(player, payload)
    local ok, result = CombatService:FireWeapon(player, payload)
    if ok then
        StateChanged:FireAllClients(NetSchema.StateEvents.CombatEvent, result)
    end
end

ActionRequest.OnServerEvent:Connect(function(player, action, payload)
    if type(action) ~= "string" or type(payload) ~= "table" then
        return
    end

    local handler = handlers[action]
    if not handler then
        return
    end

    if not RateLimiter:Allow(player, action) then
        return
    end

    local valid = Validators.ValidateActionPayload(action, payload)
    if not valid then
        return
    end

    handler(player, payload)
end)

return true
```

## Rate limiter

```lua
-- ServerScriptService/Server/Net/RateLimiter.lua
local Players = game:GetService("Players")

local RateLimiter = {}

local limits = {
    BuyItem = { rate = 2, burst = 4 },
    EquipItem = { rate = 6, burst = 10 },
    FireWeapon = { rate = 12, burst = 20 },
    UseAbility = { rate = 4, burst = 8 },
    Interact = { rate = 5, burst = 10 },
}

local buckets = {}

function RateLimiter:Allow(player: Player, action: string): boolean
    local cfg = limits[action]
    if not cfg then
        return false
    end

    local playerBuckets = buckets[player]
    if not playerBuckets then
        playerBuckets = {}
        buckets[player] = playerBuckets
    end

    local now = os.clock()
    local bucket = playerBuckets[action]
    if not bucket then
        bucket = { tokens = cfg.burst, t = now }
        playerBuckets[action] = bucket
    end

    local elapsed = now - bucket.t
    bucket.t = now
    bucket.tokens = math.min(cfg.burst, bucket.tokens + elapsed * cfg.rate)

    if bucket.tokens < 1 then
        return false
    end

    bucket.tokens -= 1
    return true
end

Players.PlayerRemoving:Connect(function(player)
    buckets[player] = nil
end)

return RateLimiter
```

## Validators

```lua
-- ServerScriptService/Server/Net/Validators.lua
local Validators = {}

local MAX_STRING = 64
local MAX_VECTOR_MAGNITUDE = 100000

local function isFiniteNumber(n)
    return type(n) == "number" and n == n and n > -math.huge and n < math.huge
end

local function isSafeString(s)
    return type(s) == "string" and #s > 0 and #s <= MAX_STRING
end

local function isSafeVector3(v)
    return typeof(v) == "Vector3" and v.Magnitude <= MAX_VECTOR_MAGNITUDE
end

function Validators.ValidateActionPayload(action: string, payload: table): boolean
    if action == "BuyItem" or action == "EquipItem" then
        return isSafeString(payload.itemId)
    end

    if action == "FireWeapon" then
        return isSafeString(payload.weaponId)
            and isSafeVector3(payload.origin)
            and isSafeVector3(payload.direction)
            and payload.direction.Magnitude > 0.9
            and payload.direction.Magnitude < 1.1
            and (payload.shotId == nil or isSafeString(tostring(payload.shotId)))
    end

    if action == "UseAbility" then
        return isSafeString(payload.abilityId)
    end

    if action == "Interact" then
        return typeof(payload.target) == "Instance"
    end

    return false
end

return Validators
```

## Economy service pattern

```lua
-- ServerScriptService/Server/Services/EconomyService.lua
local EconomyService = {}

local SERVER_ITEM_DEFS = {
    speed_boost = { price = 100 },
    double_jump = { price = 250 },
}

local function getProfile(player)
    -- Replace with the project's profile/session service.
    return _G.Profiles and _G.Profiles[player]
end

function EconomyService:BuyItem(player: Player, itemId: string)
    local item = SERVER_ITEM_DEFS[itemId]
    if not item then
        return false, "UNKNOWN_ITEM"
    end

    local profile = getProfile(player)
    if not profile then
        return false, "NO_PROFILE"
    end

    if profile.coins < item.price then
        return false, "NOT_ENOUGH_COINS"
    end

    profile.coins -= item.price
    profile.inventory[itemId] = (profile.inventory[itemId] or 0) + 1

    return true, {
        coins = profile.coins,
        itemId = itemId,
        count = profile.inventory[itemId],
    }
end

return EconomyService
```

## Combat service pattern

```lua
-- ServerScriptService/Server/Services/CombatService.lua
local Workspace = game:GetService("Workspace")

local CombatService = {}

local WEAPONS = {
    blaster = {
        damage = 20,
        range = 300,
        cooldown = 0.15,
    },
}

local lastFire = {}

local function getCharacterRoot(player)
    local character = player.Character
    if not character then
        return nil
    end
    return character:FindFirstChild("HumanoidRootPart")
end

function CombatService:FireWeapon(player: Player, payload: table)
    local weapon = WEAPONS[payload.weaponId]
    if not weapon then
        return false, "UNKNOWN_WEAPON"
    end

    local now = os.clock()
    local key = player.UserId .. ":" .. payload.weaponId
    if lastFire[key] and now - lastFire[key] < weapon.cooldown then
        return false, "COOLDOWN"
    end
    lastFire[key] = now

    local root = getCharacterRoot(player)
    if not root then
        return false, "NO_CHARACTER"
    end

    local origin = payload.origin
    local direction = payload.direction.Unit

    -- Sanity check: origin must be close to the character.
    if (origin - root.Position).Magnitude > 12 then
        origin = root.Position
    end

    local params = RaycastParams.new()
    params.FilterType = Enum.RaycastFilterType.Exclude
    params.FilterDescendantsInstances = { player.Character }

    local result = Workspace:Raycast(origin, direction * weapon.range, params)
    local hitHumanoid = nil
    local hitPlayer = nil

    if result and result.Instance then
        local model = result.Instance:FindFirstAncestorOfClass("Model")
        hitHumanoid = model and model:FindFirstChildOfClass("Humanoid")
        if hitHumanoid then
            hitPlayer = game:GetService("Players"):GetPlayerFromCharacter(model)
            -- Add team/safe-zone checks here before damaging.
            hitHumanoid:TakeDamage(weapon.damage)
        end
    end

    return true, {
        weaponId = payload.weaponId,
        shooterUserId = player.UserId,
        origin = origin,
        direction = direction,
        hitPosition = result and result.Position or (origin + direction * weapon.range),
        hitUserId = hitPlayer and hitPlayer.UserId or nil,
        damage = hitHumanoid and weapon.damage or 0,
        shotId = payload.shotId,
    }
end

return CombatService
```

## Client input pattern

```lua
-- StarterPlayerScripts/Client/InputController.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")

local NetSchema = require(ReplicatedStorage.Shared.NetSchema)
local ActionRequest = ReplicatedStorage.Remotes.ActionRequest

local InputController = {}

function InputController:BuyItem(itemId: string)
    ActionRequest:FireServer(NetSchema.Actions.BuyItem, {
        itemId = itemId,
    })
end

function InputController:FireWeapon(weaponId: string, origin: Vector3, direction: Vector3)
    local shotId = tostring(os.clock())

    -- Immediate local feedback belongs here: recoil, muzzle flash, local tracer.
    ActionRequest:FireServer(NetSchema.Actions.FireWeapon, {
        weaponId = weaponId,
        origin = origin,
        direction = direction.Unit,
        shotId = shotId,
    })
end

return InputController
```

## Client state/effects pattern

```lua
-- StarterPlayerScripts/Client/StateController.lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local NetSchema = require(ReplicatedStorage.Shared.NetSchema)
local StateChanged = ReplicatedStorage.Remotes.StateChanged

local StateController = {}
StateController.Inventory = {}
StateController.Coins = 0

StateChanged.OnClientEvent:Connect(function(eventName, payload)
    if eventName == NetSchema.StateEvents.InventoryPatch then
        if payload.coins then
            StateController.Coins = payload.coins
        end
        if payload.itemId and payload.count then
            StateController.Inventory[payload.itemId] = payload.count
        end
        -- Update UI here or signal a local BindableEvent.

    elseif eventName == NetSchema.StateEvents.CombatEvent then
        -- Play approved shared tracer/hit effects here.

    elseif eventName == NetSchema.StateEvents.Error then
        -- Show non-sensitive user-facing error.
    end
end)

return StateController
```

## Unreliable cosmetic stream pattern

```lua
-- Client: send latest-value-wins aim data at 10 Hz, not every frame.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local AimUpdate = ReplicatedStorage.Remotes.AimUpdate
local accumulator = 0

RunService.RenderStepped:Connect(function(dt)
    accumulator += dt
    if accumulator < 0.1 then
        return
    end
    accumulator = 0

    AimUpdate:FireServer({
        yaw = currentYaw,
        pitch = currentPitch,
    })
end)
```

```lua
-- Server: validate and relay only if needed.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local AimUpdate = ReplicatedStorage.Remotes.AimUpdate

AimUpdate.OnServerEvent:Connect(function(player, payload)
    if type(payload) ~= "table" then
        return
    end
    if type(payload.yaw) ~= "number" or type(payload.pitch) ~= "number" then
        return
    end

    -- Clamp to reasonable display values.
    local yaw = math.clamp(payload.yaw, -math.pi, math.pi)
    local pitch = math.clamp(payload.pitch, -1.4, 1.4)

    -- Relay cosmetic data only. Do not use this as hit truth.
    AimUpdate:FireAllClients(player.UserId, { yaw = yaw, pitch = pitch })
end)
```
