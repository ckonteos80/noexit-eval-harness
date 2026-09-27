# 2026-09-27 — "End on a fact, not on what it meant"

**Question:** every story generated so far closes by delivering its own verdict. The
tradition-given arm at 1.1 did it **5 times out of 5**:

> *"The last thing you felt was the weight of that truth."*
> *"But you knew that was the lie you always told."*
> *"You called it love. You still do. Even now. Especially now."*

The no-tradition arm did it 3 of 5 (*"You were wrong."*, *"It was greed."*, *"And in the last
moment, you still believed it."*). Same tic as the *"It was the last lie you ever told"*
formula found in experiment 05.

For this play that is backwards. In *No Exit* nobody announces their own self-deception; the
drama is two strangers prising it out over ninety minutes. **A backstory that has already
passed judgment leaves the room nothing to discover.**

## The rule added

```
End on a fact, not on what it meant. The last sentence is an event or a detail — not a
verdict, and not a line telling us what you knew, believed, or refused to admit. Leave
that for the others in the room to find out.
```

Placed with the other ending instructions, after "do not describe the room". The final
sentence gives the reason, which usually helps.

## Setup

Two arms, both against free matched controls.

- **Primary — no naming tradition** (standing instruction from 2026-09-27). Control is
  experiment 09's no-tradition arm. 5 generations, **6,564 tokens**.
- **Secondary — tradition given.** Control is experiment 08's 1.1 arm. 5 generations,
  **6,804 tokens**. Run first, before the no-tradition instruction was given; kept because it
  shows the rule works in both configurations.

Model `Qwen/Qwen3-235B-A22B-Instruct-2507` @ 1.1, no sin named, 600-word budget, system prompt
unchanged. One call in each arm dropped on a transient network error and retried.

## Result: 10 of 10

Both arms went from 0 endings on a fact to 5 of 5.

| | control | with rule |
|---|---|---|
| *"You were wrong."* | → | *"A robin landed on the empty bird feeder outside your kitchen window."* |
| *"It was greed."* | → | *"The screen stayed lit, cracked down the middle, displaying Mateo's face, four years old, grinning in a yellow life jacket."* |
| *"you whispered, 'Sofia,' not in prayer, but in fear"* | → | *"still wearing the sweatpants Daniel bought you for Christmas. They had rockets on them. You never told him you hated them."* |
| *"your last conscious thought was not of love, but of relief"* | → | *"Someone found you two days later, stiff between boxes of tater tots."* |

**Prediction on the record: I expected 2 or 3 of 5.** This project's history with prohibitions
is poor — four failures against four successes for structural changes — so a clean 10 of 10 is
the single most effective prompt line tested here.

**Neither failure mode I named beforehand appeared at the ending.** No fact tacked on after a
verdict, and no verdict smuggled into the final sentence.

Length was unaffected: 641 words against 658 (no tradition), 650 against 654 (tradition).

## But the verdict moved rather than vanished

The rule governs the last sentence only, and two of five no-tradition stories still declare
themselves mid-story:

> *"Your sin isn't ambition. It's not even lying. Your sin is that you made yourself necessary."*
> *"Your sin was not lying, or abandonment, or even pride. It was smugness."*

The control had one such line. So this is not an improvement on that axis — it is the
"verdict migrates up" failure I listed, arriving one paragraph earlier instead of at the
close. If the room is meant to do the discovering, that sentence needs the same treatment.

## The names collapsed, badly

Without a tradition, across five stories:

| name | appears in |
|---|---|
| **Daniel** | **5 of 5** — a son, two fathers, a husband, and the protagonist |
| Robert | 4 of 5 |
| Margaret, Perez | 3 of 5 |
| **Voss** | **2 of 5** — as a surname |
| Carol, Matthew, Miriam, Elaine | 2 of 5 each |

**Voss is the worst of it.** Pair 3 is born to *Helen and Robert Voss*; pair 4 to *Robert and
Carol Voss*. Two unrelated characters with the same surname and the same father's name.
Carol and Matthew also appear in both pairs 1 and 4, with the family roles inverted —
pair 1 is Carol with a son Matthew, pair 4 has a mother Carol and a brother Matthew.

Compare experiment 09's measurement: with a tradition supplied, Daniel ran at 35% across 40
stories and never once appeared in a Filipino draw. Without one he is at 100%.

This is the trade the no-tradition decision buys, and it is worth stating plainly: **the prose
the author prefers, and the strongest name collapse the project has measured.** It is fixable
without reinstating nationalities — the same input-randomisation trick one level down, a seed
name or a forbidden-name list per generation. Instructions about variety have failed four
times; an input has worked twice.

## One thing that improved without being asked

**No suicides.** Deaths in this arm: lung cancer when a thunderstorm cuts the oxygen
concentrator, a quiet death on the couch, a car swerving for a deer, cardiac arrest at work,
and a man locked in a walk-in freezer with a failed latch. Against **4 of 5 self-inflicted** in
the tradition-given arm run an hour earlier with the same rule. Could easily be noise at n=5,
but worth watching, because the deaths have drifted toward suicide repeatedly since all the
death rules were removed.

`3:17` appears again. That timestamp has now surfaced in six unrelated experiments.

## Recommendation

**Keep the rule.** It is one sentence, it is the cleanest result in the project, and it
restores the thing that makes the room worth watching.

Next candidate is the same treatment for mid-story verdicts, and after that the name problem,
which is now the largest defect in the output.
