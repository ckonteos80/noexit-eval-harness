# experiments/

Scratch prompt experiments. One folder per experiment, named `NN_YYYY-MM-DD_short-slug`.

`NN` is a running sequence number across the whole project, so the folders always list in
the order they were actually run. The date alone is not enough — several experiments can
share a day, and alphabetical ordering of slugs then puts them in the wrong order. **The
highest number is the most recent.** Next experiment is `13_`.

These are **not** sessions. A session belongs in `runs/`, is generated through the harness,
is tagged with a `game_state/` version and is scored in `ui/run_viewer.html`. An experiment
here is the opposite: it calls the proxy directly with a prompt, model and temperature pinned
inline, touches nothing in `game_state/`, and produces no drift and no version. That is the
whole point — it lets a prompt idea be tested before anything in the project changes, and
only a winning variant gets promoted into a real version with a snapshot.

## What each folder holds

- **`NOTES.md`** — required. What question the experiment was asking, exactly how it was set
  up, what came back, and what was decided because of it. Written so that someone who was not
  there can tell whether a later idea has already been tried and what happened. Record the
  predictions made *before* the run, including the ones that turned out wrong; a wrong
  prediction on the record is more useful than a clean story afterwards.
- **The script**, exactly as it was run.
- **`results.json`** — the raw responses plus per-generation tokens, timing and inputs.
- Anything else worth reading, e.g. `full_text.md` for long prose output.

## Conventions

- **Pin the model and temperature inside the script.** Never rely on `config.py`, which may
  have changed since. Every experiment here should be reproducible from its own script.
- **Pair the inputs across arms.** Draw age, gender and naming tradition once per sample and
  reuse them in every arm, so a difference between arms is the variable and not the draw.
  Seed the RNG and print the inputs.
- **Import from `game_state` read-only** — for `PROXY_URL`, `NAME_ORIGINS`, `extract_field`
  and so on. Never write to it.
- **Write nothing to `runs/`.** These are not sessions and must not be tagged as if they were.
- **Record the token cost.** Every experiment here cost real credits.

## Index — oldest first

| # | experiment | n | question | outcome |
|---|---|---|---|---|
| 01 | `2026-09-26_reasoning-model-probe` | 2 | Can a reasoning model be used for generation? | HF router 504s at ~120s; gpt-oss-120b works at 2.7s; found the U+2011 heading bug |
| 02 | `2026-09-26_death-rule-ab` | 12 | Does restoring the negative fence fix accident deaths? | Fence works; but 10/12 deaths were suicides — the two death rules were near-contradictory |
| 03 | `2026-09-27_nine-field-no-antidup` | 2 | Is the anti-duplication block causing the sameness? | No. It survives the block's absence. The block does prevent name collisions |
| 04 | `2026-09-27_story-form` | 4 | Does free-form prose beat field-by-field generation? | Frame collisions drop sharply; but stories write the room and run 750–950 words |
| 05 | `2026-09-27_deadly-sin` | 10 | Does assigning a deadly sin reduce duplication? | No measurable effect on collision; its value is guarantee, not quality |
| 06 | `2026-09-27_word-budget` | 10 | Can a word budget shorten the story prompt? | Yes, treated as approximate (+5–10%); the cost is the cast, 120 names down to 44 |
| 07 | `2026-09-27_sin-at-600-words` | 5 | Does naming the sin matter at 600 words? | Yes — max collision 29 with a sin against 55 without. No effect at full length |
| 08 | `2026-09-27_temperature-sweep` | 15 | What temperature is best for the story prompt? | 1.1. Collision falls 35.0 → 21.2 from 0.7 to 1.1, then stops. Temperature never touches names |
| 09 | `2026-09-27_no-name-origin` | 5 | What does NAME_ORIGINS actually buy? | Keep it. Removing it raises collision and collapses the milieu — but it never reached the supporting cast |
| 10 | `2026-09-27_end-on-a-fact` | 10 | Can one line stop stories closing on their own verdict? | Yes — 10 of 10 across both arms, against 0 of 10. The single most effective prompt line tested |
| 11 | `2026-09-27_questions-not-instructions` | 10 | Do four questions beat instructions in the user prompt? | Yes, but no metric detects it — every new story opens on the person the sin destroys, every old one on a birth certificate |
| 12 | `2026-09-27_the-gaze-questions` | 10 | Swap "what would break the lie" for two questions about how you are seen? | Yes — the public self plus the evidence that destroys it. Shorter, but the worst collision in the series |

**Latest: 12.** Totals so far: 95 generations, roughly 145,000 tokens.

## Open threads these left behind

- **The story prompt does not reliably produce a name or an occupation** (05). Two of ten
  protagonists were never named; two more only inside someone else's dialogue. This blocks
  the planned stage-two extractor, which would otherwise invent names for a quarter of
  characters.
- **The closing-formula prior** (05) — *"you whispered, not to God, not to X, but to
  yourself… It was the last lie you ever told"* appeared verbatim across both arms. No input
  randomisation touches it.
- **The refusal monoculture** has survived a long prompt, a short prompt, two models, the
  anti-duplication block, no block at all (03), and randomised sins (05).
- **The proxy masks every upstream status as HTTP 500** (01), so `call_proxy`'s 503/504 retry
  has never fired in the project's history.
- **`max_tokens` is still dropped by the proxy** (06), so output length cannot be capped at
  the API at all — and on a reasoning model it would be the wrong lever anyway, since
  reasoning consumes the budget before the answer does.
- **The naming rule degrades under compression** (06): third-person pronouns per 100 words
  rise from 4.3 to 4.8 under a word budget, because a pronoun is shorter than a name.
- **The protagonist is usually unnamed** (05, 06, 07): one of fifteen 600-word stories names
  the character outright. This blocks the planned stage-two extractor, which needs a Name
  field, and it has not fixed itself across three experiments.
- **The supporting cast ignores `NAME_ORIGINS`** (09). Daniel appears in 7 of 10 stories and
  4 of 5 even with a tradition supplied, across four different traditions. The list governs
  the protagonist only. Temperature does not touch it either (08).
- **Timestamp prior**: `3:17` and `2:17 a.m.` keep recurring across unrelated experiments.
- **Naming traditions are switched off** by standing instruction from 2026-09-27. Without
  one, the name collapse is the worst measured (10): Daniel in 5 of 5, Robert in 4, and the
  surname `Voss` shared by two unrelated characters. Fixing it needs a randomised input one
  level down, not another instruction.
- **The verdict moved rather than vanished** (10). The end-on-a-fact rule governs the last
  sentence only; two of five stories still declare "Your sin is..." mid-story. The question
  rewrite in 11 may have fixed this, but the old prompt scored 0 on a re-run, so it is noise
  at n=5 and cannot be claimed either way.
- **Collision and word counts do not measure dramatic usefulness** (11). The clearest quality
  gain in the project registered as zero on every metric and was only visible by reading.
- **Occupations collide too, not just names** (12): two of five gaze stories make the character
  a child-protection worker. Worth measuring alongside names in future.
- **Nothing has been tested on a pair.** Every experiment since 05 generates characters
  independently. Whether these questions survive a second character who must differ from the
  first is untested.
