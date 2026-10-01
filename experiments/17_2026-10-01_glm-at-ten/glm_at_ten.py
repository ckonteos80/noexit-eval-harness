"""Experiment 17 - GLM-5.3 at ten generations, through the proxy.

Experiment 16 ran five stories on GLM-5.3 and found four things worth checking against a
larger sample. It also could not use the proxy: `reasoning_effort` was dropped by pydantic,
so that run called router.huggingface.co directly with the body the proxy would have sent.

That change is now deployed (openai-proxy f92e941, pushed 2026-10-01), so this run goes
through `config.PROXY_URL` - the path the game actually uses. A real generation at
reasoning_effort="high" returned in 12.8s on 845 completion tokens, against 97s and 6,937 at
max, so the field is being honoured.

Ten generations: experiment 15's five inputs, each run twice. Experiment 15's own two passes
are the matched control - same prompt, same temperature, same inputs, Qwen instead of GLM.

Prediction, recorded before the run. Experiment 16's five-sample figures in brackets:

  1. Cardiovascular deaths [5 of 5]: 6 to 8 of 10. A real prior, but not total - five of
     five on five samples is too clean to survive doubling.
  2. Tuesday as the day of disaster or death [3 of 5]: 4 to 6 of 10. Holds, roughly.
  3. Q4, what kind of person you want people to think you are [4 of 5]: 8 or 9 of 10. The
     miss was noise; Qwen answered it 10 of 10 on the same prompt.
  4. Secret as a findable object [4 of 5]: 7 or 8 of 10. This is the finding the model swap
     rests on, and the one I most expect to shrink.
  5. Named or implied protagonist [3 of 5]: about 5 of 10.
  6. Timing: 13-55s per call, every call under the router's ~120s ceiling, mean near 28s.
     Through the proxy this time, which adds a hop.
  7. Length: mean near 319 words, 0 to 2 of 10 inside the 300-word cap.

Saves after every success - experiment 16 lost a story to an end-of-run save.
No naming tradition (standing instruction). No sin named. Scratch only.
"""
import sys, json, time, requests

ROOT = r"D:\Dropbox\__Projects\HuggingFace Projects\NoExit Agents"
HERE = ROOT + r"\experiments\17_2026-10-01_glm-at-ten"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from game_state import config, prompts

MODEL = "zai-org/GLM-5.3"
TEMP = 1.1
EFFORT = "high"

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

Write the story of your life, ending with how you died. No longer than 300 words.

Who did you love?
How did your sin destroy them?
What lie did you have to tell yourself and others to keep going?
What kind of person do you want people to think you are?
What secret would make everyone see you for what you really are?

Age: {AGE}
Gender: {GENDER}"""

QUESTIONS = ["Who did you love?",
             "How did your sin destroy them?",
             "What lie did you have to tell yourself and others to keep going?",
             "What kind of person do you want people to think you are?",
             "What secret would make everyone see you for what you really are?"]

INPUTS = [(51, "male"), (64, "female"), (45, "female"), (57, "female"), (55, "male")]

out = []


def save():
    json.dump(out, open(HERE + r"\results.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


json.dump(QUESTIONS, open(HERE + r"\questions.json", "w", encoding="utf-8"), indent=1)
print(f"{MODEL} @ {TEMP}, reasoning_effort={EFFORT}, through the proxy")

for rep in range(2):
    print(f"--- pass {rep + 1} of 2 ---")
    for i, (age, gender) in enumerate(INPUTS):
        user = USER.replace("{AGE}", str(age)).replace("{GENDER}", gender)
        for attempt in range(5):
            try:
                t0 = time.time()
                r = requests.post(config.PROXY_URL, timeout=330, json={
                    "model": MODEL, "temperature": TEMP, "provider": "hf",
                    "timeout": 300, "reasoning_effort": EFFORT,
                    "messages": [{"role": "system", "content": SYSTEM},
                                 {"role": "user", "content": user}]})
                if r.status_code == 200:
                    d = r.json()
                    text = d["choices"][0]["message"]["content"].strip()
                    u = d.get("usage") or {}
                    out.append({"rep": rep, "i": i, "age": age, "gender": gender,
                                "model": MODEL, "temp": TEMP, "effort": EFFORT,
                                "seconds": round(time.time() - t0, 1),
                                "tokens": u.get("total_tokens"),
                                "completion_tokens": u.get("completion_tokens"),
                                "words": len(text.split()),
                                "think_in_content": "<think>" in text,
                                "text": text})
                    save()
                    print(f"  pair {i} ({age}/{gender:6s}) {out[-1]['seconds']:5.1f}s "
                          f"{out[-1]['words']:4d}w  {out[-1]['completion_tokens']:5d} ct")
                    break
                print(f"  pair {i} attempt {attempt + 1}: HTTP {r.status_code}")
                time.sleep(5)
            except Exception as e:
                print(f"  pair {i} attempt {attempt + 1}: {type(e).__name__}")
                time.sleep(5)

if out:
    w = [c["words"] for c in out]
    s = [c["seconds"] for c in out]
    ct = [c["completion_tokens"] or 0 for c in out]
    print(f"\n{len(out)}/10 generations")
    print(f"words  mean {sum(w)/len(w):.0f}, range {min(w)}-{max(w)}, "
          f"inside 300: {sum(1 for x in w if x <= 300)}")
    print(f"time   mean {sum(s)/len(s):.1f}s, range {min(s)}-{max(s)}s")
    print(f"completion tokens mean {sum(ct)/len(ct):.0f}, max {max(ct)}")
    print(f"<think> leaked into content: {sum(1 for c in out if c['think_in_content'])}")
    print("tokens spent:", sum(c["tokens"] or 0 for c in out))
