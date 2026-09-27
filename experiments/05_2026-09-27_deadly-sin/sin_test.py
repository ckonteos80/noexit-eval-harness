"""10 scratch generations: 5 with a named deadly sin, 5 without.
Same story prompt, same system prompt, same inputs paired across arms.
Writes nothing to the project."""
import sys, json, time, random, requests

ROOT = r"D:\Dropbox\__Projects\HuggingFace Projects\NoExit Agents"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from game_state import config, prompts

MODEL = "Qwen/Qwen3-235B-A22B-Instruct-2507"
TEMP = 0.95
SYSTEM = prompts.characterSetupSystemPrompt

BODY = """Write the story of your life, ending with how you died. Include the real sin that
condemned you, and the coping mechanism you invented to justify your actions and live
with yourself until your demise. Who did you love, and who did you hurt?

Stop at the moment of your death. Do not describe arriving anywhere, and do not describe
the room.

Write in the second person \u2014 "you," not "she/he/they." Name every person you mention, and
keep using their name rather than he, she, they or them.

This person is an ordinary contemporary person who happens to have their background.
Do not make the naming tradition into the character's whole identity.

Age: {AGE}
Gender: {GENDER}
Naming tradition: {NAME_ORIGIN}"""

WITH = ("You have died and gone to hell to be tortured for all eternity, for a deadly sin you\n"
        "committed: {DEADLY_SIN}.\n\n") + BODY
WITHOUT = ("You have died and gone to hell to be tortured for all eternity, for a deadly sin you\n"
           "committed.\n\n") + BODY

# three expected to carry, two predicted to struggle
SINS = ["pride", "envy", "wrath", "sloth", "gluttony"]

random.seed(4242)
INPUTS = [(random.choice(config.NAME_ORIGINS), random.randint(*config.AGE_RANGE),
           random.choice(["male", "female"])) for _ in range(5)]
print("paired inputs:")
for i, t in enumerate(INPUTS):
    print(f"   {i}: {t}  sin={SINS[i]}")
print()

out = []
for arm in ("with_sin", "no_sin"):
    for i, (origin, age, gender) in enumerate(INPUTS):
        tmpl = WITH if arm == "with_sin" else WITHOUT
        user = (tmpl.replace("{AGE}", str(age))
                    .replace("{GENDER}", gender)
                    .replace("{NAME_ORIGIN}", origin)
                    .replace("{DEADLY_SIN}", SINS[i]))
        t0 = time.time()
        try:
            r = requests.post(config.PROXY_URL, timeout=330, json={
                "model": MODEL, "temperature": TEMP, "provider": "hf", "timeout": 300,
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": user}]})
        except Exception as e:
            print(f"{arm} {i}: FAILED {e}")
            continue
        dt = time.time() - t0
        if r.status_code != 200:
            print(f"{arm} {i}: HTTP {r.status_code} {r.text[:150]}")
            continue
        d = r.json()
        text = d["choices"][0]["message"]["content"].strip()
        out.append({"arm": arm, "i": i, "sin": SINS[i] if arm == "with_sin" else None,
                    "origin": origin, "age": age, "gender": gender,
                    "seconds": round(dt, 1),
                    "tokens": (d.get("usage") or {}).get("total_tokens"),
                    "words": len(text.split()), "text": text})
        print(f"{arm:9s} {i} sin={str(SINS[i] if arm=='with_sin' else '-'):9s} "
              f"{dt:5.1f}s {out[-1]['tokens']:5d} tok {out[-1]['words']:4d} words "
              f"{origin}/{age}/{gender}")

P = (r"C:\Users\Adim\AppData\Local\Temp\claude"
     r"\d--Dropbox---Projects-HuggingFace-Projects-NoExit-Agents"
     r"\2092e3e1-a100-4ff4-91a4-8ca557013bb9\scratchpad\sin_result.json")
json.dump(out, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n{len(out)} generations saved -> {P}")
print("total tokens:", sum(c["tokens"] or 0 for c in out))
