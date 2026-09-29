"""Minimal viewer: model output only, one block per call, tinted by question.

    python experiments/_view.py 14_2026-09-29_the-secret-question-at-200

Reads <folder>/results.json and <folder>/tags.json, writes <folder>/view.html.

tags.json maps a record's index in results.json to a map of paragraph index ->
list of question numbers, e.g.

    {"0": {"0": [1, 2, 3], "1": [4], "2": [5]},
     "1": {"0": [1], "3": [5]}}

Paragraphs with no entry are left untinted. A list of more than one question means
the paragraph answers several at once and gets a striped rule instead of a fill.
Question text and the question count come from <folder>/questions.json if present.
No commentary is added to the page: model output, call labels, colour key.
"""
import json, html, io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
COLS = ["#1F6F5C", "#A8371B", "#8A6A12", "#2C5A8A", "#93306B", "#4F5B6B",
        "#7A5C3E", "#3E6F7A"]
DARK = ["#6FC5AC", "#E4784F", "#D6B15E", "#7FB0E0", "#E08CC2", "#9FB0C4",
        "#C9A483", "#82B6C4"]
SOFT = ["#DFEFE9", "#F7E3DC", "#F6EDD6", "#DEE9F4", "#F7DFEE", "#E4E8EE",
        "#F0E7DC", "#DFEBEF"]
SOFT_DARK = ["#12241F", "#2C1B14", "#2B2413", "#141F2B", "#2A1725", "#1C2129",
             "#241D15", "#132025"]


def label(r, n):
    """A call's one-line label, from whatever fields the experiment recorded."""
    bits = [f"call {n:02d}"]
    for k in ("arm", "rep", "pass", "temp"):
        if k in r:
            v = r[k] + 1 if k in ("rep", "pass") else r[k]
            bits.append(f"{k} {v}")
    if "i" in r:
        bits.append(f"pair {r['i']}")
    if "age" in r and "gender" in r:
        bits.append(f"{r['age']} / {r['gender']}")
    if "words" in r:
        bits.append(f"{r['words']} words")
    return "&nbsp;&nbsp;&middot;&nbsp;&nbsp;".join(html.escape(str(b)) for b in bits)


def paras(text, tags):
    out = []
    for n, b in enumerate([x for x in text.split("\n\n") if x.strip()]):
        body = html.escape(b.strip()).replace("\n", "<br>")
        body = body.replace("�", "&#xFFFD;")      # keep broken chars as returned
        qs = tags.get(str(n)) or tags.get(n)
        if not qs:
            out.append(f"<p>{body}</p>")
        elif len(qs) == 1:
            out.append(f'<p class="t t{qs[0]}"><span class="m">Q{qs[0]}</span>{body}</p>')
        else:
            step = 100 / len(qs)
            stops = ", ".join(f"var(--q{q}) {i * step:.2f}% {(i + 1) * step:.2f}%"
                              for i, q in enumerate(qs))
            chips = "".join(f'<span class="m c{q}">Q{q}</span>' for q in qs)
            out.append(f'<p class="t mix" style="border-image:'
                       f'linear-gradient(to bottom, {stops}) 1">{chips}{body}</p>')
    return "\n".join(out)


