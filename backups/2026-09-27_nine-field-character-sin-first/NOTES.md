# 2026-09-27_nine-field-character-sin-first

**Date:** 2026-09-27
**Previous version:** 2026-09-26_tolerant-field-extraction (restored to, after the gpt-oss experiments were reverted)

## State

Character prompt rebuilt: 9 fields, sin first, death folded into Life, loved/hated pair replaced by an open cast.

## Changes from previous version

The largest change to character generation since the single-call merge. The prompt
was rewritten by hand by the author, discussed and corrected in chat before any file
was touched, and tested in a scratch harness before being applied.

### The shape

Eleven fields became nine. Generation order is now:

```
Name -> Occupation -> Reason for Damnation True -> Self-told -> What you refuse to admit
     -> Life (ending with the death) -> Defining personality trait
     -> What you want from the others -> People in your life
```

**Removed:** `Who you loved`, `Who you hated`, `Cause of Death`.
**Added:** `People in your life`.

Three consequences follow from that:

- **The sin is now written first, and the life is written to produce it.** The old
  order built a relationship, then a death, then derived a sin. This inverts it: the
  damnation is the seed and everything below is composed knowing it.
- **The death has no field of its own.** It is the final sentence of the `Life`
  paragraph. The word cap rose 110 -> 150 to pay for it.
- **The single loved-and-hated person is gone.** `People in your life` takes an open
  cast, each with their own want. In testing this produced three named people per
  character instead of one, which is materially more for dialogue to interrogate.

### Constraints deliberately removed

All of the death rules are gone: the accident ban, the chance-cooperation test, and
`You did not intend to die`. This was a deliberate decision by the author to strip
accumulated constraints, made with the evidence in hand. Expect vehicle deaths to
return — see "Known risk" below.

Also gone: the anti-restatement rule on `What you want` (so wants may now name the
thing being avoided), and the `Sartre` register line in the system prompt.

### The system prompt

Near-unchanged. "chamber piece" became "theater play", the room is now explicitly
where the three "torture each other for eternity", and the Sartre sentence was cut.
The four rules — usable, named, load-bearing, everyone plausible — are untouched.

### Evidence behind the anti-duplication block

The block was rewritten rather than removed, after a scratch test generated both
characters **independently, with no block at all**. That test is the reason the block
still exists:

- Without it, both characters' refusals opened with the identical phrase
  *"You need to be seen as ..."*; both traits were the same idea (`need to win` /
  `needing to be right`); both wants sought the same thing; both deaths were cardiac.
- Both characters named a **José**. The name-collision rule lives in the block, and
  its absence produced a collision on the first attempt.

So the hypothesis that the block was *causing* the psychological sameness is
disproved: those are model priors that survive its absence. What the block
demonstrably prevents is name collision.

The rewrite drops three bullets that referenced deleted structure (the hold that
person had over you, and two about the old Cause of Death field) and adds two axes
that had measurably collapsed but were never covered: **the refusal** (the same fear
appeared in both characters of four consecutive runs) and **the trait**.

Its weakest line is the last: "Do not reuse their sentence shapes." Instruction-based
anti-duplication has failed every time it has been tried here. It costs nothing; do
not expect it to work. The structural alternative held in reserve is to show
character 2 a *summary* of character 1 — occupation, death kind, sin kind, refusal,
want, names used — instead of the full bio.

### Code changes outside prompts.py

Nine fields instead of eleven touched four files:

- **`game_state/assembly.py`** — `CHARACTER_FIELDS` rebuilt; `assemble_bio` signature
  10 args -> 8, with `People in your life` shown after `Occupation` and no
  `Cause of Death` section.
- **`game_state/game.py`** — `Character` dataclass: three fields out, `people` in.
- **`tools/simulator.py`** — field extraction, session snapshot, summary, the
  `assemble_bio` call and the `Character` construction.
- **`tools/export.py`** — the `Cause of Death` line in session notes.

`ui/run_viewer.html` needed nothing; it does not hardcode field names.

**The bio handed to the dialogue system no longer has a Cause of Death section.** The
death is inside the prose at the bottom. Anything downstream that expected that
heading needs checking — in this repo nothing did.

### Verified before snapshotting

- No references to `who_loved` / `who_hated` / `cause_of_death` remain outside `backups/`.
- All nine headings are present in the prompt's format block, in `CHARACTER_FIELDS` order.
- A stubbed end-to-end `generate_character` for both characters produces a correct bio,
  stores `people`, sets `characters_generated`, and writes a 13-key session snapshot.
- The anti-duplication block still appends for character 2 and no longer mentions
  removed structure.

### Known risk, recorded before the first run

**Deaths will probably drift back to vehicles.** The evidence: across 24 characters on
record, the two versions that carried the explicit negative fence produced 4/4 deaths
inside the corridor (a third dose of sleep medication, refused antibiotics, stopped
blood-pressure medication, a refused MRI) and zero vehicles. Every version without it
produced vehicles heavily. A scratch A/B of 12 samples reproduced this: the control
arm was 3/3 vehicle, fence-plus-register was 0/3.

That same A/B found the deeper problem the fence does not fix: **ten of twelve deaths
were suicides**, because "write a death where nothing had to go wrong for it to kill
you" is close to a definition of suicide, and it contradicted "you did not intend to
die". Both of those sentences are now gone, so the contradiction is gone with them —
but so is any death constraint at all.

The two samples that landed properly showed what the corridor actually is:
self-deception about a risk that was understood ("you told yourself you didn't need it
anymore"; "so you could afford to keep sending Aunt Clara fifty dollars each week").
If deaths need fixing after this version, that is the description to write, not
another prohibition.

### Also still open

- The refusal/trait/want monoculture is a model prior and survives with or without the
  block. The one mechanism with a proven record against a prior of this kind is
  randomising an *input*, the way `NAME_ORIGINS` broke a three-run name prior after
  four failed instructions. A per-character seed on the core fear is the obvious next
  experiment.
- The 150-word cap on `Life` is unlikely to hold; 110 was breached in 14 of 19 runs.
- The proxy masks every upstream status as HTTP 500, so `call_proxy`'s 503/504 retry
  has never fired.
- `max_tokens` is still dropped by the proxy.

## Unity files to update

- **prompts.py** -> PromptsController.cs -- all prompt strings
- **assembly.py** ->
  - CharacterController.cs -- prompt assembly / dialogue formatting
  - CharacterGenerator.cs -- ExtractField, bio assembly
- **game.py** -> CharacterController.cs -- session state, CharacterEntry

**Porting note:** this is the biggest Unity port outstanding. `CharacterGenerator.cs`
needs the new field list, the new `assemble_bio` order, and the removal of the three
deleted fields from `CharacterEntry`. It stacks on two earlier unported changes to
`ExtractField`: the line-anchored end marker from
`2026-09-20_housekeeping-extract-field-and-deprecations` and the dash folding plus
`<think>` stripping from `2026-09-26_tolerant-field-extraction`. Do not port any of it
until a run under this version has been judged good.
