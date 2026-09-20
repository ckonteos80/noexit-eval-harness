# 2026-09-12_one-relationship-and-a-death-that-belongs-to-it

**Date:** 2026-09-12
**Previous version:** 2026-09-12_single-call-generation

## State

Human eval on `2026-09-12_0441d06f` rated **both** characters down for one reason: *"the cause of death has nothing to do with who they loved and who they hated… The cause of death needs to connect to every other element."*

This version makes the relationship the spine of the character. There is now **one person** the character both loved and could not forgive, and the death, the sin and the life all have to belong to that relationship.

## The diagnosis, which was structural rather than a matter of guidance

In the previous format block, **Cause of Death was field 3 and the relationships were fields 4 and 5**. Generation is autoregressive, so the model was being asked to write the death *before the people in the life existed*. It could not connect them — there was nothing yet to connect to.

The evidence is in the output: Mateo's death reads "you drove home from work the day after your daughter's call," the model reaching forward to a person it had not yet invented. That is why the link is temporal ("the day after") rather than causal.

This predates the single-call merge. The old four-call chain generated occupation → death → loved → hated inside the Life call in exactly that order, so the flaw has been present since the project began. Merging is what made it visible and cheap to fix.

**No amount of instruction would have fixed this.** Three versions of increasingly explicit rules about connection failed because the ordering made connection impossible.

## Changes

### 1. The reorder — the actual fix

```
Name → Occupation → Who you loved → Who you hated → Cause of Death → Life →
Reason True → Self-told → Refuse to admit → Trait → Want
```

Cause of Death moves from position 3 to position 5. `assembly.CHARACTER_FIELDS`, the prompt's instruction order, the prompt's format block, and `assemble_bio()`'s section order all move together — and the verification asserts all four agree. **They must stay in lockstep.**

### 2. One person, two sides

`Who you loved` and `Who you hated` now describe **the same person**, not two people.

The two fields were kept rather than merged into one. "Collapse into a single person" is about the number of *people*, not the number of *fields* — and keeping both names the two facets explicitly (what they were to you; what you could not forgive), which gives the dialogue more to work with than one blob would. It also costs **no schema change whatsoever**: `run_viewer.html` turns out never to reference these fields (it renders bios from the assembled `description`), so the viewer, `game.py`, `simulator.py`, `store.py` and the run JSON are all untouched, and the five previous runs stay directly comparable.

The prompt guards against the obvious failure — the model has written two people here for four versions and will default to it — with an explicit instruction in the field *and* in the format block's placeholder.

### 3. The death must belong to that person

> "Your death must belong to that person. It happened because of them, or in front of them, or on the way to or from them, or in the hours after something passed between you. […] A death that could be lifted out and dropped into a stranger's life is the wrong death — rewrite it."

Paired with an explicit release valve: *"That does not make the death a punishment. It can still be ordinary, avoidable and stupid."* The death was deliberately **not** made a consequence of the sin — that reads as cosmic justice, and Sartre's three do not all die for their sins (Estelle simply had pneumonia).

### 4. The sin must belong to it too

The True reason previously said "the person you loved **or** the person you hated," which stopped making sense once they are one person. Rewritten to name that person, and — directly fixing Keisha, whose sin centred on a shop employee who was neither — to forbid "a third party who happens to be nearby" or "someone introduced here for the first time."

### 5. The want, de-templated

Both wants in the last run were the same sentence: *"You want them to agree/acknowledge that you were right… so you never have to face the truth that…"*. The trailing confession clause is now banned outright — the want must name a behaviour and stop, since the thing being avoided already has its own field.

Included in this version because tightening structure is what produces templates, and this version tightens structure.

### 6. Anti-duplication: from categories to bonds

The two relation-category bullets merge into one. A new bullet polices the *kind of hold* the person had: *"Two people who were damaged the same way by the people they loved are the same character in different clothes, however different their jobs and deaths are."*

### 7. `character-eval-guide.md`

Added the criterion I was missing, which is why I rated Mateo **good** where the human rated him **bad** — I was judging internal consistency, the human was judging relational integration:

> "A character can be perfectly consistent and still be disconnected. […] Could this death be dropped into a stranger's life without anything else changing? Could the job? Could the person they loved?"

## Files changed

`game_state/prompts.py`, `game_state/assembly.py` (`CHARACTER_FIELDS` order, `assemble_bio()` section order), `character-eval-guide.md`. **Nothing else** — no dataclass, simulator, store, viewer or schema change.

## The risk this version carries

The last pair was rated **bad** because the two characters had the same psychology and nearly the same want. This version tightens the structure further, and more structure tends to produce more sameness — every character now risks becoming "someone destroyed by their one relationship."

The mitigation is change 6, but policing a *kind of bond* is a much weaker lever than policing a category. **If the next run still reads as two versions of one person, the honest conclusion is that anti-duplication by instruction has reached its limit**, and the pair needs to be composed together in one call rather than sequentially. That is the next structural move if this fails.

## What to look for in the first run

In priority order: is the death now genuinely *caused* by the person rather than merely near them; are Who you loved and Who you hated actually the same person; have the characters become over-determined or more alike than last time; did the want template break; do names still vary.

## Still open

- **Dialogue** remains the next substantive version.
- **Cross-run name repetition** is fixed by `NAME_ORIGINS`, but with one run of evidence only.
- **The load-bearing rule** has not bitten in three versions. It may be that it cannot work as a general instruction and needs to be a per-field requirement.
- **`character-eval-guide.md`** still needs the three older calibration fixes from the 28th.

## Unity files to update

- **prompts.py** ->
  - Assets/Scripts/PromptsController.cs -- Init() string field assignments (two fields changed, none added or removed)
- **assembly.py** ->
  - CharacterGenerator.cs -- the field order used for parsing and for assembling the bio. **Order is load-bearing; port it exactly.**