def build(folder):
    d = folder if os.path.isabs(folder) else os.path.join(HERE, folder)
    R = json.load(open(os.path.join(d, "results.json"), encoding="utf-8"))
    tags = json.load(open(os.path.join(d, "tags.json"), encoding="utf-8"))
    qpath = os.path.join(d, "questions.json")
    QS = json.load(open(qpath, encoding="utf-8")) if os.path.exists(qpath) else []
    n_q = max(len(QS), max((q for t in tags.values() for qs in t.values() for q in qs),
                           default=0))

    def tokens(pal, soft):
        return "\n".join(f"  --q{i + 1}:{pal[i]}; --q{i + 1}s:{soft[i]};"
                         for i in range(n_q))

    rules = "\n".join(
        f".t{i + 1}{{border-left-color:var(--q{i + 1}); background:var(--q{i + 1}s)}}\n"
        f".t{i + 1} .m,.c{i + 1}{{color:var(--q{i + 1})}}\n"
        f".key .k{i + 1}{{color:var(--q{i + 1}); background:var(--q{i + 1}s)}}"
        for i in range(n_q))

    key = "\n".join(
        f'  <span class="kk k{i + 1}"><b>Q{i + 1}</b>{html.escape(QS[i])}</span>'
        for i in range(len(QS)))

    blocks = "\n".join(
        f'<section>\n  <p class="lab">{label(r, n + 1)}</p>\n'
        f'  {paras(r["text"], tags.get(str(n), {}))}\n</section>'
        for n, r in enumerate(R))

    page = f"""<title>{html.escape(os.path.basename(d))}</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,400;7..72,600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --paper:#FCFAF7; --ink:#1F1A17; --faint:#9A8E86; --rule:#E4DCD4; --sunk:#F0EBE5;
{tokens(COLS, SOFT)}
}}
@media (prefers-color-scheme:dark){{ :root:not([data-theme="light"]){{
  color-scheme:dark;
  --paper:#15120F; --ink:#EDE6DF; --faint:#7A6E66; --rule:#2E2721; --sunk:#201B17;
{tokens(DARK, SOFT_DARK)}
}}}}
:root[data-theme="dark"]{{
  color-scheme:dark;
  --paper:#15120F; --ink:#EDE6DF; --faint:#7A6E66; --rule:#2E2721; --sunk:#201B17;
{tokens(DARK, SOFT_DARK)}
}}
*{{box-sizing:border-box}}
body{{background:var(--paper); color:var(--ink);
  font-family:Literata,Georgia,serif; font-size:16px; line-height:1.62;
  margin:0; padding:0 16px 80px; -webkit-font-smoothing:antialiased}}
main{{max-width:74ch; margin:0 auto}}
.key{{position:sticky; top:0; z-index:5; background:var(--paper);
  border-bottom:1px solid var(--rule); padding:10px 0 11px;
  display:flex; flex-wrap:wrap; gap:6px; margin-bottom:34px}}
.kk{{font-size:12px; line-height:1.35; padding:4px 9px; border-radius:2px;
  border-left:3px solid currentColor}}
.kk b{{font:500 9px/1 'IBM Plex Mono',ui-monospace,monospace; letter-spacing:.1em;
  margin-right:7px; opacity:.85}}
section{{margin:0 0 54px; padding-bottom:54px; border-bottom:1px solid var(--rule)}}
section:last-child{{border-bottom:none}}
.lab{{font:400 11px/1 'IBM Plex Mono',ui-monospace,monospace; letter-spacing:.09em;
  text-transform:uppercase; color:var(--faint); margin:0 0 20px}}
p{{margin:0 0 1.05em; padding-left:16px; border-left:3px solid transparent}}
p.t{{padding:10px 14px 11px; border-radius:2px; margin-bottom:.8em;
  border-left:3px solid currentColor; color:var(--ink)}}
p.mix{{background:var(--sunk); border-left:3px solid transparent; color:var(--ink)}}
.m{{display:inline-block; font:500 9.5px/1 'IBM Plex Mono',ui-monospace,monospace;
  letter-spacing:.1em; margin-right:9px; vertical-align:1.5px; opacity:.85}}
{rules}
@media (max-width:620px){{ .key{{font-size:11px}} }}
</style>
<main>
<div class="key">
{key}
</div>
{blocks}
</main>
"""
    out = os.path.join(d, "view.html")
    io.open(out, "w", encoding="utf-8", newline="\n").write(page)
    print(f"{len(R)} calls -> {out} ({os.path.getsize(out)} bytes)")
    return out


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else ".")
