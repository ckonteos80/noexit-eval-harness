# 2026-09-29 — six questions at 200 words, with the secret asked outright

**Question:** experiment 13's tagging pass found the gaze question answered in only 4 of 10
stories. Does asking for the secret *directly* get it, and does the whole thing survive at a
third of the word budget?

One arm, 10 generations, same five inputs as experiments 12 and 13, each run twice.

## Setup

- `Qwen/Qwen3-235B-A22B-Instruct-2507` @ 1.1, no sin named, no naming tradition, craft rules
  in the system prompt (second person, name everyone, stop at death, end on a fact).
- User prompt 102 words, **six** questions, budget **200** (was 600).
- Three changes at once against experiment 13's KIND arm: the budget, the new secret
  question, and the gaze question moving to last. Differences cannot be attributed to one.
- 10 generations, 7,891 tokens. Several transient 500/502s from the proxy; all retried clean.

The new question list:

```
Who did you love?
How did your sin destroy them?
What lie did you have to tell yourself and others to keep going?
What kind of person do you want people to think you are?
What secret would make everyone see you for what you really are?   <- new
What kind of person would they think you are, if they knew your deepest darkest secret?
```

## 1. Asking for the secret works — 10 of 10

Every story delivers a concrete, hidden, criminal fact. Against **4 of 10** for the gaze
question in experiment 13, at three times the length.

> *"The secret is that you called the tow company and gave the wrong location. You stood in
> the kitchen, snow falling outside, and let the phone ring in your hand until the line went
> dead."*

> *"The secret is this: you kept David's last text — I'd never touch her — and deleted it.
> Not because you believed him, but because you couldn't bear Miriam to be someone who
> lied."*

Asked how they would be *seen*, the model shrugs. Asked what the *secret is*, it produces
the forged bank records, the unplugged oxygen machine, the burned will, the lit match.
**The concrete question is the one that gets answered.**

## 2. It cannibalises the question after it — 1 of 10

The last question, "what kind of person would they think you are", is answered exactly once:

> *"If they knew, they'd see you as a predator. Calculating. Patient. The kind of man who
> lets his brother freeze, then wears his coat."*

Nine stories skip it. Once the secret is on the table the model treats the verdict as
redundant — which it largely is. **The two questions compete, and the concrete one wins.**
Asking both buys nothing; it costs words that 200 does not have.

## 3. At 200 words the question list becomes the skeleton

The stories stop being stories and become filled-in forms. Counting literal openers:

| label | stories |
|---|---|
| "The secret is…" / "The secret no one knows" / "Your deepest darkest secret" | 7 / 10 |
| "The lie…" | 7 / 10 |
| "You wanted people to think…" | 6 / 10 |

Most answer in the prompt's order, one paragraph per question. At 600 words the same
material was woven through the prose — that is exactly why three regex passes failed to
find it in experiments 12 and 13. **Compression trades drama for legibility.** Whether that
is a loss depends on what the text is for: as prose it is flatter, as a dossier two
characters could carry into the room it is far easier to read.

One story leaks the prompt's own words into the page: *"Your deepest darkest secret: you
rehearsed the lie before brushing your teeth."* The seam is showing.

## 4. The cost: compression breaks the ending in 3 of 10

| | |
|---|---|
| pass 2, pair 2 | never dies. Ends on *"You called 911 only after ten full minutes had passed."* |
| pass 1, pair 1 | no death scene; ends at the funeral, *"they said you died of grief."* |
| pass 2, pair 4 | funeral in one paragraph, then dies at the scene afterwards — broken order |

All ten of experiment 13's 600-word stories ended on a death. At 200 the model spends its
budget answering six questions and runs out before the ending it was told to write.

## 5. Length control, again

Mean **232** words, range 193–274, **1 of 10** inside the cap — 16% over. Same behaviour as
the 600-word budget, at the same rough proportion. The number steers, it does not bind.

## 6. Fourth confirmation: the name prior is keyed to the input

| name | stories |
|---|---|
| Daniel | 6 / 10 |
| Miriam | 4 / 10 |
| Clara | 3 / 10 |

New question set, new length, new structure — same names. Temperature (08), dropping the
naming tradition (09), restructuring the prompt (11), rewording the questions (13) and now
rewriting the whole thing have all failed to move this. It is not a prompt problem. Handle
names in a separate pass.

## Recommendation

1. **Keep the secret question.** It is the single most effective change since the gaze
   questions went in, and it is the only one that has ever produced a 10-of-10 result.
2. **Drop the final "what kind of person would they think you are".** With the secret asked
   outright, it earns one hit in ten.
3. **Raise the budget to ~300.** 200 is where the death ending starts to fall off the end.
   Five questions at 300 is the configuration I would test next.

## Two small notes

**One generation came back with a broken character.** Pass 1, pair 3 contains
`she wasn<U+FFFD>t` — the provider returned a replacement character where an apostrophe
should be. One occurrence in 115 generations across every experiment in this folder, so it
is rare, but it would have landed in a character bio unaltered. Left in the results as
returned rather than repaired.

**Page:** the ten stories, tinted by question — https://claude.ai/artifact/Tyqre9mgkq2GnBjZyHGQU7
Tagging: 54 of 64 paragraphs carry a question, and 11 of those answer more than one at once.
Every question is answered in 10 of 10 stories except Q6, which is answered in 1.
