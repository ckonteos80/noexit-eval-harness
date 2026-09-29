---
description: Start a web session for hands-on play, then score the saved run
argument-hint: [--score-only]
---

Arguments: `$ARGUMENTS`

## Part 1 — the session

Skip this and go to Part 2 if `--score-only` was passed.

**1. Confirm the state is snapshotted.** Check the working tree against `backups/CURRENT`
(see `/snapshot`). If `game_state/` has drifted, say so before generating anything — an
unattributable run is wasted credits.

**2. Start the web UI** in the background and report the URL:

```
python tools/webapp.py
```

It opens a browser at `http://127.0.0.1:<port>/`. Restart it if `config.py`, `assembly.py`,
`providers.py` or `simulator.py` changed — only `prompts.py` is hot-reloaded.

**3. Hand the session to the user and stop.** Generate the character pair if they ask, but
**do not play the dialogue.** The user does the hands-on probing themselves; a scripted test
conversation is not what they want and tells them nothing they trust. Say the UI is up, say
which version is live, and wait.

## Part 2 — the eval

When the user says the run is saved, or asks for the eval:

**4. Find the newest run** in `runs/` and read it whole — every turn, both characters, the
narrator line. Note the model actually served, not just requested.

**5. Score it against `docs/character-eval-guide.md`.**

Write it as a director or screenwriter giving a first impression: what the pair is, whether
these two people could hold a room, where it goes dead, what you would cut. Not an itemised
checklist, not a rubric with numbers per axis. Quote the lines that earn the judgement.

**6. Say what is structural rather than a bad roll.** Anything that would recur across runs —
a collision the prompt causes, a refusal pattern, a closing formula, a name prior — is a
finding. Append it to the **open threads** list in `experiments/README.md`, where it survives
this conversation.

**7. Offer the run viewer** — `ui/run_viewer.html`, opened on the run's JSON — rather than
pasting the transcript into the chat.
