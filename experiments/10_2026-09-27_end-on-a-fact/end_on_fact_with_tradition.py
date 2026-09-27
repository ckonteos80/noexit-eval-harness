"""Experiment 10 - "end on a fact, not on what it meant".

Every story so far closes by delivering its own verdict: "you still believed it",
"But you knew that was the lie you always told", "You were wrong". The
tradition-given arm at 1.1 does it 5 times out of 5. For this play that is backwards --
the drama is two strangers prising the truth out, and a backstory that has already
passed judgment leaves the room nothing to find.

One rule added. Everything else identical to experiment 08's 1.1 arm, which is
therefore a free matched control.

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

CTRL = sorted([r for r in json.load(open(
    ROOT + r"\experiments\08_2026-09-27_temperature-sweep\results.json", encoding="utf-8"))
    if abs(r["temp"] - 1.1) < 1e-6], key=lambda r: r["i"])
assert len(CTRL) == 5

# the only change: the two sentences after "do not describe the room"
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

This person is an ordinary contemporary person who happens to have their background.
Do not make the naming tradition into the character's whole identity.

Age: {AGE}
Gender: {GENDER}
Naming tradition: {NAME_ORIGIN}"""

print("control (experiment 08, temp 1.1, tradition given, no rule) \u2014 how each one ends:")
for r in CTRL:
    parts = [s.strip() for s in r["text"].replace("\n", " ").split(".") if s.strip()]
    print(f"   pair {r['i']} {r['origin']:18s} ...{parts[-1][:72]}")
print()

out = []
for b in CTRL:
    user = (PROMPT.replace("{AGE}", str(b["age"]))
                  .replace("{GENDER}", b["gender"])
                  .replace("{NAME_ORIGIN}", b["origin"]))
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
                parts = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
                out.append({"arm": "end_on_fact", "i": b["i"], "temp": TEMP,
                            "origin": b["origin"], "age": b["age"], "gender": b["gender"],
                            "seconds": round(time.time() - t0, 1),
                            "tokens": (d.get("usage") or {}).get("total_tokens"),
                            "words": len(text.split()), "text": text})
                print(f"  pair {b['i']} {out[-1]['seconds']:5.1f}s {out[-1]['words']:4d}w")
                print(f"     ends: ...{parts[-1][:88]}")
                break
            print(f"  pair {b['i']} attempt {attempt+1}: HTTP {r.status_code}")
        except Exception as e:
            print(f"  pair {b['i']} attempt {attempt+1}: {type(e).__name__}")
            time.sleep(4)

P = (r"C:\Users\Adim\AppData\Local\Temp\claude"
     r"\d--Dropbox---Projects-HuggingFace-Projects-NoExit-Agents"
     r"\2092e3e1-a100-4ff4-91a4-8ca557013bb9\scratchpad\end_on_fact_result.json")
json.dump(out, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n{len(out)} generations -> {P}")
print("tokens spent:", sum(c["tokens"] or 0 for c in out))
if out:
    print(f"mean words: with rule {sum(c['words'] for c in out)/len(out):.0f} | "
          f"control {sum(r['words'] for r in CTRL)/5:.0f}")
