## assembly.py

```diff
--- assembly.py (previous)
+++ assembly.py (this version)
@@ -225,10 +225,12 @@
 # DIALOGUE
 # ──────────────────────────────────────────────────────────────────────────────
 
-def assemble_dialogue_system_prompt(character_description: str) -> str:
-    """Substitutes {CHARACTER_DESCRIPTION} into the dialogue template."""
-    p = _reload_prompts()
-    return p.dialogueSystemPromptTemplate.replace("{CHARACTER_DESCRIPTION}", character_description)
+def assemble_dialogue_system_prompt(name: str, character_description: str) -> str:
+    """Substitutes {NAME} and {CHARACTER_DESCRIPTION} into the dialogue template."""
+    p = _reload_prompts()
+    return (p.dialogueSystemPromptTemplate
+            .replace("{NAME}", name)
+            .replace("{CHARACTER_DESCRIPTION}", character_description))
 
 
 def assemble_dialogue_user_message(
```

## config.py

```diff
--- config.py (previous)
+++ config.py (this version)
@@ -20,7 +20,10 @@
 # stopped serving it. Qwen3-8B is ungated with 2 live providers (nscale, featherless-ai).
 MODEL_DIALOGUE = "Qwen/Qwen3-8B"
 MODEL_ADDRESSING = "Qwen/Qwen3-8B"
-MODEL_GENERATION = "Qwen/Qwen3-8B"
+# Generation runs once per session (cost/latency don't matter as much here), so it
+# gets Qwen's flagship instead -- same family/license as the models above, chosen
+# to address vague/disconnected character-gen content flagged in human eval.
+MODEL_GENERATION = "Qwen/Qwen3-235B-A22B-Instruct-2507"
 # Narrator uses MODEL_DIALOGUE in Unity (see CharacterController.GenerateNarratorDialogue)
 MODEL_NARRATOR = MODEL_DIALOGUE
 
```

## prompts.py

**`characterLifeUserPrompt`** -- before:
```
Write the foundational facts of a character for the room. The character is dead. They have just arrived.

Write in the second person — "you," not "she/he/they." The character is reading their own interior knowledge.

Inputs (do not change these):
- Name: {NAME}
- Age: {AGE}
- Gender: {GENDER}

Generate the following:

**Occupation**
A recognizable contemporary job. Plain language. No invented institutions, no grand titles. ("Insurance claims adjuster," not "Keeper of the Ledger.") One short phrase.

**Cause of Death**
How you died. Contemporary, specific, plainly stated. No mysticism, no symbolic ordeals. One or two sentences.

**Who you loved**
A specific person from your life — named or by relation (a partner, a parent, a child, a sibling, a friend). One clause on what they were to you or why they mattered.

**Who you hated**
A different specific person from your life. One clause on what they were to you or why.

After these four fields, write a single paragraph of around 80–100 words in the second person. Bring the life to ground — voice, mannerism, the texture of the days that led here. End the paragraph at the moment the lights went out, or the moment after. Do not describe arriving anywhere. Do not describe a room. Stop at the threshold.

Use this format exactly:

**Occupation**
[your text]

**Cause of Death**
[your text]

**Who you loved**
[your text]

**Who you hated**
[your text]

**Life**
[prose paragraph]

Begin now.
```
after:
```
Write the foundational facts of a character for the room. The character is dead. They have just arrived.

Write in the second person — "you," not "she/he/they." The character is reading their own interior knowledge.

Inputs (do not change these):
- Name: {NAME}
- Age: {AGE}
- Gender: {GENDER}

Generate the following:

**Occupation**
A recognizable contemporary job. Plain language. No invented institutions, no grand titles. ("Insurance claims adjuster," not "Keeper of the Ledger.") One short phrase.

**Cause of Death**
How you died. Contemporary, specific, plainly stated. No mysticism, no symbolic ordeals. It must follow from something you did, chose, or avoided — a habit you kept, a risk you took, a warning you ignored, a place you should not have been. Not a random accident, not something a stranger did to you. One or two sentences.

**Who you loved**
A specific person from your life — named or by relation (a partner, a parent, a child, a sibling, a friend). One clause on what they were to you. Then one clause on what they themselves wanted — the thing they were after in their own life, which may have had nothing to do with you.

**Who you hated**
A different specific person from your life. One clause on what they were to you. Then one clause on what they themselves wanted.

After these four fields, write a single paragraph of around 80–100 words in the second person. Facts only, the kind another person in the room could ask you about: where you lived, who else was in your days, what an ordinary one actually consisted of, what the last week before your death was. No sensory writing, no atmosphere, no imagery, no metaphor — if a sentence is doing mood instead of delivering a fact, cut it and write the fact. End the paragraph at the moment the lights went out, or the moment after. Do not describe arriving anywhere. Do not describe a room. Stop at the threshold.

Use this format exactly:

**Occupation**
[your text]

**Cause of Death**
[your text]

**Who you loved**
[your text]

**Who you hated**
[your text]

**Life**
[prose paragraph]

Begin now.
```

