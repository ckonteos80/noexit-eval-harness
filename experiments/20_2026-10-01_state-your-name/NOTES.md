# 2026-10-01 — told outright to open by stating name, gender and age

**Question:** experiments 18 and 19 put a supplied name in the prompt and GLM used it 5 and 4
times in 10. Neither asked for it. This adds one sentence to the instruction line:

> Write the story of your life, ending with how you died. No longer than 300 words.
> **Start the story by stating your name, gender and age.**

Experiment 19 is the exact matched control — same name call, model, inputs, system prompt,
and the same facts-above-the-task order. 10 of 10, 11,968 tokens.

## Prediction, and where it was wrong

| prediction | outcome |
|---|---|
| 1. the name is used in 10 of 10 | **10 of 10.** Right, and decisive |
| 2. it costs experiment 11's opening outright, 0 of 10 | **Wrong — see §2.** The opening survives, one paragraph lower |
| 3. stating gender reads badly, 3+ of 10 mechanical | **Right, and worse.** 8 of 10 are a bare data line; 2 break person |
| 4. deaths cardiovascular 7–10 of 10 | **6 of 10.** Under — and 4 of 10 are now suicides |
| 5. mean 305–315 words | **311, 2 of 10 inside 300.** Right, and the worst adherence since experiment 14 |

## 1. Asking works, where supplying did not

| | name used |
|---|---|
| experiment 18 — name under the questions | 5 / 10 |
| experiment 19 — name above the task | 4 / 10 |
| **experiment 20 — asked for in the instruction** | **10 / 10** |

A fact sitting in the prompt is scenery. The same fact named in the task is the task. This
settles `{NAME}` from the prompt side, where experiments 18 and 19 could not.

## 2. The opening survives, because the header is a separate paragraph

This is the finding, and it reverses what I predicted. The identity line lands as its own
short paragraph in **8 of 10**, and then the story starts underneath it:

> You are Eliot Grant, male, 51.
>
> **You loved your brother, Marcus.** He was the funny one, the one who drove a school bus
> for thirty years…

The **second** paragraph opens *"You loved…"* in **8 of 10** — which is experiment 11's gain,
intact. It was never destroyed; it moved down one paragraph.

So the trade that experiments 17, 18 and 19 kept circling is not a trade at all. **It is a
parsing problem.** Ask for the header, read the name out of paragraph one, drop that
paragraph from the bio, and you have the name *and* the opening. The one story where this
would not work (Eleanor Hartley) merges the header into a real sentence — *"You are 64 years
old, a woman, and for thirty-one of those years you were the organist at St. Aldric's"* —
which is the best opening in the batch and the only one that earns its identity line.

## 3. The cost: the line itself is not prose, and twice it breaks person

Eight of ten openings are a form field:

> *"You are Eliot Grant, male, 51."* · *"You are Elizabeth Harper, female, 57."* ·
> *"You are Eleanor Hart, female, 57."*

Nobody writes that. It is fine if the line is going to be stripped, and unusable if it is not.

Worse, **two stories answer in the first person** — the craft rule says second person:

> *"**My name is** Clara Vega. Female, 45. **I** was a charge nurse…"*
> *"**My name is** Ethan Thompson. Male, 55."*

Ethan Thompson recovers immediately and the rest is second person. **Clara Vega does not**:
19 first-person pronouns, 0 instances of "you". The whole story is in the wrong person. That
is 1 in 10 unusable, caused by a sentence that asks the narrator to introduce themselves —
an instruction whose natural register is first person.

**If the header is going to be stripped anyway, ask only for the name.** Age and gender are
already inputs; restating them buys nothing and costs the two breakages above.

## 4. The deaths changed, and suicide came back

| | exp 17 | exp 19 | exp 20 |
|---|---|---|---|
| cardiovascular | 10 / 10 | 7 / 10 | **6 / 10** |
| suicide | 0 | 0 | **4 / 10** |

Pills with whiskey; thirty-one pills counted into the Tuesday cup; pills at the kitchen table
with the Saab keys in the coat pocket; morphine drawn from an old hospice stock. Experiment
02 found 10 of 12 deaths were suicides when the death rules contradicted each other, and that
prior has not been seen since. It is back, without any death rule changing.

The plausible cause is register: a story that opens by stating its own name, gender and age
is a confession or a testimony, and testimony ends in self-judgement. Unverified.

## 5. Question coverage, and the names

Q1, Q2, Q3 and Q5 answered in **10 of 10**, Q4 in 9 — the strongest coverage recorded,
better than experiment 17's near-sweep and far better than experiment 19's 8/10/10/8/9.

Supplied names: Eleanor three times again, Clara twice, Ethan twice, and `Voss` once more.
Inside the stories, **Marcus in 4 of 10 and Daniel in 3** — the prior is untouched, as it has
been by every change since experiment 08.

## Recommendation

1. **Keep the instruction, reduced to the name.** *"Start the story by stating your name."*
   It is the only thing that has ever moved name adoption, and dropping gender and age from
   the request should remove both the data-line register and the first-person risk. That is
   experiment 21, and it is a one-line change.
2. **Treat paragraph one as a header, not as prose** — parse the name from it, then drop it.
   This is a pipeline decision, not a prompt one, and it is what makes §2 free.
3. **Watch the suicides.** 4 of 10 on one run is not a finding yet, but it is the same prior
   that dominated experiment 02, and three characters in a room who all killed themselves is
   a worse problem than three who all died of heart attacks.
