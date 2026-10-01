"""Experiment 19 - the given facts moved to the top of the user prompt.

Experiment 18 supplied a name and the story used it in 5 of 10. The name sat at the bottom,
under the questions, beside Age and Gender - metadata trailing the task.

This moves the three given facts directly under the hell framing, before the instruction and
before the questions, so they arrive as premises rather than as a label:

    You have died and gone to hell ...

    Your name: {NAME}
    Age: {AGE}
    Gender: {GENDER}

    Write the story of your life ...

    (the five questions)

Nothing else changes. Same name call (Qwen3-8B @ 1.2), same model (GLM-5.3 @ 1.1, high),
same five inputs twice, same system prompt and craft rules, same 89 words. Experiment 18's
arm A is the matched control, differing only in where three lines sit.

Prediction, recorded before the run:

  1. The story uses the supplied name in 8 to 10 of 10, against experiment 18's 5. A fact
     stated before the task is a premise; stated after it, it is a footnote.
  2. The cost lands on the opening. Experiment 18 found that stories taking the name open
     "You are <name>" and stories refusing it open on the person the sin destroys. If 1 is
     right, openings on the loved one fall to 0 to 2 of 10, from 5.
  3. Deaths stay cardiovascular, 9 or 10 of 10. Nothing here touches that.
  4. Length unchanged, mean near 300.

If 1 and 2 both hold, the trade is confirmed as mechanical and the choice is the user's:
a named protagonist, or experiment 11's opening. If 1 holds and 2 does not, this is free.

Saves after every success; the name call retries. Scratch only.
"""
import sys, os, json, time, requests

ROOT = r"D:\Dropbox\__Projects\HuggingFace Projects\NoExit Agents"
HERE = ROOT + r"\experiments\19_2026-10-01_facts-first"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from game_state import config, prompts, assembly

MODEL = "zai-org/GLM-5.3"
TEMP = 1.1
EFFORT = "high"
NAME_MODEL = config.MODEL_DIALOGUE
NAME_TEMP = 1.2

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

Your name: {NAME}
Age: {AGE}
Gender: {GENDER}

Write the story of your life, ending with how you died. No longer than 300 words.

Who did you love?
How did your sin destroy them?
What lie did you have to tell yourself and others to keep going?
What kind of person do you want people to think you are?
What secret would make everyone see you for what you really are?"""

NAME_PROMPT = ("Invent one full name — first name and surname — for a person aged {AGE}, "
               "{GENDER}. Any background. Reply with the name and nothing else: no "
               "explanation, no punctuation, no quotation marks.")

INPUTS = [(51, "male"), (64, "female"), (45, "female"), (57, "female"), (55, "male")]

out = []
if os.path.exists(HERE + r"\results.json"):
    out = json.load(open(HERE + r"\results.json", encoding="utf-8"))
    print(f"resuming: {len(out)} already saved")
DONE = {(c["rep"], c["i"]) for c in out}

json.dump(["Who did you love?",
           "How did your sin destroy them?",
           "What lie did you have to tell yourself and others to keep going?",
           "What kind of person do you want people to think you are?",
           "What secret would make everyone see you for what you really are?"],
          open(HERE + r"\questions.json", "w", encoding="utf-8"), indent=1)


def save():
    json.dump(out, open(HERE + r"\results.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


def post(body, timeout=330):
    return requests.post(config.PROXY_URL, timeout=timeout, json=body)


def make_name(age, gender, attempts=4):
    body = {"model": NAME_MODEL, "temperature": NAME_TEMP, "provider": "hf", "timeout": 120,
            "messages": [{"role": "user",
                          "content": NAME_PROMPT.replace("{AGE}", str(age))
                                                .replace("{GENDER}", gender)}]}
    last = "no attempt"
    for _ in range(attempts):
        try:
            r = post(body, timeout=150)
            if r.status_code == 200:
                raw = r.json()["choices"][0]["message"]["content"]
                name = assembly.strip_reasoning(raw).strip().strip('."\u201c\u201d')
                if name:
                    return name, raw[:80]
                last = "empty"
            else:
                last = f"HTTP {r.status_code}"
        except Exception as e:
            last = type(e).__name__
        time.sleep(5)
    return None, last


print(f"facts first: {len(USER.split())} words  ({NAME_MODEL} -> {MODEL})")
for rep in range(2):
    print(f"--- pass {rep + 1} of 2 ---")
    for i, (age, gender) in enumerate(INPUTS):
        if (rep, i) in DONE:
            continue
        name, why = make_name(age, gender)
        if not name:
            print(f"  pair {i}: name call failed ({why})")
            continue
        user = (USER.replace("{NAME}", name).replace("{AGE}", str(age))
                    .replace("{GENDER}", gender))
        for attempt in range(5):
            try:
                t0 = time.time()
                r = post({"model": MODEL, "temperature": TEMP, "provider": "hf",
                          "timeout": 300, "reasoning_effort": EFFORT,
                          "messages": [{"role": "system", "content": SYSTEM},
                                       {"role": "user", "content": user}]})
                if r.status_code == 200:
                    d = r.json()
                    text = d["choices"][0]["message"]["content"].strip()
                    u = d.get("usage") or {}
                    first = name.split()[0]
                    out.append({"rep": rep, "i": i, "age": age, "gender": gender,
                                "supplied_name": name,
                                "uses_full_name": name in text,
                                "uses_first_name": first in text,
                                "opens_with_name": text.lstrip().startswith(
                                    ("You are " + first, "You are " + name)),
                                "seconds": round(time.time() - t0, 1),
                                "tokens": u.get("total_tokens"),
                                "words": len(text.split()), "text": text})
                    save()
                    c = "full" if name in text else ("first" if first in text else "NOT USED")
                    print(f"  pair {i} ({age}/{gender:6s}) {name:22s} "
                          f"{out[-1]['seconds']:5.1f}s {out[-1]['words']:4d}w  {c}")
                    break
                print(f"  pair {i} attempt {attempt + 1}: HTTP {r.status_code}")
                time.sleep(5)
            except Exception as e:
                print(f"  pair {i} attempt {attempt + 1}: {type(e).__name__}")
                time.sleep(5)

if out:
    w = [c["words"] for c in out]
    print(f"\n{len(out)}/10 generations")
    print(f"  used the supplied name : {sum(1 for c in out if c['uses_first_name'])}/{len(out)}"
          f"   (exp 18, name last: 5/10)")
    print(f"  opens 'You are <name>' : {sum(1 for c in out if c['opens_with_name'])}/{len(out)}")
    print(f"  distinct names supplied: {len({c['supplied_name'] for c in out})}/{len(out)}")
    print(f"  words mean {sum(w)/len(w):.0f}, inside 300: {sum(1 for x in w if x <= 300)}")
    print(f"  tokens: {sum(c['tokens'] or 0 for c in out)}")