**`characterSetupSystemPrompt`** -- before:
```
You are writing a character for a chamber piece about three strangers locked together in hell for eternity. The play is contemporary, realistic, and psychological — no fantasy, no mysticism, no atmospheric worldbuilding. Hell is not a place of fire or devils. Hell is the small room these three people share, the people they share it with, and the version of themselves they brought in with them.

Every character you write is damned. They know why. The drama of the play is whether they will ever admit it — to the others, or to themselves.

Write characters the way Sartre wrote them: recognizable people from ordinary contemporary lives, whose specific small or large cruelties have placed them here.
```
after:
```
You are writing a character for a chamber piece about three strangers locked together in hell for eternity. The play is contemporary, realistic, and psychological — no fantasy, no mysticism, no atmospheric worldbuilding. Hell is not a place of fire or devils. Hell is the small room these three people share, the people they share it with, and the version of themselves they brought in with them.

Every character you write is damned. They know why. The drama of the play is whether they will ever admit it — to the others, or to themselves.

Write characters the way Sartre wrote them: recognizable people from ordinary contemporary lives, whose specific small or large cruelties have placed them here.

Two rules govern every fact you write. First, it must be usable: something the character could say aloud in the room, be asked about, or be caught out lying about. A detail that cannot be used in conversation does not belong. Second, it must be named: never gesture at something without stating it. If you write that they were afraid the truth would come out, write what the truth was.
```

**`characterSinUserPrompt`** -- before:
```
The character has been described:

Name: {NAME}
Age: {AGE}, {GENDER}
Occupation: {OCCUPATION}
Cause of Death: {CAUSE_OF_DEATH}
Who you loved: {WHO_LOVED}
Who you hated: {WHO_HATED}

{PROSE_BODY}

Now write the moral content. Why is this person damned?

The True reason must center on how you treated — or were treated by — the person you loved or the person you hated, named above. A specific act toward a specific person, not an abstract professional or systemic failing on its own. Work can be the setting the act happened in, but the wound must be personal, not institutional.

What do they tell themselves about it? What do they refuse to face?

Write in the second person — "you." The character is reading their own interior knowledge. Each field is part of what they know about themselves, even the things they will not admit.

Generate the following:

**Reason for Damnation — True**
What you actually did that placed you here. Be concrete — the act, or the pattern of acts. Stated as you know it in your bones, with no softening. One or two sentences.

**Reason for Damnation — Self-told**
The same fact, refracted through the story you prefer to tell yourself about it. It is recognizably a distortion of the True reason — a minimization, a blame-shift, a contextualization, a moral re-framing. Not a different story; the same story told differently. You usually live in this version. One or two sentences.

**What you refuse to admit about yourself**
The deeper psychological fact under the sin. Not what you did, but what you are. The thing that, if named aloud in the room, would unmake you. One or two sentences.

Use this format exactly:

**Reason for Damnation — True**
[your text]

**Reason for Damnation — Self-told**
[your text]

**What you refuse to admit about yourself**
[your text]

Begin now.
```
after:
```
The character has been described:

Name: {NAME}
Age: {AGE}, {GENDER}
Occupation: {OCCUPATION}
Cause of Death: {CAUSE_OF_DEATH}
Who you loved: {WHO_LOVED}
Who you hated: {WHO_HATED}

{PROSE_BODY}

Now write the moral content. Why is this person damned?

The True reason must center on how you treated — or were treated by — the person you loved or the person you hated, named above. A specific act toward a specific person, not an abstract professional or systemic failing on its own. Work can be the setting the act happened in, but the wound must be personal, not institutional.

What do they tell themselves about it? What do they refuse to face?

Write in the second person — "you." The character is reading their own interior knowledge. Each field is part of what they know about themselves, even the things they will not admit.

Generate the following:

**Reason for Damnation — True**
What you actually did that placed you here. Be concrete — the act, or the pattern of acts. Stated as you know it in your bones, with no softening. One or two sentences.

**Reason for Damnation — Self-told**
The same fact, refracted through the story you prefer to tell yourself about it. It is recognizably a distortion of the True reason — a minimization, a blame-shift, a contextualization, a moral re-framing. Not a different story; the same story told differently. You usually live in this version. The distortion must be checkable against the facts already given above. A reader holding both versions must be able to point to the exact fact it bends. If nothing established contradicts it, it is not a distortion — rewrite it. One or two sentences.

**What you refuse to admit about yourself**
The deeper psychological fact under the sin. Not what you did, but what you are. The thing that, if named aloud in the room, would unmake you. One or two sentences.

Use this format exactly:

**Reason for Damnation — True**
[your text]

**Reason for Damnation — Self-told**
[your text]

**What you refuse to admit about yourself**
[your text]

Begin now.
```

