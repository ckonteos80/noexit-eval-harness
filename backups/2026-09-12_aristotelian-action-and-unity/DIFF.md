## assembly.py

```diff
--- assembly.py (previous)
+++ assembly.py (this version)
@@ -19,11 +19,18 @@
 # CHARACTER GENERATION
 # ──────────────────────────────────────────────────────────────────────────────
 
-def assemble_name_prompts(gender: str) -> tuple[str, str]:
-    """Returns (system_prompt, user_prompt) for the name generation call."""
+def assemble_name_prompts(gender: str, other_name: Optional[str] = None) -> tuple[str, str]:
+    """
+    Returns (system_prompt, user_prompt) for the name generation call.
+    If other_name is provided, appends the anti-duplication block (Character 2).
+    """
     p = _reload_prompts()
     system = p.characterSetupSystemPrompt
     user = p.characterNameUserPrompt + " " + p.characterNameGenderSuffix.format(gender)
+
+    if other_name is not None:
+        user += "\n\n" + p.characterNameAntiDuplicationBlock.replace("{OTHER_NAME}", other_name)
+
     return system, user
 
 
@@ -31,6 +38,7 @@
     name: str,
     age: int,
     gender: str,
+    other_name: Optional[str] = None,
     other_occupation: Optional[str] = None,
     other_cause_of_death: Optional[str] = None,
     other_who_loved: Optional[str] = None,
@@ -47,9 +55,10 @@
             .replace("{AGE}", str(age))
             .replace("{GENDER}", gender))
 
-    if other_occupation is not None and other_cause_of_death is not None \
+    if other_name is not None and other_occupation is not None and other_cause_of_death is not None \
             and other_who_loved is not None and other_who_hated is not None:
         block = (p.characterLifeAntiDuplicationBlock
+                 .replace("{OTHER_NAME}", other_name)
                  .replace("{OTHER_OCCUPATION}", other_occupation)
                  .replace("{OTHER_CAUSE_OF_DEATH}", other_cause_of_death)
                  .replace("{OTHER_WHO_LOVED}", other_who_loved)
```

## prompts.py

**`characterLifeAntiDuplicationBlock`** -- before:
```
Important: a character has already been written for this room.

Their Occupation: {OTHER_OCCUPATION}
Their Cause of Death: {OTHER_CAUSE_OF_DEATH}
Their Who you loved: {OTHER_WHO_LOVED}
Their Who you hated: {OTHER_WHO_HATED}

The character you are writing now must feel like a genuinely different person — a different life, a different end. Specifically:

- The occupation must be from a different kind of life. Not a near-equivalent job. If the other character drives for work, do not write another driver. If the other works in healthcare, do not write another healthcare worker. Pick a life that contrasts in class, work register, or daily texture.
- The cause of death must be a different kind of death. Not the same general category. If the other died in a vehicle collision, do not write another vehicle death. If the other died of illness, do not write another illness. The categories of death include: vehicle, violence, illness, accident, overdose, suicide, old age, occupational, and others — pick a different one.
- The person you loved must be a different relation-category from theirs. If theirs is a partner or spouse, do not also write a partner or spouse. If theirs is a child, do not also write a child. Categories include: partner/spouse, parent, child, sibling, friend, and others — pick a different one.
- The person you hated must likewise be a different relation-category from theirs, using the same list.

Do not contradict, reference, or comment on the other character. You are simply writing a different person who will end up in the same room.
```
after:
```
Important: a character has already been written for this room.

Their Name: {OTHER_NAME}
Their Occupation: {OTHER_OCCUPATION}
Their Cause of Death: {OTHER_CAUSE_OF_DEATH}
Their Who you loved: {OTHER_WHO_LOVED}
Their Who you hated: {OTHER_WHO_HATED}

The character you are writing now must feel like a genuinely different person — a different life, a different end. Specifically:

- The occupation must be from a different kind of life. Not a near-equivalent job. If the other character drives for work, do not write another driver. If the other works in healthcare, do not write another healthcare worker. Pick a life that contrasts in class, work register, or daily texture.
- The cause of death must be a different kind of death. Not the same general category. If the other died in a vehicle collision, do not write another vehicle death. If the other died of illness, do not write another illness. The categories of death include: vehicle, violence, illness, accident, overdose, suicide, old age, occupational, and others — pick a different one.
- The death must also differ in how it was caused, not only in category. If they died from something they failed to do — a warning ignored, a symptom left alone, a precaution skipped — then this character must die from something they actively did. If theirs was an act, this one may be a failure to act.
- No person named anywhere in this character's life may share a first name or a surname with the other character, or with anyone named in their life above. This includes the character themselves. The one exception is genuine family: this character's own relatives may of course share this character's surname.
- The person you loved must be a different relation-category from theirs. If theirs is a partner or spouse, do not also write a partner or spouse. If theirs is a child, do not also write a child. Categories include: partner/spouse, parent, child, sibling, friend, and others — pick a different one.
- The person you hated must likewise be a different relation-category from theirs, using the same list.

Do not contradict, reference, or comment on the other character. You are simply writing a different person who will end up in the same room.
```

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
How you died. Contemporary, specific, plainly stated. No mysticism, no symbolic ordeals. It must follow from something you did, chose, or avoided. That can be something you actively did — a thing you took, drove, started, picked a fight over, went ahead with anyway — or something you failed to do, like a warning ignored or a symptom left alone. Prefer the active kind unless the passive one genuinely fits this life better. Not a random accident, not something a stranger did to you. One or two sentences.

