"""Experiment 14 - six questions at 200 words, with "what secret" asked outright.

One arm only, 10 generations. Three changes against experiment 13's KIND arm:

  1. word budget 600 -> 200
  2. a new question: "What secret would make everyone see you for what you really are?"
     Experiment 13's tagging found Q5 answered in only 4 of 10 stories; this asks for
     the secret directly rather than asking how it would be seen.
  3. the gaze question keeps the KIND wording and moves to last.

Same five inputs as experiments 12 and 13, each run twice, so those batches are free
matched controls for the same age/gender at 600 words.

No naming tradition (standing instruction, 2026-09-27). No sin named.
Scratch only: writes nothing to game_state.
"""
import sys, json, time, requests

ROOT = r"D:\Dropbox\__Projects\HuggingFace Projects\NoExit Agents"
HERE = ROOT + r"\experiments\14_2026-09-29_the-secret-question-at-200"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from game_state import config, prompts

MODEL = "Qwen/Qwen3-235B-A22B-Instruct-2507"
TEMP = 1.1

CRAFT = """

Write in the second person — "you," not "she/he/they." Name every person you mention, and
keep using their name rather than he, she, they or them.

Stop at the moment of your death. Do not describe arriving anywhere, and do not describe
the room.

End on a fact, not on what it meant. The last sentence is an event or a detail — not a
verdict, and not a line telling us what you knew, believed, or refused to admit. Leave
that for the others in the room to find out."""

SYSTEM = prompts.characterSetupSystemPrompt.rstrip() + CRAFT

USER = """You have died and gone to hell to be tortured for all eternity, for a deadly sin you
committed.

Write the story of your life, ending with how you died. No longer than 200 words.

Who did you love?
How did your sin destroy them?
What lie did you have to tell yourself and others to keep going?
What kind of person do you want people to think you are?
What secret would make everyone see you for what you really are?
What kind of person would they think you are, if they knew your deepest darkest secret?

Age: {AGE}
Gender: {GENDER}"""

INPUTS = [(51, "male"), (64, "female"), (45, "female"), (57, "female"), (55, "male")]

print(f"user prompt: {len(USER.split())} words, {USER.count(chr(10) + 'What') + USER.count(chr(10) + 'Who') + USER.count(chr(10) + 'How')} questions")

out = []
for rep in range(2):
    print(f"--- pass {rep + 1} of 2 ---")
    for i, (age, gender) in enumerate(INPUTS):
        user = USER.replace("{AGE}", str(age)).replace("{GENDER}", gender)
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
                    out.append({"rep": rep, "i": i, "age": age, "gender": gender,
                                "temp": TEMP, "seconds": round(time.time() - t0, 1),
                                "tokens": (d.get("usage") or {}).get("total_tokens"),
                                "words": len(text.split()), "text": text})
                    print(f"  pair {i} ({age}/{gender:6s}) {out[-1]['seconds']:5.1f}s "
                          f"{out[-1]['words']:4d}w")
                    break
                print(f"  pair {i} attempt {attempt + 1}: HTTP {r.status_code}")
                time.sleep(5)
            except Exception as e:
                print(f"  pair {i} attempt {attempt + 1}: {type(e).__name__}")
                time.sleep(5)

if out:
    w = [c["words"] for c in out]
    print(f"\nmean {sum(w) / len(w):.0f} words, range {min(w)}-{max(w)}, "
          f"inside 200: {sum(1 for x in w if x <= 200)}/{len(w)}")

json.dump(out, open(HERE + r"\results.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print(f"{len(out)} generations -> results.json")
print("tokens spent:", sum(c["tokens"] or 0 for c in out))
