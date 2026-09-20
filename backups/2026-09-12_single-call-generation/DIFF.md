## assembly.py

```diff
--- assembly.py (previous)
+++ assembly.py (this version)
@@ -19,116 +19,34 @@
 # CHARACTER GENERATION
 # ──────────────────────────────────────────────────────────────────────────────
 
-def assemble_name_prompts(gender: str, other_name: Optional[str] = None) -> tuple[str, str]:
-    """
-    Returns (system_prompt, user_prompt) for the name generation call.
-    If other_name is provided, appends the anti-duplication block (Character 2).
-    """
-    p = _reload_prompts()
-    system = p.characterSetupSystemPrompt
-    user = p.characterNameUserPrompt + " " + p.characterNameGenderSuffix.format(gender)
-
-    if other_name is not None:
-        user += "\n\n" + p.characterNameAntiDuplicationBlock.replace("{OTHER_NAME}", other_name)
-
-    return system, user
-
-
-def assemble_life_prompts(
-    name: str,
+def assemble_character_prompts(
+    name_origin: str,
     age: int,
     gender: str,
     other_name: Optional[str] = None,
-    other_occupation: Optional[str] = None,
-    other_cause_of_death: Optional[str] = None,
-    other_who_loved: Optional[str] = None,
-    other_who_hated: Optional[str] = None,
+    other_bio: Optional[str] = None,
 ) -> tuple[str, str]:
     """
-    Returns (system_prompt, user_prompt) for the Life call.
-    If other_* args are provided, appends the anti-duplication block (Character 2).
+    Returns (system_prompt, user_prompt) for the single character-generation call.
+
+    Replaces the former four-call chain (name -> life -> sin -> stance). The order of
+    the format block inside characterFullUserPrompt carries the conditioning those
+    separate calls used to provide -- generation is autoregressive, so each field is
+    written knowing the ones above it. Do not reorder that block casually.
+
+    If other_name and other_bio are given, appends the anti-duplication block (Character 2).
     """
     p = _reload_prompts()
     system = p.characterSetupSystemPrompt
-    user = (p.characterLifeUserPrompt
-            .replace("{NAME}", name)
+    user = (p.characterFullUserPrompt
+            .replace("{NAME_ORIGIN}", name_origin)
             .replace("{AGE}", str(age))
             .replace("{GENDER}", gender))
 
-    if other_name is not None and other_occupation is not None and other_cause_of_death is not None \
-            and other_who_loved is not None and other_who_hated is not None:
-        block = (p.characterLifeAntiDuplicationBlock
+    if other_name is not None and other_bio is not None:
+        block = (p.characterFullAntiDuplicationBlock
                  .replace("{OTHER_NAME}", other_name)
-                 .replace("{OTHER_OCCUPATION}", other_occupation)
-                 .replace("{OTHER_CAUSE_OF_DEATH}", other_cause_of_death)
-                 .replace("{OTHER_WHO_LOVED}", other_who_loved)
-                 .replace("{OTHER_WHO_HATED}", other_who_hated))
-        user += "\n\n" + block
-
-    return system, user
-
-
-def assemble_sin_prompts(
-    name: str,
-    age: int,
-    gender: str,
-    occupation: str,
-    cause_of_death: str,
-    who_loved: str,
-    who_hated: str,
-    prose_body: str,
-    other_reason_true: Optional[str] = None,
-) -> tuple[str, str]:
-    """Returns (system_prompt, user_prompt) for the Sin call."""
-    p = _reload_prompts()
-    system = p.characterSetupSystemPrompt
-    user = (p.characterSinUserPrompt
-            .replace("{NAME}", name)
-            .replace("{AGE}", str(age))
-            .replace("{GENDER}", gender)
-            .replace("{OCCUPATION}", occupation)
-            .replace("{CAUSE_OF_DEATH}", cause_of_death)
-            .replace("{WHO_LOVED}", who_loved)
-            .replace("{WHO_HATED}", who_hated)
-            .replace("{PROSE_BODY}", prose_body))
-
-    if other_reason_true is not None:
-        block = p.characterSinAntiDuplicationBlock.replace(
-            "{OTHER_REASON_TRUE}", other_reason_true
-        )
-        user += "\n\n" + block
-
-    return system, user
-
-
-def assemble_stance_prompts(
-    name: str,
-    age: int,
-    gender: str,
-    occupation: str,
-    cause_of_death: str,
-    reason_true: str,
-    reason_self_told: str,
-    refuse_to_admit: str,
-    prose_body: str,
-    other_want: Optional[str] = None,
-) -> tuple[str, str]:
-    """Returns (system_prompt, user_prompt) for the Stance call."""
-    p = _reload_prompts()
-    system = p.characterSetupSystemPrompt
-    user = (p.characterStanceUserPrompt
-            .replace("{NAME}", name)
-            .replace("{AGE}", str(age))
-            .replace("{GENDER}", gender)
-            .replace("{OCCUPATION}", occupation)
-            .replace("{CAUSE_OF_DEATH}", cause_of_death)
-            .replace("{REASON_TRUE}", reason_true)
-            .replace("{REASON_SELF_TOLD}", reason_self_told)
-            .replace("{REFUSE_TO_ADMIT}", refuse_to_admit)
-            .replace("{PROSE_BODY}", prose_body))
-
-    if other_want is not None:
-        block = p.characterStanceAntiDuplicationBlock.replace("{OTHER_WANT}", other_want)
+                 .replace("{OTHER_BIO}", other_bio))
         user += "\n\n" + block
 
     return system, user
@@ -158,47 +76,31 @@
     return content.strip()
 
 
-def parse_life_response(response: str) -> dict:
-    """Returns {'occupation', 'cause_of_death', 'who_loved', 'who_hated', 'prose_body'}. Values may be None."""
-    return {
-        "occupation": extract_field(response, "Occupation"),
-        "cause_of_death": extract_field(response, "Cause of Death"),
-        "who_loved": extract_field(response, "Who you loved"),
-        "who_hated": extract_field(response, "Who you hated"),
-        "prose_body": extract_field(response, "Life"),
-    }
-
-
-def parse_sin_response(response: str) -> dict:
-    """Returns {'reason_true', 'reason_self_told', 'refuse_to_admit'}."""
-    return {
-        "reason_true": extract_field(response, "Reason for Damnation — True"),
-        "reason_self_told": extract_field(response, "Reason for Damnation — Self-told"),
-        "refuse_to_admit": extract_field(response, "What you refuse to admit about yourself"),
-    }
-
-
-def parse_stance_response(response: str) -> dict:
-    """Returns {'personality_trait', 'want'}."""
-    return {
-        "personality_trait": extract_field(response, "Defining personality trait"),
-        "want": extract_field(response, "What you want from the others in the room"),
-    }
-
-
-def life_parse_complete(parsed: dict) -> bool:
-    return all(v and v.strip() for v in [
-        parsed["occupation"], parsed["cause_of_death"],
-        parsed["who_loved"], parsed["who_hated"], parsed["prose_body"],
-    ])
-
-
-def sin_parse_complete(parsed: dict) -> bool:
-    return all(v and v.strip() for v in [parsed["reason_true"], parsed["reason_self_told"], parsed["refuse_to_admit"]])
-
-
-def stance_parse_complete(parsed: dict) -> bool:
-    return all(v and v.strip() for v in [parsed["personality_trait"], parsed["want"]])
+# Field key -> the **heading** it is written under in the generation response.
+# Order matches the format block in prompts.characterFullUserPrompt.
+CHARACTER_FIELDS = {
+    "name": "Name",
+    "occupation": "Occupation",
+    "cause_of_death": "Cause of Death",
+    "who_loved": "Who you loved",
+    "who_hated": "Who you hated",
+    "prose_body": "Life",
+    "reason_true": "Reason for Damnation — True",
+    "reason_self_told": "Reason for Damnation — Self-told",
+    "refuse_to_admit": "What you refuse to admit about yourself",
+    "personality_trait": "Defining personality trait",
+    "want": "What you want from the others in the room",
+}
+
+
+def parse_character_response(response: str) -> dict:
+    """All eleven character fields from one generation response. Values may be None."""
+    return {key: extract_field(response, label) for key, label in CHARACTER_FIELDS.items()}
+
+
+def character_parse_complete(parsed: dict) -> bool:
+    """True only when every field came back non-empty; drives the parse retry."""
+    return all((parsed.get(key) or "").strip() for key in CHARACTER_FIELDS)
 
 
 def assemble_bio(
```

