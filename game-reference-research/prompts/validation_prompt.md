# Validation Prompt

Use this after drafting a report.

```text
Audit this game reference research report.

Check for:
- Unsupported factual claims
- Assumptions presented as facts
- Missing source/evidence log items
- Missing confidence labels
- Clone-like or IP-risky wording
- Decompilation/ripping/copying risk
- Unsupported technical architecture claims
- Overly vague statements such as "good UI" or "fun gameplay"
- Missing unknowns/limitations
- Sections that accidentally become a build plan

Return:
1. Blocking issues
2. Warnings
3. Missing evidence
4. Claims that need lower confidence
5. Suggested wording fixes
6. Final pass/fail decision
```
