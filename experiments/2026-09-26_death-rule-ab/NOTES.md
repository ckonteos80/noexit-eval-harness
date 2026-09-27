# 2026-09-26 — Death rule A/B

**Question:** the explicit negative fence had been deleted from the prompt in
`2026-09-13_experiment-no-examples`, which stripped *all* examples including the negative
ones. Every run since had produced vehicle deaths. Does restoring the fence fix it, and does
a register constraint fix the escalation the fence never addressed?

**This experiment started from a correction.** In the eval of `runs/2026-09-20_13372a1e.json`
I had written that the prompt "names weather explicitly — *No falls, no fires, no machinery,
no weather*" and called Ravi's flood death "the first breach since". Both were wrong: that
text had not been in the prompt since 09-13. I had marked a death down against a rule that
was already deleted. Checking the version history properly is what produced this experiment.

## Setup

- Model `Qwen/Qwen3-235B-A22B-Instruct-2507` @ 0.95, pinned in the script.
- **Character 1 only** (halves cost; the death is a character-1-visible property).
- 4 variants x 3 samples = **12 generations, 32,128 tokens**.
- Inputs seeded and shared across variants: (African-American, 27, m), (British, 62, m),
  (Greek, 57, m) — so origin/age are not a confound.

| variant | change |
|---|---|
| V0 | control, current prompt |
| V1 | negative fence restored verbatim, **without** the positive "write instead..." list |
| V2 | register constraint: "the kind that gets a two-line obituary, not a news story" |
| V3 | both |

The positive list was deliberately excluded from V1. Three of its four suggestions were
medical, and every death generated under the version that carried it was medical.

## Results

| variant | vehicle | "stopped taking..." | actually in-corridor |
|---|---|---|---|
| V0 control | 3/3 | 0/3 | **0/3** |
| V1 fence | 1/3 | 2/3 | **1/3** |
| V2 register | 2/3 | 1/3 | **0/3** |
| V3 both | 0/3 | 3/3 | **1/3** |

The fence works on what it targets — V3 eliminated vehicles entirely. But:

**Ten of the twelve deaths are suicides.** V0's Dimitri drove into oncoming traffic "knowing
the road well enough to know that doing it there would make survival impossible". V2's
Darnell sat in his car for forty-seven minutes before driving into the Detroit River. V2's
Dimitri had *practised the manoeuvre three times the week before*. Closing the accident wall
did not fix the deaths; it moved them from accident-suicides to medication-suicides.

**And the two rules are close to contradictory.** "Write a death where nothing had to go
wrong for it to kill you" is nearly a definition of suicide. A death that is (a) caused by
your decision, (b) certain, and (c) unintended is very nearly a null set, and the model
resolves the contradiction by dropping "unintended".

**Removing the positive list did not prevent the medical monoculture.** V3 was 3/3
"stopped taking [medication]". The fence's constraint space is narrow enough that the model
finds medication non-compliance on its own — so the earlier explanation, that the positive
examples caused it, was wrong.

## The two that landed, and why they matter

> *"You stopped taking your blood pressure medication because you told yourself you didn't
> need it anymore, and three weeks later, your heart failed while you were grading finals."*

> *"You stopped taking your heart medication so you could afford to keep sending Aunt Clara
> fifty dollars each week instead of using it for your prescriptions."*

Neither wanted to die. The lethality was real and **they believed it did not apply to them**.
That is the corridor: self-deception about a risk that was understood — not ignorance of it,
and not acceptance of it. It is the positive description the prompt never contained.

## What was decided

All death constraints were removed in `2026-09-27_death-need-not-belong`, on the author's
decision, with this evidence in hand. If a death rule is ever reinstated, the sentence to
write from is the self-deception one above — a positive description, not another prohibition.

**Prediction recorded at the time, which was right:** removing the fence would bring vehicle
deaths back. The first run after the rewrite had two internal-collapse deaths and I said I
had been wrong; the second run produced a wet on-ramp and a concrete barrier. The prediction
just needed a second sample.