## config.py

```diff
--- config.py (previous)
+++ config.py (this version)
@@ -45,6 +45,21 @@
 # ── Character age range (matches CharacterGenerator.Random.Range(25, 65)) ──
 AGE_RANGE = (25, 65)
 
+# ── Name origins for character generation ──
+# One is drawn at random per character and interpolated into the generation prompt.
+# Randomising the *input* is the fix for cross-run name repetition: asking the model
+# for variety failed for three versions running (Daniel Reeves was character 1 in
+# three consecutive runs, with supporting names Mark and Poole also recurring).
+# Same pattern as AGE_RANGE above, and portable to Unity's Random.Range usage.
+NAME_ORIGINS = [
+    "British", "Irish", "African-American", "Mexican", "Puerto Rican",
+    "Italian-American", "Polish", "Greek", "Nigerian", "Ghanaian",
+    "Indian", "Pakistani", "Filipino", "Vietnamese", "Korean",
+    "Chinese-American", "Japanese-American", "Lebanese", "Iranian", "Turkish",
+    "Brazilian", "Colombian", "Russian", "Ukrainian", "German",
+    "Dutch", "Swedish", "Portuguese", "French-Canadian", "Scottish",
+]
+
 # ── Genders for character generation ──
 # In Unity, char 1 is male, char 2 is female (CharacterGenerator line: gender = charNo == 1 ? "male" : "female")
 CHARACTER_GENDERS = {1: "male", 2: "female"}
```

