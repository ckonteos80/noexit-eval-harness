# 2026-09-27 — "See you" vs "what kind of person"

**Question:** a rewording of experiment 12's two gaze questions.

| current (SEE) | proposed (KIND) |
|---|---|
| How do you want people to **see** you? | What **kind of person** do you want people to **think** you are? |
| How would people **see** you if they knew your deepest, darkest **secret**? | What **kind of person** would they **think** you are, if they knew your deepest darkest **secrets**? |

The axis moves from perception to category. That mattered because the strength of the gaze
version was that the second question **detonated with specifics** — a spreadsheet totalling
$417,250, a stolen keycard, a burned notebook. A question phrased "what kind of person" invites
a label instead.

## Setup

- Model `Qwen/Qwen3-235B-A22B-Instruct-2507` @ 1.1, no sin named, no naming tradition,
  600-word budget, craft rules in the system prompt.
- Both arms fresh in one batch, 5 + 5 = **10 generations, 13,434 tokens**.
- User prompt 82 → 91 words.

## Prediction, and it was wrong

**Recorded before the run:** *"The first question improves, the second gets worse. Concrete
images give way to character labels, and 'secrets' plural spreads focus rather than
concentrating it."*

Wrong on the second half. KIND returns images, not adjectives:

> *"They would think you are something else if they knew you **turned off the oxygen twice**.
> If they knew you **waited four minutes before calling 911**. If they knew, when Miriam hugged
> you at the funeral, you thought, **She still doesn't know. She never will.**"*

And the first question also returns acts rather than labels:

> *"You were kind. You paid for coffee lines behind you. You drove your neighbour, Mr Lowell, to
> dialysis every Tuesday and Thursday, even in the snow… That's what people said: **Eli stays.
> Eli fixes it.**"*

Compare SEE's version of the same field, which is equally concrete but works through props:
*"You wanted to be seen as principled, committed, deep. You wore tweed, quoted Camus, kept a
copy of Letters to a Young Poet on your desk."*

## Result: no separation on five samples each

| arm | mean words | inside 600 |
|---|---|---|
| see | 662 | 1/5 |
| kind | 637 | 2/5 |

KIND runs slightly shorter and tighter to the cap. Both keep `You loved X` as the opening in
5 of 5, so the experiment 11 gain survives another rewrite. Neither shows a quality advantage
I can defend from this sample size.

**Method note:** two regex passes failed to locate the gaze passages — one found 3 of 10, a
broader one found 3 of 10 different ones. The material is woven through the stories rather than
concentrated in a "People see you as…" paragraph. Reading was the only way to answer. That is
the third time in this project a regex has counted a surface pattern and missed what the text
was doing (see experiments 06 and 12).

## The finding I was not looking for

**The name prior is keyed to the input, not the prompt.** Matched pairs — same age and gender,
different prompt wording — land on the same names:

| input | see | kind | shared |
|---|---|---|---|
| 51 / male | **Eli**, **Mira**, Tomas, Lila | **Eli**, **Mira**, Lena, Tanya | Eli, Mira |
| 64 / female | **Miriam**, Julian | **Miriam**, Daniel, Lila, Carol | Miriam |
| 45 / female | Eli, Lila | Daniel | none |
| 57 / female | **Daniel**, Robert | **Daniel**, Lila | Daniel |
| 55 / male | Lila, Miriam | Mira, Lena, Amina | none |

Three of five matched pairs share the protagonist's or the loved one's name across two
different prompts. `Lila` or `Lena` appears in seven of the ten.

This explains why nothing has touched the name problem: temperature did not (08), removing the
naming tradition did not (09), restructuring the user prompt did not (11), and rewording the
questions does not. **The prompt is not where the name is decided.** Worth knowing before
anyone spends more effort on it from the prompt side — it supports handling names in a separate
pass, as the user has already suggested.

## Recommendation

**Either phrasing is fine.** KIND reads more naturally and comes in shorter; SEE has no
measurable disadvantage. Picking between them needs more samples or a human read, not another
metric.

The larger open item is unchanged and now overdue: **nothing has been tested on a pair.** Every
experiment since 05 generates characters independently, and the whole point of the play is two
characters who have to differ from each other in a room.

