"""Experiment 10 - "end on a fact, not on what it meant", with NO naming tradition.

Standing instruction from 2026-09-27: no naming tradition is supplied.

The matched control is free: experiment 09's no-tradition arm is this exact prompt,
same inputs, same temperature, same budget, with no sin and no ending rule. So the only
difference here is the three sentences about how to end.

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

CTRL = sorted(json.load(open(
    ROOT + r"\experiments\09_2026-09-27_no-name-origin\results_no_origin.json",
    encoding="utf-8")), key=lambda r: r["i"])
assert len(CTRL) == 5

# no {NAME_ORIGIN} line, and no guard clause that refers to it.
# the only addition against experiment 09 is the "end on a fact" paragraph.
PROMPT = """You have died and gone to hell to be tortured for all eternity, for a deadly sin you
committed.

Write the story of your life, ending with how you died. No longer than 600 words. Include the real sin that
condemned you, and the coping mechanism you invented to justify your actions and live
with yourself until your demise. Who did you love, and who did you hurt?

Stop at the moment of your death. Do not describe arriving anywhere, and do not describe
the room.

End on a fact, not on what it meant. The last sentence is an event or a detail \u2014 not a
verdict, and not a line telling us what you knew, believed, or refused to admit. Leave
that for the others in the room to find out.

Write in the second person \u2014 "you," not "she/he/they." Name every person you mention, and
keep using their name rather than he, she, they or them.

Age: {AGE}
Gender: {GENDER}"""

print("control (experiment 09, no tradition, no ending rule) \u2014 how each one ends:")
for r in CTRL:
    parts = [s.strip() for s in r["text"].replace("\n", " ").split(".") if s.strip()]
    print(f"   pair {r['i']} ({r['age']}/{r['gender']:6s}) ...{parts[-1][:70]}")
print()

out = []
for b in CTRL:
    user = PROMPT.replace("{AGE}", str(b["age"])).replace("{GENDER}", b["gender"])
    for attempt in range(3):
        try:
            t0 = time.time()
            r = requests.post(config.PROXY_URL, timeout=330, json={
                "model": MODEL, "temperature": TEMP, "provider": "hf", "timeout": 300,
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": user}]})
            if r.status_code == 200:
                d = r.json()
                text = d["choices"][0]["message"]["content"].strip()
                paras = [p.strip() for p in text.split("\n") if p.strip()]
                out.append({"arm": "end_on_fact_no_tradition", "i": b["i"], "temp": TEMP,
                            "age": b["age"], "gender": b["gender"],
                            "seconds": round(time.time() - t0, 1),
                            "tokens": (d.get("usage") or {}).get("total_tokens"),
                            "words": len(text.split()), "text": text})
                print(f"  pair {b['i']} ({b['age']}/{b['gender']:6s}) {out[-1]['seconds']:5.1f}s "
                      f"{out[-1]['words']:4d}w")
                print(f"     ends: {paras[-1][:100]}")
                break
            print(f"  pair {b['i']} attempt {attempt+1}: HTTP {r.status_code}")
        except Exception as e:
            print(f"  pair {b['i']} attempt {attempt+1}: {type(e).__name__}")
            time.sleep(4)

P = (r"C:\Users\Adim\AppData\Local\Temp\claude"
     r"\d--Dropbox---Projects-HuggingFace-Projects-NoExit-Agents"
     r"\2092e3e1-a100-4ff4-91a4-8ca557013bb9\scratchpad\end_on_fact_notrad_result.json")
json.dump(out, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n{len(out)} generations -> {P}")
print("tokens spent:", sum(c["tokens"] or 0 for c in out))
if out:
    print(f"mean words: with rule {sum(c['words'] for c in out)/len(out):.0f} | "
          f"control {sum(r['words'] for r in CTRL)/5:.0f}")