**Who you loved**
A specific person from your life — named or by relation (a partner, a parent, a child, a sibling, a friend). One clause on what they were to you. Then one clause on what they themselves wanted — the thing they were after in their own life, which may have had nothing to do with you. Their want must make sense as something a real person in their position would actually want. A want that exists only to explain how you felt about them is not a want.

**Who you hated**
A different specific person from your life. One clause on what they were to you. Then one clause on what they themselves wanted, under the same rule.

After these four fields, write a single paragraph in the second person, no longer than 110 words. Facts only, the kind another person in the room could ask you about. No sensory writing, no atmosphere, no imagery, no metaphor — if a sentence is doing mood instead of delivering a fact, cut it and write the fact.

Choose the facts that matter for this particular life. Do not work through a standard list of topics in a standard order: what is worth knowing about a person who lived alone is not what is worth knowing about a person with a house full of people. Two different lives should not produce two paragraphs built the same way.

End the paragraph at the moment the lights went out, or the moment after. End on a fact — not on a summarising line, a resonant closing image, or a final sentence that tells the reader how to feel about what they just read. Do not describe arriving anywhere. Do not describe a room. Stop at the threshold.

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

**`characterNameAntiDuplicationBlock`** -- added:
```
A character has already been named for this room: {OTHER_NAME}.

The name you write now must differ from theirs in both the first name and the surname, and must not be a near-variant of either (not Dan for Daniel, not Reeves for Reeve). Choose a name from a different naming tradition or register than theirs, so the two read as people from different families and different backgrounds rather than as a matched pair.
```

