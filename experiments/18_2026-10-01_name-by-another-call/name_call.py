"""Experiment 18 - getting a name out of the story prompt, by a second call.

The promotion of experiments 15-17 into game_state is blocked on one thing: the dialogue
system prompt needs {NAME}, and a 300-word story supplies one only half the time. GLM-5.3
named or implied the protagonist in 5 of 10 in experiment 17; Qwen named one in 0 of 10 in
experiment 15.

Two ways to solve it with a second call, both tested here.

  ARM A - supply.  A separate cheap call invents a name from age and gender. It is passed
                   into the story prompt as a given, the way Age and Gender already are.
                   Ten fresh generations.

  ARM B - extract. The existing info extractor (config.INFO_EXTRACTOR_URL, the Space Unity
                   calls as InfoExtractorHandler.ExtractInfo) is run over experiment 17's
                   ten stories and asked for the protagonist's name. No new generations.

Held constant: zai-org/GLM-5.3 @ 1.1 at reasoning_effort="high", through the proxy, the same
five inputs twice, the same system prompt and craft rules. Arm A adds one line to the user
prompt. NAME_ORIGINS is not used - the no-naming-tradition rule stands.

Prediction, recorded before the run:

  A1. The story uses the supplied name in 9 or 10 of 10. It is in the prompt as a fact.
  A2. The supplied names break the input prior. Experiment 17 gave Danny or Daniel in 5 of
      10 and the same $410,000 for pair 1 in both passes; a separate call at temperature 1.2
      should not collide that way. 0 or 1 repeats across the ten.
  A3. The deaths stay cardiovascular, 9 or 10 of 10. A name does not touch that.
  A4. Supplying the name costs the "You are <name>" opening, which is where GLM currently
      puts it, so the opening gets no better - still 1 or 2 of 10 opening on the loved one.
  B1. The extractor finds a name in about 5 of 10 - it cannot invent what is not there, and
      5 of 10 is the hand count for experiment 17.
  B2. Where it does answer, it is right. The 0.6B model is doing extraction, not judgement.

Saves after every success. Scratch only: writes nothing to game_state or runs/.
"""
import sys, os, json, time, requests

ROOT = r"D:\Dropbox\__Projects\HuggingFace Projects\NoExit Agents"
HERE = ROOT + r"\experiments\18_2026-10-01_name-by-another-call"
EXP17 = ROOT + r"\experiments\17_2026-10-01_glm-at-ten\results.json"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from game_state import config, prompts, providers, assembly

MODEL = "zai-org/GLM-5.3"
TEMP = 1.1
EFFORT = "high"
NAME_MODEL = config.MODEL_DIALOGUE      # Qwen3-8B: small, already in the pipeline
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

Write the story of your life, ending with how you died. No longer than 300 words.

Who did you love?
How did your sin destroy them?
What lie did you have to tell yourself and others to keep going?
What kind of person do you want people to think you are?
What secret would make everyone see you for what you really are?

Your name: {NAME}
Age: {AGE}
Gender: {GENDER}"""

NAME_PROMPT = ("Invent one full name — first name and surname — for a person aged {AGE}, "
               "{GENDER}. Any background. Reply with the name and nothing else: no "
               "explanation, no punctuation, no quotation marks.")

EXTRACT_PROMPT = ("Return only the full name of the person whose story this is — the person "
                  "the story calls 'you'. If the story never gives that person a name, "
                  "return exactly: none")

INPUTS = [(51, "male"), (64, "female"), (45, "female"), (57, "female"), (55, "male")]

out = {"arm_a": [], "arm_b": []}

# Resume: this machine's DNS drops often enough that experiment 16 logged two failures and
# this script lost its tenth name call to one. Anything already saved is kept.
if os.path.exists(HERE + r"\results.json"):
    prior = json.load(open(HERE + r"\results.json", encoding="utf-8"))
    out["arm_a"] = prior.get("arm_a", [])
    print(f"resuming: {len(out['arm_a'])} arm A generations already saved")
DONE_A = {(c["rep"], c["i"]) for c in out["arm_a"]}


def save():
    json.dump(out, open(HERE + r"\results.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)


def post(body, timeout=330):
    return requests.post(config.PROXY_URL, timeout=timeout, json=body)


def make_name(age, gender, attempts=4):
    """The second call, before the story. Retries: DNS here is unreliable."""
    body = {"model": NAME_MODEL, "temperature": NAME_TEMP, "provider": "hf", "timeout": 120,
            "messages": [{"role": "user",
                          "content": NAME_PROMPT.replace("{AGE}", str(age))
                                                .replace("{GENDER}", gender)}]}
    last = "no attempt"
    for attempt in range(attempts):
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


# ── ARM A ────────────────────────────────────────────────────────────────────
print(f"ARM A - supply the name  ({NAME_MODEL} @ {NAME_TEMP} -> {MODEL})")
for rep in range(2):
    print(f"--- pass {rep + 1} of 2 ---")
    for i, (age, gender) in enumerate(INPUTS):
        if (rep, i) in DONE_A:
            continue
        name, raw = make_name(age, gender)
        if not name:
            print(f"  pair {i}: name call failed ({raw})")
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
                    out["arm_a"].append({
                        "rep": rep, "i": i, "age": age, "gender": gender,
                        "supplied_name": name,
                        "uses_full_name": name in text,
                        "uses_first_name": first in text,
                        "seconds": round(time.time() - t0, 1),
                        "tokens": u.get("total_tokens"),
                        "words": len(text.split()), "text": text})
                    save()
                    c = "full" if name in text else ("first" if first in text else "NOT USED")
                    print(f"  pair {i} ({age}/{gender:6s}) {name:22s} "
                          f"{out['arm_a'][-1]['seconds']:5.1f}s "
                          f"{out['arm_a'][-1]['words']:4d}w  {c}")
                    break
                print(f"  pair {i} attempt {attempt + 1}: HTTP {r.status_code}")
                time.sleep(5)
            except Exception as e:
                print(f"  pair {i} attempt {attempt + 1}: {type(e).__name__}")
                time.sleep(5)

# ── ARM B ────────────────────────────────────────────────────────────────────
print(f"\nARM B - extract from experiment 17's ten stories  ({config.INFO_EXTRACTOR_URL})")
R17 = json.load(open(EXP17, encoding="utf-8"))
for n, r in enumerate(R17):
    try:
        res = providers.call_info_extractor(r["text"], EXTRACT_PROMPT)
        got = (res.content or "").strip()
    except Exception as e:
        got = f"<{type(e).__name__}>"
    out["arm_b"].append({"rep": r["rep"], "i": r["i"], "age": r["age"],
                         "gender": r["gender"], "extracted": got})
    save()
    print(f"  call {n + 1:2d} (pass {r['rep'] + 1} pair {r['i']})  -> {got!r}")

a = out["arm_a"]
if a:
    print(f"\nARM A: {len(a)}/10 generated")
    print(f"  supplied name used in full : {sum(1 for c in a if c['uses_full_name'])}/{len(a)}")
    print(f"  first name at least        : {sum(1 for c in a if c['uses_first_name'])}/{len(a)}")
    print(f"  distinct names supplied    : {len({c['supplied_name'] for c in a})}/{len(a)}")
    w = [c["words"] for c in a]
    print(f"  words mean {sum(w)/len(w):.0f}, inside 300: {sum(1 for x in w if x <= 300)}")
    print(f"  tokens: {sum(c['tokens'] or 0 for c in a)}")
print(f"ARM B: {sum(1 for c in out['arm_b'] if c['extracted'].lower() not in ('none', ''))}"
      f"/{len(out['arm_b'])} returned something other than none")
