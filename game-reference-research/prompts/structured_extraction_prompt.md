# Structured Extraction Prompt

Use this to convert a source into a reusable research record.

```text
Extract the supplied source into the schema exactly.

Rules:
- Do not invent missing fields.
- Use null when unknown.
- Separate observed evidence from interpretation.
- Label each claim as observed, confirmed, inferred, or unknown.
- Assign confidence: high, medium, low, or unknown.
- Add anything uncertain to needs_human_check.
- Do not create code, new game ideas, asset prompts, or implementation plans.

Schema:
{
  "reference_id": "",
  "title": "",
  "source_type": "user_provided|direct_play|official|platform_store|database|professional|academic|curated_archive|community|unknown",
  "source_owner": "",
  "url": "",
  "date_published": "",
  "date_accessed": "",
  "game_titles": [],
  "platforms": [],
  "research_domains": [],
  "claims": [
    {
      "claim": "",
      "claim_type": "observed|confirmed|inferred|unknown",
      "confidence": "high|medium|low|unknown",
      "supporting_evidence_ids": []
    }
  ],
  "evidence_items": [
    {
      "evidence_id": "",
      "description": "",
      "source_location": "",
      "evidence_kind": "screenshot|video_timestamp|store_text|official_doc|code|user_note|database_field|article|other"
    }
  ],
  "rights_or_license": "",
  "confidence": "high|medium|low|unknown",
  "needs_human_check": []
}
```
