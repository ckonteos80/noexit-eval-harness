# Stanislavski — *An Actor Prepares*: Reference Notes

*Research notes on Constantin Stanislavski's system, gathered as background for character-generation and eval work. The book is structured as the training diary of a young actor, Kostya, under his teacher Tortsov — one core concept per chapter. Notes below follow that structure. A short "relevance" line under each connects it to what actually surfaced in the human/AI eval comparison on the 2026-08-28 run.*

## The concepts

### Action
"Whatever happens on the stage must be for a purpose." Nothing an actor does — no gesture, no line, no detail — is decoration. Everything is there because a specific person is trying to do a specific thing.
*Relevance: this is the direct counter to "poetic prose that doesn't help the game." A detail earns its place by doing work (revealing a fact, driving an objective), not by sounding evocative.*

### Given Circumstances
The concrete facts of the character's life and situation — who, what, when, where, why — that the actor must know and treat as true before anything else can be built. Not mood, not atmosphere: facts.
*Relevance: this is exactly what "utilitarian, not poetic" is asking for. Given circumstances are specific and factual by definition — a occupation, a cause of death, a named relationship — not sensory texture layered on top.*

### The Magic If
Instead of "pretending," the actor asks: *what would I actually do if I were really in this situation?* Stanislavski calls this the move that takes the actor out of abstraction and "arouses an inner and real activity" — real, situationally-grounded reasoning rather than performance of a feeling.
*Relevance: this is the test a generated detail should pass. Would a mother who complimented her son's classroom voice really tell him a fabricated reason for rejection, given he was demonstrably nervous and off-key at the audition? "Magic if" reasoning is what would have caught that — reasoning from the actual situation instead of reaching for what sounds dramatic.*

### Units and Objectives
A scene (or a life) breaks into units — chunks in which the character pursues one clear, specific objective. Every unit answers "what do I want, right now, in this moment," and the units chain together.
*Relevance: Occupation → Cause of Death → Who Loved/Hated → Sin → Stance is already a unit structure. Each field should read as its own answerable objective, not a fragment that only sounds good next to the others.*

### The Super-Objective
The single overarching want that drives a character through the entire piece — the thing every smaller objective ultimately serves. Without it, individual choices don't cohere into one person.
*Relevance: this is what "Defining personality trait" and "What you want from the others in the room" are supposed to be. The super-objective is the test for whether a trait is load-bearing (drives the sin, drives the want) or decorative (just an adjective sitting next to the story) — exactly the gap flagged in the AI eval guide already.*

### Inner Motive Forces
Every truthful action is driven by three forces working together: mind (thought/reasoning), will (intention/desire), and feeling (emotion). A performance — or a written character — that has only one of these (feeling without reasoning, e.g.) reads as false.
*Relevance: this is the missing check from the last eval. Claire's "lie" had feeling (the shame, the fear) but the *mind* piece didn't hold up — the established facts (he genuinely sang off-key) meant the reasoning behind calling it a lie didn't actually track. All three forces need to agree, not just the emotionally compelling one.*

### The Unbroken Line
Continuity of thought and emotion through a performance — every action and reaction has to follow logically from what came before, with no gaps or contradictions the audience has to paper over themselves.
*Relevance: directly the "if the son performed off key, what his mother said wasn't a lie" catch. A self-told distortion has to actually contradict the true version given everything else already established — if it doesn't, the line is broken and the sin doesn't hold.*

### Faith and a Sense of Truth
The actor has to believe the given circumstances are real before anything built on top of them can read as true — including to themselves. Truthfulness here is about specific, believable facts, not generalized or vague ones.
*Relevance: vague, dangling implications ("afraid the truth would come out" with no truth named) are a faith-and-truth failure — there's nothing concrete enough underneath for anyone, including the writer, to believe.*

### Communion
Real connection between characters — actually listening and reacting to the other person, not performing at them. Built from specific knowledge of who the other person actually is.
*Relevance: mainly a dialogue-stage concept (later work), but it also bears on Who You Loved/Hated — a relationship only reads as real if the other person in it has a plausible inner life of their own, not just a colorful trait assigned to justify a feeling ("why would the kid sing off-key at home but not in the classroom" — the sub-character needs their own believable motive too).*

### Adaptation
How a character adjusts their behavior moment to moment as circumstances shift — flexibility and responsiveness, not a fixed performance. Squarely a dialogue/live-scene concept, less applicable to one-shot character generation.

### Emotion Memory
The actor draws on real remembered sensation to ground an emotion truthfully, rather than generating the emotion generically. Stanislavski warns against forcing it or letting personal memory overwhelm the character's own truth.
*Relevance: the useful parallel isn't literal (a model has no memory) but structural — an emotion grounded in one specific, sense-based detail reads as earned; an emotion stated in the abstract ("you felt betrayed") does not. The line is thin, though, between this and the "poetic prose" problem — specificity should serve the fact being conveyed, not become texture for its own sake.*

### Concentration of Attention, Relaxation of Muscles, The Inner Creative State, On the Threshold of the Subconscious
These four are squarely actor-craft chapters — managing a live performer's focus, physical tension, and psychological readiness in the moment of performance. No direct analogue in text generation; included here only for completeness of the source material.

---

## Sources

- [An Actor Prepares — Wikipedia](https://en.wikipedia.org/wiki/An_Actor_Prepares)
- [An Actor Prepares Summary of Key Ideas and Review — Blinkist](https://www.blinkist.com/books/an-actor-prepares-en)
- [The Stanislavsky Technique: an Actor's Guide — Backstage](https://www.backstage.com/magazine/article/the-definitive-guide-to-the-stanislavsky-acting-technique-65716/)
- [Stanislavski Method: Acting Guide — MasterClass](https://www.masterclass.com/articles/stanislavski-method)
- [An Actor Prepares Summary and Study Guide — SuperSummary](https://www.supersummary.com/an-actor-prepares/summary/)
