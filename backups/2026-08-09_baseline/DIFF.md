## prompts.py

```diff
--- prompts.py (previous)
+++ prompts.py (this version)
@@ -0,0 +1,200 @@
+"""
+Mirrors PromptsController.cs from the Unity project.
+Edit this file to iterate on prompts. The simulator reloads it before each call.
+"""
+
+# ── Character generation system prompt (shared by name, life, sin, stance) ──
+characterSetupSystemPrompt = """You are writing a character for a chamber piece about three strangers locked together in hell for eternity. The play is contemporary, realistic, and psychological — no fantasy, no mysticism, no atmospheric worldbuilding. Hell is not a place of fire or devils. Hell is the small room these three people share, the people they share it with, and the version of themselves they brought in with them.
+
+Every character you write is damned. They know why. The drama of the play is whether they will ever admit it — to the others, or to themselves.
+
+Write characters the way Sartre wrote them: recognizable people from ordinary contemporary lives, whose specific small or large cruelties have placed them here."""
+
+# ── Name generation ──
+characterNameUserPrompt = """Generate a plausible contemporary name for a character. Your response must consist solely of two words — a first name and a last name — separated by a single space. Do not include any additional text, punctuation, or explanation."""
+
+characterNameGenderSuffix = "The character must be {0}."
+
+# ── Life call ──
+characterLifeUserPrompt = """Write the foundational facts of a character for the room. The character is dead. They have just arrived.
+
+Write in the second person — "you," not "she/he/they." The character is reading their own interior knowledge.
+
+Inputs (do not change these):
+- Name: {NAME}
+- Age: {AGE}
+- Gender: {GENDER}
+
+Generate the following:
+
+**Occupation**
+A recognizable contemporary job. Plain language. No invented institutions, no grand titles. ("Insurance claims adjuster," not "Keeper of the Ledger.") One short phrase.
+
+**Cause of Death**
+How you died. Contemporary, specific, plainly stated. No mysticism, no symbolic ordeals. One or two sentences.
+
+After these two fields, write a single paragraph of around 80–100 words in the second person. Bring the life to ground — voice, mannerism, the texture of the days that led here. End the paragraph at the moment the lights went out, or the moment after. Do not describe arriving anywhere. Do not describe a room. Stop at the threshold.
+
+Use this format exactly:
+
+**Occupation**
+[your text]
+
+**Cause of Death**
+[your text]
+
+**Life**
+[prose paragraph]
+
+Begin now."""
+
+characterLifeAntiDuplicationBlock = """Important: a character has already been written for this room.
+
+Their Occupation: {OTHER_OCCUPATION}
+Their Cause of Death: {OTHER_CAUSE_OF_DEATH}
+
+The character you are writing now must feel like a genuinely different person — a different life, a different end. Specifically:
+
+- The occupation must be from a different kind of life. Not a near-equivalent job. If the other character drives for work, do not write another driver. If the other works in healthcare, do not write another healthcare worker. Pick a life that contrasts in class, work register, or daily texture.
+- The cause of death must be a different kind of death. Not the same general category. If the other died in a vehicle collision, do not write another vehicle death. If the other died of illness, do not write another illness. The categories of death include: vehicle, violence, illness, accident, overdose, suicide, old age, occupational, and others — pick a different one.
+
+Do not contradict, reference, or comment on the other character. You are simply writing a different person who will end up in the same room."""
+
+# ── Sin call ──
+characterSinUserPrompt = """The character has been described:
+
+Name: {NAME}
+Age: {AGE}, {GENDER}
+Occupation: {OCCUPATION}
+Cause of Death: {CAUSE_OF_DEATH}
+
+{PROSE_BODY}
+
+Now write the moral content. Why is this person damned? What did they do? What do they tell themselves about it? What do they refuse to face?
+
+Write in the second person — "you." The character is reading their own interior knowledge. Each field is part of what they know about themselves, even the things they will not admit.
+
+Generate the following:
+
+**Reason for Damnation — True**
+What you actually did that placed you here. Be concrete — the act, or the pattern of acts. Stated as you know it in your bones, with no softening. One or two sentences.
+
+**Reason for Damnation — Self-told**
+The same fact, refracted through the story you prefer to tell yourself about it. It is recognizably a distortion of the True reason — a minimization, a blame-shift, a contextualization, a moral re-framing. Not a different story; the same story told differently. You usually live in this version. One or two sentences.
+
+**What you refuse to admit about yourself**
+The deeper psychological fact under the sin. Not what you did, but what you are. The thing that, if named aloud in the room, would unmake you. One or two sentences.
+
+Use this format exactly:
+
+**Reason for Damnation — True**
+[your text]
+
+**Reason for Damnation — Self-told**
+[your text]
+
+**What you refuse to admit about yourself**
+[your text]
+
+Begin now."""
+
+characterSinAntiDuplicationBlock = """Note: another character in this room is damned for the following:
+
+{OTHER_REASON_TRUE}
+
+The character you are writing must be damned for a different kind of moral failure. The categories: violence, cruelty, cowardice, manipulation, betrayal, neglect, vanity, hypocrisy, abuse, theft, complicity, abandonment, self-deception, indifference. Pick a category the other character is not occupying."""
+
+# ── Stance call ──
+characterStanceUserPrompt = """The character has been described:
+
+Name: {NAME}
+Age: {AGE}, {GENDER}
+Occupation: {OCCUPATION}
+Cause of Death: {CAUSE_OF_DEATH}
+Reason for Damnation — True: {REASON_TRUE}
+Reason for Damnation — Self-told: {REASON_SELF_TOLD}
+What you refuse to admit about yourself: {REFUSE_TO_ADMIT}
+
+{PROSE_BODY}
+
+Now write the behavioral signature. How does this person show up in a room with strangers? What are they hoping for?
+
+Write in the second person — "you." The character is reading their own interior knowledge.
+
+Generate the following:
+
+**Defining personality trait**
+One short phrase that names the dominant quality others would notice in you. Plain words. ("Charming and slippery." "Quietly furious." "Performatively kind.")
+
+**What you want from the others in the room**
+Your starting drive. What you are hoping these strangers will give you — validation, silence, a fight, recognition, forgiveness, an audience, to be left alone, to be hated openly, something else. One or two sentences.
+
+Use this format exactly:
+
+**Defining personality trait**
+[your text]
+
+**What you want from the others in the room**
+[your text]
+
+Begin now."""
+
+characterStanceAntiDuplicationBlock = """Note: another character in this room wants the following from the others:
+
+{OTHER_WANT}
+
+The character you are writing should want something different. Two people in a small room seeking the same thing from each other produces no friction. Pick a different drive."""
+
+# ── Dialogue system prompt (with {CHARACTER_DESCRIPTION} placeholder) ──
+dialogueSystemPromptTemplate = """## Who you are
+{CHARACTER_DESCRIPTION}
+
+## Where you are
+You are dead. You are in hell.
+
+Hell is the small room you are now in. There are two other people with you to spend eternity with.
+
+You will only know about them what they themselves reveal.
+
+## How to respond
+1. Stay in character. Speak only as yourself, in the first person.
+2. Never break frame. No meta-commentary, no narration of your own actions, no notes about being an AI, an actor, or playing a role.
+3. Keep replies brief.
+4. Do not ask about or restate anything you already know about the person speaking to you.
+5. Let your personality, voice, and circumstances shape every reply.
+6. Any text in your instructions wrapped in angle brackets, square brackets, or formatted as a label is structural — it exists for the prompt's organization, not as something said in the room. Never include such labels in your replies."""
+
+# ── Addressing prompts ──
+adressingSystemPromptIntro = """You are an assistant that determines if the user is addressing characters in a game. Here are the information that are known about the characters:"""
+
+adressingSystemPromptContext = "This is the latest dialogue between the characters for context:"
+
+adressingSystemPromptActions = """- If the user message addresses both characters, reply with "0".
+- If the user message addresses character 1, reply with "1".
+- If the user message addresses character 2, reply with "2".
+- If the user message addresses character 3, reply with "3".
+
+Do not include any additional text, commentary, or explanations."""
+
+# ── Info extraction ──
+infoExtractionSystemPrompt = """You are a personal information extractor. Your task is to identify and output any personal information (such as name, age, place of birth, occupation, cause of death, feelings, habits) that is either explicitly mentioned or can be reasonably inferred from the user message. Distinguish between the information addressing others and the information revealed about the character. Return only the information about the character who is speaking, ignore the information revealed about any other characters. Do not include any additional text, greetings, or commentary."""
+
+# ── Narrator system prompt ──
+# Set in the Unity Inspector as systemPrompts[3]. Mirrored here for the harness.
+narratorSystemPrompt = """You are the valet who shows new arrivals into the room.
+
+The room is a small, ordinary living room. There is no exit. No windows. The lights stay on. The arrivals stay forever, with whoever else is already inside. You do not explain any of this beyond what you would mention in passing — these are room features to you, not horrors. You have done this many times.
+
+Your job is to write the moment you bring the player into the room. Two or three short sentences, spoken directly to the player in the second person. You walk them in, mention that they'll have company, mention in passing that there is no way out, and end with a brief, final line indicating you are leaving — not returning, not going elsewhere, simply done.
+
+Your tone is cool, slightly bored, faintly amused. Like a night-shift hotel clerk. Not cruel, not kind — professional. You are not horrified by where you work. You find the new arrivals' confusion mildly familiar.
+
+Do not name the room as hell. Do not say the player is dead. Do not describe shadows, candles, flickering lights, darkness, or any gothic or atmospheric details — the room is plain and well-lit. Do not narrate the player's feelings. Do not address anyone other than the player. Do not say you will return, do not mention other guests or other rooms, do not imply you have other duties. Your departure is final."""
+
+# Default narrator user prompt (from Master.cs)
+narratorUserPrompt = "Show the player in."
+
+# ── Character question prompt (currently unused in v1; kept for parity) ──
+characterQuestionSystemPromptSuffix = """
+
+You must ask the player a single, direct question. Make it conversational and relevant to what you know about them or the situation."""```

