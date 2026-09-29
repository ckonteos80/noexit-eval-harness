# 2026-09-29 — GLM-5.3 on experiment 15's prompt

**Question:** does a different model family write the story differently? GLM-5.3 is #6 on
EQ-Bench Creative Writing v3 with the lowest slop score of any open model on the board (8.4;
the Qwen3-235B family sits around 29). The router serves it through 7 providers, and its
license is effectively MIT for NoExit: the only extra condition is a Z.AI security review for
companies selling model access with over $10B in revenue.

One arm, five generations, one per input. Experiment 15's first pass (`rep == 0`) is the
matched control.

**Page:** the five pairs, Qwen then GLM, tinted by question — https://claude.ai/artifact/35RtMpd2wk3uFPx6KLZSAB

The same pairing sits in `glm-beside-qwen/` as `view.html`, `view.md`, `view.docx`,
`view.color.md` and `view.ansi`. It is built by `side_by_side.py`, then the shared
`_view.py` and `_doc.py`.

## Setup

- `zai-org/GLM-5.3` @ 1.1, identical to experiment 15 otherwise: the same system prompt plus
  craft rules, the same 86-word user prompt with five questions and a 300-word budget, and
  the same five inputs.
- The vendor recommends 1.0. 1.1 was kept so the model is the only variable.
- GLM-5.3 is a thinking model with three effort levels: `low`, `high`, `max`. Any other value
  or no value means `max`.

## Run 1: max effort, through the proxy, failed

- The proxy cannot forward `reasoning_effort` (pydantic drops it), so GLM ran at `max`.
- **Pair 0:** **97s**, **6,937 completion tokens**, 26,702 characters of reasoning, 288
  words of story.
- **Pair 1:** **HTTP 500 after 120.7s**, wrapping the router's `504 Gateway Time-out`. This
  is the same ~120s ceiling as experiment 01. The script stopped by design.
- The pair-0 story was **lost**: the script saved only at the end, as experiment 15's did.
  It now saves after every success.

## Run 2: high effort, direct to the router

- A `reasoning_effort` pass-through was added to the proxy and committed locally in
  `openai-proxy/`. It is **not deployed**: git push was rejected, and the stored HF token is
  read-only.
- This run therefore calls `router.huggingface.co` directly with the local token, sending
  exactly the body the updated proxy would forward. The proxy is a pass-through, so the
  output is comparable with experiment 15's.
- Two DNS failures on first attempts; both retried fine.

## Prediction, and where it was wrong

| prediction (in the script, before run 2) | outcome |
|---|---|
| 40–80s per call, all under 120s | **12.7–52.6s**, mean 27.8s. All under, faster than predicted |
| about half of max's thinking, ~3,500 completion tokens | **688–981**, mean 797. About an eighth of max, not half |
| story length unchanged | mean **319** words (304–333), 0 of 5 inside 300. Unchanged; Qwen's same five: 321, 1 of 5 |
| reasoning in a separate field, no `<think>` in content | **5 of 5 clean** |
| death ending in 5 of 5 | **5 of 5 stop at the death**, but only 3 say so (§4) |
| no "last lie"-style closing formula (from the run-1 docstring) | **Right:** 0 of 5. Qwen's same five had 0 too, so this was not tested |

## 1. Every question answered except one; half the braiding

All paragraphs were tagged by question, with the same method as experiment 15.

| | Qwen, exp 15 pass 1 | GLM-5.3 |
|---|---|---|
| paragraphs / tagged | 33 / 27 | 37 / 31 |
| stories answering Q1, Q2, Q3, Q5 | 5 of 5 each | 5 of 5 each |
| stories answering **Q4** (what kind of person you want people to think you are) | 5 of 5 | **4 of 5** |
| braided paragraphs (answering more than one question) | 11 | **6** |
| *"The secret is…"* label, by literal search | **4 of 5** | **1 of 5** |

- **Q4 is missing from pair 1**: the Ruth and Howard story never says how you want to be
  seen.
- **Pair 3's Q4 is weak.** It rests on Ruth calling you *"the only honest person she knew"*.
  That is someone else's view of you, not a stated wish.
- GLM also moves Q4 around rather than slotting it in after the lie. Two stories **open** on
  it: *"people called you the man who built half the churches in Kane County"*, and *"You
  were the one who made it."*
- In my reading, the form-filling that experiment 15 flagged loosens. GLM braids half as
  often and drops the *"The secret is…"* label in 4 of 5, so fewer paragraphs read as one
  answer per question. The page shows this directly: GLM's tints are mostly single colours,
  Qwen's mostly mixed.

## 2. The secret is an object in 4 of 5, against 2 of 5

This is experiment 15's headline finding, tested on a new model.

- **GLM's secrets are things someone could find:**
  - the box labelled in your own handwriting, *"Bell St. — certification, original"*
  - Howard's 1989 phone bill with the Chicago number
  - the bank statements in your filing cabinet, which your daughter finds
  - the ledger page in your jewellery box, then in your coat pocket
- The fifth is knowledge rather than an object: *"you knew."*
- **Qwen's same five inputs give 2 objects:** the voicemail and the voided ledger payment.
  The other three are acts or facts: *"you chose, calmly"*, the years of watching through
  the wall, the hidden half-sister.
