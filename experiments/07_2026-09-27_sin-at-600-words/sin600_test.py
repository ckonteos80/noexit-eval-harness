"""Experiment 07 - at a 600-word budget, does naming the deadly sin change anything?

Only one arm is new. The sin-assigned arm already exists: experiment 06's 600-word
generations used this exact prompt, this exact budget and these exact inputs, so it is a
matched control and costs nothing to reuse. This script generates the no-sin half only.

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

# the matched sin-assigned arm, straight out of experiment 06
E6 = ROOT + r"\experiments\06_2026-09-27_word-budget\results.json"
SIN600 = sorted([r for r in json.load(open(E6, encoding="utf-8")) if r["budget"] == 600],
                key=lambda r: r["i"])
assert len(SIN600) == 5

# identical to experiment 06's prompt except the sin is not named
HEAD = ("You have died and gone to hell to be tortured for all eternity, for a deadly sin you\n"
        "committed.\n\n")

BODY = """Write the story of your life, ending with how you died. No longer than 600 words. Include the real sin that
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

print("matched arm (experiment 06, 600 words, sin named):")
for r in SIN600:
    print(f"   {r['sin']:9s} {r['origin']}/{r['age']}/{r['gender']:6s} {r['words']:4d} words")
print(f"   mean {sum(r['words'] for r in SIN600)/5:.0f} words\n")
print("generating the no-sin half at the same budget:\n")

out = []
for b in SIN600:
    user = (HEAD + BODY).replace("{AGE}", str(b["age"])) \
                        .replace("{GENDER}", b["gender"]) \
                        .replace("{NAME_ORIGIN}", b["origin"])
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
    out.append({"arm": "no_sin_600", "i": b["i"], "sin": None,
                "paired_sin": b["sin"],
                "origin": b["origin"], "age": b["age"], "gender": b["gender"],
                "seconds": round(dt, 1),
                "tokens": (d.get("usage") or {}).get("total_tokens"),
                "words": len(text.split()), "text": text})
    print(f"  pair {b['i']} (paired with {b['sin']:9s}) {dt:5.1f}s "
          f"{out[-1]['words']:4d} words  vs {b['words']} with the sin named")

P = (r"C:\Users\Adim\AppData\Local\Temp\claude"
     r"\d--Dropbox---Projects-HuggingFace-Projects-NoExit-Agents"
     r"\2092e3e1-a100-4ff4-91a4-8ca557013bb9\scratchpad\sin600_result.json")
json.dump(out, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n{len(out)} generations -> {P}")
print("tokens spent:", sum(c["tokens"] or 0 for c in out))
if out:
    print(f"mean words: no sin {sum(c['words'] for c in out)/len(out):.0f} | "
          f"sin named {sum(r['words'] for r in SIN600)/5:.0f}")
