"""Experiment 11 - restructured prompt: craft rules moved to system, user reduced to
four questions.

OLD arm = the experiment 10 no-tradition prompt (craft rules in the user prompt, and the
          "include the real sin... and the coping mechanism" instruction).
NEW arm = the same craft rules moved into the system prompt, and the user prompt replaced
          by four questions. The instruction to state the sin and the coping mechanism is
          gone; "What lie did you have to tell yourself" asks for the same material as
          something the character does rather than something the story declares.
          A fourth question is new: what would make the lie fall apart.

Both arms run fresh, same five inputs, so nothing is carried across sessions.
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
BASE_SYSTEM = prompts.characterSetupSystemPrompt.rstrip()

CRAFT = """

Write in the second person \u2014 "you," not "she/he/they." Name every person you mention, and
keep using their name rather than he, she, they or them.

Stop at the moment of your death. Do not describe arriving anywhere, and do not describe
the room.

End on a fact, not on what it meant. The last sentence is an event or a detail \u2014 not a
verdict, and not a line telling us what you knew, believed, or refused to admit. Leave
that for the others in the room to find out."""

OLD_USER = """You have died and gone to hell to be tortured for all eternity, for a deadly sin you
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

NEW_USER = """You have died and gone to hell to be tortured for all eternity, for a deadly sin you
committed.

Write the story of your life, ending with how you died. No longer than 600 words.

Who did you love?
How did your sin destroy them?
What lie did you have to tell yourself and others to keep going?
And what would it take for your lie to fall apart?

Age: {AGE}
Gender: {GENDER}"""

ARMS = {
    "old": (BASE_SYSTEM, OLD_USER),
    "new": (BASE_SYSTEM + CRAFT, NEW_USER),
}
INPUTS = [(51, "male"), (64, "female"), (45, "female"), (57, "female"), (55, "male")]

print(f"old: system {len(BASE_SYSTEM.split()):3d}w  user {len(OLD_USER.split()):3d}w")
print(f"new: system {len((BASE_SYSTEM+CRAFT).split()):3d}w  user {len(NEW_USER.split()):3d}w\n")

out = []
for arm, (system, tmpl) in ARMS.items():
    print(f"--- {arm} ---")
    for i, (age, gender) in enumerate(INPUTS):
        user = tmpl.replace("{AGE}", str(age)).replace("{GENDER}", gender)
        for attempt in range(3):
            try:
                t0 = time.time()
                r = requests.post(config.PROXY_URL, timeout=330, json={
                    "model": MODEL, "temperature": TEMP, "provider": "hf", "timeout": 300,
                    "messages": [{"role": "system", "content": system},
                                 {"role": "user", "content": user}]})
                if r.status_code == 200:
                    d = r.json()
                    text = d["choices"][0]["message"]["content"].strip()
                    paras = [p.strip() for p in text.split("\n") if p.strip()]
                    out.append({"arm": arm, "i": i, "age": age, "gender": gender, "temp": TEMP,
                                "seconds": round(time.time() - t0, 1),
                                "tokens": (d.get("usage") or {}).get("total_tokens"),
                                "words": len(text.split()), "text": text})
                    print(f"  pair {i} ({age}/{gender:6s}) {out[-1]['seconds']:5.1f}s "
                          f"{out[-1]['words']:4d}w")
                    print(f"     ends: {paras[-1][:92]}")
                    break
                print(f"  pair {i} attempt {attempt+1}: HTTP {r.status_code}")
            except Exception as e:
                print(f"  pair {i} attempt {attempt+1}: {type(e).__name__}")
                time.sleep(4)
    arm_rows = [c for c in out if c["arm"] == arm]
    if arm_rows:
        print(f"  mean {sum(c['words'] for c in arm_rows)/len(arm_rows):.0f} words\n")

P = (r"C:\Users\Adim\AppData\Local\Temp\claude"
     r"\d--Dropbox---Projects-HuggingFace-Projects-NoExit-Agents"
     r"\2092e3e1-a100-4ff4-91a4-8ca557013bb9\scratchpad\restructure_result.json")
json.dump(out, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"{len(out)} generations -> {P}")
print("tokens spent:", sum(c["tokens"] or 0 for c in out))
