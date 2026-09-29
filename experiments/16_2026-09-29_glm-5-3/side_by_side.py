"""Builds glm-beside-qwen/: experiment 15's first-pass Qwen story and this experiment's GLM-5.3
story for each of the five inputs, interleaved, as a folder the shared viewers can read.

    python experiments/16_2026-09-29_glm-5-3/side_by_side.py
    python experiments/_view.py 16_2026-09-29_glm-5-3/glm-beside-qwen
    python experiments/_doc.py  16_2026-09-29_glm-5-3/glm-beside-qwen

Writes glm-beside-qwen/results.json (texts verbatim, an `arm` field per record, no `rep`),
glm-beside-qwen/tags.json (both tag sets remapped to the interleaved order) and
glm-beside-qwen/questions.json.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
EXP15 = os.path.join(HERE, "..", "15_2026-09-29_five-questions-at-300")
OUT = os.path.join(HERE, "glm-beside-qwen")


def load(path):
    return json.load(open(path, encoding="utf-8"))


r15, t15 = load(os.path.join(EXP15, "results.json")), load(os.path.join(EXP15, "tags.json"))
r16, t16 = load(os.path.join(HERE, "results.json")), load(os.path.join(HERE, "tags.json"))

# experiment 15 ran pass 1 first, so its rep-0 records sit at indices 0-4
qwen = {r["i"]: (n, r) for n, r in enumerate(r15) if r["rep"] == 0}
glm = {r["i"]: (n, r) for n, r in enumerate(r16)}

keep = ("i", "age", "gender", "words", "seconds", "tokens", "text")
results, tags = [], {}
for i in sorted(glm):
    for arm, (src_n, rec), src_tags in (("Qwen3-235B · exp 15", qwen[i], t15),
                                        ("GLM-5.3 · high", glm[i], t16)):
        tags[str(len(results))] = src_tags.get(str(src_n), {})
        results.append({"arm": arm, **{k: rec[k] for k in keep}})

os.makedirs(OUT, exist_ok=True)
json.dump(results, open(os.path.join(OUT, "results.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
json.dump(tags, open(os.path.join(OUT, "tags.json"), "w", encoding="utf-8"), indent=1)
json.dump(load(os.path.join(EXP15, "questions.json")),
          open(os.path.join(OUT, "questions.json"), "w", encoding="utf-8"), indent=1)
print(f"{len(results)} records -> glm-beside-qwen/")