- In GLM the object is also usually **physically present at the death**. The box is on the
  shelf you are climbing to. The letter is in your hand. The ledger page is in your coat
  pocket. For a game that wants props, that is the strongest result here.

## 3. Specificity: named places in every story, against none

All counts are literal. Years were matched as four-digit 19xx/20xx and checked by reading.

| | Qwen, same five | GLM-5.3 |
|---|---|---|
| stories naming a place | **0 of 5** | **5 of 5** |
| four-digit years | 1, in 1 story | **12**, in 3 stories |
| dollar amounts | 2, in 2 stories | 4, in 2 stories |
| protagonist named | **0 of 5** | **2 of 5**, plus 1 implied |

- **Places named by GLM** include Kane County, Toledo, Dayton, Rockford, Bathurst, Route 9,
  St. Brigid's and the Bank of Nova Scotia.
- **Named protagonists:** *"You are Dana Ruggiero"*; *"Eileen"*, with maiden name Voss. The
  implied one is the surname in *"Rourke & Son Construction"*.
- **This bears on the stage-two extractor.** Experiments 05–07 found the protagonist almost
  never named, which blocks the extractor's Name field. GLM names or implies a name in 3 of
  5 without being asked.

## 4. Deaths: all stop at the moment, most are the same death

- **All five stop at the death, but only three say so.**
  - Pair 1 ends *"when your right hand stopped working"*.
  - Pair 4 ends mid-dial: *"got as far as the area code"*.
  - Both are deaths only by implication.
  - Qwen's five all open their final paragraph with *"You died…"*. GLM's open with it in
    0 of 5.
- **The cause is a monoculture.**
  - GLM: heart ×3, stroke ×1, and a hand that stops working, which reads as a stroke.
  - Qwen's same five: heart attack, not stated, choking on your tongue in a courtroom,
    choking on blood in hospice, and an elevator cable.
  - Five of five cardiovascular is the kind of prior experiments 05–15 kept finding in Qwen,
    now appearing in GLM.

## 5. Names and priors

- **Daniel** in 2 of 5 (Daniel, Danny), against Qwen's 3 of 5 on the same inputs and 6 of 10
  in experiments 14 and 15. Experiment 13 found the name prior is keyed to the input, not
  the prompt; it now shows up across model families too.
- **Voss** is a surname in both pair-3 stories: Qwen's Linda Voss and GLM's Eileen Voss.
  Same input, different models, same surname.
- **GLM's own priors:**
  - **Ruth** in 2 of 5.
  - **Tuesday** as the day of disaster or death in 3 of 5.
  - Scaffolding, food-bank books and a contracting firm: three of five sins are money or
    paperwork in a small business.
- **Qwen's** Miriam, Mira and Linda do not appear in GLM.

## 6. Defects found by reading

- **GLM: none.** No person breaks (its only first-person "I" is inside quoted dialogue), no
  broken characters, no run-together words.
- **Pair 3 uses Canadian spelling:** *licence*, *jewellery*, *apologise*, *neighbours*. This
  is consistent with its Bathurst and Bank of Nova Scotia setting, not a defect.
- **Qwen's same five** carry the two defects experiment 15 found: *"when **we** were kids"*
  and *"Karabegged"*.
- Checked by literal search: ` we `, ` I `, ` my ` (space-delimited) and `U+FFFD`.

## 7. Speed and cost

| | seconds per call | tokens (5 calls) |
|---|---|---|
| Qwen | 4.8–6.4 | 4,412 |
| GLM `high` | 12.7–52.6 | 6,332 (3,987 completion) |
| GLM `max` | 97, then a 504 | 7,400+ for one story |

- GLM at `high` is 2–10× slower than Qwen. That is acceptable for generation, a
  once-per-session call that earlier versions ran at 12–26s, and too slow for dialogue.
- `max` is unusable through the router without streaming.
- Cost: run 2 used 6,332 tokens. Run 1 used about 7,400 for pair 0, plus an unknown amount
  for the timed-out pair 1, which the provider has likely billed. At GLM's cheapest router
  price ($4/M output) both runs together cost under 10 cents.

## Recommendation

§1–§4 are my reading. The page is there to check them against.

1. **GLM earns the full 10-generation run** at `high`, experiment 15's two passes, before any
   decision. Five stories cannot separate a real prior from chance. The things to settle:
   - the cardiovascular deaths (5 of 5)
   - Tuesday (3 of 5)
   - the Q4 drop (4 of 5)
   - the secret-as-object rate (4 of 5)
2. **If it holds, the case for GLM on generation is prop and specificity:** a findable
   secret present at the death, and named places, years and protagonists. It is not length
   or question coverage; those match Qwen.
3. **The death needs a push either way.** One line in the craft rules varying the cause, or
   naming it outright, would address both the monoculture and the implied deaths.
4. **Deploy the proxy change first.** It is committed in `openai-proxy/`. Nothing in the
   harness or Unity can use GLM until `jejunepixels/noexit-proxy` forwards
   `reasoning_effort`, and that needs a push with a write token.
