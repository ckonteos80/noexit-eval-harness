# NoExit Agents

A Python harness that mirrors, call for call, the LLM calls a Unity game makes. Three
strangers wake in a room in hell and talk. This repo is where the prompts, models and
generated characters are built and tested before they are ported back into Unity.

## The map

| | |
|---|---|
| `game_state/` | **the mirror.** Every file has a Unity counterpart. Changing it changes the game |
| `tools/` | harness only — simulator, web UI, version management, export. No Unity counterpart |
| `experiments/` | prompt A/B runs. Scratch: never writes to `game_state/`, `runs/` or `index.sqlite` |
| `backups/` | version history of `game_state/`. `backups/CURRENT` names the live version |
| `runs/`, `index.sqlite` | saved sessions |
| `docs/` | the change process, the eval guide, the Unity integration brief, the craft references |
| `ui/` | `webapp.html`, `run_viewer.html` |

## Non-negotiable

**Read `docs/CHANGE_PROCESS.md` before editing anything in `game_state/`.** Short form: check
for drift against `backups/CURRENT` → make the change → **snapshot before generating a single
run** → fill in the NOTES → generate and evaluate. A run generated from an unsnapshotted state
cannot be attributed to anything, and that is the whole point of the version history.

Experiments pin their own model and temperature inside the script, so they stay reproducible
after `config.py` moves on.

**No naming tradition is passed to character generation.** Standing since 2026-09-27, until
the user lifts it.

## Things that cost a session an hour if it does not know them

- **Only `prompts.py` is hot-reloaded** (`assembly._reload_prompts`). Edits to `config.py`,
  `assembly.py`, `providers.py`, `simulator.py` or `webapp.py` need the server restarted.
- **The proxy masks every upstream status as HTTP 500.** A 503 or 504 arrives as a 500, so
  the 503/504 retry path in `providers.call_proxy` has never fired in this project's history.
  Transient 500/502 bursts are normal — retry and they clear.
- **The proxy silently drops `max_tokens`, `top_p` and `reasoning_effort`.** Pydantic v2
  discards undeclared fields, so output length cannot be capped at the API at all. Ask for a
  word budget in the prompt instead and expect 4–16% over it.
- **The HF router times out near 120 seconds** on a single call. Generation sends
  `PROXY_TIMEOUT_GENERATION = 300` and the proxy honours it, but the router is the real
  ceiling.
- **Temperature range is 0–2**, not 0–1.
- Reasoning models spend `max_tokens` on reasoning before answering, and return it either in a
  separate `reasoning` field or inline in `<think>` tags, depending on the provider.
  `assembly.strip_reasoning` handles the inline case.

## Measuring generated text

**Read it. Do not regex it.** Five separate regex passes in this project have counted a
surface pattern and missed what the text was actually doing — experiments 06, 12, 13 and 15,
where a pattern found 3 of 10 cases and reading found all 10, and where a defect search
returned zero for two defects that were plainly there. A literal string search is fine. A
regex standing in for a judgement is not.

## Commands

- `/experiment <slug>` — scaffold, run, tag and write up a new experiment; `--views <folder>`
  rebuilds an existing one's views
- `/snapshot` — version `game_state/` and report what Unity still needs
- `/eval` — start a web session for hands-on play, then score the saved run

## More

- `experiments/CLAUDE.md` — conventions, the run checklist, the viewers
- `game_state/CLAUDE.md` — the mirror, snapshots, outstanding Unity ports
- `experiments/README.md` — the index of every experiment and the **open threads** list.
  New findings go there, not in a chat transcript. A transcript is compacted and lost; that
  file is not.
