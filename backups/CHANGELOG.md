# Prompt version changelog

## 2026-08-23_relational-sin-anchors

**Add explicit relational fields to character generation: each character now generates a named 'Who you loved' and 'Who you hated' during the Life call, required to be from different relation-categories between the two characters (anti-duplication). The Sin call is rewired to anchor the True reason for damnation on one of these two people instead of an abstract professional/systemic failing -- direct response to today's human eval feedback (both character-level, pair-level, and session-level evals flagged 'too much emphasis on line of work'). Also swapped MODEL_* from Qwen2.5-7B-Instruct to Qwen3-8B since the old model's only working HF provider (Together) stopped serving it.**

Previous: 2026-08-09_baseline

---

## 2026-08-09_baseline

**Initial snapshot of the current prompts, assembly structure, and config (models/temperatures/max_tokens) before any further prompt tuning.**

Previous: (none)

---

