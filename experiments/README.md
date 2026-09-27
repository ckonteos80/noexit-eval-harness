# experiments/

Scratch prompt experiments. One folder per experiment, named `YYYY-MM-DD_short-slug`.

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
- **Record the token cost.** Every experiment below cost real credits.

## Index

| experiment | n | question | outcome |
|---|---|---|---|
| `2026-09-26_death-rule-ab` | 12 | Does restoring the negative fence fix accident deaths? | Fence works; but 10/12 deaths were suicides — the two death rules were near-contradictory |
| `2026-09-26_reasoning-model-probe` | 2 | Can a reasoning model be used for generation? | HF router 504s at ~120s; gpt-oss-120b works at 2.7s; found the U+2011 heading bug |
| `2026-09-27_nine-field-no-antidup` | 2 | Is the anti-duplication block causing the sameness? | No. It survives the block's absence. The block does prevent name collisions |
| `2026-09-27_story-form` | 4 | Does free-form prose beat field-by-field generation? | Frame collisions drop sharply; but stories write the room and run 750-950 words |
| `2026-09-27_deadly-sin` | 10 | Does assigning a deadly sin reduce duplication? | No measurable effect on collision; its value is guarantee, not quality |
