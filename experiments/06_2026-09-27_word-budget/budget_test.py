"""Experiment 06 - does a word budget shorten the story prompt?

Arms: 600 words, 400 words. The no-budget control is experiment 05's with_sin arm,
which used these exact inputs and these exact sins, so it is a matched baseline and
costs nothing to reuse.
Scratch only: writes nothing to the project.
"""
import sys, json, time, requests

ROOT = r"D:\Dropbox\__Projects\HuggingFace Projects\NoExit Agents"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from game_state import config, prompts

MODEL = "Qwen/Qwen3-235B-A22B-Instruct-2507"
TEMP = 0.95
SYSTEM = prompts.characterSetupSystemPrompt

# exact inputs + sins from experiment 05, read from its results so the match is guaranteed
EXP05 = (ROOT + r"\experiments\05_2026-09-27_deadly-sin\results.json")
prev = json.load(open(EXP05, encoding="utf-8"))
BASE = [r for r in prev if r["arm"] == "with_sin"]
BASE.sort(key=lambda r: r["i"])
assert len(BASE) == 5

HEAD = ("You have died and gone to hell to be tortured for all eternity, for a deadly sin you\n"
        "committed: {DEADLY_SIN}.\n\n")

BODY = """Write the story of your life, ending with how you died.{BUDGET} Include the real sin that
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

ARMS = {"600": " No longer than 600 words.", "400": " No longer than 400 words."}

print("matched baseline (experiment 05, no budget):")
for r in BASE:
    print(f"   {r['sin']:9s} {r['origin']}/{r['age']}/{r['gender']:6s} {r['words']:5d} words")
print(f"   mean {sum(r['words'] for r in BASE)/5:.0f} words\n")

out = []
for arm, clause in ARMS.items():
    for b in BASE:
        user = (HEAD + BODY).replace("{DEADLY_SIN}", b["sin"]) \
                            .replace("{BUDGET}", clause) \
                            .replace("{AGE}", str(b["age"])) \
                            .replace("{GENDER}", b["gender"]) \
                            .replace("{NAME_ORIGIN}", b["origin"])
        t0 = time.time()
        try:
            r = requests.post(config.PROXY_URL, timeout=330, json={
                "model": MODEL, "temperature": TEMP, "provider": "hf", "timeout": 300,
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": user}]})
        except Exception as e:
            print(f"budget={arm} {b['sin']}: FAILED {e}")
            continue
        dt = time.time() - t0
        if r.status_code != 200:
            print(f"budget={arm} {b['sin']}: HTTP {r.status_code} {r.text[:150]}")
            continue
        d = r.json()
        text = d["choices"][0]["message"]["content"].strip()
        w = len(text.split())
        target = int(arm)
        out.append({"budget": target, "sin": b["sin"], "i": b["i"],
                    "origin": b["origin"], "age": b["age"], "gender": b["gender"],
                    "seconds": round(dt, 1),
                    "tokens": (d.get("usage") or {}).get("total_tokens"),
                    "words": w, "over_by": w - target,
                    "baseline_words": b["words"], "text": text})
        flag = "OVER" if w > target else "ok"
        print(f"budget={arm} {b['sin']:9s} {dt:5.1f}s {w:5d} words  ({flag}, "
              f"baseline was {b['words']})")

P = (r"C:\Users\Adim\AppData\Local\Temp\claude"
     r"\d--Dropbox---Projects-HuggingFace-Projects-NoExit-Agents"
     r"\2092e3e1-a100-4ff4-91a4-8ca557013bb9\scratchpad\budget_result.json")
json.dump(out, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n{len(out)} generations -> {P}")
print("tokens spent:", sum(c["tokens"] or 0 for c in out))
for t in (600, 400):
    arm = [c for c in out if c["budget"] == t]
    if arm:
        print(f"  budget {t}: mean {sum(c['words'] for c in arm)/len(arm):.0f} words, "
              f"{sum(1 for c in arm if c['words'] <= t)}/{len(arm)} inside")
