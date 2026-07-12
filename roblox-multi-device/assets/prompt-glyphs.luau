--!strict
-- PromptGlyphs.lua
-- Converts semantic binding metadata into current-device prompt presentation.

local UserInputService = game:GetService("UserInputService")

export type PromptPresentation = {
    image: string?,
    text: string,
    keyCode: Enum.KeyCode?,
}

export type BindingPresentation = {
    keyCode: Enum.KeyCode?,
    label: string?,
    image: string?,
}

local PromptGlyphs = {}

local function safeImageForKeyCode(keyCode: Enum.KeyCode): string?
    local ok, result = pcall(function()
        return UserInputService:GetImageForKeyCode(keyCode)
    end)

    if ok and type(result) == "string" and result ~= "" then
        return result
    end
    return nil
end

local function safeStringForKeyCode(keyCode: Enum.KeyCode): string?
    local ok, result = pcall(function()
        return UserInputService:GetStringForKeyCode(keyCode)
    end)

    if ok and type(result) == "string" and result ~= "" then
        return result
    end
    return nil
end

function PromptGlyphs.fromBinding(binding: BindingPresentation, fallbackText: string?): PromptPresentation
    local keyCode = binding.keyCode

    if binding.image and binding.image ~= "" then
        return {
            image = binding.image,
            text = binding.label or fallbackText or (keyCode and keyCode.Name) or "",
            keyCode = keyCode,
        }
    end

    if keyCode then
        local image = safeImageForKeyCode(keyCode)
        local text = binding.label
            or safeStringForKeyCode(keyCode)
            or fallbackText
            or keyCode.Name

        return {
            image = image,
            text = text,
            keyCode = keyCode,
        }
    end

    return {
        image = nil,
        text = binding.label or fallbackText or "",
        keyCode = nil,
    }
end

function PromptGlyphs.forPreferredInput(
    bindingSet: { [string]: BindingPresentation },
    preferredInput: Enum.PreferredInput,
    fallbackText: string?
): PromptPresentation
    local key: string
    if preferredInput == Enum.PreferredInput.Touch then
        key = "touch"
    elseif preferredInput == Enum.PreferredInput.Gamepad then
        key = "gamepad"
    else
        key = "keyboardMouse"
    end

    local binding = bindingSet[key]
        or bindingSet.keyboardMouse
        or bindingSet.gamepad
        or bindingSet.touch

    if not binding then
        return {
            image = nil,
            text = fallbackText or "",
            keyCode = nil,
        }
    end

    return PromptGlyphs.fromBinding(binding, fallbackText)
end

return PromptGlyphs
