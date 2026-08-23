## assembly.py

```diff
--- assembly.py (previous)
+++ assembly.py (this version)
@@ -33,6 +33,8 @@
     gender: str,
     other_occupation: Optional[str] = None,
     other_cause_of_death: Optional[str] = None,
+    other_who_loved: Optional[str] = None,
+    other_who_hated: Optional[str] = None,
 ) -> tuple[str, str]:
     """
     Returns (system_prompt, user_prompt) for the Life call.
@@ -45,10 +47,13 @@
             .replace("{AGE}", str(age))
             .replace("{GENDER}", gender))
 
-    if other_occupation is not None and other_cause_of_death is not None:
+    if other_occupation is not None and other_cause_of_death is not None \
+            and other_who_loved is not None and other_who_hated is not None:
         block = (p.characterLifeAntiDuplicationBlock
                  .replace("{OTHER_OCCUPATION}", other_occupation)
-                 .replace("{OTHER_CAUSE_OF_DEATH}", other_cause_of_death))
+                 .replace("{OTHER_CAUSE_OF_DEATH}", other_cause_of_death)
+                 .replace("{OTHER_WHO_LOVED}", other_who_loved)
+                 .replace("{OTHER_WHO_HATED}", other_who_hated))
         user += "\n\n" + block
 
     return system, user
@@ -60,6 +65,8 @@
     gender: str,
     occupation: str,
     cause_of_death: str,
+    who_loved: str,
+    who_hated: str,
     prose_body: str,
     other_reason_true: Optional[str] = None,
 ) -> tuple[str, str]:
@@ -72,6 +79,8 @@
             .replace("{GENDER}", gender)
             .replace("{OCCUPATION}", occupation)
             .replace("{CAUSE_OF_DEATH}", cause_of_death)
+            .replace("{WHO_LOVED}", who_loved)
+            .replace("{WHO_HATED}", who_hated)
             .replace("{PROSE_BODY}", prose_body))
 
     if other_reason_true is not None:
@@ -141,10 +150,12 @@
 
 
 def parse_life_response(response: str) -> dict:
-    """Returns {'occupation', 'cause_of_death', 'prose_body'}. Values may be None."""
+    """Returns {'occupation', 'cause_of_death', 'who_loved', 'who_hated', 'prose_body'}. Values may be None."""
     return {
         "occupation": extract_field(response, "Occupation"),
         "cause_of_death": extract_field(response, "Cause of Death"),
+        "who_loved": extract_field(response, "Who you loved"),
+        "who_hated": extract_field(response, "Who you hated"),
         "prose_body": extract_field(response, "Life"),
     }
 
@@ -167,7 +178,10 @@
 
 
 def life_parse_complete(parsed: dict) -> bool:
-    return all(v and v.strip() for v in [parsed["occupation"], parsed["cause_of_death"], parsed["prose_body"]])
+    return all(v and v.strip() for v in [
+        parsed["occupation"], parsed["cause_of_death"],
+        parsed["who_loved"], parsed["who_hated"], parsed["prose_body"],
+    ])
 
 
 def sin_parse_complete(parsed: dict) -> bool:
@@ -181,6 +195,8 @@
 def assemble_bio(
     occupation: str,
     cause_of_death: str,
+    who_loved: str,
+    who_hated: str,
     reason_true: str,
     reason_self_told: str,
     personality_trait: str,
@@ -192,6 +208,8 @@
     sections = [
         f"**Occupation**\n{occupation}",
         f"**Cause of Death**\n{cause_of_death}",
+        f"**Who you loved**\n{who_loved}",
+        f"**Who you hated**\n{who_hated}",
         f"**Reason for Damnation — True**\n{reason_true}",
         f"**Reason for Damnation — Self-told**\n{reason_self_told}",
         f"**Defining personality trait**\n{personality_trait}",
```

## config.py

```diff
--- config.py (previous)
+++ config.py (this version)
@@ -16,9 +16,11 @@
 PROVIDER = "hf"  # "hf" or "openai"
 
 # ── Model strings (from ModelNamesController) ──
-MODEL_DIALOGUE = "Qwen/Qwen2.5-7B-Instruct"
-MODEL_ADDRESSING = "Qwen/Qwen2.5-7B-Instruct"
-MODEL_GENERATION = "Qwen/Qwen2.5-7B-Instruct"
+# Swapped from Qwen2.5-7B-Instruct 2026-08-23: its only working provider (Together AI)
+# stopped serving it. Qwen3-8B is ungated with 2 live providers (nscale, featherless-ai).
+MODEL_DIALOGUE = "Qwen/Qwen3-8B"
+MODEL_ADDRESSING = "Qwen/Qwen3-8B"
+MODEL_GENERATION = "Qwen/Qwen3-8B"
 # Narrator uses MODEL_DIALOGUE in Unity (see CharacterController.GenerateNarratorDialogue)
 MODEL_NARRATOR = MODEL_DIALOGUE
 
```

## game.py

```diff
--- game.py (previous)
+++ game.py (this version)
@@ -23,6 +23,8 @@
     # Parsed fields (used for character generation anti-duplication and other tooling)
     occupation: str = ""
     cause_of_death: str = ""
+    who_loved: str = ""
+    who_hated: str = ""
     prose_body: str = ""
     reason_true: str = ""
     reason_self_told: str = ""
```

## prompts.py

**`characterLifeAntiDuplicationBlock`** -- before:
```
Important: a character has already been written for this room.

Their Occupation: {OTHER_OCCUPATION}
Their Cause of Death: {OTHER_CAUSE_OF_DEATH}

The character you are writing now must feel like a genuinely different person — a different life, a different end. Specifically:

- The occupation must be from a different kind of life. Not a near-equivalent job. If the other character drives for work, do not write another driver. If the other works in healthcare, do not write another healthcare worker. Pick a life that contrasts in class, work register, or daily texture.
- The cause of death must be a different kind of death. Not the same general category. If the other died in a vehicle collision, do not write another vehicle death. If the other died of illness, do not write another illness. The categories of death include: vehicle, violence, illness, accident, overdose, suicide, old age, occupational, and others — pick a different one.

Do not contradict, reference, or comment on the other character. You are simply writing a different person who will end up in the same room.
```
after:
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

After these two fields, write a single paragraph of around 80–100 words in the second person. Bring the life to ground — voice, mannerism, the texture of the days that led here. End the paragraph at the moment the lights went out, or the moment after. Do not describe arriving anywhere. Do not describe a room. Stop at the threshold.

Use this format exactly:

**Occupation**
[your text]

**Cause of Death**
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

**`characterSinUserPrompt`** -- before:
```
The character has been described:

Name: {NAME}
Age: {AGE}, {GENDER}
Occupation: {OCCUPATION}
Cause of Death: {CAUSE_OF_DEATH}

{PROSE_BODY}

Now write the moral content. Why is this person damned? What did they do? What do they tell themselves about it? What do they refuse to face?

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
