# 2026-09-27 — Word budget on the story prompt

**Question:** the story prompt produces ~1,000-word backstories, about 3.5x the length of the
nine-field bio. Can a word budget in the prompt shorten them, and what does the shortening
cost?

This came out of a different question — whether `max_tokens` could be used to cap output.
It cannot, for two separate reasons, both worth recording:

- **The proxy still drops it.** `ChatRequest` in `jejunepixels/noexit-proxy` declares only
  `model`, `temperature`, `messages`, `provider` and `timeout`; pydantic v2 discards
  undeclared fields. Verified against the live Space at commit `c13ccbe`. The project's own
  data agrees: of 52 dialogue calls, 28 exceeded the 75-token cap, the longest reached 2,479,
  and `finish_reason` is `"stop"` in all 52 — never once `"length"`.
- **Even fixed, it is the wrong tool.** `max_tokens` truncates mid-sentence; it does not
  produce a shorter *complete* story. And on a reasoning model it is actively dangerous:
  reasoning tokens consume the budget before the answer does. On the gpt-oss-120b probe,
  2,159 of 2,559 completion tokens were reasoning — a 500-token cap there would have returned
  nothing usable. `reasoning_effort` cannot be forwarded either, same pydantic cause.

So the budget has to live in the prompt.

## Setup

Matched three-way, and **the baseline was free**. Experiment 05's `with_sin` arm used these
exact five sins and these exact five input triples, so it is a proper no-budget control that
did not need re-running. The script reads those inputs out of `05_.../results.json` rather
than reproducing them, so the match is guaranteed rather than assumed.

- Model `Qwen/Qwen3-235B-A22B-Instruct-2507` @ 0.95, pinned. System prompt unchanged.
- 10 new generations (5 at 600 words, 5 at 400), **11,557 tokens**.
- The budget clause sits immediately after "Write the story of your life, ending with how you
  died" — the same position the old 150-word cap occupied relative to its field.

## Result: it works, and it is read as approximate

| arm | mean words | inside budget | overshoot | time |
|---|---|---|---|---|
| no budget | 1,076 | — | — | 22–47s |
| 600 | 652 | 0/5 | +8.7% | 9–34s |
| 400 | 414 | 2/5 | +3.5% | 7.6–9.0s |

Every generation overshot by a small, consistent margin rather than ignoring the number.
**Practical rule: ask for 5–10% under the real target** — 550 lands near 600, 370 lands near
400. This is a much better record than the 110-word cap on the `Life` field, which was
breached in 14 of 19 runs and sometimes by 60%.

Cost falls with length: 11,557 tokens for ten generations against 18,799 for ten in
experiment 05, and the 400-word calls returned in about 8 seconds.

## What it costs: the cast

| arm | words | distinct names | 3rd-person pronouns | per 100 words |
|---|---|---|---|---|
| no budget | 5,382 | 120 | 231 | 4.3 |
| 600 | 3,260 | 88 | 157 | 4.8 |
| 400 | 2,072 | 44 | 99 | 4.8 |

**The cast shrinks roughly in proportion to the length** — 120 names to 88 to 44. That is the
real price, because those names are exactly what the other two characters interrogate in
dialogue. A 400-word story supplies about a third of the people a 1,000-word one does.

**And the naming rule degrades.** Third-person pronouns per 100 words rise from 4.3 to 4.8
under both budgets. Compression reaches for *he* and *she* because they are shorter than a
name — and that is the one rule with a functional reason behind it, since a pronoun about
somebody absent gets heard in the room as pointing at somebody present.

The threshold rule held everywhere: 0/5 wrote the room in all three arms.

## A measurement error worth recording

My first pass reported that two of the 400-word stories contained **zero** named people and
one contained **zero** self-justification. Both were artifacts of my own regexes, not findings.

- The name regex matched only `First Last` pairs. The shorter stories use first names —
  wrath@400 names Mateo, Ramon, Lourdes, Dr. Kim and Nadine.
- The self-justification regex looked for "told yourself" and similar. wrath@400 phrases it as
  revelation instead: *"you kept him alive not for him, but to prove you weren't weak."*

Caught by reading the two stories before reporting. The lesson is narrow and repeatable:
when an automated count returns **zero** on something the prompt explicitly asks for, read the
text before believing the number.

## Recommendation

**600, not 400.** It removes 40% of the length while keeping about three-quarters of the cast.
The 400s read noticeably thinner — pride@400 compresses an entire marriage into two sentences.

If a shorter target is wanted anyway, the naming rule needs strengthening in the same change,
or the brevity is bought with the pronoun problem.

## Still open

- Whether the shortened stories survive stage-two extraction as well as the long ones. Fewer
  named people may mean a thinner `People in your life` field, which was already selecting
  inert relatives over load-bearing ones.
- The protagonist-naming problem from experiment 05 is unchanged here: 3/5 named in the
  baseline, 1/5 in each budget arm. Shortening did not cause it and does not fix it.
