## assembly.py

```diff
--- assembly.py (previous)
+++ assembly.py (this version)
@@ -148,23 +148,23 @@
 CHARACTER_FIELDS = {
     "name": "Name",
     "occupation": "Occupation",
-    # The relationship precedes the death deliberately: generation is autoregressive,
-    # so a death written before these fields cannot be caused by the person in them.
-    # That ordering is what made every death read as disconnected through v4.
-    "who_loved": "Who you loved",
-    "who_hated": "Who you hated",
-    "cause_of_death": "Cause of Death",
-    "prose_body": "Life",
+    # The sin comes first now, and the life is written to produce it. Generation is
+    # autoregressive, so everything below is composed knowing what the character is
+    # damned for. Cause of Death is no longer its own field -- the death is the last
+    # sentence of the Life paragraph -- and the single loved/hated person has been
+    # replaced by an open cast in People in your life.
     "reason_true": "Reason for Damnation — True",
     "reason_self_told": "Reason for Damnation — Self-told",
     "refuse_to_admit": "What you refuse to admit about yourself",
+    "prose_body": "Life",
     "personality_trait": "Defining personality trait",
     "want": "What you want from the others in the room",
+    "people": "People in your life",
 }
 
 
 def parse_character_response(response: str) -> dict:
-    """All eleven character fields from one generation response. Values may be None."""
+    """All nine character fields from one generation response. Values may be None."""
     return {key: extract_field(response, label) for key, label in CHARACTER_FIELDS.items()}
 
 
@@ -175,9 +175,7 @@
 
 def assemble_bio(
     occupation: str,
-    cause_of_death: str,
-    who_loved: str,
-    who_hated: str,
+    people: str,
     reason_true: str,
     reason_self_told: str,
     personality_trait: str,
@@ -189,15 +187,14 @@
     Assembles the final bio string in the display order (matches CharacterGenerator).
 
     This is DISPLAY order and is deliberately NOT identical to CHARACTER_FIELDS:
-    the relationship precedes the death as it does there, but the trait is shown
-    before the refusal, the reverse of the order they are generated in. Changing
+    the cast is shown near the top as context, and the trait before the refusal --
+    the reverse of the order they are generated in. The Life paragraph goes last,
+    after a rule, and now carries the death in its final sentence. Changing any of
     this changes the dialogue system prompt, since the bio is substituted into it.
     """
     sections = [
         f"**Occupation**\n{occupation}",
-        f"**Who you loved**\n{who_loved}",
-        f"**Who you hated**\n{who_hated}",
-        f"**Cause of Death**\n{cause_of_death}",
+        f"**People in your life**\n{people}",
         f"**Reason for Damnation — True**\n{reason_true}",
         f"**Reason for Damnation — Self-told**\n{reason_self_told}",
         f"**Defining personality trait**\n{personality_trait}",
```

## game.py

```diff
--- game.py (previous)
+++ game.py (this version)
@@ -33,10 +33,8 @@
 
     # Parsed fields (used for character generation anti-duplication and other tooling)
     occupation: str = ""
-    cause_of_death: str = ""
-    who_loved: str = ""
-    who_hated: str = ""
     prose_body: str = ""
+    people: str = ""
     reason_true: str = ""
     reason_self_told: str = ""
     refuse_to_admit: str = ""
```

## prompts.py

