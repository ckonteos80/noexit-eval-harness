# Hell Is Other Chatbots — Eval Loop: Scoring Design Notes

*Working notes from the design session. Captures every decision made so far about how the automated evaluation loop will score character generation and dialogue. Nothing here is code — this is the design that drives the code. Keep this; drop it into the project or a fresh chat / Claude Code when building begins.*

---

## What this is for

The goal is a human-in-the-loop evaluation loop that measures whether prompt (and model) changes make the generated **characters** and **dialogue** more human and realistic — so good changes can be identified with scores rather than vibes, then ported to Unity by hand.

The load-bearing part of the whole project is **evaluation**, not the agent that tweaks prompts. An agent that rewrites prompts and swaps models is only as good as its ability to tell whether a change helped. These notes define that measurement.

Current priorities, in order: **character background generation**, **dialogue realism**, then **addressing** (which is measured differently — it has a correct answer, so it's scored as plain accuracy against hand-labeled examples, no subjective judge needed).

---

## Decisions locked

- **Two rubrics**: one for character generation (scored once per character, at "birth," before anyone speaks), one for dialogue (scored per reply).
- **Hybrid scoring**: practical dimensions are pass/flag; mood dimensions are a **1–3** scale.
- **1–3 scale must be anchored**: each point has a concrete description, or the scores drift. Anchors are written below.
- **Relative comparison for mood**: the highest-signal question is "did the new prompt's batch beat the old prompt's batch, head to head," not "did the score hit an absolute target." LLM judges are far more reliable at A-vs-B than at absolute ratings.
- **Dialogue judged per-reply to start.** Windowing (judging a short run of turns together) is deferred — added later for the three flow-dependent mood dimensions once the basic loop is proven.
- **Midpoint convention**: `2 = works but doesn't shine`, `3 = genuinely good`. So 3 is a real bar; most early replies land at 2, and improvement shows as 2→3 movement. (If we later want a harsher scale, reframe 2 as the failure midpoint — a one-word change across all anchors.)

---

## Why these choices (so future-me remembers the reasoning)

- **Why hybrid, not a uniform scale?** The practical dimensions (label leakage, frame breaks, length, restating known info) are genuinely binary and several are pure code — forcing them onto a 1–5 scale invents precision that isn't there. The mood dimensions are where gradient matters (incremental realism gains), so they get a scale. Spend the fragile, noisy judge budget only where nuance lives.
- **Why 1–3, not 1–5 or 1–10?** LLM judges are wobbly on fine scales. Finer than 1–3 is largely judge jitter and gives false confidence. Narrow + anchored is more trustworthy than wide + vague.
- **Why per-reply first?** Clean attribution (you know exactly which reply failed and on which dimension), simpler and cheaper to build, more data points per session for stable batch averages. The cost: three dialogue dimensions that are really cross-turn get scored on limited context (see parked items).
- **Why human-in-the-loop makes this comfortable:** with modest batch sizes and you eyeballing transcripts alongside numbers, judge noise hurts less, and there's no need for a single clean scalar to feed an automated optimizer. Numbers inform your judgment rather than replace it.

---

## Rubric 1 — Character generation

Scored once per generated character (except Distinctness, which is a pair-level property scored across both characters together).

### Practical (pass / flag)

1. **Parse & completeness** — every field the chain should produce came out and was extractable (Occupation, Cause of Death, Life prose, both Reasons for Damnation, the refusal, the trait, the want). *Fail:* a field is blank, malformed, or the `**marker**` structure broke.
2. **Distinctness from the other character** *(pair-level)* — the two people are genuinely different lives. *Fail:* same/adjacent occupation, same category of death, same category of sin, or wanting the same thing.
3. **Internal consistency** — the fields agree. *Fail:* the Self-told reason isn't a distortion of the True reason (different story, or identical); trait contradicts the life; want doesn't follow from who they are.
4. **Constraint adherence** — obeys the prompt rules: second person throughout, contemporary/realistic register, no fantasy/mysticism, plain-language occupation, Life paragraph stops at the threshold and doesn't describe arriving in a room. *Fail:* any violated.
5. **Length & format discipline** — Life prose in its ~80–100 word target; fields the right size. *Fail:* bloated or clipped.

### Mood (1–3, anchored)

**6. Reads as a real person**
- 1 — Template. Could be any "troubled person." Generic damaged-soul mush with no particular identity.
- 2 — Recognizable but familiar. A real *type* rather than a real *person* — competent but not specific.
- 3 — A specific contemporary human you could imagine meeting. Couldn't be swapped for someone else.

**7. Specificity of voice & texture**
- 1 — Abstraction only. "You made bad choices," "you hurt people." Gestures at a life without grain.
- 2 — Some concrete detail, unevenly. A real object or mannerism, floating in otherwise generic prose.
- 3 — Grained throughout. Exact detail — the object, the tic, the precise small cruelty — that makes the life feel lived.

**8. Psychological coherence of the sin**
- 1 — Cartoonish or disconnected. Mustache-twirling evil, or a sin that doesn't belong to this life; the triad is shallow or the "refusal" just restates the sin.
- 2 — Plausible but thin. The sin fits, but the self-told version is an obvious lie rather than a believable one, or the refusal doesn't cut deep.
- 3 — Fully coherent and deep. The self-told story is a lie *this person would actually tell themselves*, and the refusal names something true underneath that the sin was hiding.

**9. Thematic resonance**
- 1 — Wrong register. Gothic creep, supernatural, melodrama, or on-the-nose "I am damned because—."
- 2 — Correct register, no lift. Contemporary and realistic, fits, but doesn't evoke the *No Exit* weight.
- 3 — In the key and resonant. Damned by ordinary human failing, hell-is-other-people, without naming the play — and it lands.

**10. Dramatic potential**
- 1 — Inert. Agreeable, passive, or wants something so quiet nothing happens.
- 2 — Some pull. A want that could create friction, but muted or conventional.
- 3 — Charged. Wants something that will collide with the room — guaranteed friction, a person the scene needs.

**11. Concealment architecture**
- 1 — Nothing to hide. The self-told version equals the true version, or the truth is so bare there's no gap to guard.
- 2 — A gap exists but it's slight. Some distance between told and true story, not much tension in it.
- 3 — A real, load-bearing secret. Genuine distance between the flattering story and the true one — something worth concealing, that would cost them to admit.

---

## Rubric 2 — Dialogue

Scored per reply (plus minimal immediate context). The unit is "reply + its immediate preceding turn," not a bare line.

### Practical (pass / flag)

1. **No label leakage** — no structural tags in the reply (`<other_1>`, `[speaking to you]`, "Person 1," etc.). *Fail:* any scaffolding appears in what the character "says." (Known past failure mode.)
2. **Holds the frame** — no meta-commentary, no "as an AI," no narrating its own actions, no acknowledging a role. *Fail:* any frame break.
3. **Length discipline** — brief, within the token budget (currently 75). *Fail:* runs long or gets cut off mid-thought.
4. **Doesn't restate the known** — doesn't re-ask or repeat info it already has about the speaker. *Fail:* asking a name it already knows; re-explaining the established.
5. **Addresses the right person** — responds to who actually spoke and what they said. *Fail:* answering a question nobody asked, or replying to the wrong person. *(Seam with addressing — a failure here may really be an addressing failure upstream.)*

### Mood (1–3, anchored)

**6. In-character**
- 1 — Off. Generic voice that could be any of the three, or a tone that contradicts the bio.
- 2 — Consistent but flat. Not *wrong*, but doesn't strongly express this person.
- 3 — Unmistakably them. Trait, circumstances, and voice come through; couldn't be another character's line.

**7. Natural cadence**
- 1 — Clearly a chatbot. Over-helpful, tidy, explanatory, therapist-speak, balanced-and-agreeable.
- 2 — Passable but stiff. Human-ish, but with a whiff of the assistant register.
- 3 — Sounds like a person talking. The rhythm, incompleteness, and edge of real speech.

**8. Emotional coherence** *(context-limited per-reply — expect noise)*
- 1 — Wrong. Flat where there should be heat, or an emotional jump that doesn't track what was just said.
- 2 — Fine but muted. Emotionally plausible, not particularly alive.
- 3 — Tracks and lands. The feeling makes sense for who they are and what just happened, and it has charge.

**9. Concealment behavior** *(context-limited per-reply — expect noise; scores low until the prompt drives it)*
- 1 — Over-shares. Confesses the true sin, narrates their own psychology, hands over the interior.
- 2 — Guards unevenly. Holds some back but leaks more than they should, or offers the true version too readily when pressed.
- 3 — Withholds with intent. Guards the true sin, deflects or offers the self-told version, reveals slowly and reluctantly.

**10. Advances the room** *(context-limited per-reply — expect noise)*
- 1 — Inert filler. Pure agreement or "yes, this is hell" — deletable with nothing lost.
- 2 — Mild movement. Responds meaningfully but doesn't shift the dynamic.
- 3 — Does something. Creates friction, deflects with purpose, probes another character, changes the room's temperature.

**11. Thematic register**
- 1 — Breaks the key. Gothic, melodramatic, or on-the-nose "we're damned" narration.
- 2 — In-key, neutral. Contemporary and psychological, fits, but doesn't add resonance.
- 3 — In-key and charged. Holds the *No Exit* register and deepens it.

---

## Addressing (scored separately, later)

Addressing has a **correct answer** (who the player was actually talking to), so it does not need a subjective judge. Hand-label a small set of player messages against known character info — "addresses char 1," "addresses both," etc. — and score the addressing call as plain **accuracy**. Cheapest and most reliable of the three to iterate on; slot in once the batch runner exists.

---

## Parked items (not blocking; each has a trigger)

- **Concealment prompt addition.** Nothing in the dialogue prompt currently tells characters to withhold — it says stay in character and keep replies brief, but not "guard your true sin, offer the self-told version instead." So **Concealment behavior (dialogue #9) will score low in early runs by design.** That low score is the trigger: it confirms the prompt needs a concealment instruction. This is exactly what the loop is for — a new rubric dimension *and* a likely new prompt lever.
- **Windowing.** The three flow-dependent dialogue dimensions (8 Emotional coherence, 9 Concealment behavior, 10 Advances the room) are really cross-turn and are being scored on limited context under per-reply. Trigger to add windowing: if those three are where the judge and your own eye most often disagree, that's windowing calling. Windowing = judge a short run of 3–5 consecutive turns together for those dimensions only; practical checks and the static mood dimensions stay per-reply.

---

## Two levers the loop can pull (and one it can't)

- **Prompt text / structure** — lives in `prompts.py`. Free to restructure (split, merge, add/drop fields). This is the main lever for dialogue, addressing, character generation, narrator.
- **Model + temperature** — lives in `config.py` (currently all `Qwen2.5-7B-Instruct`). The model-sweep dimension is a `config.py` knob, not a prompt edit. Ties into the planned 7B→72B upgrade and OpenAI→HF migration.
- **Info extractor — the exception.** Its system prompt is in `prompts.py`, but its behavior is baked into the fine-tuned Qwen3-0.6B weights. The documented failures (atmosphere hallucination, 2nd→1st person reattribution, denial-as-fact) are training-data problems. The loop can **measure and flag** extraction failures and tweak the prompt at the margins, but can't truly fix them without new training data + retrain. Fine-tuning / dataset generation is a separate, later stage.

---

## Build steps still ahead

Roughly in order. The heavy lift is the simulated player, judge, and batch runner — restructuring prompts is trivial by comparison; the value is entirely in being able to measure.

0. **Stand up the harness in the sandbox, as-is.** Confirm `prompts.py`/`config.py` import; make one live call to the proxy and one to the extractor to confirm they respond and the `*.hf.space` egress allowlist isn't blocking. (Cheap place to catch the egress issue.)
1. **Capture a baseline.** Run current prompts to generate several character pairs + play a handful of dialogue exchanges by hand. Not scored yet — just see what "current quality" looks like, and calibrate the rubric/anchors against real output.
2. **Build the simulated player** — a capable model (frontier via API, or a large HF model) playing the human, with its own separate guidance (persona + goals + how much to reveal per turn). Start with 2–3 personas that stress characters differently (e.g. an over-sharer, an evasive antagonist). Prerequisite for running at volume.
3. **Write the anchors into a judge** — the anchors above become the judge's scoring guide. (Anchors already drafted — this step is wiring them in.)
4. **Add the judge + a small experiment store** — judge model ideally a *different family* from the Qwen models under test (avoid self-preference bias). Store = SQLite or JSON tracking prompts, models, scores, transcript path. Extend `session_viewer.html` to show scores alongside transcripts as the review surface.
5. **Fold in addressing** as the cheap objective win (accuracy against hand-labeled messages).
6. **Run the human-in-the-loop cycle** — you set batch size; run N sessions; master agent reads lowest-scoring transcripts, proposes specific prompt edits (or a `config.py` model swap); you approve; re-run same scenarios; compare; keep winners, revert losers. Nothing reaches Unity until you decide to port it.

### Environment split
- **This chat / sandbox** — good for the interactive, low-volume, judgment-heavy steps: standing up the harness, baseline, rubric/anchor work. Limits: everything accumulates in one context window; sandbox resets when the chat ends (no persistence).
- **Claude Code (later)** — for the batch, unattended, repeated steps: persistent codebase, survives sessions, manages long runs via compaction/subagents. The scripts + rubric developed in the sandbox become its starting point.
- Plan: rubric/baseline here → build the loop (player, judge, batch runner) in Claude Code.

---

## Harness recap (what already exists)

A Python harness mirroring the full Unity call flow, run against live HF infra (proxy for dialogue/addressing/narrator/generation; Qwen3-0.6B space for extraction). Files: `prompts.py` (all prompt strings, mirrors `PromptsController.cs`), `config.py` (endpoints/models/temps/tokens), `providers.py` (proxy + extractor HTTP wrappers, retry on cold start), `assembly.py` (pure prompt-assembly functions, reloads prompts each call), `game.py` (state, person mapping, dialogue history), `simulator.py` (orchestrator: generation chain, narrator, `run_player_turn`, transcript logging, `apply_prompt_edit`), `export.py` (zips outputs, writes session notes + Unity migration brief). Currently single-session and human-driven — the loop reshapes it into batch + simulated-player + scoring.
