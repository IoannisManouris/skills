# Evaluation and Grading Guide

Use `evals/evals.json` to compare a clean run **with** this skill against a run without it or against the previous skill version. Use fresh context and the same project fixture for both runs.

## Grading principles

For every assertion:

- mark **PASS** only with concrete output or code evidence
- mark **FAIL** when the output merely mentions the concept without implementing or specifying it
- quote the file/path, code behavior, table row, or report section that proves the grade
- do not infer physical-device testing from an emulator result
- do not accept a generic checklist where the prompt asks for implementation
- do not accept separate device-specific mechanic logic when the assertion requires one semantic path

Suggested result shape:

```json
{
  "assertion_results": [
    {
      "text": "The implementation uses semantic InputActions/controllers rather than scattered key checks.",
      "passed": true,
      "evidence": "ReplicatedStorage/Inputs contains Interact and PrimaryAction; ActionRouter binds both, and old InputBegan listeners were removed from Combat.client.lua."
    }
  ],
  "summary": {
    "passed": 1,
    "failed": 0,
    "total": 1,
    "pass_rate": 1.0
  }
}
```

## High-value failure conditions

Fail the relevant assertion when the output:

- hard-codes hardware keys in core gameplay controllers
- says `TouchEnabled` or gamepad presence is the one active-input mode
- updates prompts only at spawn
- adds a second mobile/controller combat path
- converts analog input to digital before the mechanic
- applies deadzones in multiple layers without a deliberate model
- uses mouse click/hover/drag as the only UI path
- sets `SelectedObject` without focus restoration or scrolling behavior
- uses deprecated `IsTenFootInterface()` or `UserInputService.VREnabled` in new code
- rotates/smooths the VR headset pose
- accepts client-authored damage, price, reward, teleport, or placement truth
- declares a device family supported from code review or Studio emulation alone

## Human review dimensions

Assertions do not cover everything. A human should also compare:

- architecture clarity and fit with the supplied project
- amount of unnecessary churn
- feel/tuning assumptions and whether they are labeled
- focus and touch layout quality
- VR comfort and physical reach
- accessibility quality
- completeness of code and teardown/lifecycle behavior
- honesty of limitations
- token/time overhead versus baseline

## Trigger evaluation

`trigger-evals.json` follows the Agent Skills trigger-query pattern. Run each query multiple times in the target agent client and observe whether `roblox-multi-device` loads.

- should-trigger query: target trigger rate greater than 0.5
- should-not-trigger query: target trigger rate less than 0.5
- use at least three runs per query for an initial estimate
- keep a held-out set when optimizing the description

The negative cases intentionally include nearby Roblox work, networking, optimization, and UI styling so the description does not activate for every Roblox prompt.

## Iteration loop

1. Run every eval with the current skill and baseline.
2. Grade each assertion with evidence.
3. Review both outputs blind when possible.
4. Inspect execution traces for wasted steps, missed references, or ambiguous defaults.
5. Generalize fixes into `SKILL.md`, a focused reference, template, or validator.
6. Keep `SKILL.md` lean; remove instructions that do not improve results.
7. Re-run all evals in a new iteration directory.
8. Update the changelog when behavior or packaging changes.