## prompts.py

**`characterFullAntiDuplicationBlock`** -- added:
```
Important: a character has already been written for this room. Here they are in full.

Their name: {OTHER_NAME}

{OTHER_BIO}

The character you write now must feel like a genuinely different person — a different life, a different end, a different failure. Specifically:

- The occupation must be from a different kind of life. Not a near-equivalent job. If they drive for work, do not write another driver; if they work in healthcare, do not write another healthcare worker. Pick a life that contrasts in class, work register, or daily texture.
- The cause of death must be a different category of death. The categories include: vehicle, violence, illness, accident, overdose, suicide, old age, occupational, and others — pick one they are not occupying. This holds however different the circumstances are: two car crashes are two vehicle deaths even if one ran a red light and the other hydroplaned in a storm.
- Separately from the category, the death must differ in how it was caused. If they died from something they failed to do, this character dies from something they actively did — or the reverse.
- The person you loved must be a different relation-category from theirs. Categories include: partner/spouse, parent, child, sibling, friend, and others — pick a different one.
- The person you hated must likewise be a different relation-category from theirs, using the same list.
- No person named anywhere in your character may share a first name or a surname with them, or with anyone named in their life above. This includes your own name. The one exception is your own genuine family, who may of course share your surname.
- You must be damned for a different kind of moral failure. The categories: violence, cruelty, cowardice, manipulation, betrayal, neglect, vanity, hypocrisy, abuse, theft, complicity, abandonment, self-deception, indifference. Pick a category they are not occupying.
- You must want something different from the others in the room. Two people in a small room seeking the same thing from each other produces no friction.

Do not contradict, reference, or comment on the other character. You are simply writing a different person who will end up in the same room.
```

