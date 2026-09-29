---
description: Run a new prompt experiment end to end, or rebuild an existing one's views
argument-hint: <slug>  |  --views <folder>
---

Arguments: `$ARGUMENTS`

## If the first argument is `--views`

Rebuild the views for the named folder and stop. Nothing else.

```
python experiments/_view.py <folder>
python experiments/_doc.py  <folder>
```

Report the paths, and say which view suits where the user is reading — `view.color.md` with
Ctrl+Shift+V for VS Code, `view.ansi` for the terminal, `view.html` for a published page.

## Otherwise: a new experiment, `<slug>`

Read `experiments/CLAUDE.md` first. Then:

**1. Agree the change before spending credits.** State in the chat what is being varied and
what is held constant, and what the matched control is — an earlier experiment sharing the
same inputs is free. If more than one thing changes at once, say so plainly; it is sometimes
the right call, but it must be recorded.

**2. Scaffold** `experiments/NN_<today>_<slug>/`, NN being the next number. Copy the most
recent experiment's script as the template — it carries the current prompt, the craft rules,
the retry loop and the results format. Pin the model and temperature inside the script.

**3. Write the prediction into the script's docstring, before running it.** Concrete enough
to be wrong: counts, means, which arm wins. This is not optional and it is not written
afterwards.

**4. Run it.** Background the run. Transient HTTP 500/502 from the proxy is normal — the
retry loop handles it.

**5. Read every generation.** Print them in full and read them. Do not pattern-match. Then
write `tags.json` by hand, and `questions.json` if the script has not already.

**6. Build the views** with `_view.py` and `_doc.py`.

**7. Write `NOTES.md`**: the question, the setup, the prediction and where it was wrong, the
results with counts, and a recommendation. Where a number does not support a claim, say that.

**8. Update `experiments/README.md`** — a row in the index, the totals line, and anything
structural in **open threads**.

**9. Commit** the folder and the README together, with a message that states the finding
rather than the file list.

Report to the user: what landed, what the prediction got wrong, and the single most useful
observation. Offer the page rather than pasting the stories into the chat.
