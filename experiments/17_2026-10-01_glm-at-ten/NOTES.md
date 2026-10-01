# 2026-10-01 — GLM-5.3 at ten generations, through the proxy

**Question:** experiment 16 made four claims off five stories. Do they hold at ten?

It also ran direct to the router, because the proxy dropped `reasoning_effort`. That change
is deployed now (`openai-proxy` f92e941, pushed today), so this run goes through
`config.PROXY_URL` — the path the game uses.

Ten generations: experiment 15's five inputs, each twice. Experiment 15 is the matched
control — same prompt, same temperature, same inputs, Qwen instead of GLM.

## Setup

- `zai-org/GLM-5.3` @ 1.1, `reasoning_effort="high"`, through the proxy.
- 10 of 10 first time, no retries. 12,384 tokens.
- Mean **7.1s** per call (4.9–10.4), 769 completion tokens. No `<think>` leaked into content.

## Prediction, and where it was wrong

| prediction | outcome |
|---|---|
| cardiovascular deaths 6–8 of 10 | **10 of 10.** Wrong, and in the worse direction |
| Tuesday 4–6 of 10 | **4 of 10.** Right |
| Q4 answered 8 or 9 of 10 | **10 of 10.** Slightly under |
| secret as a findable object 7–8 of 10 | **10 of 10.** Wrong, in the better direction |
| named or implied protagonist ~5 of 10 | **5 of 10.** Right |
| 13–55s per call, mean near 28 | **4.9–10.4s, mean 7.1.** Badly wrong — 4× faster |
| mean near 319 words, 0–2 inside 300 | **304 mean, 3 inside.** Close |

Two of seven were badly wrong, and they are the two that decide this.

## 1. The secret is a findable object in 10 of 10

Experiment 15's headline finding, at 4 of 5 in experiment 16, does not shrink. It goes to
ten of ten:

> the invoices you put on your brother's desk · the folder of your mother's bank statements ·
> a photoshopped account statement · three drafts in the bottom drawer, in his handwriting ·
> the second set of statements in the gun safe · the ledger, 96% deleted · a quarterly
> statement reading $312,440.17 on an account still titled *Marcus D. Trust* · a packed duffel
> in the rafters with the ferry ticket still in the pocket · the batch verification logs ·
> a half-written email saying *I need to tell you what actually happened*

**And the object is usually in the room when you die** — the folder taken out of the drawer,
the statement open on the table, the copies still in your hand, the phone unlocked on the
unsent email. For a play where two people have to find each other out, that is the strongest
result the series has produced. Qwen on the same five inputs gave 2 objects out of 5.

## 2. Every question answered, Q2 once excepted

| | Qwen, exp 15 | GLM, exp 17 |
|---|---|---|
| Q1 who did you love | 10/10 | 10/10 |
| Q2 how the sin destroyed them | 10/10 | **9/10** |
| Q3 the lie | 10/10 | 10/10 |
| Q4 what kind of person | 10/10 | 10/10 |
| Q5 the secret | 10/10 | 10/10 |

Q4's wobble in experiment 16 was noise. The Q2 miss is pass 2, pair 0: the sin has no living
victim — the money is stolen from a foundation named after the narrator's drowned daughter,
so what it destroys is a dead child's memory and an anonymous public.

**Braiding did not halve.** Experiment 16 reported 6 braided paragraphs against Qwen's 11, and
read it as the form-filling loosening. At ten it is **20 of 55 tagged paragraphs, 36%** —
higher than Qwen's 29% in experiment 15. That claim was a five-sample artefact.

## 3. The deaths are one death, told ten times

Every story ends cardiovascular. Not 5 of 5 as a small sample, but **10 of 10**: an aorta
tearing mid-toast, an aneurysm, three named strokes, a heart stopping on the stairs, and four
that never name it because they all use the same sentence —

> **"your left arm went numb"** — literal, in 4 of 10

This is worse than experiment 16 could see, and it is now the clearest defect in the output.
It is also a closing formula, the thing experiment 10's *end on a fact* rule was written to
kill. The rule is still working — the last line is an event — but the event is the same event.

Qwen's ten on these inputs: a courtroom choking, an elevator cable, hospice, a hydroplane,
heart attacks. Varied, and less interesting sentence by sentence.

## 4. What GLM gives up: the opening

Experiment 11's gain was that **every story opened on the person the sin destroys**. Qwen held
that 10 of 10 across experiments 11–15. GLM opens that way **once in ten**. Instead it opens
on the self —

> *"You are Diane Wechsler, sixty-four, and your sin is greed."*
> *"You are Marcus Aldridge, and you have been a very good surgeon for thirty-one years."*

Two stories name the sin outright, though the prompt never names one. The named-protagonist
rate — 5 of 10, against Qwen's 0 of 10 — comes from the same habit, and it is the thing that
would unblock a `Name` field. **The same habit is both the gain and the loss.**

## 5. The priors are keyed to the input, across model families

| | |
|---|---|
| `$410,000` embezzled from family | pair 1, **both passes** — spelled out in one, digits in the other |
| `Voss` as a surname | 2 of 10 — and in Qwen's exp 15, and in GLM's exp 16 |
| `Route 9` | 2 of 10 — and in exp 16 |
| `Priya`, aged twenty-six both times | 2 of 10 |
| `thirty-one years` in the job | 3 of 10 |
| `Danny` / `Daniel` | 5 of 10 |
| `Karen`, `Ruth` | 3 of 10 each |

Experiment 13 found the name prior keyed to the input rather than the prompt. This shows the
same for a **figure** and a **street**, across two model families, on the same inputs. Pair 1
produced a $410,000 embezzlement from a family member in both passes, with different names
and a different victim.

**And the sins collapse too:** 6 of 10 are financial crimes, and 5 of 10 end with someone
innocent losing a career, a licence or six years in prison for what the narrator did.

## Recommendation

**GLM-5.3 wins on the thing the game needs and loses on variety.**

1. **The prop case is now proven at ten**: a findable secret in 10 of 10, usually physically
   present at the death. Qwen does not do this.
2. **Speed is a non-issue** — 7.1s mean through the proxy, against the 12–26s earlier
   generation versions ran at. The 120s ceiling is nowhere near.
3. **The death monoculture must be fixed before promotion, whichever model wins.** One craft
   line naming the cause, or forbidding cardiac and cerebrovascular deaths outright. Ten of
   ten and a repeated sentence is not a sample artefact.
4. **The opening is a real loss.** Experiment 11's gain was worth having. A craft line
   restoring it — open on the person, not on yourself — may also cost the names, since both
   come from the same habit. That trade needs its own experiment.

Next, unchanged: the `{NAME}` and field-extraction decision, which blocks promotion whichever
model is chosen.
