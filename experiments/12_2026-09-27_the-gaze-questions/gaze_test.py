"""Experiment 12 - the gaze questions.

FOUR = experiment 11's winning prompt.
FIVE = question four ("what would it take for your lie to fall apart") replaced by two
       questions about how the character is seen:
           How do you want people to see you?
           How would people see you if they knew your deepest, darkest secret?

Both arms run fresh in one batch, same five inputs. Experiment 11's new arm gives a
third sample of FOUR for free.

No naming tradition (standing instruction, 2026-09-27).
Scratch only: writes nothing to the project.
"""
import sys, json, time, requests

ROOT = r"D:\Dropbox\__Projects\HuggingFace Projects\NoExit Agents"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from game_state import config, prompts

MODEL = "Qwen/Qwen3-235B-A22B-Instruct-2507"
TEMP = 1.1

CRAFT = """

Write in the second person \u2014 "you," not "she/he/they." Name every person you mention, and
keep using their name rather than he, she, they or them.

Stop at the moment of your death. Do not describe arriving anywhere, and do not describe
the room.

End on a fact, not on what it meant. The last sentence is an event or a detail \u2014 not a
verdict, and not a line telling us what you knew, believed, or refused to admit. Leave
that for the others in the room to find out."""

SYSTEM = prompts.characterSetupSystemPrompt.rstrip() + CRAFT

HEAD = """You have died and gone to hell to be tortured for all eternity, for a deadly sin you
committed.

Write the story of your life, ending with how you died. No longer than 600 words.

"""
TAIL = """

Age: {AGE}
Gender: {GENDER}"""

FOUR = HEAD + """Who did you love?
How did your sin destroy them?
What lie did you have to tell yourself and others to keep going?
And what would it take for your lie to fall apart?""" + TAIL

FIVE = HEAD + """Who did you love?
How did your sin destroy them?
What lie did you have to tell yourself and others to keep going?
How do you want people to see you?
How would people see you if they knew your deepest, darkest secret?""" + TAIL

ARMS = {"four": FOUR, "five": FIVE}
INPUTS = [(51, "male"), (64, "female"), (45, "female"), (57, "female"), (55, "male")]

for k, v in ARMS.items():
    print(f"{k}: user prompt {len(v.split())} words")
print()

out = []
for arm, tmpl in ARMS.items():
    print(f"--- {arm} ---")
    for i, (age, gender) in enumerate(INPUTS):
        user = tmpl.replace("{AGE}", str(age)).replace("{GENDER}", gender)
        for attempt in range(5):
            try:
                t0 = time.time()
                r = requests.post(config.PROXY_URL, timeout=330, json={
                    "model": MODEL, "temperature": TEMP, "provider": "hf", "timeout": 300,
                    "messages": [{"role": "system", "content": SYSTEM},
                                 {"role": "user", "content": user}]})
                if r.status_code == 200:
                    d = r.json()
                    text = d["choices"][0]["message"]["content"].strip()
                    ps = [p.strip() for p in text.split("\n") if p.strip()]
                    out.append({"arm": arm, "i": i, "age": age, "gender": gender, "temp": TEMP,
                                "seconds": round(time.time() - t0, 1),
                                "tokens": (d.get("usage") or {}).get("total_tokens"),
                                "words": len(text.split()), "text": text})
                    print(f"  pair {i} ({age}/{gender:6s}) {out[-1]['seconds']:5.1f}s "
                          f"{out[-1]['words']:4d}w")
                    print(f"     opens: {' '.join(text.split()[:14])}")
                    print(f"     ends : {ps[-1][:82]}")
                    break
                print(f"  pair {i} attempt {attempt+1}: HTTP {r.status_code}")
                time.sleep(5)
            except Exception as e:
                print(f"  pair {i} attempt {attempt+1}: {type(e).__name__}")
                time.sleep(5)
    rows = [c for c in out if c["arm"] == arm]
    if rows:
        print(f"  mean {sum(c['words'] for c in rows)/len(rows):.0f} words\n")

P = (r"C:\Users\Adim\AppData\Local\Temp\claude"
     r"\d--Dropbox---Projects-HuggingFace-Projects-NoExit-Agents"
     r"\2092e3e1-a100-4ff4-91a4-8ca557013bb9\scratchpad\gaze_result.json")
json.dump(out, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"{len(out)} generations -> {P}")
print("tokens spent:", sum(c["tokens"] or 0 for c in out))

