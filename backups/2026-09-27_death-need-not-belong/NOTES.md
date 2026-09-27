# 2026-09-27_death-need-not-belong

**Date:** 2026-09-27
**Previous version:** 2026-09-27_nine-field-character-sin-first

## State

The death no longer has to be caused by the character or connect to anyone; attention moves to the two Reasons for Damnation.

## Changes from previous version

One deletion, four sentences, from the `Life` field of `characterFullUserPrompt`:

> ~~Your death must also belong to the person named above. Someone reading the death and
> the relationship together must see why one led to the other. A death that could be lifted
> out and dropped into a stranger's life is the wrong death — rewrite it.~~

What remains is only: *"End the paragraph describing how you died. Contemporary, specific,
plainly stated."*

Nothing replaced it. The death is now unconstrained: it may be caused by the character, it
may be arbitrary, and neither is preferred. A permissive sentence was considered and
rejected — telling the model the death *may* be unrelated would push toward randomness, and
the decision is that both are acceptable, not that random is better.

### Why

An author decision, and it closes out the longest-running unsolved thread in the project.
Six versions and roughly forty generated characters went into trying to make deaths follow
from the character's own chain of action: the accident ban, the chance-cooperation test,
"you did not intend to die", the negative fence, the field reordering that put the
relationship before the death. The record:

- A 12-sample scratch A/B on 2026-09-26 showed the two surviving death rules were close to
  contradictory. "Write a death where nothing had to go wrong for it to kill you" is nearly a
  definition of suicide, and it fought "you did not intend to die." Ten of twelve samples
  were suicides. Tightening one wall pushed characters through the other.
- Across 24 characters, deaths escalated toward spectacle and then homicide — a bus of
  children into a reservoir, a prison break, a truck into a maternity hospital — on two
  unrelated models. The escalation was prompt-driven, because the most decisive death
  available is killing someone.
- The effort bought little. In the two runs since the nine-field rewrite, the death that
  landed best (Lena Chang ignoring chest pain for three days to finish an audit) arrived with
  no death rules in the prompt at all, and the one that landed worst (Kenji Tanaka's wet
  on-ramp) barely hurt its character, because the sin carried him.

That last point is the structural argument. The old rule existed because, in the pre-rewrite
field order, the death was written *before* the sin and had nothing to attach to. Sin-first
ordering removed that problem: the damnation is now the seed and the death is a detail of the
life. It no longer needs to be load-bearing, because something else is bearing the load.

**What is given up:** deaths like Lena's, which were good precisely because they were
intrinsic. Expect more arbitrary deaths. That is the accepted price.

### Docs updated alongside (not in this snapshot — they live outside game_state/)

- **`docs/character-eval-guide.md`** — the per-character section previously ended "Pay
  particular attention to the death: it is the easiest field to write well in isolation and
  the one most often unrelated to everyone else in the character." That spotlight is now the
  opposite of policy, and it was actively mis-scoring: Kenji Tanaka's neutral rating in
  `runs/2026-09-27_a5f4d60b.json` rests largely on his death being disconnected, which is no
  longer a defect. Replaced with an explicit exemption for the death, and the spotlight moved
  to the True / Self-told pair — which the guide previously said nothing specific about at
  all, despite it being the strongest field in recent runs. The removability test still
  applies to the occupation and the people.
- **`docs/eval-loop-scoring-design.md`** — three stale items fixed. The parse list named
  `Cause of Death` (removed in the previous version); the length item targeted 80–100 words
  (the cap is 150); the distinctness item counted "same category of death" as a failure,
  which is kept but demoted to a variety check, since two embolisms in consecutive runs is
  still dull even when neither death has to be load-bearing.
- **`docs/aristotle-poetics.md`** — a dated "superseded in part" marker at the top. The
  relevance note calling the unity principle "the cause-of-death rule, stated 2,300 years
  early" is left exactly as written. It is a research record of why the 2026-09-12 changes
  were made and it was accurate then; rewriting it would falsify the history. Same convention
  this project uses for backup NOTES.

### Deliberately not done

- **No prohibition replaced the rule.** If deaths ever need attention again, the sentence to
  write from is the one the A/B evidence produced: self-deception about a risk that was
  understood ("you told yourself you didn't need it anymore"). A positive description, not
  another ban.
- **Nothing else in the prompt changed**, so this version is cleanly attributable.

### Still open, carried forward

- The `What you want` field is degrading — in the last two runs three of four wants either
  restate the Self-told reason or are ungrammatical. Restoring "Do not end by naming the thing
  you are avoiding" is one sentence.
- `People in your life` selects inert relatives over load-bearing people. Lena Chang's field
  lists her mother, father and brother and omits Maria Ruiz, the patient her damnation is
  about.
- The refusal monoculture (needing to be needed / needing others to supply your worth) has
  survived every prompt and both models, and a scratch test with no anti-duplication block at
  all. The untried lever is randomising an input, as `NAME_ORIGINS` does.
- Both lives have become date-ordered chronologies since "Do not work through a standard set
  of topics in a standard order" was removed.

## Unity files to update

- **prompts.py** -> PromptsController.cs -- all prompt strings

**Porting note:** a four-sentence deletion inside the character generation user prompt. It
stacks on the unported nine-field rewrite from the previous version; port them together, not
separately.
