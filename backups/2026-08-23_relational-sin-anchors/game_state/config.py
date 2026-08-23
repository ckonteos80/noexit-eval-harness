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
MODEL_GENERATION = "Qwen/Qwen3-8B"
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

# ── Genders for character generation ──
# In Unity, char 1 is male, char 2 is female (CharacterGenerator line: gender = charNo == 1 ? "male" : "female")
CHARACTER_GENDERS = {1: "male", 2: "female"}

# ── Request timeout (seconds) ──
REQUEST_TIMEOUT = 180

# ── Parsing retry config ──
PARSE_RETRY_ATTEMPTS = 2