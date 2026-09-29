"""Experiment 16 - experiment 15's prompt on zai-org/GLM-5.3 instead of Qwen3-235B.

GLM-5.3 is #6 on EQ-Bench Creative Writing v3 with the lowest slop score of any open
model there (8.4; the Qwen3-235B family sits around 29). It is a thinking model, and
the proxy cannot forward reasoning_effort, so it runs at its default (max).

Everything else identical to experiment 15: same system prompt + craft rules, same user
prompt, same temperature (1.1), same five inputs. One pass only - five generations.
Experiment 15's first pass (rep 0) is the matched control.

Recorded prediction, before the run:
  - every call succeeds, but slowly: 30-90s each against Qwen's ~5s, most of it thinking;
    at least one risk of the ~120s router gateway timeout seen in experiment 01
  - reasoning arrives in a separate field; no <think> in content
  - length control looser than Qwen's 4% over - mean about 330 words
  - death ending in 5 of 5; the secret still lands as a findable object
  - fewer stock phrases: no "It was the last lie you ever told"-style closing formula

RUN 1 (above) at max effort: pair 0 took 97s and 6,937 completion tokens, pair 1 hit the
router's 504 at 120.7s, the script stopped. See NOTES.md.

RUN 2: reasoning_effort="high", GLM-5.3's middle level (low / high / max). The proxy drops
the field and its fix could not be deployed (the local HF token is read-only), so this run
calls the HF router DIRECTLY with the local token - the exact body the updated proxy would
forward. The proxy is a pass-through, so the output is comparable with experiment 15's.

Prediction for run 2: 40-80s per call, all five under the 120s gateway; roughly half the
thinking of max (~3,500 completion tokens); the story itself unchanged in length.

No naming tradition (standing instruction, 2026-09-27). No sin named.
Scratch only: writes nothing to game_state.
"""
import sys, json, time, requests
from huggingface_hub import get_token

ROOT = r"D:\Dropbox\__Projects\HuggingFace Projects\NoExit Agents"
HERE = ROOT + r"\experiments\16_2026-09-29_glm-5-3"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from game_state import config, prompts

MODEL = "zai-org/GLM-5.3"
TEMP = 1.1
EFFORT = "high"
ROUTER = "https://router.huggingface.co/v1/chat/completions"

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

INPUTS = [(51, "male"), (64, "female"), (45, "female"), (57, "female"), (55, "male")]

out = []
for i, (age, gender) in enumerate(INPUTS):
    user = USER.replace("{AGE}", str(age)).replace("{GENDER}", gender)
    for attempt in range(5):
        try:
            t0 = time.time()
            r = requests.post(ROUTER, timeout=330,
                              headers={"Authorization": f"Bearer {get_token()}"}, json={
                "model": MODEL, "temperature": TEMP, "reasoning_effort": EFFORT,
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": user}]})
            secs = round(time.time() - t0, 1)
            if r.status_code == 200:
                d = r.json()
                msg = d["choices"][0]["message"]
                text = (msg.get("content") or "").strip()
                reasoning = msg.get("reasoning_content") or msg.get("reasoning") or ""
                usage = d.get("usage") or {}
                out.append({"rep": 0, "i": i, "age": age, "gender": gender,
                            "model": MODEL, "temp": TEMP, "effort": EFFORT,
                            "seconds": secs,
                            "tokens": usage.get("total_tokens"),
                            "completion_tokens": usage.get("completion_tokens"),
                            "reasoning_chars": len(reasoning),
                            "think_inline": "<think>" in text,
                            "served_model": d.get("model"),
                            "finish_reason": d["choices"][0].get("finish_reason"),
                            "words": len(text.split()), "text": text})
                print(f"  pair {i} ({age}/{gender:6s}) {secs:5.1f}s {out[-1]['words']:4d}w "
                      f"completion={out[-1]['completion_tokens']} "
                      f"reasoning_chars={len(reasoning)}")
                # Saved after every success: a later timeout exits the script, and each of
                # these calls costs ~7,000 tokens of thinking.
                json.dump(out, open(HERE + r"\results.json", "w", encoding="utf-8"),
                          ensure_ascii=False, indent=2)
                break
            print(f"  pair {i} attempt {attempt + 1}: HTTP {r.status_code} after {secs}s "
                  f"{r.text[:200]}")
            # The router's ~120s gateway timeout (experiment 01) - retrying just repeats it
            # at max effort, and the provider has likely already billed the thinking.
            if secs > 100:
                sys.exit("gateway timeout at max reasoning effort - stopping")
            time.sleep(5)
        except Exception as e:
            print(f"  pair {i} attempt {attempt + 1}: {type(e).__name__}: {e}")
            time.sleep(5)

if out:
    w = [c["words"] for c in out]
    print(f"\nmean {sum(w) / len(w):.0f} words, range {min(w)}-{max(w)}, "
          f"inside 300: {sum(1 for x in w if x <= 300)}/{len(w)}")

json.dump(out, open(HERE + r"\results.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print(f"{len(out)} generations -> results.json")
print("tokens spent:", sum(c["tokens"] or 0 for c in out))
