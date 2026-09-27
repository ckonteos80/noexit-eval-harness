"""
New 9-field character prompt, both characters generated INDEPENDENTLY --
no anti-duplication block, character 2 never sees character 1.
Scratch only: reads game_state for config/extract_field, writes nothing to the project.
"""
import sys, json, time, random, requests

ROOT = r"D:\Dropbox\__Projects\HuggingFace Projects\NoExit Agents"
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
from game_state import assembly, config

MODEL = "Qwen/Qwen3-235B-A22B-Instruct-2507"   # baseline every eval is calibrated against
TEMP = 0.95

SYSTEM = """You are writing a character for a theater play about three strangers locked together in hell
for eternity. The play is contemporary, realistic, and psychological. Hell is the small room
these three people will share to torture each other for eternity.

Every character you write is damned. They know why. The drama of the play is whether they will
ever admit it \u2014 to the others, or to themselves.

Four rules govern every fact you write.

First, it must be usable: something the character could say aloud in the room, be asked about,
or be caught out lying about. A detail that cannot be used in conversation does not belong.

Second, it must be named: never gesture at something without stating it.

Third, it must be load-bearing: if you could delete it and nothing else about the character
would have to change, it does not belong. Every fact should be holding something else up.

Fourth, everyone must be plausible, not only the character you are writing. Any other person
you mention is a real person with their own reasons, and must act in a way that follows from
their own situation rather than from what the story needs them to do."""

USER = """Write a complete character for the room. The character just died. They have just arrived in
the room to spend eternity in hell.

Write in the second person \u2014 "you," not "she/he/they." The character is reading their own
interior knowledge. Every field is part of what they know about themselves, even the things
they will not admit.

Name every person from your own life every time you mention them, in every field. Once you have
given somebody a name, use that name again \u2014 never he, she, him, her, they or them \u2014 even where
it repeats and even where it reads a little stiffly.

The two people in that room are the exception. You have never met them and do not know their
names, so "they" and "them" are the correct words for them. The field about what you want from
the others in the room is the only field about those two, and cannot be written any other way.

Inputs (do not change these):
- Age: {AGE}
- Gender: {GENDER}
- Naming tradition: {NAME_ORIGIN}

Write the fields below in the order given. Each is written knowing everything above it: a later
field must be consistent with the facts already established and must never contradict them.

**Name**
A plausible contemporary first name and last name \u2014 two words \u2014 drawn from the {NAME_ORIGIN}
naming tradition. This person is an ordinary contemporary person who happens to have that
background. Do not write their origin into any other field unless it genuinely matters to the life.

**Occupation**
A recognizable contemporary job. Plain language. No invented institutions, no grand titles.
One short phrase.

**Reason for Damnation \u2014 True**
What you actually did that condemned you to spend eternity in hell.

**Reason for Damnation \u2014 Self-told**
The same fact, refracted through the story you prefer to tell yourself about it. It is recognizably
a distortion of the True reason. Not a different story; the same story told differently. You usually
live in this version. The distortion must be checkable against the facts of the true reason. A
reader holding both versions must be able to point to the exact fact it bends. If nothing established
contradicts it, it is not a distortion \u2014 rewrite it. One or two sentences.

**What you refuse to admit about yourself**
The deeper psychological fact under the sin. Not what you did, but what you are. The thing that, if
named aloud in the room, would unmake you.

State it flatly, in the same plain register as every other field. No imagery, no metaphor, no
rhetorical cadence, no piling up of clauses for effect \u2014 this is a fact about a person, written the
way a fact is written.

**Life**
A single paragraph in the second person, no longer than 150 words. Facts only, the kind another
person in the room could ask you about. No sensory writing, no atmosphere, no imagery, no
metaphor \u2014 if a sentence is doing mood instead of delivering a fact, cut it and write the fact.

End the paragraph describing how you died. Contemporary, specific, plainly stated.
Your death must also belong to the person named above. Someone reading the death and the
relationship together must see why one led to the other. A death that could be lifted out and
dropped into a stranger's life is the wrong death \u2014 rewrite it.

**Defining personality trait**
One short phrase \u2014 two or three words, plain ones \u2014 naming the dominant thing others would notice in
you. Write the words only: no asterisks, no quotation marks, no emphasis of any kind around them.

It must be demonstrated by what is already written above. Something in the life, the death, or the sin
has to show this quality in action; if nothing there would make a reader arrive at it, it is the wrong
trait.

**What you want from the others in the room**
Your starting drive. What you are hoping these strangers will give you. It must be a strategy for
protecting what you refuse to admit \u2014 the thing you are doing to keep it buried, not a wish
unconnected to it.

**People in your life**
The people you already named above. For each one, say what they were to you, and one clause on what
they themselves wanted \u2014 the thing they were after in their own life, which may have had nothing to
do with you. Their want must make sense as something a real person in their position would actually
want; a want that exists only to explain how you felt about them is not a want.

Use this format exactly, with every heading present, spelled as written, and in this order:

**Name**
[your text]

**Occupation**
[your text]

**Reason for Damnation \u2014 True**
[your text]

**Reason for Damnation \u2014 Self-told**
[your text]

**What you refuse to admit about yourself**
[your text]

**Life**
[prose paragraph, ending with the death]

**Defining personality trait**
[your text]

**What you want from the others in the room**
[your text]

**People in your life**
[your text]

Begin now."""

FIELDS = {
    "name": "Name",
    "occupation": "Occupation",
    "reason_true": "Reason for Damnation \u2014 True",
    "reason_self_told": "Reason for Damnation \u2014 Self-told",
    "refuse_to_admit": "What you refuse to admit about yourself",
    "life": "Life",
    "personality_trait": "Defining personality trait",
    "want": "What you want from the others in the room",
    "people": "People in your life",
}

random.seed()
out = {}
for char_no in (1, 2):
    gender = config.CHARACTER_GENDERS[char_no]
    age = random.randint(*config.AGE_RANGE)
    origin = random.choice(config.NAME_ORIGINS)
    user = (USER.replace("{AGE}", str(age))
                .replace("{GENDER}", gender)
                .replace("{NAME_ORIGIN}", origin))
    t0 = time.time()
    r = requests.post(config.PROXY_URL, timeout=330, json={
        "model": MODEL, "temperature": TEMP, "provider": "hf", "timeout": 300,
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": user}]})
    dt = time.time() - t0
    if r.status_code != 200:
        print(f"char{char_no}: HTTP {r.status_code} {r.text[:300]}")
        continue
    d = r.json()
    content = d["choices"][0]["message"]["content"]
    parsed = {k: assembly.extract_field(content, lbl) for k, lbl in FIELDS.items()}
    missing = [k for k, v in parsed.items() if not (v or "").strip()]
    out[char_no] = {"inputs": {"age": age, "gender": gender, "origin": origin},
                    "usage": d.get("usage"), "seconds": round(dt, 1),
                    "raw": content, "parsed": parsed, "missing": missing}
    print(f"char{char_no}: {dt:.1f}s  {(d.get('usage') or {}).get('total_tokens')} tok  "
          f"origin={origin} age={age}  missing={missing or 'none'}")

P = (r"C:\Users\Adim\AppData\Local\Temp\claude"
     r"\d--Dropbox---Projects-HuggingFace-Projects-NoExit-Agents"
     r"\2092e3e1-a100-4ff4-91a4-8ca557013bb9\scratchpad\newprompt_result.json")
json.dump(out, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("saved ->", P)