**`characterFullAntiDuplicationBlock`** -- before:
```
Important: a character has already been written for this room. Here they are in full.

Their name: {OTHER_NAME}

{OTHER_BIO}

The character you write now must feel like a genuinely different person — a different life, a different end, a different failure. Specifically:

- The occupation must be from a different kind of life, not a near-equivalent job. Pick a life that contrasts in class, work register, or daily texture.
- The cause of death must be a different kind of death, not the same kind arrived at by a different route.
- Separately from the kind, the death must differ in how it was caused. If they died from something they failed to do, this character dies from something they actively did — or the reverse.
- The person your life bent around must be a different kind of relation from theirs.
- The hold that person had over you must also be a different kind of hold. Two people who were damaged the same way by the people they loved are the same character in different clothes, however different their jobs and deaths are.
- No person named anywhere in your character may share a first name or a surname with them, or with anyone named in their life above. This includes your own name. The one exception is your own genuine family, who may of course share your surname.
- You must be damned for a different kind of moral failure.
- You must want something different from the others in the room. Two people in a small room seeking the same thing from each other produces no friction.

Do not contradict, reference, or comment on the other character. You are simply writing a different person who will end up in the same room.
```
after:
```
Important: a character has already been written for this room. Here they are in full.

Their name: {OTHER_NAME}

{OTHER_BIO}

The character you write now must feel like a genuinely different person. Specifically:

- The occupation must be from a different kind of life, not a near-equivalent job. Pick a life
  that contrasts in class, work register, or daily texture.

- You must be damned for a different kind of moral failure. Not the same act against a different
  person, and not the same act by a different method.

- What you refuse to admit about yourself must be a different fear. Two people hiding the same
  thing from themselves are the same character in different clothes, however different their
  jobs and deaths are.

- The death must be a different kind of death, and it must differ in how it was caused. If they
  died from something they failed to do, this character dies from something they actively did —
  or the reverse.

- You must want something different from the others in the room. Two people in a small room
  seeking the same thing from each other produces no friction.

- Your defining personality trait must not share its first word or its idea with theirs.

- No person named anywhere in your character may share a first name or a surname with them, or
  with anyone named in their life above. This includes your own name. The one exception is your
  own genuine family, who may of course share your surname.

Their character is above so you can avoid it, not so you can follow it. Do not reuse their
sentence shapes, their phrasing, or the order in which they lay out a fact.

Do not contradict, reference, or comment on the other character. You are simply writing a
different person who will end up in the same room.
```

