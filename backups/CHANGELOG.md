# Prompt version changelog

## 2026-09-20_housekeeping-extract-field-and-deprecations

**Housekeeping only, no prompt or behavioural change: extract_field ends a value at the next line-initial '**' rather than any '**', so inline bold can no longer truncate a field; game.py drops deprecated datetime.utcnow() while keeping the exact naive timestamp shape; providers.py loses an unused import; assemble_bio's docstring corrected to say its display order is deliberately not CHARACTER_FIELDS order.**

Previous: 2026-09-20_addressing-drop-character-3

---

## 2026-09-20_addressing-drop-character-3

**Stops offering character 3 in the addressing prompt -- the valet has left the room and is not addressable, so a '3' reply was rejected as invalid, burning three retries before defaulting to 'both reply'. Also states the one-digit contract that simulator's now-strict parse enforces.**

Previous: 2026-09-13_experiment-no-examples

---

## 2026-09-13_experiment-no-examples

**EXPERIMENT: strips every concrete example, positive and negative, from the three character-generation prompts. All 24 rules survive, stated abstractly, with nothing nameable left for the model to lift. Tests whether the examples were widening the space or collapsing it -- two were provably leaking into output (the name Sanne, and 'need to be needed'). Restore the previous version if this performs worse.**

Previous: 2026-09-13_pronoun-rule-scoped-to-life-characters

---

## 2026-09-13_pronoun-rule-scoped-to-life-characters

**Scopes the no-pronoun rule to people from the character's own life only. The previous version banned they/them globally, which made the final field -- about the two strangers in the room, whom the character has not met and cannot name -- impossible to write, and accounted for 4 of each character's pronoun count.**

Previous: 2026-09-12_deaths-by-decision-and-no-pronouns

---

## 2026-09-12_deaths-by-decision-and-no-pronouns

**Bans accidental deaths outright -- if chance had to cooperate it is an accident -- and replaces them with deaths that follow from a decision the character made knowing the risk. Removes the v5 wording that was causing the driving deaths. Also bans third-person pronouns in every field so the bio names people instead, since a pronoun read aloud in the room points at whoever is present.**

Previous: 2026-09-12_one-relationship-and-a-death-that-belongs-to-it

---

## 2026-09-12_one-relationship-and-a-death-that-belongs-to-it

**Moves Who you loved / Who you hated above Cause of Death so the death can be caused by a person who exists, makes both fields describe the same person seen from two sides, requires the death and the sin to belong to that relationship, and stops the want from ending in a confession clause.**

Previous: 2026-09-12_single-call-generation

---

## 2026-09-12_single-call-generation

**Collapses character generation from four calls per character to one. All eleven fields now come back in a single response, ordered so each is written knowing the ones above it. Adds randomised NAME_ORIGINS to break the model's name prior, merges the four anti-duplication blocks into one showing character 1's full bio, and adds cross-field consistency rules so the prose cannot invent a second death.**

Previous: 2026-09-12_aristotelian-action-and-unity

---

## 2026-09-12_aristotelian-action-and-unity

**Applies Aristotle's Poetics to character generation (load-bearing facts, plausibility for all characters, peripeteia in the sin, trait must be demonstrated, consistently-inconsistent) and fixes the five defects found in the previous version's run: name collisions, prose template, death narrowing to omission, residual mood-writing in the refusal, and copied trait examples.**

Previous: 2026-08-29_stanislavski-given-circumstances

---

## 2026-08-29_stanislavski-given-circumstances

**Grounded character generation in Stanislavski's system (An Actor Prepares): usability + name-the-thing rules in the shared setup prompt, cause of death must stem from the character's own choices, loved/hated people get wants of their own, Life prose rewritten as given circumstances (facts, not mood), self-told sin must be checkable against established facts, and the want must protect the refusal.**

Previous: 2026-08-23_relational-sin-anchors

---

## 2026-08-23_relational-sin-anchors

**Add explicit relational fields to character generation: each character now generates a named 'Who you loved' and 'Who you hated' during the Life call, required to be from different relation-categories between the two characters (anti-duplication). The Sin call is rewired to anchor the True reason for damnation on one of these two people instead of an abstract professional/systemic failing -- direct response to today's human eval feedback (both character-level, pair-level, and session-level evals flagged 'too much emphasis on line of work'). Also swapped MODEL_* from Qwen2.5-7B-Instruct to Qwen3-8B since the old model's only working HF provider (Together) stopped serving it.**

Previous: 2026-08-09_baseline

---

## 2026-08-09_baseline

**Initial snapshot of the current prompts, assembly structure, and config (models/temperatures/max_tokens) before any further prompt tuning.**

Previous: (none)

---