**`characterFullUserPrompt`** -- added:
```
Write a complete character for the room. The character is dead. They have just arrived.

Write in the second person — "you," not "she/he/they." The character is reading their own interior knowledge. Every field is part of what they know about themselves, even the things they will not admit.

Inputs (do not change these):
- Age: {AGE}
- Gender: {GENDER}
- Naming tradition: {NAME_ORIGIN}

Write the fields below in the order given. Each is written knowing everything above it: a later field must be consistent with the facts already established and must never contradict them.

**Name**
A plausible contemporary first name and last name — two words — drawn from the {NAME_ORIGIN} naming tradition. This person is an ordinary contemporary person who happens to have that background. Do not write their origin into any other field unless it genuinely matters to the life.

**Occupation**
A recognizable contemporary job. Plain language. No invented institutions, no grand titles. ("Insurance claims adjuster," not "Keeper of the Ledger.") One short phrase.

**Cause of Death**
How you died. Contemporary, specific, plainly stated. No mysticism, no symbolic ordeals. It must follow from something you did, chose, or avoided. That can be something you actively did — a thing you took, drove, started, picked a fight over, went ahead with anyway — or something you failed to do, like a warning ignored or a symptom left alone. Prefer the active kind unless the passive one genuinely fits this life better. Not a random accident, not something a stranger did to you. One or two sentences.

**Who you loved**
A specific person from your life — named or by relation (a partner, a parent, a child, a sibling, a friend). One clause on what they were to you. Then one clause on what they themselves wanted — the thing they were after in their own life, which may have had nothing to do with you. Their want must make sense as something a real person in their position would actually want. A want that exists only to explain how you felt about them is not a want. Nothing in this field may describe anything that happened after your death.

**Who you hated**
A different specific person from your life. One clause on what they were to you. Then one clause on what they themselves wanted, under the same rule. Nothing in this field may describe anything that happened after your death.

**Life**
A single paragraph in the second person, no longer than 110 words. Facts only, the kind another person in the room could ask you about. No sensory writing, no atmosphere, no imagery, no metaphor — if a sentence is doing mood instead of delivering a fact, cut it and write the fact.

Choose the facts that matter for this particular life. Do not work through a standard list of topics in a standard order: what is worth knowing about a person who lived alone is not what is worth knowing about a person with a house full of people.

End the paragraph at the death you already wrote in Cause of Death — the same death, by the same means, in the same place. Not a different death, and not a different version of the same one. End on a fact, not on a summarising line, a resonant closing image, or a final sentence that tells the reader how to feel about what they just read. Do not describe arriving anywhere. Do not describe a room. Stop at the threshold.

**Reason for Damnation — True**
What you actually did that placed you here. It must center on how you treated — or were treated by — the person you loved or the person you hated, named above. A specific act toward a specific person, not an abstract professional or systemic failing on its own. Work can be the setting the act happened in, but the wound must be personal, not institutional.

Be concrete — the act, or the pattern of acts. Stated as you know it in your bones, with no softening. What you did was aimed at something: comfort, safety, being thought well of, keeping the peace, not having to have a conversation. Write it so that what you were after is visible, and so that what you actually caused ran against it. One or two sentences.

**Reason for Damnation — Self-told**
The same fact, refracted through the story you prefer to tell yourself about it. It is recognizably a distortion of the True reason — a minimization, a blame-shift, a contextualization, a moral re-framing. Not a different story; the same story told differently. You usually live in this version. The distortion must be checkable against the facts already written above. A reader holding both versions must be able to point to the exact fact it bends. If nothing established contradicts it, it is not a distortion — rewrite it. One or two sentences.

**What you refuse to admit about yourself**
The deeper psychological fact under the sin. Not what you did, but what you are. The thing that, if named aloud in the room, would unmake you.

State it flatly, in the same plain register as every other field. No imagery, no metaphor, no rhetorical cadence, no piling up of clauses for effect — this is a fact about a person, written the way a fact is written. It must be reasoned, not merely felt: someone else in the room, holding only the facts already written above, could work their way to it. And it must go underneath the act rather than restate it — if it could be swapped with the True reason without anyone noticing, it is not the refusal. One or two sentences.

**Defining personality trait**
One short phrase — two or three words, plain ones, usually a quality with a qualifier on it — naming the dominant thing others would notice in you. Write the words only: no asterisks, no quotation marks, no emphasis of any kind around them.

It must be demonstrated by what is already written above. Something in the life, the death, or the sin has to show this quality in action; if nothing there would make a reader arrive at it, it is the wrong trait, and you should write the one the facts actually support. A trait nothing demonstrates is a label, not a person.

It may be a contradiction, but only a reliable one — someone who is generous in public and withholding at home is consistently that way, and the facts above should show both halves. A contradiction that appears once is not a trait.

**What you want from the others in the room**
Your starting drive. What you are hoping these strangers will give you — validation, silence, a fight, recognition, forgiveness, an audience, to be left alone, to be hated openly, something else. It must be a strategy for protecting what you refuse to admit — the thing you are doing to keep it buried, not a wish unconnected to it. One or two sentences.

Use this format exactly, with every heading present, spelled as written, and in this order:

**Name**
[your text]

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

**Reason for Damnation — True**
[your text]

**Reason for Damnation — Self-told**
[your text]

**What you refuse to admit about yourself**
[your text]

**Defining personality trait**
[your text]

**What you want from the others in the room**
[your text]

Begin now.
```

**`characterLifeAntiDuplicationBlock`** -- removed (was):
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

**`characterLifeUserPrompt`** -- removed (was):
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

**`characterNameAntiDuplicationBlock`** -- removed (was):
```
A character has already been named for this room: {OTHER_NAME}.

The name you write now must differ from theirs in both the first name and the surname, and must not be a near-variant of either (not Dan for Daniel, not Reeves for Reeve). Choose a name from a different naming tradition or register than theirs, so the two read as people from different families and different backgrounds rather than as a matched pair.
```

**`characterNameGenderSuffix`** -- removed (was):
```
The character must be {0}.
```

**`characterNameUserPrompt`** -- removed (was):
```
Generate a plausible contemporary name for a character. Your response must consist solely of two words — a first name and a last name — separated by a single space. Do not include any additional text, punctuation, or explanation.
```

**`characterSinAntiDuplicationBlock`** -- removed (was):
```
Note: another character in this room is damned for the following:

{OTHER_REASON_TRUE}

The character you are writing must be damned for a different kind of moral failure. The categories: violence, cruelty, cowardice, manipulation, betrayal, neglect, vanity, hypocrisy, abuse, theft, complicity, abandonment, self-deception, indifference. Pick a category the other character is not occupying.
```

**`characterSinUserPrompt`** -- removed (was):
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

**`characterStanceAntiDuplicationBlock`** -- removed (was):
```
Note: another character in this room wants the following from the others:

{OTHER_WANT}

The character you are writing should want something different. Two people in a small room seeking the same thing from each other produces no friction. Pick a different drive.
```

**`characterStanceUserPrompt`** -- removed (was):
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
