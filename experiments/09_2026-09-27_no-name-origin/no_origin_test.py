"""Experiment 09 - temp 1.1, no naming tradition given at all.

The matched control is free: experiment 08's temp-1.1 arm is this exact prompt WITH a
naming tradition, on these exact ages and genders. This script generates the without half.

The guard clause about not making the tradition the character's whole identity is removed
along with the input line, since it refers to something that no longer exists.

Scratch only: writes nothing to the project.
"""
import sys, json, time, requests

ROOT = r"D:\Dropbox\__Projects\HuggingFace Projects\NoExit Agents"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from game_state import config, prompts

MODEL = "Qwen/Qwen3-235B-A22B-Instruct-2507"
TEMP = 1.1
SYSTEM = prompts.characterSetupSystemPrompt

SP = (r"C:\Users\Adim\AppData\Local\Temp\claude"
      r"\d--Dropbox---Projects-HuggingFace-Projects-NoExit-Agents"
      r"\2092e3e1-a100-4ff4-91a4-8ca557013bb9\scratchpad")
WITH = sorted([r for r in json.load(open(SP + r"\temp_sweep_result.json", encoding="utf-8"))
               if abs(r["temp"] - 1.1) < 1e-6], key=lambda r: r["i"])
assert len(WITH) == 5

PROMPT = """You have died and gone to hell to be tortured for all eternity, for a deadly sin you
committed.

Write the story of your life, ending with how you died. No longer than 600 words. Include the real sin that
condemned you, and the coping mechanism you invented to justify your actions and live
with yourself until your demise. Who did you love, and who did you hurt?

Stop at the moment of your death. Do not describe arriving anywhere, and do not describe
the room.

Write in the second person \u2014 "you," not "she/he/they." Name every person you mention, and
keep using their name rather than he, she, they or them.

Age: {AGE}
Gender: {GENDER}"""

print("matched control (experiment 08, temp 1.1, tradition given):")
for r in WITH:
    print(f"   pair {r['i']} {r['origin']:18s} {r['age']}/{r['gender']:6s} {r['words']:4d} words")
print()
print("generating the same ages and genders with NO tradition:\n")

out = []
for b in WITH:
    user = PROMPT.replace("{AGE}", str(b["age"])).replace("{GENDER}", b["gender"])
    t0 = time.time()
    try:
        r = requests.post(config.PROXY_URL, timeout=330, json={
            "model": MODEL, "temperature": TEMP, "provider": "hf", "timeout": 300,
            "messages": [{"role": "system", "content": SYSTEM},
                         {"role": "user", "content": user}]})
    except Exception as e:
        print(f"  pair {b['i']}: FAILED {e}")
        continue
    dt = time.time() - t0
    if r.status_code != 200:
        print(f"  pair {b['i']}: HTTP {r.status_code} {r.text[:150]}")
        continue
    d = r.json()
    text = d["choices"][0]["message"]["content"].strip()
    out.append({"arm": "no_origin", "i": b["i"], "temp": TEMP,
                "withheld_origin": b["origin"], "age": b["age"], "gender": b["gender"],
                "seconds": round(dt, 1),
                "tokens": (d.get("usage") or {}).get("total_tokens"),
                "words": len(text.split()), "text": text})
    print(f"  pair {b['i']} ({b['age']}/{b['gender']:6s}) {dt:5.1f}s "
          f"{out[-1]['words']:4d} words   [held-out tradition was {b['origin']}]")

P = SP + r"\no_origin_result.json"
json.dump(out, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n{len(out)} generations -> {P}")
print("tokens spent:", sum(c["tokens"] or 0 for c in out))
if out:
    print(f"mean words: no tradition {sum(c['words'] for c in out)/len(out):.0f} | "
          f"tradition given {sum(r['words'] for r in WITH)/5:.0f}")
