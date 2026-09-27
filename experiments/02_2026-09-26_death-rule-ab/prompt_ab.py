"""
Prompt A/B harness. Calls the proxy directly with explicitly-pinned model,
temperature and prompt text. Touches nothing in game_state/, writes nothing to
runs/ -- these are experiments, not sessions. Only a winning variant gets
promoted into a real version with a snapshot.
"""
import sys, json, time, random, requests

ROOT = r"D:\Dropbox\__Projects\HuggingFace Projects\NoExit Agents"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from game_state import assembly, prompts, config

MODEL = "Qwen/Qwen3-235B-A22B-Instruct-2507"   # the baseline, pinned regardless of config
TEMP = 0.95
SAMPLES = 3

BASE = prompts.characterFullUserPrompt
SYSTEM = prompts.characterSetupSystemPrompt

# the sentence the variants attach to
ANCHOR = ("Write a death that follows from the act itself, where nothing had to go "
          "wrong for it to kill you.")
assert BASE.count(ANCHOR) == 1, "anchor missing from characterFullUserPrompt"

# V1: the negative fence, restored verbatim from
# backups/2026-09-13_pronoun-rule-scoped-to-life-characters -- WITHOUT the positive
# "write instead..." list that followed it, since that list was 3/4 medical and every
# death generated under it was medical.
FENCE = (" No crashes or collisions of any kind. No falls, no fires, no machinery, "
         "no weather, no violence done to you by someone else.")

# V2: a register constraint rather than a content prohibition. Targets the escalation
# toward spectacle and homicide that appeared on two unrelated models.
REGISTER = (" Your death should be the kind that gets a two-line obituary, not a news "
            "story. Nobody else was harmed by it, and no stranger had to be involved. "
            "It is small, private and unremarkable to everyone except the people who "
            "knew you.")

VARIANTS = {
    "V0_control":       BASE,
    "V1_fence":         BASE.replace(ANCHOR, ANCHOR + FENCE),
    "V2_register":      BASE.replace(ANCHOR, ANCHOR + REGISTER),
    "V3_fence_register": BASE.replace(ANCHOR, ANCHOR + FENCE + REGISTER),
}

# identical inputs across variants so origin/age/gender are not a confound
random.seed(20260926)
INPUTS = [(random.choice(config.NAME_ORIGINS), random.randint(*config.AGE_RANGE), "male")
          for _ in range(SAMPLES)]
print("shared inputs per sample:", INPUTS, "\n")

results = []
for vname, template in VARIANTS.items():
    for si, (origin, age, gender) in enumerate(INPUTS):
        user = (template.replace("{NAME_ORIGIN}", origin)
                        .replace("{AGE}", str(age))
                        .replace("{GENDER}", gender))
        t0 = time.time()
        try:
            r = requests.post(config.PROXY_URL, timeout=330, json={
                "model": MODEL, "temperature": TEMP, "provider": "hf", "timeout": 300,
                "messages": [{"role": "system", "content": SYSTEM},
                             {"role": "user", "content": user}]})
        except Exception as e:
            print(f"{vname} s{si}: REQUEST FAILED {e}")
            continue
        dt = time.time() - t0
        if r.status_code != 200:
            print(f"{vname} s{si}: HTTP {r.status_code} {r.text[:120]}")
            continue
        d = r.json()
        content = d["choices"][0]["message"]["content"]
        p = assembly.parse_character_response(content)
        results.append({
            "variant": vname, "sample": si, "origin": origin, "age": age,
            "tokens": (d.get("usage") or {}).get("total_tokens"),
            "seconds": round(dt, 1),
            "name": p.get("name"), "occupation": p.get("occupation"),
            "cause_of_death": p.get("cause_of_death"),
            "who_loved": p.get("who_loved"),
            "complete": assembly.character_parse_complete(p),
        })
        print(f"{vname:19s} s{si} {dt:5.1f}s {str(p.get('name'))[:20]:22s} "
              f"{(p.get('cause_of_death') or '')[:96]}")

OUT = (r"C:\Users\Adim\AppData\Local\Temp\claude"
       r"\d--Dropbox---Projects-HuggingFace-Projects-NoExit-Agents"
       r"\2092e3e1-a100-4ff4-91a4-8ca557013bb9\scratchpad\prompt_ab_results.json")
json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"\n{len(results)} results -> {OUT}")
print("total tokens spent:", sum(r["tokens"] or 0 for r in results))
