# 2026-09-13_pronoun-rule-scoped-to-life-characters

**Date:** 2026-09-13
**Previous version:** 2026-09-12_deaths-by-decision-and-no-pronouns

## State

A single correction to one rule. Prompt-only, one field changed.

## What was wrong

The previous version banned third-person pronouns outright:

> "Never write he, she, him, her, they or them about **anybody** […] The only pronoun in these fields is 'you,' meaning the character."

That is **impossible to obey**. The last field — *What you want from the others in the room* — is about the two strangers the character is locked in with. The character has never met them and does not know their names, so "they" and "them" are the only words available. In the run generated under that version, those unavoidable pronouns accounted for **4 of each character's count**.

Human eval identified it precisely: *"The issue with the pronouns is only for their background characters only. not for the part about the other characters in the game."*

## The fix

The ban now applies to **people from the character's own life** — anyone the character has named — and explicitly exempts the room's occupants:

> "Once you have given somebody a name, use that name again — never he, she, him, her, they or them […] The two people in that room are the exception. You have never met them and do not know their names, so 'they' and 'them' are the correct words for them. The last field is about those two and cannot be written any other way."

The reason is also stated more precisely: *"a pronoun about somebody absent will be heard as pointing at somebody present."* That is the actual failure mode — this text becomes the dialogue system prompt, and the character speaks from it while two other people are in the room.

## Honest expectation

Scoping the rule makes it **possible** to obey. It does not make it **likely**.

Measured across the last two runs, this rule changed the pronoun count from 46 to 45. That is the third prohibition-on-wording to be routed around, after the refusal-restating-the-sin rule and the want's banned closing clause. Structural changes — reordering fields, one person instead of two, randomising the name origin — have worked every time they were tried. "Do not write X" is now 0 for 3.

Excluding the unavoidable room pronouns, the real counts under the previous version were 15 and 22. If the next run does not land well below that, the rule should be abandoned as a prompt instruction and replaced with something structural.

**Structural options considered and not taken now:**

- *Enforce via the existing parse retry.* `character_parse_complete()` already gates `_call_with_parse_retry`, so it could reject responses containing pronouns in life-person fields. Rejected because the retry re-sends **the same prompt with no feedback** (`simulator.py`, `_call_with_parse_retry`) — it would resample blindly, almost certainly fail both attempts given the observed rate, and triple the call cost while still returning non-compliant text.
- *A feedback-carrying retry*, where the second attempt is told what was wrong. This is the viable version of the above and a genuinely structural fix, but it changes the retry contract used by every generation call.
- *A post-generation repair pass* over the parsed fields. Cheap to run, but substituting names for pronouns correctly requires knowing each referent, which is not reliably decidable from the text.

## Files changed

`game_state/prompts.py` only — `characterFullUserPrompt`. No code, schema, or structural change.

## Unchanged and still open

The **pair duplication** problem is untouched by this version and remains the largest open issue — four consecutive bad pair ratings, with duplication now occurring at the level of the premise rather than the details. Both characters in the last run were people whose loved one wanted to leave and who used their own body as leverage to stop them.

The conclusion from two versions ago stands: instruction-based anti-duplication has reached its limit, and each new quality constraint narrows the space both characters are drawn from, so quality and distinctness now pull against each other. The scoped structural move is to compose both characters in a single response — separator-based splitting (`=== CHARACTER 2 ===`) with the existing per-character parser run on each half and `extract_field` untouched — deliberately not implemented yet.

Also still open: `NAME_ORIGINS` draws independently per character and produced German and Dutch in the last run, after which the model set both characters in the Netherlands; and "Sanne" recurred from the run before.

## Unity files to update

- **prompts.py** ->
  - Assets/Scripts/PromptsController.cs -- Init() string field assignments (one field changed)
