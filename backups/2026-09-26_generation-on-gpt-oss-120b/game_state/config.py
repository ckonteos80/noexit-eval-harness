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
# Generation runs once per session, so quality matters more here than cost or
# latency -- it gets a reasoning model. The reasoning itself is returned by the
# provider in a separate field and deliberately ignored: providers.py reads only
# choices[0].message.content, and assembly.strip_reasoning covers the providers
# that inline it as <think> instead.
# Chosen over Qwen/Qwen3-235B-A22B-Thinking-2507, which is the stronger model but
# unreachable through this path: the HF router returns 504 at roughly 120s and
# that prompt needs longer. gpt-oss-120b answered the same prompt in 2.7s.
# reasoning_effort stays at the provider default -- the proxy cannot forward it.
# TEMP_GENERATION deliberately stays at 0.95 so the model is the only variable
# that moved in this version.
MODEL_GENERATION = "openai/gpt-oss-120b"
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

# ── Proxy-side read timeout (seconds) ──
# The proxy Space decides how long it waits on the upstream provider. It uses 60s
# when we send nothing, which is fine for dialogue but too short for generation
# once a slower or reasoning-capable model is in play. Sent per request as
# "timeout"; the proxy clamps it to [1, 600]. Every other call type omits the
# field entirely and keeps the proxy's own default.
PROXY_TIMEOUT_GENERATION = 300

# The harness must outlast the proxy so the proxy's timeout fires first and we get
# a real error back, rather than the client giving up on a call that is still running.
PROXY_TIMEOUT_MARGIN = 30

# ── Parsing retry config ──
PARSE_RETRY_ATTEMPTS = 2
