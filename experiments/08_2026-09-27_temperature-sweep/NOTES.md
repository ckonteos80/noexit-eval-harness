# 2026-09-27 — Temperature sweep, no sin, 600 words

**Question:** the author preferred the no-sin stories to read, but experiment 07 showed those
collide more at 600 words. Can temperature buy back the separation the sin was providing?

Temperature had been fixed at 0.95 for every version and every experiment on record. This is
the first sweep on the story prompt.

## Setup

- Model `Qwen/Qwen3-235B-A22B-Instruct-2507`, pinned. System prompt unchanged. No sin named,
  600-word budget.
- Three new arms (0.7, 1.1, 1.4) x 5 = **15 generations, 19,923 tokens**.
- The 0.95 arm was free: experiment 07's no-sin generations are this exact prompt at 0.95 on
  these exact inputs. Fifteen new calls therefore bought four temperature points.

**The valid range is [0, 2]**, established directly — 2.5 returns
`"temperature must be in [0, 2]"` while 1.0, 1.4 and 2.0 all return 200. Worth recording
because the question came up mid-run and guessing would have invalidated the two high arms.

(That probe also re-demonstrated the proxy's status masking: the provider returned a clean
**400** with a useful message and the proxy re-raised it as a **500**.)

## Result

| temp | mean collision | max | words | protagonist named |
|---|---|---|---|---|
| 0.70 | 35.0 | 44 | 663 | 0/5 |
| 0.95 | 29.9 | **55** | 645 | 0/5 |
| **1.10** | **21.2** | 28 | 654 | 1/5 |
| 1.40 | 21.1 | 24 | 676 | 1/5 |

Collision falls with temperature and then stops falling. **1.10 captures the whole benefit** —
a 29% cut against the current 0.95 — and 1.40 adds nothing measurable while sitting further
from the model's tuned range with no `top_p` available to steady it (the proxy cannot forward
it, same pydantic cause as `max_tokens`).

The 600-word budget held at every temperature, and nothing wrote the room.

## Predictions, and how they fared

- **"0.7 will collide more, not less."** Correct — 35.0 against 29.9 at 0.95. Lower
  temperature sits closer to the mode and the prior wins. Consistent with the earlier
  gpt-oss-120b result, where dropping to 0.6 raised verbatim overlap from 132 to 194 chars.
- **"1.1 will give the best collision numbers."** Correct.
- **"1.4 will reduce collision further and start costing coherence."** **Wrong on both.**
  21.1 against 21.2 is nothing, and no coherence damage could be demonstrated.

A measurement caveat on that last point: the first-person counter was unreliable. Most hits at
1.4 were italicised quoted thought (`*I followed the rules.*`), which is legitimate, and the
quote-stripper only recognised double quotes. What 1.4 actually does is use *more* interior
monologue — a style shift, not a rule break.

## The finding that outlasts the sweep

**Temperature separates phrasing. It does not touch names.**

Pairs 1 and 4 both drew "British". The mother is called **Margaret** in all eight of those
stories, at every temperature:

| temp | pair 1 | pair 4 |
|---|---|---|
| 0.70 | Sheffield, mother Margaret | Bristol, mother Margaret |
| 0.95 | Sheffield, mother Margaret | Sheffield, mother Margaret |
| 1.10 | Croydon, Margaret and Peter Whitaker | Bristol, Margaret and Robert Turner |
| 1.40 | Bristol | Sheffield, Margaret and Thomas Reed |

Doubling the sampling entropy from 0.7 to 1.4 does not shift it. This is consistent with the
project's whole history — `NAME_ORIGINS` fixed the tradition monoculture and never fixed the
names inside a tradition (Carmen three runs running, Lena in six, Daniel repeatedly).
Experiment 09 follows this thread.

## Recommendation

**1.1**, with two limits stated plainly: this measures collision and format, not quality —
nothing here has been through the eval loop — and every eval in the archive was scored at
0.95, so the first runs at 1.1 are not strictly comparable to that history.

Nothing changed in the project. `TEMP_GENERATION` stays 0.95 for the nine-field prompt that is
actually live; 1.1 goes in if and when the story form is promoted.