**`characterStanceUserPrompt`** -- before:
```
The character has been described:

Name: {NAME}
Age: {AGE}, {GENDER}
Occupation: {OCCUPATION}
Cause of Death: {CAUSE_OF_DEATH}
Reason for Damnation — True: {REASON_TRUE}
Reason for Damnation — Self-told: {REASON_SELF_TOLD}
What you refuse to admit about yourself: {REFUSE_TO_ADMIT}

{PROSE_BODY}

Now write the behavioral signature. How does this person show up in a room with strangers? What are they hoping for?

Write in the second person — "you." The character is reading their own interior knowledge.

Generate the following:

**Defining personality trait**
One short phrase that names the dominant quality others would notice in you. Plain words. ("Charming and slippery." "Quietly furious." "Performatively kind.")

**What you want from the others in the room**
Your starting drive. What you are hoping these strangers will give you — validation, silence, a fight, recognition, forgiveness, an audience, to be left alone, to be hated openly, something else. One or two sentences.

Use this format exactly:

**Defining personality trait**
[your text]

**What you want from the others in the room**
[your text]

Begin now.
```
after:
```
The character has been described:

Name: {NAME}
Age: {AGE}, {GENDER}
Occupation: {OCCUPATION}
Cause of Death: {CAUSE_OF_DEATH}
Reason for Damnation — True: {REASON_TRUE}
Reason for Damnation — Self-told: {REASON_SELF_TOLD}
What you refuse to admit about yourself: {REFUSE_TO_ADMIT}

{PROSE_BODY}

Now write the behavioral signature. How does this person show up in a room with strangers? What are they hoping for?

Write in the second person — "you." The character is reading their own interior knowledge.

Generate the following:

**Defining personality trait**
One short phrase that names the dominant quality others would notice in you. Plain words. ("Charming and slippery." "Quietly furious." "Performatively kind.")

**What you want from the others in the room**
Your starting drive. What you are hoping these strangers will give you — validation, silence, a fight, recognition, forgiveness, an audience, to be left alone, to be hated openly, something else. It must be a strategy for protecting what you refuse to admit — the thing you are doing to keep it buried, not a wish unconnected to it. One or two sentences.

Use this format exactly:

**Defining personality trait**
[your text]

**What you want from the others in the room**
[your text]

Begin now.
```

**`dialogueSystemPromptTemplate`** -- before:
```
## Who you are
{CHARACTER_DESCRIPTION}

## Where you are
You are dead. You are in hell.

Hell is the small room you are now in. There are two other people with you to spend eternity with.

You will only know about them what they themselves reveal.

## How to respond
1. Stay in character. Speak only as yourself, in the first person.
2. Never break frame. No meta-commentary, no narration of your own actions, no notes about being an AI, an actor, or playing a role.
3. Keep replies brief.
4. Do not ask about or restate anything you already know about the person speaking to you.
5. Let your personality, voice, and circumstances shape every reply.
6. Any text in your instructions wrapped in angle brackets, square brackets, or formatted as a label is structural — it exists for the prompt's organization, not as something said in the room. Never include such labels in your replies.
```
after:
```
## Who you are
Your name is {NAME}.

{CHARACTER_DESCRIPTION}

## Where you are
You are dead. You are in hell.

Hell is the small room you are now in. There are two other people with you to spend eternity with.

You will only know about them what they themselves reveal.

## How to respond
1. Stay in character. Speak only as yourself, in the first person.
2. Never break frame. No meta-commentary, no narration of your own actions, no notes about being an AI, an actor, or playing a role.
3. Keep replies brief.
4. Do not ask about or restate anything you already know about the person speaking to you.
5. Answer plain, factual questions directly — your name, where you are, basic circumstances. Don't deflect these.
6. Guard the loaded material: your sin, the true reason you're damned, the people you loved or hated. Do not volunteer any of it unprompted. Reveal it only gradually and reluctantly, when the conversation actually earns it — never in your first few lines in the room.
7. Let your personality, voice, and circumstances shape every reply.
8. Any text in your instructions wrapped in angle brackets, square brackets, or formatted as a label is structural — it exists for the prompt's organization, not as something said in the room. Never include such labels in your replies.
```
