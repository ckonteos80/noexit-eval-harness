# Promotion plan — experiments 15–20 into `game_state/`

The design agreed for taking the story-form character generation live. This is the input to
`/update-game`; it is not itself a change. Nothing here is in `game_state/` yet.

Status: **one question open — experiment 21.** Written 2026-10-01.

## The shape

Generation becomes two calls, and the response is no longer parsed.

```
name call   (Qwen3-8B @ 1.2)   -> char.name
story call  (GLM-5.3 @ 1.1, reasoning_effort="high")
                               -> strip_reasoning -> sanity check -> char.description
dialogue                       -> {NAME} + {CHARACTER_DESCRIPTION}
```

**Decided: whatever character generation produces passes directly as one variable into
dialogue.** No field extraction, no header parsing, no assembled bio.

## What this retires

| | |
|---|---|
| `extract_field` on the generation path | used only at `simulator.py:240` |
| `CHARACTER_FIELDS`, `parse_character_response`, `character_parse_complete` | no fields to parse |
| `assemble_bio` | the bio is the generation text |
| the parse-retry loop | replaced by the sanity check below |
| **Unity: the line-anchored `**` end marker port** | nothing to match |
| **Unity: the dash/space folding port** | nothing to match |
| **Unity: the nine-field rewrite port** | no fields |

Two of the three outstanding Unity ports are cancelled by this decision.

## What must survive

**`strip_reasoning` still runs on the generation response**, and matters more than before: with
pass-through, an inline `<think>…</think>` block goes verbatim into the dialogue system prompt
and nothing else inspects the text. GLM leaked none in twenty generations through the proxy,
but that is per-provider behaviour and the router load-balances, so the same model can answer
either way between two calls. Unity needs the same helper: strip `<think>…</think>` and an
unclosed `<think>` through end-of-string.

## The sanity check (replaces `character_parse_complete`)

`character_parse_complete` was not only a parser — it was the only test that generation had
succeeded, and it drove the retry. Pass-through removes it, so a truncated response, a
refusal, or a first-person story would go straight into the dialogue prompt.

A generation is accepted only if, after `strip_reasoning`:

| test | threshold | why |
|---|---|---|
| non-empty | — | obvious |
| word count | 150–450 | the 300-word prompt has produced 273–348 across experiments 17–20 |
| no `<think>` remaining | — | an unclosed block that stripping could not resolve |
| second person | at least **5** occurrences of `you`/`You` | experiment 20 produced one story entirely in the first person, 19 `I` and **zero** `you`; every sound story had 19–26 |

Retry budget: the existing `PARSE_RETRY_ATTEMPTS = 2`. The second-person threshold is set from
data — the one failing story scored 0 and the nearest sound story scored 19, so there is a
wide margin and no risk of rejecting good output.

## Code changes

### `game_state/` — the mirror, and therefore Unity

| file | change |
|---|---|
| `prompts.py` | `characterSetupSystemPrompt` + three craft paragraphs; `characterFullUserPrompt` replaced by the story prompt; anti-duplication block reworded for a prose bio; `{NAME_ORIGIN}` removed; new name-call prompt |
| `config.py` | `MODEL_GENERATION = "zai-org/GLM-5.3"`, `TEMP_GENERATION = 1.1`, new reasoning-effort constant, name-call model and temperature |
| `providers.py` | `call_proxy` forwards `reasoning_effort` |
| `assembly.py` | generation path returns the stripped text; the sanity check lives here |

### `tools/` — harness only

| file | change |
|---|---|
| `simulator.py` | the name call before the story call; stop calling `parse_character_response`; **the character-2 gate at line 225 moves from `other_char.occupation` to `other_char.description`**, or character 2 generation raises `RuntimeError` |

### Unity

1. `PromptsController.cs` — the new strings
2. `CharacterGenerator.cs` — temperature 1.1, `reasoning_effort`, the name call, no `ExtractField`, remove the name-origin pick
3. `CharacterController.cs` — bio is the raw string; character-2 gate on the bio, not occupation
4. `APIRequestHandler.cs` — send `reasoning_effort` and `timeout`; treat HTTP 500 as retryable, since the proxy masks every upstream status as 500
5. a `strip_reasoning` helper plus the sanity check

## Consequences accepted knowingly

- **The run record's nine per-character fields go empty** — `occupation`, `reason_true`,
  `want` and the rest. The viewer renders from the bio so it still works; historical runs keep
  theirs; anything keyed to a named field gets blanks.
- **Nothing downstream can query a structured fact about a character.** Fine for dialogue.
- `game_state` has been passing a naming tradition all along — `simulator.py:221` picks
  `random.choice(config.NAME_ORIGINS)` and the live prompt still has `{NAME_ORIGIN}`. The
  standing no-naming-tradition rule has only ever been honoured in experiments. This change
  removes it incidentally.

## Decided

**The name comes from the supply call** — `Qwen3-8B` @ 1.2, as in experiments 18–20. It gives
a name every time, which is what `{NAME}` needs.

Recorded so it is not rediscovered as a surprise: this call is the source of the name
collisions. Ten names in experiment 19 gave **nine beginning with E**, `Eleanor` three times,
and `Voss` — which also appears in experiments 15, 16, 18 and 20, across four different
models. It is a reliable name generator and not a varied one. Swapping it for a random draw
in code is a one-function change if the collisions become a problem; that option is parked
rather than closed, and it would touch the standing `NAME_ORIGINS` hold.

**The death distribution ships as it is.** Experiment 20's 4 of 10 suicides and 6 of 10
cardiovascular are accepted. Worth re-reading once characters are generated as a pair: the
risk is not any single death but three in one room.

## Still open

1. **Experiment 21** — asking for the name only, dropping gender and age from the identity
   line. One word change, and it matters more under pass-through than it did before: the
   opening ships into the dialogue prompt exactly as written, so *"You are Elizabeth Harper,
   female, 57."* becomes part of the character the dialogue model is handed. Experiment 20's
   line also produced two first-person breaks, one of them total.

## Verification before the version is called good

- a generated **pair** through `tools/webapp.py` — never done since experiment 05
- **a dialogue session on a story-shaped bio** — never tested at all; everything measured so
  far is generation quality, and the bio exists to feed dialogue
- the AI eval on the saved run
