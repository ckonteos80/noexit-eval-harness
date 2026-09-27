# 2026-09-27 — The gaze questions

**Question:** experiment 11's fourth question — *"And what would it take for your lie to fall
apart?"* — is **replaced** by two:

```
How do you want people to see you?
How would people see you if they knew your deepest, darkest secret?
```

Four questions become five. Everything else is identical.

**Why this might be the better fit:** *No Exit* runs on the gaze. Garcin's torment is that
Inez sees him as a coward and he cannot make her stop; "hell is other people" is about being
seen. Question four asked what would *break* the lie — a mechanism. This pair asks what the
lie is *for* — a conflict, and the one the other two characters actually attack.

## Setup

- Model `Qwen/Qwen3-235B-A22B-Instruct-2507` @ 1.1, no sin named, no naming tradition,
  600-word budget, craft rules in the system prompt.
- Both arms fresh in one batch, 5 + 5 = **10 generations, 12,960 tokens**. Experiment 11's new
  arm is a third sample of the four-question version.
- User prompt 73 → 82 words.

## Result

| arm | words | inside 600 | collision mean | max | gaze language |
|---|---|---|---|---|---|
| four (this run) | 655 | 1/5 | 22.5 | 33 | 5 |
| four (experiment 11) | 672 | 1/5 | 21.3 | 28 | 1 |
| **five (gaze)** | **612** | **2/5** | **25.8** | **38** | **9** |

**The questions do what they were written to do** — roughly double the "how people saw you"
language — and the stories come in shorter. **Collision is the cost**, 25.8 against 21.3–22.5,
with the highest maximum measured in this series.

`You loved X` still opens 5 of 5 in both arms, so experiment 11's gain is untouched.

## A measurement of mine that was wrong

My declaration flag fired on 3 of 5 in the gaze arm — the phrase *"If they knew…"* — against 0
of 5 for question four. I nearly reported that as the verdict habit returning. Reading the
passages, it is the opposite:

> *"You want people to see you as a good father. A careful man. A professional who made hard
> calls for the greater good.*
>
> *If they knew, they would see the spreadsheet you kept — not of costs or doses, but of
> denials. Column A: Town names. Column B: Number of children diagnosed. Column C: Payments
> received. At the bottom, a formula summing the total: $417,250. Below that, one handwritten
> line: Eli's college fund."*

That is the sin delivered **as an image through someone else's eyes**, not as a judgment. The
two questions work as a pair: the first states the performed self flatly and briefly, the
second detonates it with specifics. Another case of a regex counting a surface pattern and
missing what the text is doing — the same lesson as experiment 06.

## Predictions, and how they fared

- **"Deepest, darkest secret will pull toward melodrama."** **Wrong.** No hidden murders, no
  secret children. A spreadsheet of denied claims, a case file marked *Not suitable. Risk of
  emotional entanglement*, a stolen microfiche keycard and a notebook burned in a firepit with
  *Dr. Lila Chen* still on the cover.
- **"'How do you want people to see you' will be answered as a declaration."** Technically
  yes, and it is fine — see above.
- **"Question two should survive."** Correct, 5 of 5 both arms.
- **"Losing question four may cost the pressure point."** It did not. The gaze pair supplies
  the same lever by naming what is at stake rather than what triggers it.

## Names: a different monoculture, not a smaller one

| arm | recurring |
|---|---|
| four | `Daniel` 4/5, `Clara` 2/5 |
| five | `Lila` 2/5, `Lily` 2/5, `Miriam` 2/5 |

The gaze arm has no single name in four of five — but `Lila` and `Lily` are the same name one
letter apart and between them cover 4 of 5. A Daniel monoculture traded for a Li- one.
Unchanged problem; the user has said it may be handled by a separate renaming pass.

## Recommendation

**Adopt the gaze version.** It supplies the public self and the evidence that destroys it,
which is the material the room needs, and it is shorter. The cost is real and should be
watched: collision is the worst in the series, and if it does not come down, the four-question
version is the fallback.

The open question this raises for the next experiment: whether these five questions survive
being asked of a **second** character who has to differ from the first — none of this has yet
been tested on a pair.
