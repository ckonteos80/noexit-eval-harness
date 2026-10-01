# 2026-10-01 — getting a name out of the story, by a second call

**Question:** promotion is blocked because `dialogueSystemPromptTemplate` needs `{NAME}` and a
300-word story supplies one half the time. Two second-call mechanisms, tested against each
other.

- **Arm A — supply.** A cheap call (`Qwen3-8B` @ 1.2) invents a name from age and gender; it
  goes into the story prompt as a given, beside Age and Gender. Ten fresh generations on
  GLM-5.3 @ 1.1, `high`.
- **Arm B — extract.** The existing info extractor (`Qwen3-0.6B`, the Space Unity calls as
  `InfoExtractorHandler.ExtractInfo`) reads experiment 17's ten stories and is asked for the
  protagonist's name. No new generations.

14,315 tokens for arm A. Arm B is free — a separate Space with no usage reporting.

## Prediction, and where it was wrong

| prediction | outcome |
|---|---|
| A1. the story uses the supplied name in 9–10 of 10 | **5 of 10.** Badly wrong |
| A2. supplied names break the input prior, 0–1 repeats | **Wrong.** Eleanor ×3, Clara ×2, Silas ×2, Hale ×2 — and `Silas Voss` |
| A3. deaths stay cardiovascular | not re-counted; not this experiment's question |
| A4. the opening gets no better | **Right, and it is the finding.** See §3 |
| B1. the extractor finds a name in about 5 of 10 | **5 of 5** where one exists — better than predicted |
| B2. where it answers, it is right | **Wrong where no name exists.** See §2 |

## 1. Supplying the name works exactly half the time

Five of ten stories adopt the supplied name. Every one of them opens the same way:

> *"You are **Silas Vega**. You tell people you built Vega Capital from a folding table…"*
> *"You are **Clara Thorne**, forty-five. You loved your mother, Dolores…"*
> *"You are **Eleanor Grace**, and for thirty-one years you ran Gracewood Manor…"*

The other five ignore it completely and name no one:

> *"You were with your mother, Margaret, every day for the last four years of her life."*
> *"You loved Jean, your younger sister, who called you Nell."*

**A name in the prompt does not become a name in the story.** It becomes an opening — or
nothing.

## 2. The extractor finds a real name, but cannot report its absence

Two mistakes of mine had to be cleared first, and both are worth recording:

- **My first arm B run returned `none` ten times out of ten**, which looked like a broken
  extractor. It was my prompt. Adding *"if the story never gives that person a name, return
  exactly: none"* makes the 0.6B model answer `none` to everything, including
  *"You are Diane Wechsler, sixty-four."* Removing that clause fixes it entirely. **Do not
  offer a small model an escape hatch; it will take it every time.**
- **Feeding it the whole 300-word story** degrades it — it returns a summary of whichever
  paragraph it liked. The first paragraph alone is what works.

With the short prompt, on first paragraphs:

| | result |
|---|---|
| protagonist **is** named (5 stories) | **5 of 5 extracted correctly** — Diane Wechsler, Dana Ruiz, Marianne Colby, Frank Doherty, Marcus Aldridge |
| protagonist is **not** named (5 stories) | **1 of 5 correct.** The other four return someone else's name |

Those four failures are the dangerous part. The story with no protagonist name returns
`Tom Kessler` — the husband she murdered. Another returns `Claire`, the daughter. Another
`Marcus`, the son. **A confidently wrong name is worse than an empty one**, because nothing
downstream can tell the difference: the dialogue prompt would say *"Your name is Tom
Kessler"* to the woman who killed him.

## 3. The two mechanisms want opposite things

The five stories that take the supplied name open *"You are &lt;name&gt;"*. The five that
refuse it open on the person the sin destroys — *"You loved Jean, your younger sister"* —
which is experiment 11's gain, the single clearest quality finding in the series.

So the trade experiment 17 noticed is now mechanical, not incidental:

> **a story that names its protagonist is a story that opens on itself.**

Supplying the name does not break the trade. It just decides which half of it you get.

## 4. A separate call does not break the name prior either

Ten names from a dedicated call at temperature 1.2: **Eleanor three times**, Clara twice,
Silas twice, Hale twice as a surname — and `Silas Voss`, the third experiment running in
which `Voss` appears, now from a different model (`Qwen3-8B`) than the two that produced it
before. The prior is not the story prompt's fault and not GLM's; it is in the weights.

## Recommendation

**Supply the name, and use the supplied value for `{NAME}` directly. Do not extract.**

The realisation that falls out of §1 and §2: *the story does not need to use the name.*
`{NAME}` is needed by the dialogue prompt, and the supply call already gives it
deterministically, 10 of 10. Extraction only exists to recover something we would otherwise
have thrown away — and it fails in the one case that matters, silently and confidently.

This unblocks the promotion. The remaining field question is narrower than it was: `{NAME}`
is solved; what `assemble_bio` does with a story instead of seven labelled sections is not.

Worth testing next, as experiment 19: **one craft line requiring the story to use the name it
is given.** If it closes the 5-of-10 gap without costing the *"You loved…"* opening, both
halves of §3 can be had at once. If it cannot, the opening is worth more than the
consistency — the name is already in hand either way.

## Note on views

No tinted views were built here. `results.json` holds two arms plus two extraction tables
rather than ten comparable stories, and the finding is tabular. The arm A stories are under
`arm_a` if they are worth reading side by side later.