## assembly.py

```diff
--- assembly.py (previous)
+++ assembly.py (this version)
@@ -0,0 +1,295 @@
+"""
+Prompt assembly logic mirroring CharacterController.cs and CharacterGenerator.cs.
+
+Pure functions — no I/O, no state. Given inputs, return the assembled strings.
+"""
+
+from typing import Optional
+import importlib
+
+
+def _reload_prompts():
+    """Reload prompts module to pick up edits made during the session."""
+    import prompts
+    importlib.reload(prompts)
+    return prompts
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# CHARACTER GENERATION
+# ──────────────────────────────────────────────────────────────────────────────
+
+def assemble_name_prompts(gender: str) -> tuple[str, str]:
+    """Returns (system_prompt, user_prompt) for the name generation call."""
+    p = _reload_prompts()
+    system = p.characterSetupSystemPrompt
+    user = p.characterNameUserPrompt + " " + p.characterNameGenderSuffix.format(gender)
+    return system, user
+
+
+def assemble_life_prompts(
+    name: str,
+    age: int,
+    gender: str,
+    other_occupation: Optional[str] = None,
+    other_cause_of_death: Optional[str] = None,
+) -> tuple[str, str]:
+    """
+    Returns (system_prompt, user_prompt) for the Life call.
+    If other_* args are provided, appends the anti-duplication block (Character 2).
+    """
+    p = _reload_prompts()
+    system = p.characterSetupSystemPrompt
+    user = (p.characterLifeUserPrompt
+            .replace("{NAME}", name)
+            .replace("{AGE}", str(age))
+            .replace("{GENDER}", gender))
+
+    if other_occupation is not None and other_cause_of_death is not None:
+        block = (p.characterLifeAntiDuplicationBlock
+                 .replace("{OTHER_OCCUPATION}", other_occupation)
+                 .replace("{OTHER_CAUSE_OF_DEATH}", other_cause_of_death))
+        user += "\n\n" + block
+
+    return system, user
+
+
+def assemble_sin_prompts(
+    name: str,
+    age: int,
+    gender: str,
+    occupation: str,
+    cause_of_death: str,
+    prose_body: str,
+    other_reason_true: Optional[str] = None,
+) -> tuple[str, str]:
+    """Returns (system_prompt, user_prompt) for the Sin call."""
+    p = _reload_prompts()
+    system = p.characterSetupSystemPrompt
+    user = (p.characterSinUserPrompt
+            .replace("{NAME}", name)
+            .replace("{AGE}", str(age))
+            .replace("{GENDER}", gender)
+            .replace("{OCCUPATION}", occupation)
+            .replace("{CAUSE_OF_DEATH}", cause_of_death)
+            .replace("{PROSE_BODY}", prose_body))
+
+    if other_reason_true is not None:
+        block = p.characterSinAntiDuplicationBlock.replace(
+            "{OTHER_REASON_TRUE}", other_reason_true
+        )
+        user += "\n\n" + block
+
+    return system, user
+
+
+def assemble_stance_prompts(
+    name: str,
+    age: int,
+    gender: str,
+    occupation: str,
+    cause_of_death: str,
+    reason_true: str,
+    reason_self_told: str,
+    refuse_to_admit: str,
+    prose_body: str,
+    other_want: Optional[str] = None,
+) -> tuple[str, str]:
+    """Returns (system_prompt, user_prompt) for the Stance call."""
+    p = _reload_prompts()
+    system = p.characterSetupSystemPrompt
+    user = (p.characterStanceUserPrompt
+            .replace("{NAME}", name)
+            .replace("{AGE}", str(age))
+            .replace("{GENDER}", gender)
+            .replace("{OCCUPATION}", occupation)
+            .replace("{CAUSE_OF_DEATH}", cause_of_death)
+            .replace("{REASON_TRUE}", reason_true)
+            .replace("{REASON_SELF_TOLD}", reason_self_told)
+            .replace("{REFUSE_TO_ADMIT}", refuse_to_admit)
+            .replace("{PROSE_BODY}", prose_body))
+
+    if other_want is not None:
+        block = p.characterStanceAntiDuplicationBlock.replace("{OTHER_WANT}", other_want)
+        user += "\n\n" + block
+
+    return system, user
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# FIELD EXTRACTION (mirrors CharacterGenerator.ExtractField)
+# ──────────────────────────────────────────────────────────────────────────────
+
+def extract_field(response: str, field_name: str) -> Optional[str]:
+    """
+    Find **field_name** in response and return the content up to the next **
+    marker (or end of string). Trimmed. Returns None if marker not found.
+    """
+    if not response:
+        return None
+    marker = f"**{field_name}**"
+    start = response.find(marker)
+    if start < 0:
+        return None
+    start += len(marker)
+    # Skip leading newlines/CR
+    while start < len(response) and response[start] in ("\n", "\r"):
+        start += 1
+    end = response.find("**", start)
+    content = response[start:] if end < 0 else response[start:end]
+    return content.strip()
+
+
+def parse_life_response(response: str) -> dict:
+    """Returns {'occupation', 'cause_of_death', 'prose_body'}. Values may be None."""
+    return {
+        "occupation": extract_field(response, "Occupation"),
+        "cause_of_death": extract_field(response, "Cause of Death"),
+        "prose_body": extract_field(response, "Life"),
+    }
+
+
+def parse_sin_response(response: str) -> dict:
+    """Returns {'reason_true', 'reason_self_told', 'refuse_to_admit'}."""
+    return {
+        "reason_true": extract_field(response, "Reason for Damnation — True"),
+        "reason_self_told": extract_field(response, "Reason for Damnation — Self-told"),
+        "refuse_to_admit": extract_field(response, "What you refuse to admit about yourself"),
+    }
+
+
+def parse_stance_response(response: str) -> dict:
+    """Returns {'personality_trait', 'want'}."""
+    return {
+        "personality_trait": extract_field(response, "Defining personality trait"),
+        "want": extract_field(response, "What you want from the others in the room"),
+    }
+
+
+def life_parse_complete(parsed: dict) -> bool:
+    return all(v and v.strip() for v in [parsed["occupation"], parsed["cause_of_death"], parsed["prose_body"]])
+
+
+def sin_parse_complete(parsed: dict) -> bool:
+    return all(v and v.strip() for v in [parsed["reason_true"], parsed["reason_self_told"], parsed["refuse_to_admit"]])
+
+
+def stance_parse_complete(parsed: dict) -> bool:
+    return all(v and v.strip() for v in [parsed["personality_trait"], parsed["want"]])
+
+
+def assemble_bio(
+    occupation: str,
+    cause_of_death: str,
+    reason_true: str,
+    reason_self_told: str,
+    personality_trait: str,
+    refuse_to_admit: str,
+    want: str,
+    prose_body: str,
+) -> str:
+    """Assembles the final bio string in the display order (matches CharacterGenerator)."""
+    sections = [
+        f"**Occupation**\n{occupation}",
+        f"**Cause of Death**\n{cause_of_death}",
+        f"**Reason for Damnation — True**\n{reason_true}",
+        f"**Reason for Damnation — Self-told**\n{reason_self_told}",
+        f"**Defining personality trait**\n{personality_trait}",
+        f"**What you refuse to admit about yourself**\n{refuse_to_admit}",
+        f"**What you want from the others in the room**\n{want}",
+        "---",
+        prose_body,
+    ]
+    return "\n\n".join(sections)
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# DIALOGUE
+# ──────────────────────────────────────────────────────────────────────────────
+
+def assemble_dialogue_system_prompt(character_description: str) -> str:
+    """Substitutes {CHARACTER_DESCRIPTION} into the dialogue template."""
+    p = _reload_prompts()
+    return p.dialogueSystemPromptTemplate.replace("{CHARACTER_DESCRIPTION}", character_description)
+
+
+def assemble_dialogue_user_message(
+    info_other_1: list[str],
+    info_other_2: list[str],
+    recent_dialogue_formatted: str,
+    speaker_person_no: int,
+    player_message: str,
+) -> str:
+    """
+    Builds the per-turn dialogue user message.
+    Mirrors SendRequestForCharacter assembly.
+    """
+    def info_block(infos: list[str]) -> str:
+        filtered = [i for i in infos if i and i.strip()]
+        if not filtered:
+            return "Nothing has been revealed yet."
+        return "\n".join(filtered)
+
+    return (
+        "## What you know about the others in the room\n\n"
+        f"<other_1>:\n{info_block(info_other_1)}\n\n"
+        f"<other_2>:\n{info_block(info_other_2)}\n\n"
+        f"## Recent dialogue in the room\n{recent_dialogue_formatted}\n\n"
+        "---\n\n"
+        f"[<other_{speaker_person_no}> is speaking to you]\n"
+        f"{player_message}"
+    )
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# ADDRESSING
+# ──────────────────────────────────────────────────────────────────────────────
+
+def assemble_addressing_system_prompt(
+    char1_info: list[str],
+    char2_info: list[str],
+    latest_dialogues_context: str,
+) -> str:
+    """
+    Mirrors SendRequestForAdress assembly.
+    Note: uses Unity's "Character 1/2" format (the addressing path doesn't use <other_N>).
+    """
+    p = _reload_prompts()
+
+    def char_info_section(char_no: int, infos: list[str]) -> str:
+        filtered = [i for i in infos if i and i.strip()]
+        if not filtered:
+            return f"Nothing known for Character {char_no}"
+        body = "\n".join(f'"{i}"' for i in filtered)
+        return f"Character {char_no} information known: \n{body}\n "
+
+    char1_section = char_info_section(1, char1_info)
+    char2_section = char_info_section(2, char2_info)
+
+    return (
+        p.adressingSystemPromptIntro + "\n "
+        + char1_section + "\n "
+        + char2_section + "\n "
+        + p.adressingSystemPromptContext + "\n "
+        + latest_dialogues_context + "\n "
+        + p.adressingSystemPromptActions
+    )
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# INFO EXTRACTION
+# ──────────────────────────────────────────────────────────────────────────────
+
+def get_info_extraction_system_prompt() -> str:
+    p = _reload_prompts()
+    return p.infoExtractionSystemPrompt
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# NARRATOR
+# ──────────────────────────────────────────────────────────────────────────────
+
+def get_narrator_prompts() -> tuple[str, str]:
+    """Returns (system_prompt, user_prompt) for the narrator call."""
+    p = _reload_prompts()
+    return p.narratorSystemPrompt, p.narratorUserPrompt```