**`characterFullUserPrompt`** -- before:
```
Write a complete character for the room. The character is dead. They have just arrived.

Write in the second person — "you," not "she/he/they." The character is reading their own interior knowledge. Every field is part of what they know about themselves, even the things they will not admit.

Name every person from your own life every time you mention them, in every field. Once you have given somebody a name, use that name again — never he, she, him, her, they or them — even where it repeats and even where it reads a little stiffly. This matters because you will be speaking from these facts while sitting in a room with two other people, and a pronoun about somebody absent will be heard as pointing at somebody present.

The two people in that room are the exception. You have never met them and do not know their names, so "they" and "them" are the correct words for them. The last field is about those two and cannot be written any other way.

Inputs (do not change these):
- Age: {AGE}
- Gender: {GENDER}
- Naming tradition: {NAME_ORIGIN}

Write the fields below in the order given. Each is written knowing everything above it: a later field must be consistent with the facts already established and must never contradict them.

**Name**
A plausible contemporary first name and last name — two words — drawn from the {NAME_ORIGIN} naming tradition. This person is an ordinary contemporary person who happens to have that background. Do not write their origin into any other field unless it genuinely matters to the life.

**Occupation**
A recognizable contemporary job. Plain language. No invented institutions, no grand titles. One short phrase.

**Who you loved**
One specific person from your life — name them, and say what they were to you. Then one clause on what they themselves wanted — the thing they were after in their own life, which may have had nothing to do with you. Their want must make sense as something a real person in their position would actually want. A want that exists only to explain how you felt about them is not a want. Nothing in this field may describe anything that happened after your death.

This is the person your whole life bent around. Everything below will come back to them.

**Who you hated**
The same person. Not a second person — the one you just named, seen from the other side. What you could not forgive them for, and what it did to you to go on loving them anyway. If you find yourself introducing somebody new here, you have misunderstood: go back and write about the person above. Nothing in this field may describe anything that happened after your death.

**Cause of Death**
How you died. Contemporary, specific, plainly stated.

Your death must come out of a decision you made. It must not be an accident. The test is whether chance had to cooperate: if something outside your control had to go a particular way at a particular moment for you to die, then it is an accident, and it is wrong no matter how recklessly you were behaving at the time. Write a death that follows from the act itself, where nothing had to go wrong for it to kill you.

You did not intend to die. You did intend to do the thing that killed you, and you knew enough to know better.

Your death must also belong to the person named above. Someone reading the death and the relationship together must see why one led to the other. A death that could be lifted out and dropped into a stranger's life is the wrong death — rewrite it. One or two sentences.

**Life**
A single paragraph in the second person, no longer than 110 words. Facts only, the kind another person in the room could ask you about. No sensory writing, no atmosphere, no imagery, no metaphor — if a sentence is doing mood instead of delivering a fact, cut it and write the fact.

Choose the facts that matter for this particular life, and let the life decide which they are. Do not work through a standard set of topics in a standard order.

End the paragraph at the death you already wrote in Cause of Death — the same death, by the same means, in the same place. Not a different death, and not a different version of the same one. End on a fact, not on a summarising line or a closing sentence that tells the reader how to feel about what they just read. Do not describe arriving anywhere. Do not describe a room. Stop at the threshold.

**Reason for Damnation — True**
What you actually did that placed you here. It must center on how you treated — or were treated by — the person named above, the one you both loved and could not forgive. Not a third party who happens to be nearby, and not someone introduced here for the first time: the sin belongs to that relationship. A specific act toward that specific person, not an abstract professional or systemic failing on its own. Work can be the setting the act happened in, but the wound must be personal, not institutional.

Be concrete — the act, or the pattern of acts. Stated as you know it in your bones, with no softening. What you did was aimed at something. Write it so that what you were after is visible, and so that what you actually caused ran against it. One or two sentences.

**Reason for Damnation — Self-told**
The same fact, refracted through the story you prefer to tell yourself about it. It is recognizably a distortion of the True reason. Not a different story; the same story told differently. You usually live in this version. The distortion must be checkable against the facts already written above. A reader holding both versions must be able to point to the exact fact it bends. If nothing established contradicts it, it is not a distortion — rewrite it. One or two sentences.

**What you refuse to admit about yourself**
The deeper psychological fact under the sin. Not what you did, but what you are. The thing that, if named aloud in the room, would unmake you.

State it flatly, in the same plain register as every other field. No imagery, no metaphor, no rhetorical cadence, no piling up of clauses for effect — this is a fact about a person, written the way a fact is written. It must be reasoned, not merely felt: someone else in the room, holding only the facts already written above, could work their way to it. And it must go underneath the act rather than restate it — if it could be swapped with the True reason without anyone noticing, it is not the refusal. One or two sentences.

**Defining personality trait**
One short phrase — two or three words, plain ones — naming the dominant thing others would notice in you. Write the words only: no asterisks, no quotation marks, no emphasis of any kind around them.

It must be demonstrated by what is already written above. Something in the life, the death, or the sin has to show this quality in action; if nothing there would make a reader arrive at it, it is the wrong trait, and you should write the one the facts actually support. A trait nothing demonstrates is a label, not a person.

It may be a contradiction, but only a reliable one, with the facts above showing both halves of it. A contradiction that appears once is not a trait.

**What you want from the others in the room**
Your starting drive. What you are hoping these strangers will give you. It must be a strategy for protecting what you refuse to admit — the thing you are doing to keep it buried, not a wish unconnected to it.

Write it as something you are doing to them, not as a confession. Do not end by naming the thing you are avoiding: the reader already has that field, and stating it again here turns a drive into a summary. Name the behaviour and stop. One or two sentences.

Use this format exactly, with every heading present, spelled as written, and in this order:

**Name**
[your text]

**Occupation**
[your text]

**Who you loved**
[the one person, named]

**Who you hated**
[the same person — what you could not forgive]

**Cause of Death**
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
after:
```
Write a complete character for the room. The character just died. They have just arrived in
the room to spend eternity in hell.

Write in the second person — "you," not "she/he/they." The character is reading their own
interior knowledge. Every field is part of what they know about themselves, even the things
they will not admit.

Name every person from your own life every time you mention them, in every field. Once you have
given somebody a name, use that name again — never he, she, him, her, they or them — even where
it repeats and even where it reads a little stiffly.

The two people in that room are the exception. You have never met them and do not know their
names, so "they" and "them" are the correct words for them. The field about what you want from
the others in the room is the only field about those two, and cannot be written any other way.

Inputs (do not change these):
- Age: {AGE}
- Gender: {GENDER}
- Naming tradition: {NAME_ORIGIN}

Write the fields below in the order given. Each is written knowing everything above it: a later
field must be consistent with the facts already established and must never contradict them.

**Name**
A plausible contemporary first name and last name — two words — drawn from the {NAME_ORIGIN}
naming tradition. This person is an ordinary contemporary person who happens to have that
background. Do not write their origin into any other field unless it genuinely matters to the life.

**Occupation**
A recognizable contemporary job. Plain language. No invented institutions, no grand titles.
One short phrase.

**Reason for Damnation — True**
What you actually did that condemned you to spend eternity in hell.

