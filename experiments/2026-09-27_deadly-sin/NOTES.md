# 2026-09-27 — Deadly sin as a randomised input

**Question:** the author's redraft of the story prompt used the phrase "a deadly sin". That
word has a specific referent — pride, greed, lust, envy, gluttony, wrath, sloth — which turns
it into a **randomisable input**, the way `NAME_ORIGINS` is. Does assigning a sin per
character reduce duplication?

The reasoning behind trying it: randomising an input is the only mechanism with a proven
record on this project — it broke a three-run name prior after four failed instructions —
and the axis it would attack is the one that has survived everything else (the refusal/sin
monoculture persisted through a long prompt, a short prompt, two models, the block, and no
block at all).

The intended mechanism is `random.sample(SINS, 2)` per session, **not** two independent
draws: with 7 sins, independent draws collide about 14% of the time, and sampling without
replacement makes "damned for a different kind of moral failure" a guarantee by construction
rather than an instruction that has repeatedly failed.

## Setup

- Model `Qwen/Qwen3-235B-A22B-Instruct-2507` @ 0.95, pinned.
- **10 generations, 18,799 tokens.** 5 with a named sin, 5 without.
- The control keeps *"for a deadly sin you committed"* but does not say which, so the
  variable is the assignment and not the word "deadly".
- Inputs seeded and paired row-by-row across arms, so a within-row difference is the sin.
- Sins chosen deliberately to include the two predicted to struggle: **pride, envy, wrath,
  sloth, gluttony**.
- `full_text.md` has all ten stories paired; `results.json` has the raw data.

## Result: no measurable effect on duplication

Longest verbatim shared run, all 10 within-arm pairs:

| | mean | max |
|---|---|---|
| with sin | 26.0 chars | 33 |
| without sin | 27.0 chars | 43 |

No difference. The hypothesis is not supported at n=5 per arm.

**But the story form itself is doing the work.** In the nine-field format, *single fields*
shared verbatim runs of 45–48 characters. Here, stories eight times longer share a maximum of
33. Longer text, shorter overlap. The slot hypothesis was right; the sin was the wrong lever
on the same problem.

**The strongest collision crosses both arms and is an ending.** The pride story and no-sin #1
both close:

> *"you whispered, not to God, not to [X], but to yourself: 'I did what I had to do.'
> **It was the last lie you ever told.**"*

Identical closing formula, different arms, different sins. A model prior in how it ends a
damnation story, which no input randomisation touches.

## Predictions recorded before the run, and how they fared

- **"Sloth and gluttony may not carry."** **Wrong.** Sloth produced a mother whose inaction
  kills her husband and hollows out her daughter — *"tomorrow never came"*. Gluttony produced
  the sharpest line in the batch: *"It was about making sure that, for once, someone had to
  watch you destroy yourself."* Keep all seven.
- **"A bare label risks allegory."** Mostly did not materialise — only sloth announced itself
  (*"the sin that damns you is sloth"*). Four of five embedded it.
- **"The threshold line should hold."** Held: **0 violations in 10**.

## Two things the sin did not fix

- **Vehicle deaths ran 2-in-5 in both arms**, and "a delivery van ran a red light" killed both
  the wrath character and no-sin #2.
- **Names recycled freely** — Mateo twice, Maria three times, Daniel twice, plus Lourdes and
  Eleanor which had appeared in earlier project runs.

## An unprompted control result worth keeping

No-sin #3 opened: *"You are Maria Lombardi, and you are in hell for pride."* Unprompted. The
model reaches for the seven deadly sins whether or not you name them.

## A blocker for stage two, found while tabulating

**The story prompt does not reliably produce a name or an occupation.** Two of ten
protagonists are never named at all; two more are named only in passing inside someone else's
dialogue (*"Jesus, Miguel…"*, *"Follow protocol, Carlos"*), with surnames inferable only from
the parents. Two stories never state an occupation.

`Name` is a field the bio cannot do without — it is what the other characters call you — and
the field-based prompt guaranteed it by asking directly. A free-form story does not. Fix
before building the extractor, or stage two will invent names for a quarter of characters,
which is exactly the fabrication problem the two-stage design is meant to avoid.

## Standing recommendation

Adopt the sin assignment for the **guarantee**, not for quality: drawn without replacement
across a pair it makes the damnation axis structurally impossible to collapse. Do not expect
it to reduce collision — this experiment says it will not.