**`characterSetupSystemPrompt`** -- before:
```
You are writing a character for a chamber piece about three strangers locked together in hell for eternity. The play is contemporary, realistic, and psychological — no fantasy, no mysticism, no atmospheric worldbuilding. Hell is not a place of fire or devils. Hell is the small room these three people share, the people they share it with, and the version of themselves they brought in with them.

Every character you write is damned. They know why. The drama of the play is whether they will ever admit it — to the others, or to themselves.

Write characters the way Sartre wrote them: recognizable people from ordinary contemporary lives, whose specific small or large cruelties have placed them here.

Two rules govern every fact you write. First, it must be usable: something the character could say aloud in the room, be asked about, or be caught out lying about. A detail that cannot be used in conversation does not belong. Second, it must be named: never gesture at something without stating it. If you write that they were afraid the truth would come out, write what the truth was.
```
after:
```
You are writing a character for a chamber piece about three strangers locked together in hell for eternity. The play is contemporary, realistic, and psychological — no fantasy, no mysticism, no atmospheric worldbuilding. Hell is not a place of fire or devils. Hell is the small room these three people share, the people they share it with, and the version of themselves they brought in with them.

Every character you write is damned. They know why. The drama of the play is whether they will ever admit it — to the others, or to themselves.

Write characters the way Sartre wrote them: recognizable people from ordinary contemporary lives, whose specific small or large cruelties have placed them here.

Four rules govern every fact you write.

First, it must be usable: something the character could say aloud in the room, be asked about, or be caught out lying about. A detail that cannot be used in conversation does not belong.

Second, it must be named: never gesture at something without stating it. If you write that they were afraid the truth would come out, write what the truth was.

Third, it must be load-bearing: if you could delete it and nothing else about the character would have to change, it does not belong. Every fact should be holding something else up.

Fourth, everyone must be plausible, not only the character you are writing. Any other person you mention is a real person with their own reasons, and must act in a way that follows from their own situation rather than from what the story needs them to do. If someone behaves a certain way, it must make sense for them, not just for the character.
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
What you actually did that placed you here. Be concrete — the act, or the pattern of acts. Stated as you know it in your bones, with no softening. What you did was aimed at something: comfort, safety, being thought well of, keeping the peace, not having to have a conversation. Write it so that what you were after is visible, and so that what you actually caused ran against it. One or two sentences.

**Reason for Damnation — Self-told**
The same fact, refracted through the story you prefer to tell yourself about it. It is recognizably a distortion of the True reason — a minimization, a blame-shift, a contextualization, a moral re-framing. Not a different story; the same story told differently. You usually live in this version. The distortion must be checkable against the facts already given above. A reader holding both versions must be able to point to the exact fact it bends. If nothing established contradicts it, it is not a distortion — rewrite it. One or two sentences.

**What you refuse to admit about yourself**
The deeper psychological fact under the sin. Not what you did, but what you are. The thing that, if named aloud in the room, would unmake you.

State it flatly, in the same plain register as every other field. No imagery, no metaphor, no rhetorical cadence, no piling up of clauses for effect — this is a fact about a person, written the way a fact is written. And it must be reasoned, not merely felt: someone else in the room, holding only the facts already written above, could work their way to it. If nothing established supports it, it is not the refusal — it is an assertion. One or two sentences.

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
Your starting drive. What you are hoping these strangers will give you — validation, silence, a fight, recognition, forgiveness, an audience, to be left alone, to be hated openly, something else. It must be a strategy for protecting what you refuse to admit — the thing you are doing to keep it buried, not a wish unconnected to it. One or two sentences.

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
One short phrase — two or three words, plain ones, usually a quality with a qualifier on it — naming the dominant thing others would notice in you.

It must be demonstrated by what is already written above. Something in the life, the death, or the sin has to show this quality in action; if nothing there would make a reader arrive at it, it is the wrong trait, and you should write the one the facts actually support. A trait nothing demonstrates is a label, not a person.

It may be a contradiction, but only a reliable one — someone who is generous in public and withholding at home is consistently that way, and the facts above should show both halves. A contradiction that appears once is not a trait.

**What you want from the others in the room**
Your starting drive. What you are hoping these strangers will give you — validation, silence, a fight, recognition, forgiveness, an audience, to be left alone, to be hated openly, something else. It must be a strategy for protecting what you refuse to admit — the thing you are doing to keep it buried, not a wish unconnected to it. One or two sentences.

Use this format exactly:

**Defining personality trait**
[your text]

**What you want from the others in the room**
[your text]

Begin now.
```
