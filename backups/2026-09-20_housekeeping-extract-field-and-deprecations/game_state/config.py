"""
Configuration for the noexit harness.
Mirrors the values currently set in the Unity Inspector.
"""

# ── Endpoints ──
PROXY_URL = "https://jejunepixels-noexit-proxy.hf.space/chat"
INFO_EXTRACTOR_URL_0_6B = "https://jejunepixels-qwen3-0-6b-info-extractor-api.hf.space/extract"
INFO_EXTRACTOR_URL_4B = "https://jejunepixels-qwen3-4B-info-extractor-fastapi.hf.space/extract"

# Which info extractor to use (mirrors useQween0_6 = true in CharacterController)
USE_QWEN_0_6 = True
INFO_EXTRACTOR_URL = INFO_EXTRACTOR_URL_0_6B if USE_QWEN_0_6 else INFO_EXTRACTOR_URL_4B

# ── Provider routing (mirrors useHuggingFaceProvider) ──
PROVIDER = "hf"  # "hf" or "openai"

# ── Model strings (from ModelNamesController) ──
# Swapped from Qwen2.5-7B-Instruct 2026-08-23: its only working provider (Together AI)
# stopped serving it. Qwen3-8B is ungated with 2 live providers (nscale, featherless-ai).
MODEL_DIALOGUE = "Qwen/Qwen3-8B"
MODEL_ADDRESSING = "Qwen/Qwen3-8B"
# Generation runs once per session (cost/latency don't matter as much here), so it
# gets Qwen's flagship instead -- same family/license as the models above, chosen
# to address vague/disconnected character-gen content flagged in human eval.
MODEL_GENERATION = "Qwen/Qwen3-235B-A22B-Instruct-2507"
# Narrator uses MODEL_DIALOGUE in Unity (see CharacterController.GenerateNarratorDialogue)
MODEL_NARRATOR = MODEL_DIALOGUE

# ── Temperatures (from Inspector) ──
TEMP_DIALOGUE = 0.5     # CharacterController.temp
TEMP_ADDRESSING = 0.5   # CharacterController.temp (same field)
TEMP_NARRATOR = 0.5     # CharacterController.temp (same field)
TEMP_GENERATION = 0.95  # CharacterGenerator.temperature

# ── Max tokens (from Inspector / code) ──
MAX_TOKENS_DIALOGUE = 75
MAX_TOKENS_ADDRESSING = 10
MAX_TOKENS_NARRATOR = 0     # unlimited
MAX_TOKENS_GENERATION = 0   # unlimited

# ── Dialogue history window (matches FormatDialogueForCharacter) ──
DIALOGUE_HISTORY_WINDOW = 5

# ── Character age range (matches CharacterGenerator.Random.Range(25, 65)) ──
AGE_RANGE = (25, 65)

# ── Name origins for character generation ──
# One is drawn at random per character and interpolated into the generation prompt.
# Randomising the *input* is the fix for cross-run name repetition: asking the model
# for variety failed for three versions running (Daniel Reeves was character 1 in
# three consecutive runs, with supporting names Mark and Poole also recurring).
# Same pattern as AGE_RANGE above, and portable to Unity's Random.Range usage.
NAME_ORIGINS = [
    "British", "Irish", "African-American", "Mexican", "Puerto Rican",
    "Italian-American", "Polish", "Greek", "Nigerian", "Ghanaian",
    "Indian", "Pakistani", "Filipino", "Vietnamese", "Korean",
    "Chinese-American", "Japanese-American", "Lebanese", "Iranian", "Turkish",
    "Brazilian", "Colombian", "Russian", "Ukrainian", "German",
    "Dutch", "Swedish", "Portuguese", "French-Canadian", "Scottish",
]

# ── Genders for character generation ──
# In Unity, char 1 is male, char 2 is female (CharacterGenerator line: gender = charNo == 1 ? "male" : "female")
CHARACTER_GENDERS = {1: "male", 2: "female"}

# ── Request timeout (seconds) ──
REQUEST_TIMEOUT = 180

# ── Parsing retry config ──
PARSE_RETRY_ATTEMPTS = 2
