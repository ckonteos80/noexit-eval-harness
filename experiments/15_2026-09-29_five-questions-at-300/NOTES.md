# 2026-09-29 — five questions at 300 words

**Question:** experiment 14's recommendation, run. Cut the question that earned 1 of 10, give
the story back the 100 words it needed to reach a death.

One arm, 10 generations, same five inputs as experiments 12–14, each run twice.
Experiment 14 is the matched control: same inputs, 200 words, six questions.

## Setup

- `Qwen/Qwen3-235B-A22B-Instruct-2507` @ 1.1, no sin named, no naming tradition, craft rules
  in the system prompt.
- User prompt 86 words, **five** questions, budget **300**.
- Two changes against experiment 14: the trailing *"what kind of person would they think you
  are, if they knew"* is gone, and the budget is 200 → 300.
- 10 generations, 8,732 tokens, no retries — every call returned first time, 4.7–6.4s.

## Prediction, and where it was wrong

Recorded in the script before the run:

| prediction | outcome |
|---|---|
| the death comes back in 9 or 10 of 10 | **9 of 10** — right |
| the secret holds at 10 of 10 | **10 of 10** — right |
| mean about 340 words, the usual 10–15% over | **312, 4% over** — wrong, much tighter |
| braided paragraphs drop from 11 to about 6 | **16** — wrong, and in the opposite direction |

## 1. The best length control measured in this project

Mean **312** words against a 300 cap — **4% over**, where 200 ran 16% over and 600 ran 6–10%
over. Range 275–333, 3 of 10 inside the cap. Whatever the model is doing with the number, it
tracks 300 more closely than either end tested so far.

## 2. The death came back, and one story still has none

Nine of ten end on a death, against seven of ten at 200 words — and the deaths are better,
not just present: an elevator cable on the twelfth floor, choking on your own tongue in the
witness box while testifying against your father, a heart attack while tying your son's
baseball cleats.

The exception is **call 10**, which ends on *"You burned the box the next day."* No death.
**Call 6** puts the secret *after* its own death paragraph, breaking the "stop at the moment
of your death" rule from the other side.

## 3. The finding worth keeping: the secret became an object in a place

At 200 words the secret was an act. At 300 it is a **findable thing with an address**:

> the voicemail still on your phone, listened to seventeen times the night he died
> · the ledger, the payment voided and "insufficient funds" written in red
> · a plastic bin in the basement freezer, beneath the frozen peas and the leftover lasagna
> from the memorial, holding her diary
> · the real acceptance letter, folded in the lining of your Bible at page 23 in Acts
> · the torn sketchbook pages in a shoebox in the garage, burned the next day

This is the first output in the series that hands the game a **prop**. Two characters in a
room can ask about a freezer or a Bible; they cannot ask about an abstraction. If anything
from experiments 11–15 goes into `game_state/`, this is the line that earns it.

## 4. The labels did not relax — they hardened

| | exp 14 (200w) | exp 15 (300w) |
|---|---|---|
| announces the secret with a label | 7 / 10 | **10 / 10** |
| labels the lie | 7 / 10 | 7 / 10 |
| labels the wanted self | 6 / 10 | 7 / 10 |
| opens *"You loved…"* | 10 / 10 | 10 / 10 |
| paragraphs answering several questions at once | 11 of 54 (20%) | **16 of 55 (29%)** |

So more room did not buy less form-filling. What it bought is **braiding**: the lie and the
destruction now arrive in the same paragraph rather than one per line. The *"The secret
is…"* label is now universal. If that phrase is unwanted in the final text, it has to be
forbidden in the prompt — length will not dissolve it.

All five questions are answered in 10 of 10 stories. That is the first clean sweep in the
series, and it is what cutting the sixth question bought.

## 5. Two defects in the raw output

- **Call 2 breaks person:** *"You called her 'Riri' when **we** were kids"* — first person in
  a second-person story. 1 of 10.
- **Call 5 has a run-together word:** *"when **Karabegged** you not to take the drawings off
  the fridge"* — the model dropped a space in "Karan begged". 1 of 10.

Both were found by reading. My first pass to count them by regex returned zero for both and
was wrong — the **fifth** time in this project a regex has mismeasured this material. Literal
string search confirmed them.

## 6. Fifth confirmation on names

Daniel in **6 of 10** again, Miriam in 3, Mira in 2. Identical to experiment 14's 6/10 on the
same inputs with a different prompt. Nothing on the prompt side has ever moved this.

## Recommendation

**This is the configuration to promote.** Five questions, 300 words, no sin named, no naming
tradition, craft rules in the system prompt. It is the first run where every question is
answered in every story, the death survives in 9 of 10, and the secret arrives as a physical
object.

Two things to fix before it goes into `game_state/`:

1. the *"The secret is…"* label, now in 10 of 10 — either forbid the phrase or accept it
2. nothing here has been **tested on a pair**. Still true since experiment 05, and now the
   only thing standing between this prompt and the game.
