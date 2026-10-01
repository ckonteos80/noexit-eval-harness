# Character Generation — AI Eval Guide

## What this is for

One note and one verdict per character. That is the whole output: a short written reaction,
and **good / neutral / bad**. No sub-scores, no pass/flag list, no per-axis ratings — the
viewer's form takes exactly this and nothing else.

Write the note the way a director writes after a first read: what you actually felt, and the
line or detail that caused it. If you find yourself producing a checklist, stop — a checklist
is what this replaced.

As of `2026-10-01_story-generation-glm-pass-through` a character is **a 300-word story in the
second person**, not a set of labelled fields. There is nothing to check for completeness; the
harness already rejected anything empty, too short, too long, or written in the first person
before it reached you.

## The note

Read the story once, at reading speed, and write what you are left with.

The question underneath everything: **does this feel like a person, or like parts?** A
character can be perfectly consistent and still be assembled. Test it by lifting things out —
could this job, this house, this dead brother be dropped into a stranger's life without
anything else changing? If yes, you have a set of good parts rather than a life.

Things worth naming when they snag you, not as a list to walk but as the kind of thing that
usually causes the feeling:

- **The lie against the truth.** The story says what the sin did, and what the narrator told
  themselves to keep going. The lie should keep every fact and move only the motive, and you
  should be able to point at the exact fact it bends. If the self-told version is a *different
  story* rather than the same story told differently, that is the failure worth naming — the
  whole play is whether they ever stop living in it.
- **The secret.** It should be something a person could find — a voicemail, a ledger page, a
  packed duffel in the rafters with the ferry ticket still in the pocket. A secret that is only
  a feeling gives the other two people in the room nothing to catch them with.
- **Gestures without content.** "Afraid the truth would come out" — what truth? Name it where
  the story will not.
- **Anything the story was asked for and quietly skipped.** It was asked who they loved, what
  the sin did to them, the lie, how they want to be seen, and the secret. A missing one usually
  reads as thinness rather than as an absence, which is why it is worth looking for.
- **Register breaks.** Second person throughout, contemporary and realistic, stops at the
  death, does not describe arriving anywhere or the room.

The death is **exempt** from the connectedness test, as of 2026-09-27. It does not have to be
caused by the character or connected to anyone. A death that is simply what happened to them
is fine. A death that *is* intrinsic is a bonus, not a requirement.

## The verdict

**good** — you would put this character on stage. Specific, the lie bends a nameable fact, and
you could not swap it for someone else.

**neutral** — competent and familiar. A real *type* rather than a real *person*. Nothing wrong
with it; nothing that makes you want to watch them.

**bad** — a construct. Generic damaged-soul material, abstraction instead of grain, or a lie
that is really just a second story. Also bad if it broke register badly enough that you
noticed the prompt rather than the person.

When you are between two, pick the lower one and say why in the note. The scale is only useful
if **good** stays expensive.

## The pair

The viewer has one slot for the pair as well. Same shape: one note, one verdict.

Read both stories back to back, as if casting two actors for the same scene. Do they feel like
two people, or did the writer open the same drawer twice? Look for shared surnames, the same
kind of person in the loved slot, the same category of work or sin or death, and for phrasing
that echoes between them without either character meaning it. If you could move a detail from
one into the other and nothing would feel wrong, that is the tell.

This is the part the generation prompt has the least evidence for: until
`2026-10-01_story-generation-glm-pass-through`, every experiment generated characters
independently, so the anti-duplication block had never run against a story-shaped bio. Treat
pair verdicts as the most informative thing you produce right now.

## What the harness already decided before you see it

So you do not spend the note on it:

- the response was non-empty, 150–450 words, carried no surviving `<think>` block, and
  contained at least five second-person markers
- anything failing those was regenerated, up to twice
- the name came from a separate call and is correct whether or not the prose uses it
