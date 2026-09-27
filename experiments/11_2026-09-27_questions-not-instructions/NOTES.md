# 2026-09-27 — Questions instead of instructions

**Question:** the user prompt had grown a contradiction. It carried
*"Include the real sin that condemned you, and the coping mechanism you invented"* — an
instruction to **state the verdict** — alongside the end-on-a-fact rule telling the story not
to. Two of five stories in experiment 10 duly declared *"Your sin is that you made yourself
necessary"* in the body while obeying the rule at the close.

The rewrite does two things at once:

1. **Craft rules move to the system prompt** — second person and naming, where to stop, how to
   end. Everything about *how to write* leaves the user prompt, which keeps only *what to
   write*.
2. **The user prompt becomes four questions**, and the instruction to state the sin and the
   coping mechanism is gone.

```
Who did you love?
How did your sin destroy them?
What lie did you have to tell yourself and others to keep going?
And what would it take for your lie to fall apart?
```

The fourth question is new. Nothing in any previous version asked for the pressure point —
the thing the other two characters could push on.

System prompt goes 201 → 292 words; user prompt 163 → 73.

## Setup

- Model `Qwen/Qwen3-235B-A22B-Instruct-2507` @ 1.1, no sin named, no naming tradition
  (standing instruction), 600-word budget.
- **Both arms run fresh** in the same batch, 5 + 5 = **10 generations, 13,534 tokens**, so
  nothing is carried across sessions. Experiment 10's no-tradition arm gives a third sample of
  the old config for free.
- The provider was flaky: several calls returned HTTP 500 and recovered on retry, and one
  old-arm generation failed three attempts and was recovered separately.

**Confound, stated up front:** craft-relocation and the question rewrite moved together. A
good result cannot be split between them by measurement, only by reading. They are logically
joined — the questions only work once the craft rules have somewhere else to live — but this
is not a clean single-variable test.

## What the measurements say: nothing

| arm | words | collision mean | max | mid-story verdicts |
|---|---|---|---|---|
| old (this run) | 658 | 21.0 | 24 | 0 |
| old (experiment 10) | 641 | 23.2 | 32 | 2 |
| new | 672 | 21.3 | 28 | 0 |

**The verdict result is confounded and cannot be claimed.** The old prompt scored 0 this run
against 2 in experiment 10, so that was noise at n=5. Collision is unchanged. The new arm runs
slightly longer.

One prediction did hold: **question four is never answered as a declaration**. No
*"what would break you is…"* anywhere in the new arm, 0 of 5. That was the failure mode I named
before running and it did not appear.

## What reading them says: the new prompt is clearly better

**Every old story opens with a birth certificate. Every new story opens with the person the
sin destroys.** 5 of 5 each way.

> old: *"You were born in Gary, Indiana, to Miriam and Robert Varga."*
> old: *"You were born in a suburb of Cleveland where snow fell six months of the year."*
> **new:** *"You loved your son, Daniel, more than anything, though you told yourself you were
> teaching him strength when you broke his spirit."*
> **new:** *"You loved Naomi from the moment she walked into your literature class."*

**The structural gain is question two.** In the old arm the sin and the loved one are separate
stories:

- pair 0 embezzles heating grants and three strangers freeze, while his son dies of an
  unrelated seizure at school
- pair 1 falsifies a chart and kills a stranger called Martha Greer, while her son died of
  pneumonia years earlier
- pair 2 defrauds a community centre, while wounding her daughter through a separate cruelty

In the new arm the sin **is** the damage to the loved one. A principal uses the brother he
killed driving drunk as the standard his son can never meet, then drives past that son begging
on an overpass. A mother finds her daughter behind the bathtub with taped wrists and says
*"One more thing. Just one more, and then rest."* A professor grooms a nineteen-year-old
student and publishes her ideas for fifteen years, until the novel arrives dedicated
*"For the thief who made me write this."*

This is the old "the death must belong to the person named above" rule, reborn attached to the
**sin** rather than the death — and far better placed, because the sin is the seed now.

**Question four works and works invisibly.** The thing that would collapse the lie is present
in every story and stated in none: the truth about who was driving; the deathbed exchange
*"Tell her I'm sorry" / "She knows." / "No. She never knew."*; the dedication. That is what the
room needs, supplied without a verdict.

**Deaths improved too.** 2 of 5 old stories end in suicide — a belt in a garage, two bottles
of pills. None of the new ones do.

## Names got worse

| | recurring inside the arm |
|---|---|
| old | `Lillian` 3/5, `Robert` 4/5, `Daniel` 3/5 |
| new | `Daniel` 4/5, `Miriam` 2/5 |

Unchanged by this rewrite, as expected — it targets structure, not names. This is now the
largest remaining defect in the output, and the user has said it may be handled by a separate
renaming pass afterwards rather than in this prompt.

## Recommendation

**Adopt the new prompt.** The improvement is structural and visible in every story, even
though no metric detects it — which is itself worth recording: collision and word counts do
not measure whether a backstory is dramatically useful.

Next candidates: the name problem, and whether the four questions survive being asked of a
second character who must differ from the first.
