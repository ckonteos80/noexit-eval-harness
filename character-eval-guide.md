# Character Generation — AI Eval Guide

*Companion to `eval-loop-scoring-design.md`. Scope: character generation only (the name/life/sin/stance chain), not dialogue, addressing, or narrator — those get their own guide later.*

## What this is for

`run_viewer.html` already has three eval slots for character generation — per-character, pair-level, and overall character design — each scored **good / bad / neutral** with a free-text note, same scheme as the human eval. This guide is what a judge (for now, me, applying it by hand when asked; later possibly an automated model call) should have in mind when filling in that note. The rating is a byproduct of the note, not the other way around — write the reaction first, let the rating fall out of it.

**Don't run this as a checklist.** Read the bio the way a director reads an actor's breakdown, or a screenwriter reads their own draft back — first impression, gut reaction, what snags you. The specific things to watch for below are what tends to go wrong, not boxes to tick in order.

---

## Per-character eval

What's your gut reaction? Does this feel like a real person, or a construct? Does the life hang together — the job, the death, the people they loved and hated, the sin — like one person's history, or like ingredients that never mixed? Note whatever snags you: a line that gestures at something without saying it ("afraid the truth would come out" — what truth?), a detail that contradicts another, a reference to someone who was never established, a personality trait that's just an adjective sitting next to the story rather than something the story actually demonstrates.

The hardest thing to see, and the thing most worth looking for: **a character can be perfectly consistent and still be disconnected.** Nothing contradicts anything, every field is well written, and the pieces still don't belong to each other. Test it by lifting things out. Could this death be dropped into a stranger's life without anything else changing? Could the job? Could the person they loved? If the answer is yes, the character is a set of good parts rather than a life — and no amount of internal consistency fixes that. Pay particular attention to the death: it is the easiest field to write well in isolation and the one most often unrelated to everyone else in the character.

## Pair-level eval

Read both bios back to back, like you're casting two actors for the same scene. Do they feel like two different people, or did the writer reach for the same drawer twice? Check specifically for repeats — shared surnames, the same kind of person filling the "loved" or "hated" slot in both (two spouses, two parents), the same category of job or death, even phrasing or imagery that echoes between the two without either character meaning to. If you could swap a detail from one into the other and nothing would feel wrong, that's the tell.

## Overall character design eval

Step back and take in the pair as a set — your reaction to the room as a whole, not either character alone. Does this feel like two distinct people who happen to be in the same hell together, or two copies of the same damaged-soul template wearing different names? Flag it here if the same patterns keep showing up — not just between these two characters, but the kind of thing that would nag at you if you'd seen it in the last few runs too (a phrase, a shape of sentence, a go-to relationship type the model keeps defaulting to). Note whether the traits and wants feel specific enough to actually cause friction once these two are talking to each other, or whether they're vague enough to belong to anyone.
