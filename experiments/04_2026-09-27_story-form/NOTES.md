# 2026-09-27 — Story form vs field-by-field, and does the system prompt earn its place

**Question:** every duplication measured so far is a *per-field frame collision* —
`"You need to be seen as…"` in both refusals, `", and that betrayal made you cling to her
memory"` verbatim in both hatred fields, `"Name — your relation, wanted X"` in both People
fields. Those collisions exist because two characters answer the same narrow question in the
same slot. **A story has no slots.** Does free-form prose reduce them?

Second question, asked at the same time because it is nearly free: **is the system prompt
helping or is it part of the problem?**

## Setup

- Model `Qwen/Qwen3-235B-A22B-Instruct-2507` @ 0.95, pinned.
- Two arms x two characters = **4 generations, 5,535 tokens**.
- Arm A: current `characterSetupSystemPrompt` + minimal story prompt.
  Arm B: **no system prompt at all** + the same story prompt.
- Inputs seeded and paired across arms: (French-Canadian, 40, m), (Chinese-American, 45, f).

Two deliberate choices in the user prompt: second person and name-everyone were **kept**,
because they are functional rather than stylistic — a pronoun about somebody absent gets
heard by the other characters as pointing at somebody present. And rather than asking for the
"coping mechanism" by name, it asked for the facts to be present *and* the whole thing told
the way the character tells it to themselves, so the truth stays recoverable underneath the
spin instead of the character narrating their own self-deception.

## Result: keep the system prompt

The no-system arm is worse on exactly what matters.

- Its character 1 has an affair, lies about it, and then his wife dies when **a truck
  hydroplanes across Route 15**. He is not damned for anything; the tragedy is weather.
- The self-justification layer is *absent* — no "you told yourself" beat anywhere in that
  story, where the with-system arm had nine across two.
- Twice the similes (6 and 3, against 3 and 0).
- Both no-system stories spend 300–400 words on childhood before reaching anything usable.

The four rules — usable, named, load-bearing, everyone plausible — are visibly doing work.

## Result: the story form works, with caveats

**What it gets right.** The true/self-told layering emerges as one living thing instead of
two fields:

> *"You told yourself it was normal. That's how things worked. You told yourself Claudine
> didn't care about rights."* … *"But — and this is the truth you swallow every morning — you
> went back to Étienne."*

Better than the two-field version had ever managed. And the sentence-frame collisions were
gone.

**Three problems, one fatal as written.**

1. **Both with-system stories wrote the room.** Jean-Luc wakes in four grey walls with two
   strangers. Eleanor wakes in a windowless room and finds **Lila Gupta and Daniel Reyes
   sitting in the chairs** — her own victims. That destroys the premise; the play depends on
   three strangers who do not know each other. The old prompt's *"Do not describe arriving
   anywhere. Stop at the threshold."* was load-bearing. Note the interaction: the no-system
   arm did *not* do this, because the system prompt describes the room and so invites writing
   it.
2. **Length: 754–956 words against 284 for the nine-field bio.** The bio is substituted into
   the dialogue system prompt on *every turn*, so that is roughly 3x the per-turn cost for a
   whole session, not a one-off.
3. **Plot-level collision persisted.** Both with-system characters weaponise a third party
   against someone they loved, and in both cases that person kills themselves — Claudine with
   pills in a motel, Lila walking into the Atlantic.

## What was decided

The story form is good raw material but cannot *be* the bio, so a two-stage design — story,
then extract the fields from it — is the right shape. Three fixes before stage two: keep the
system prompt, restore the threshold line, and cap or compress the length.

The threshold line was added for the next experiment and held: **0 violations in 10**.