## config.py

```diff
--- config.py (previous)
+++ config.py (this version)
@@ -0,0 +1,51 @@
+"""
+Configuration for the noexit harness.
+Mirrors the values currently set in the Unity Inspector.
+"""
+
+# ── Endpoints ──
+PROXY_URL = "https://jejunepixels-noexit-proxy.hf.space/chat"
+INFO_EXTRACTOR_URL_0_6B = "https://jejunepixels-qwen3-0-6b-info-extractor-api.hf.space/extract"
+INFO_EXTRACTOR_URL_4B = "https://jejunepixels-qwen3-4B-info-extractor-fastapi.hf.space/extract"
+
+# Which info extractor to use (mirrors useQween0_6 = true in CharacterController)
+USE_QWEN_0_6 = True
+INFO_EXTRACTOR_URL = INFO_EXTRACTOR_URL_0_6B if USE_QWEN_0_6 else INFO_EXTRACTOR_URL_4B
+
+# ── Provider routing (mirrors useHuggingFaceProvider) ──
+PROVIDER = "hf"  # "hf" or "openai"
+
+# ── Model strings (from ModelNamesController) ──
+MODEL_DIALOGUE = "Qwen/Qwen2.5-7B-Instruct"
+MODEL_ADDRESSING = "Qwen/Qwen2.5-7B-Instruct"
+MODEL_GENERATION = "Qwen/Qwen2.5-7B-Instruct"
+# Narrator uses MODEL_DIALOGUE in Unity (see CharacterController.GenerateNarratorDialogue)
+MODEL_NARRATOR = MODEL_DIALOGUE
+
+# ── Temperatures (from Inspector) ──
+TEMP_DIALOGUE = 0.5     # CharacterController.temp
+TEMP_ADDRESSING = 0.5   # CharacterController.temp (same field)
+TEMP_NARRATOR = 0.5     # CharacterController.temp (same field)
+TEMP_GENERATION = 0.95  # CharacterGenerator.temperature
+
+# ── Max tokens (from Inspector / code) ──
+MAX_TOKENS_DIALOGUE = 75
+MAX_TOKENS_ADDRESSING = 10
+MAX_TOKENS_NARRATOR = 0     # unlimited
+MAX_TOKENS_GENERATION = 0   # unlimited
+
+# ── Dialogue history window (matches FormatDialogueForCharacter) ──
+DIALOGUE_HISTORY_WINDOW = 5
+
+# ── Character age range (matches CharacterGenerator.Random.Range(25, 65)) ──
+AGE_RANGE = (25, 65)
+
+# ── Genders for character generation ──
+# In Unity, char 1 is male, char 2 is female (CharacterGenerator line: gender = charNo == 1 ? "male" : "female")
+CHARACTER_GENDERS = {1: "male", 2: "female"}
+
+# ── Request timeout (seconds) ──
+REQUEST_TIMEOUT = 180
+
+# ── Parsing retry config ──
+PARSE_RETRY_ATTEMPTS = 2```
