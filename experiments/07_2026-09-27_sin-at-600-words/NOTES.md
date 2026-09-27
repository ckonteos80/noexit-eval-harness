# 2026-09-27 — Does naming the sin matter at 600 words?

**Question:** experiment 05 found that assigning a deadly sin had no measurable effect on
duplication — 26.0 against 27.0 characters of verbatim overlap. But those stories ran ~1,076
words. Experiment 06 settled 600 words as the target length. Does the sin matter more when
there is less room to diverge?

The reasoning for expecting a difference: at 1,000 words two stories have enough space to walk
apart on their own. At 600 they have less, so whatever prior the model falls back on has
proportionally more influence.

## Setup

**Only one arm was new.** Experiment 06's 600-word generations already are "600 words + sin
named" on these exact five inputs, so they serve as a matched control at no cost. The script
reads them out of `06_.../results.json` rather than reproducing them.

- Model `Qwen/Qwen3-235B-A22B-Instruct-2507` @ 0.95, pinned. System prompt unchanged.
- 5 new generations, **6,433 tokens**.
- Prompts identical except the first line: `"...for a deadly sin you committed: {SIN}."`
  against `"...for a deadly sin you committed."` The control still calls it a deadly sin; it
  just does not say which.

`results_no_sin.json` holds the new arm. The sin-named arm lives in experiment 06.

## Result: at 600 words, the sin does make a difference

| arm | mean collision | max collision |
|---|---|---|
| sin named | 25.4 chars | **29** |
| no sin | 29.9 chars | **55** |

Against experiment 05's 26.0 / 27.0 at full length, where there was no difference at all.

**The clearest evidence is the two British inputs.** Pairs 1 and 4 both drew "British" as the
naming tradition (64f and 55m). Without a sin, they open with the identical 55-character
sentence:

> *"You were born in Sheffield, and your mother, Margaret, …"*

Both have a mother called **Margaret**, both a father called **Robert**, both born in
**Sheffield**. Different ages, different genders, different lives thereafter.

Run those same two inputs *with* a sin and the longest shared run drops to 21 characters, and
the openings separate:

- envy: *"You were born in Bristol, and your mother, Margaret, used to say you had a face that
  showed your thoughts…"*
- gluttony: *"You loved food because your mother, Helen, said it was the only thing she could
  give you that cost nothing."*

Gluttony pulled its story off the British-naming default entirely — different city, different
mother, a completely different opening move.

**The mechanism that fits:** at 1,000 words two stories diverge on their own. At 600 they do
not, the naming-tradition prior takes over, and an assigned sin is what breaks it.

## The caveat, stated plainly

n=5 per arm, and the mean gap is driven substantially by that one British pair. The **max** is
the dramatic number; the **mean** is the modest one (25.4 vs 29.9, an 18% difference). This is
promising rather than settled.

It is nonetheless the first result in this project where the sin assignment earned its place
on evidence rather than on the guarantee argument from experiment 05.

## Secondary measures

| | sin named | no sin |
|---|---|---|
| mean words | 652 | 645 |
| distinct names | 88 | 84 |
| 3rd-person pronouns / 100 words | 4.8 | **5.7** |
| protagonist named | 1/5 | 0/5 |
| wrote the room | 0/5 | 0/5 |

- **Length is unaffected** by the sin — 652 against 645. The budget does the work.
- **The pronoun rate is worse without a sin**, 5.7 against 4.8. Consistent with the collision
  result: a story falling back on a default reaches for default phrasing too.
- **The protagonist naming problem persists in both arms**, and has now failed across
  experiments 05, 06 and 07. It will not fix itself and needs a line in the prompt.
- The threshold rule held everywhere.

## Unprompted sin words

One of five control stories used a deadly-sin word unbidden ("pride"), the same rate as
experiment 05. The model reaches for that vocabulary occasionally whether or not it is asked.

## What this supports

Keep the sin assignment, drawn **without replacement** across a pair so two characters can
never receive the same one. Experiment 05 established the guarantee argument; this adds a
measured benefit at the length actually being used.

## Still open

- **The protagonist is usually unnamed.** Three experiments, one named out of fifteen at 600
  words. This blocks the stage-two extractor, which needs a `Name` field.
- Whether the effect holds at n greater than 5, and whether it is really about compression or
  about the naming tradition specifically. A cheap follow-up would repeat the two-British-input
  case several times.
