# 2026-09-27 — No naming tradition at all

**Question:** experiment 08 showed temperature does not touch the name prior — Margaret was
the mother in all eight British stories at every temperature. So what does `NAME_ORIGINS`
actually buy? Remove it entirely and see.

## Setup

- Model `Qwen/Qwen3-235B-A22B-Instruct-2507` @ **1.1** (experiment 08's recommendation),
  pinned. No sin named, 600-word budget.
- 5 generations, **6,455 tokens** including one retry.
- The matched control is free: experiment 08's 1.1 arm is this exact prompt *with* a tradition
  on these exact ages and genders.
- The `{NAME_ORIGIN}` input line was removed, and with it the guard clause *"This person is an
  ordinary contemporary person who happens to have their background. Do not make the naming
  tradition into the character's whole identity"* — which refers to something that no longer
  exists.

One call failed on a DNS resolution error (a transient network fault, not the API) and was
re-run, so the set is complete at five.

## Result: removing it makes everything worse

| | tradition given | no tradition |
|---|---|---|
| mean collision | **21.2** | 26.0 |
| max collision | **28** | 31 |
| mean words | 654 | 648 |
| "apartment above a laundromat" | 0 | **2 of 5** |

**The convergence is on specifics, not just on ethnicity.** Two of the five open with a
character born in an *apartment above a laundromat* — one on 82nd Street, one in East
Cleveland. That image appears nowhere in the prompt.

**Margaret and Robert are the model's default parents, not a British artifact.** Pair 4 opens
*"You were born to Margaret and Robert, but Robert left when you were six, and Margaret raised
you alone"* — with nothing in the prompt saying British. So `NAME_ORIGINS` was never
suppressing a *British* prior; it was suppressing **this**, and experiment 08's Margaret
finding was the same default leaking through wherever the assigned tradition happened to
permit it.

Every held-out tradition became American. Portuguese, British, Filipino and Italian-American
all produced 82nd Street, East Cleveland, Sheridan Road, Elm and 23rd.

A prediction recorded before the run — that the names would skew Anglo-American — was right,
but understated: they converge on particular names and particular images, not merely a region.

A caution recorded before the run did **not** materialise, and it is worth saying so. I warned
that removing the input might *reduce* measured collision while making the set duller, which
the metrics would score as an improvement and a reader would score as worse. It didn't happen:
collision rose *and* the content got more uniform, so the number and the reading agree.

## The larger finding: NAME_ORIGINS never reached the supporting cast

Counting across all ten stories in both arms:

| name | tradition given | no tradition | total |
|---|---|---|---|
| **Daniel** | **4/5** | 3/5 | **7/10** |
| Margaret | 2/5 | 2/5 | 4/10 |
| Lila | 1/5 | 2/5 | 3/10 |
| Claire, Diane, Elena, Mateo, Miriam, Lena | — | — | 2/10 each |

**Daniel is in seven of ten stories, and four of five even with a tradition specified** —
across Portuguese, British, Filipino and Italian-American inputs. He appears as a son, a
boyfriend, a best friend, a father and a husband.

Daniel Reeves was character 1 in three consecutive runs, and that is precisely why
`NAME_ORIGINS` was introduced. It worked on the axis it touches: the **protagonist's** name
follows the assigned tradition. It never reached the **supporting cast**, which reverts to
Daniel, Margaret, Lila and Claire regardless of what tradition is assigned.

The timestamp prior persists too: `3:17` appears in one story from each arm, joining the `2:17
a.m.` sightings from earlier experiments.

## One coherence failure worth recording

No-tradition pair 4 declares *"The sin is this: you killed Michael."* Michael is the
brother-in-law who lent the character $12,000. The story then never kills him — it ends with
the **narrator** dying in the car crash after a phone argument, while Michael is alive. The
stated sin is not the sin the story tells. This is the only outright incoherence in the ten
and it is in the no-tradition arm.

## Conclusion

**Keep `NAME_ORIGINS`.** This is the first direct evidence for it rather than inference from
the runs that preceded it: removing it raises collision, collapses the milieu to one country,
and brings back the exact default the list was written to displace.

**But it is only half a fix.** It governs the protagonist and leaves the supporting cast to
the prior. If the recurring-name problem is worth solving, the lever is the same one applied
one level deeper — randomising an input for the cast, not another instruction about variety.
Instructions on variety have failed four times on this project.
