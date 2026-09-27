"""Minimal story prompt, one call per character, no extractor, no anti-duplication.
Two arms: with the current system prompt, and with none.
Scratch only -- writes nothing to the project."""
import sys, json, time, random, requests

ROOT = r"D:\Dropbox\__Projects\HuggingFace Projects\NoExit Agents"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from game_state import config, prompts

MODEL = "Qwen/Qwen3-235B-A22B-Instruct-2507"
TEMP = 0.95

USER = """You have died and gone to hell for a sin you committed.

Write the story of your life, ending with how you died. Include what you actually did that
condemned you \u2014 and tell the whole thing the way you tell it to yourself.

Write in the second person \u2014 "you," not "she/he/they." Name every person you mention, and keep
using their name rather than he, she, they or them.

Age: {AGE}
Gender: {GENDER}
Naming tradition: {NAME_ORIGIN}"""

ARMS = {
    "with_system": prompts.characterSetupSystemPrompt,
    "no_system": None,
}

# identical inputs across arms so origin/age/gender are not a confound
random.seed(20260927)
INPUTS = [(random.choice(config.NAME_ORIGINS), random.randint(*config.AGE_RANGE), "male"),
          (random.choice(config.NAME_ORIGINS), random.randint(*config.AGE_RANGE), "female")]
print("shared inputs:", INPUTS, "\n")

out = {}
for arm, system in ARMS.items():
    out[arm] = []
    for i, (origin, age, gender) in enumerate(INPUTS, start=1):
        user = (USER.replace("{AGE}", str(age))
                    .replace("{GENDER}", gender)
                    .replace("{NAME_ORIGIN}", origin))
        msgs = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": user}]
        t0 = time.time()
        r = requests.post(config.PROXY_URL, timeout=330, json={
            "model": MODEL, "temperature": TEMP, "provider": "hf",
            "timeout": 300, "messages": msgs})
        dt = time.time() - t0
        if r.status_code != 200:
            print(f"{arm} char{i}: HTTP {r.status_code} {r.text[:200]}")
            continue
        d = r.json()
        text = d["choices"][0]["message"]["content"].strip()
        out[arm].append({"char": i, "origin": origin, "age": age, "gender": gender,
                         "seconds": round(dt, 1),
                         "tokens": (d.get("usage") or {}).get("total_tokens"),
                         "text": text})
        print(f"{arm:12s} char{i}: {dt:5.1f}s  {(d.get('usage') or {}).get('total_tokens'):5d} tok  "
              f"{len(text.split()):4d} words  origin={origin} age={age}")

P = (r"C:\Users\Adim\AppData\Local\Temp\claude"
     r"\d--Dropbox---Projects-HuggingFace-Projects-NoExit-Agents"
     r"\2092e3e1-a100-4ff4-91a4-8ca557013bb9\scratchpad\story_result.json")
json.dump(out, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\nsaved ->", P)
print("total tokens:", sum(c["tokens"] or 0 for arm in out.values() for c in arm))