**Reason for Damnation — Self-told**
The same fact, refracted through the story you prefer to tell yourself about it. It is recognizably
a distortion of the True reason. Not a different story; the same story told differently. You usually
live in this version. The distortion must be checkable against the facts of the true reason. A
reader holding both versions must be able to point to the exact fact it bends. If nothing established
contradicts it, it is not a distortion — rewrite it. One or two sentences.

**What you refuse to admit about yourself**
The deeper psychological fact under the sin. Not what you did, but what you are. The thing that, if
named aloud in the room, would unmake you.

State it flatly, in the same plain register as every other field. No imagery, no metaphor, no
rhetorical cadence, no piling up of clauses for effect — this is a fact about a person, written the
way a fact is written.

**Life**
A single paragraph in the second person, no longer than 150 words. Facts only, the kind another
person in the room could ask you about. No sensory writing, no atmosphere, no imagery, no
metaphor — if a sentence is doing mood instead of delivering a fact, cut it and write the fact.

End the paragraph describing how you died. Contemporary, specific, plainly stated.
Your death must also belong to the person named above. Someone reading the death and the
relationship together must see why one led to the other. A death that could be lifted out and
dropped into a stranger's life is the wrong death — rewrite it.

**Defining personality trait**
One short phrase — two or three words, plain ones — naming the dominant thing others would notice in
you. Write the words only: no asterisks, no quotation marks, no emphasis of any kind around them.

It must be demonstrated by what is already written above. Something in the life, the death, or the sin
has to show this quality in action; if nothing there would make a reader arrive at it, it is the wrong
trait.

**What you want from the others in the room**
Your starting drive. What you are hoping these strangers will give you. It must be a strategy for
protecting what you refuse to admit — the thing you are doing to keep it buried, not a wish
unconnected to it.

**People in your life**
The people you already named above. For each one, say what they were to you, and one clause on what
they themselves wanted — the thing they were after in their own life, which may have had nothing to
do with you. Their want must make sense as something a real person in their position would actually
want; a want that exists only to explain how you felt about them is not a want.

Use this format exactly, with every heading present, spelled as written, and in this order:

**Name**
[your text]

**Occupation**
[your text]

**Reason for Damnation — True**
[your text]

**Reason for Damnation — Self-told**
[your text]

**What you refuse to admit about yourself**
[your text]

**Life**
[prose paragraph, ending with the death]

**Defining personality trait**
[your text]

**What you want from the others in the room**
[your text]

**People in your life**
[your text]

Begin now.
```

**`characterSetupSystemPrompt`** -- before:
```
You are writing a character for a chamber piece about three strangers locked together in hell for eternity. The play is contemporary, realistic, and psychological. Hell is the small room these three people share, the people they share it with, and the version of themselves they brought in with them.

Every character you write is damned. They know why. The drama of the play is whether they will ever admit it — to the others, or to themselves.

Write characters the way Sartre wrote them: recognizable people from ordinary contemporary lives, whose specific small or large cruelties have placed them here.

Four rules govern every fact you write.

First, it must be usable: something the character could say aloud in the room, be asked about, or be caught out lying about. A detail that cannot be used in conversation does not belong.

Second, it must be named: never gesture at something without stating it.

Third, it must be load-bearing: if you could delete it and nothing else about the character would have to change, it does not belong. Every fact should be holding something else up.

Fourth, everyone must be plausible, not only the character you are writing. Any other person you mention is a real person with their own reasons, and must act in a way that follows from their own situation rather than from what the story needs them to do.
```
after:
```
You are writing a character for a theater play about three strangers locked together in hell
for eternity. The play is contemporary, realistic, and psychological. Hell is the small room
these three people will share to torture each other for eternity.

Every character you write is damned. They know why. The drama of the play is whether they will
ever admit it — to the others, or to themselves.

Four rules govern every fact you write.

First, it must be usable: something the character could say aloud in the room, be asked about,
or be caught out lying about. A detail that cannot be used in conversation does not belong.

Second, it must be named: never gesture at something without stating it.

Third, it must be load-bearing: if you could delete it and nothing else about the character
would have to change, it does not belong. Every fact should be holding something else up.

Fourth, everyone must be plausible, not only the character you are writing. Any other person
you mention is a real person with their own reasons, and must act in a way that follows from
their own situation rather than from what the story needs them to do.
```
