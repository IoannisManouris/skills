# Multi-Device Implementation Report — [Experience / Feature]

**Date:** [YYYY-MM-DD]
**Implementer:** [name/agent]
**Roblox documentation verified:** [date or “not rechecked”]
**Build/commit:** [identifier]

## 1. Executive summary

[What was implemented or audited, which device families are ready, and the most important remaining risk.]

## 2. Scope and assumptions

### Target families

- [ ] Keyboard and mouse
- [ ] Touch phone/tablet
- [ ] Gamepad
- [ ] TV/large-display presentation
- [ ] VR

### Preserved systems

- [Default PlayerModule movement/camera or named custom systems]

### Explicit exclusions

- [Unsupported mechanic, orientation, hardware, local multiplayer, hand tracking, etc.]

## 3. Architecture

```text
[Project-specific input → actions/contexts → controllers → server flow]
```

### Files added

| Path | Purpose |
|---|---|
|  |  |

### Files changed

| Path | Change |
|---|---|
|  |  |

### Files removed/deprecated

| Path | Reason |
|---|---|
|  |  |

## 4. Action map

| Context | Action | Type | Keyboard/mouse | Touch | Gamepad | VR | Authority |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

### Analog tuning

| Action | Deadzone | Curve | Sensitivity/max speed | Smoothing | Notes |
|---|---:|---|---|---|---|
|  |  |  |  |  |  |

### Rebinding/conflict policy

[Policy or “not in scope.”]

## 5. Context and state transitions

| Game/UI state | Enabled contexts | Sink/priority behavior | Cleanup/return behavior |
|---|---|---|---|
| Gameplay |  |  |  |
| Menu/modal |  |  |  |
| Text entry |  |  |  |
| Vehicle/build/VR |  |  |  |

## 6. UI navigation map

| Screen | Entry focus | Directional rules | Scroll behavior | Cancel/back | Pointer/touch path | VR path |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

### Responsive/accessibility behavior

- safe-area policy:
- large-display/TV policy:
- preferred text size:
- transparency/high contrast:
- reduced motion:
- hover/drag alternatives:
- subtitles/haptics/other alternatives:

## 7. Device-specific decisions

### Keyboard/mouse

[Mouse lock, sensitivity, wheel, shortcuts, layout-aware prompts, text/IME.]

### Touch

[Button placement, thumb zones, target sizing, multi-touch, gestures, camera, aim assistance, orientation.]

### Gamepad and TV

[Common mapping, deadzones/curves, camera/aim assist, focus, prompts, disconnect, haptics, couch readability.]

### VR

[Detection/tracking, locomotion/turning, recenter, grab/use, UI, comfort, seated/standing, networking.]

## 8. Prompt and hot-swap behavior

[How `PreferredInput`, capability changes, controller connection, VR state, touch visibility, selection, cursor, and prompts are handled.]

## 9. Client/server authority

| Semantic request | Client sends | Server validates/derives | Result/replication |
|---|---|---|---|
|  |  |  |  |

### Security tests

- [ ] malformed payload
- [ ] spam/rate limit
- [ ] wrong state/context
- [ ] impossible range/target/destination
- [ ] ownership/entitlement
- [ ] server-derived price/damage/reward
- [ ] duplicate/replay where applicable

## 10. Test evidence

| ID | Family/configuration | Scenario | Evidence level | Result | Notes/issue |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

Evidence levels: Code-inspected, Automated, Studio-emulated, Physical-device, Live-session, Not tested.

### Hot-swap results

| From → To | State | Result | Notes |
|---|---|---|---|
|  |  |  |  |

### Physical hardware tested

[List exact device/controller/headset/display configurations, or state none.]

## 11. Performance and network observations

| Metric/area | Before | After | Evidence | Notes |
|---|---|---|---|---|
| Client frame time/FPS |  |  |  |  |
| Memory/lifecycle |  |  |  |  |
| Remote calls/payload |  |  |  |  |
| Mobile thermal/battery |  |  |  |  |
| VR frame-time stability |  |  |  |  |

Do not fabricate values. Use “Not measured” where appropriate.

## 12. Defects and remaining work

| Severity | Family/path | Issue | User impact | Recommended fix |
|---|---|---|---|---|
|  |  |  |  |  |

## 13. Release declaration

| Family | Status | Basis | Conditions/limitations |
|---|---|---|---|
| Keyboard/mouse | Ready / Conditional / Unsupported |  |  |
| Touch | Ready / Conditional / Unsupported |  |  |
| Gamepad | Ready / Conditional / Unsupported |  |  |
| TV/large display | Ready / Conditional / Unsupported |  |  |
| VR | Ready / Conditional / Unsupported |  |  |

## 14. Validation

```text
python scripts/validate_action_map.py [map]
[project lint/typecheck/tests]
[Studio test modes used]
```

**Known unverified APIs or unavailable hardware:** [list]
