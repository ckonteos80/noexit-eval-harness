"""Experiment 08 - temperature sweep, no sin named, 600-word budget.

Three new arms (0.7, 1.1, 1.4). The 0.95 arm already exists: experiment 07's no-sin
generations used this exact prompt, budget and inputs at 0.95, so it is a matched
fourth point at no cost.

Scratch only: writes nothing to the project.
"""
import sys, json, time, requests

ROOT = r"D:\Dropbox\__Projects\HuggingFace Projects\NoExit Agents"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from game_state import config, prompts

MODEL = "Qwen/Qwen3-235B-A22B-Instruct-2507"
SYSTEM = prompts.characterSetupSystemPrompt
TEMPS = [0.7, 1.1, 1.4]

# matched inputs + the free 0.95 arm, from experiment 07
E7 = ROOT + r"\experiments\07_2026-09-27_sin-at-600-words\results_no_sin.json"
BASE = sorted(json.load(open(E7, encoding="utf-8")), key=lambda r: r["i"])
assert len(BASE) == 5

PROMPT = """You have died and gone to hell to be tortured for all eternity, for a deadly sin you
committed.

Write the story of your life, ending with how you died. No longer than 600 words. Include the real sin that
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

print("free arm (experiment 07, temp 0.95, no sin, 600 words):")
for r in BASE:
    print(f"   pair {r['i']} {r['origin']}/{r['age']}/{r['gender']:6s} {r['words']:4d} words")
print(f"   mean {sum(r['words'] for r in BASE)/5:.0f} words\n")

out = []
for temp in TEMPS:
    print(f"--- temperature {temp} ---")
    for b in BASE:
        user = (PROMPT.replace("{AGE}", str(b["age"]))
                      .replace("{GENDER}", b["gender"])
                      .replace("{NAME_ORIGIN}", b["origin"]))
        t0 = time.time()
        try:
            r = requests.post(config.PROXY_URL, timeout=330, json={
                "model": MODEL, "temperature": temp, "provider": "hf", "timeout": 300,
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": user}]})
        except Exception as e:
            print(f"  temp {temp} pair {b['i']}: FAILED {e}")
            continue
        dt = time.time() - t0
        if r.status_code != 200:
            print(f"  temp {temp} pair {b['i']}: HTTP {r.status_code} {r.text[:130]}")
            continue
        d = r.json()
        text = d["choices"][0]["message"]["content"].strip()
        out.append({"temp": temp, "i": b["i"],
                    "origin": b["origin"], "age": b["age"], "gender": b["gender"],
                    "seconds": round(dt, 1),
                    "tokens": (d.get("usage") or {}).get("total_tokens"),
                    "words": len(text.split()), "text": text})
        print(f"  pair {b['i']} {dt:5.1f}s {out[-1]['words']:4d} words "
              f"(0.95 gave {b['words']})")
    arm = [c for c in out if c["temp"] == temp]
    if arm:
        print(f"  mean {sum(c['words'] for c in arm)/len(arm):.0f} words\n")

P = (r"C:\Users\Adim\AppData\Local\Temp\claude"
     r"\d--Dropbox---Projects-HuggingFace-Projects-NoExit-Agents"
     r"\2092e3e1-a100-4ff4-91a4-8ca557013bb9\scratchpad\temp_sweep_result.json")
json.dump(out, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"{len(out)} generations -> {P}")
print("tokens spent:", sum(c["tokens"] or 0 for c in out))
