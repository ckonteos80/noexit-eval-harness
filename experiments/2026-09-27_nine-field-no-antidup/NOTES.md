# 2026-09-27 — Nine-field prompt with no anti-duplication block

**Question:** is the anti-duplication block *causing* the sameness rather than preventing it?

The hypothesis was specific. Character 2 is the only one shown character 1's finished bio and
told not to repeat it. A model that reasons about structure might read that bio as a
*specification* rather than a warning — which would explain why `gpt-oss-120b` produced six
verbatim shared sentence frames, and why the collapse got *worse* as sampling tightened.

**Test:** generate both characters independently, with the new nine-field prompt and **no
block at all**, so character 2 never sees character 1. Any collision is then pure model prior.

## Setup

- Model `Qwen/Qwen3-235B-A22B-Instruct-2507` @ 0.95, pinned in the script.
- The nine-field prompt as finalised in chat, before it was applied to the project.
- 2 generations, one per character. Inputs drawn independently.
- 3,504 tokens for the pair — against ~6,500 on the eleven-field prompt.
- 9/9 fields parsed on both, no retries. The format block did its job.

Ran before `2026-09-27_nine-field-character-sin-first` existed, which is why the prompt is
inlined in the script rather than imported.

## Result: the hypothesis is wrong

**Mateo Rios** (36, Mexican, construction supervisor) and **Maria Silva** (65, Brazilian,
retired schoolteacher). With no block in play, these collided anyway:

- **Both refusals share their opening verbatim.**
  *"**You need to be seen as** right, even when people die because of it."*
  *"**You need to be seen as** a victim to feel worthy of love."*
- **Both traits are the same idea** — `need to win` / `needing to be right`.
- **Both wants are the same want** — *"Agreement, so you never have to face being wrong"* /
  *"to confirm that you were wronged."*
- **Both deaths are cardiac** — a heart attack at his own trial, a heart the paramedics
  could not restart.
- **Both characters have a José.** José Rios the brother, José Silva the husband.

So the block is not the source of the psychological monoculture — those are model priors that
survive its absence. What the block *does* demonstrably prevent is name collision, which
appeared on the first attempt without it.

## What was decided

The block was **rewritten rather than removed** in
`2026-09-27_nine-field-character-sin-first`. Three bullets referencing deleted structure were
dropped; the name rule was kept; and two axes that had measurably collapsed but were never
covered — the refusal and the trait — were added.

Its weakest line is the last, "Do not reuse their sentence shapes." Instruction-based
anti-duplication has failed every time it has been tried here. It costs nothing; do not
expect it to work. The structural alternative still in reserve is to show character 2 a
*summary* of character 1 — occupation, death kind, sin kind, refusal, want, names used —
instead of the full bio.

## Also observed

`People in your life` worked well and is the clearest gain of the nine-field design: three
named people per character, each with their own want, versus one relationship before. That is
materially more for dialogue to interrogate.
