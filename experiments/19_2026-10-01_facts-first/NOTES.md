# 2026-10-01 — the given facts moved to the top of the user prompt

**Question:** experiment 18 put `Your name:` at the bottom of the user prompt, under the
questions, and the story used it 5 times in 10. Does moving the three given facts directly
under the hell framing — before the instruction, before the questions — make the name a
premise rather than a footnote?

Nothing else changed. Same 89 words, same name call, same model, same five inputs twice.
Experiment 18's arm A is an exact matched control differing only in where three lines sit.

## Prediction, and it was wrong

| prediction | outcome |
|---|---|
| the name is used in 8–10 of 10, against 18's 5 | **4 of 10.** Wrong, and slightly worse |
| openings on the loved one fall to 0–2 of 10 | not the way it moved — see §2 |
| deaths stay cardiovascular | unchanged |
| length near 300 | **306 mean, 7 of 10 inside 300** — the best adherence recorded |

## 1. Where the fact sits does not decide whether it is used

4 of 10 against 5 of 10 is no difference at this sample size. **Position is not the lever.**
GLM-5.3 takes a supplied name about half the time wherever it is put, and the half that
refuses it names nobody.

Worth saying plainly because it is a cheap hypothesis to keep re-testing: it has now been
tested, and prompt order is not where this is decided.

## 2. What the reorder did change is the opening

In experiment 18, every story that used the name opened by declaring it — *"You are Silas
Vega."* 5 of 5. With the facts moved up, that drops to **1 of 10**, and two of the four
stories that use the name now weave it in instead:

> *"You were the daughter who stayed. Your brother Gary moved to Denver in 1994…"* — and
> Eleanor Hartley is named later, in the body.

So the order of the prompt moves the *shape* of the story without moving whether the name is
adopted. That is a smaller result than hoped for, but it is a real one: **the "You are
&lt;name&gt;" opening is an artefact of where the fact sits, not of naming the character.**
If the name can be used without that opening, experiment 11's gain and a named protagonist
are not strictly opposed — which is what experiment 18 §3 suspected they were.

## 3. The surname gets given to the spouse

Of the six stories that ignored the supplied first name, **two used the surname for someone
else** — the wife and the husband:

> supplied *Ethan Harper* → *"You married **Dana Harper** in 1996…"*
> supplied *Elena Martinez* → *"You married **Rafael Martinez** at twenty-two…"*

The other four use neither name anywhere. So the model does not discard the given name so
much as redistribute it, which is worse: a character sheet would say the protagonist is
Ethan Harper while the story says Harper is his wife's married name.

## 4. The weak link is the name call, not the story prompt

Ten names from `Qwen3-8B` at temperature 1.2:

> Ethan · Eleanor · Elara · Elara · Elijah · **Elias** · Eleanor · Elena · Elara · Silas

**Nine of ten begin with E.** Surnames: Voss three times, Harper twice. Experiment 18's ten
from the same call gave Eleanor three times and Silas twice. Across both experiments `Voss`
appears four times, and it had already appeared in Qwen's experiment 15 and GLM's experiment
16 — four models now, on the same inputs.

A dedicated call at high temperature is not a source of variety. It is the same prior with an
extra round trip.

**The fix is probably not an LLM call at all.** A name drawn at random in code is free,
instant, and actually varied; nothing about `{NAME}` requires a model to invent it. That
touches the no-naming-tradition rule, though — a name list is adjacent to `NAME_ORIGINS` —
so it is the user's decision, not mine.

## What this means for the promotion

Nothing here blocks it. Experiment 18 settled `{NAME}`: the supplied value is authoritative
whether or not the prose uses it. Experiments 19's findings are about quality, not viability:

1. prompt order is not worth further experiments — this is settled
2. the name generator needs replacing before any of this ships, or half the cast will be
   called Elara Voss
3. §3 is a genuine defect to watch: when the name is ignored, the surname can reappear on the
   wrong character
