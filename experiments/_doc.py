"""Same view as _view.py, as a document instead of a web page.

    python experiments/_doc.py 15_2026-09-29_five-questions-at-300

Reads <folder>/results.json, <folder>/tags.json and, if present, <folder>/questions.json,
and writes two files next to them:

    view.docx   Word/Google Docs,each paragraph shaded in its question's colour
    view.md     plain text, the same thing with [Q1] markers instead of colour

The .docx is assembled by hand - a zip of three XML parts - so nothing needs installing.
Model output only: a colour key, a one-line label per call, and the text.
"""
import json, os, sys, zipfile, datetime

HERE = os.path.dirname(os.path.abspath(__file__))

# question colour, paragraph fill
INK = ["1F6F5C", "A8371B", "8A6A12", "2C5A8A", "93306B", "4F5B6B", "7A5C3E", "3E6F7A"]
FILL = ["DFEFE9", "F7E3DC", "F6EDD6", "DEE9F4", "F7DFEE", "E4E8EE", "F0E7DC", "DFEBEF"]
MIXFILL = "F0EBE5"
GREY = "9A8E86"
BODY, LABEL = "Georgia", "Consolas"


def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def run(text, color=None, size=22, font=BODY, caps=False, space=False):
    rpr = f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}"/><w:sz w:val="{size}"/>'
    if color:
        rpr += f'<w:color w:val="{color}"/>'
    if caps:
        rpr += "<w:caps/>"
    if space:
        rpr += '<w:spacing w:val="30"/>'
    return (f"<w:r><w:rPr>{rpr}</w:rPr>"
            f'<w:t xml:space="preserve">{esc(text)}</w:t></w:r>')


def para(runs, fill=None, bar=None, after=120, before=0, indent=0, rule=False):
    ppr = f'<w:spacing w:before="{before}" w:after="{after}"/>'
    if indent:
        ppr += f'<w:ind w:left="{indent}" w:right="120"/>'
    if bar:
        ppr += ('<w:pBdr><w:left w:val="single" w:sz="18" w:space="8" '
                f'w:color="{bar}"/></w:pBdr>')
    if rule:
        ppr += ('<w:pBdr><w:bottom w:val="single" w:sz="4" w:space="1" '
                f'w:color="E4DCD4"/></w:pBdr>')
    if fill:
        ppr += f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
    return f"<w:p><w:pPr>{ppr}</w:pPr>{''.join(runs)}</w:p>"


def label_of(r, n):
    bits = [f"call {n:02d}"]
    for k in ("arm", "rep", "pass"):
        if k in r:
            v = r[k] + 1 if k in ("rep", "pass") else r[k]
            bits.append(f"{k} {v}")
    if "i" in r:
        bits.append(f"pair {r['i']}")
    if "age" in r and "gender" in r:
        bits.append(f"{r['age']} / {r['gender']}")
    if "words" in r:
        bits.append(f"{r['words']} words")
    return "   ·   ".join(str(b) for b in bits)


def build(folder):
    d = folder if os.path.isabs(folder) else os.path.join(HERE, folder)
    R = json.load(open(os.path.join(d, "results.json"), encoding="utf-8"))
    T = json.load(open(os.path.join(d, "tags.json"), encoding="utf-8"))
    qp = os.path.join(d, "questions.json")
    QS = json.load(open(qp, encoding="utf-8")) if os.path.exists(qp) else []

    body, md = [], []
    body.append(para([run(os.path.basename(d), GREY, 18, LABEL, caps=True, space=True)],
                     after=200))
    md.append(f"# {os.path.basename(d)}\n")

    for i, q in enumerate(QS):
        body.append(para([run(f"Q{i + 1}   ", INK[i], 16, LABEL, space=True),
                          run(q, size=20)],
                         fill=FILL[i], bar=INK[i], after=60, indent=120))
        md.append(f"**Q{i + 1}**  {q}")
    body.append(para([run("")], after=240))
    md.append("")

    for n, r in enumerate(R):
        tags = T.get(str(n), {})
        body.append(para([run(label_of(r, n + 1), GREY, 16, LABEL, space=True)],
                         before=360, after=160, rule=True))
        md.append(f"\n---\n\n## {label_of(r, n + 1)}\n")

        for p, block in enumerate([x for x in r["text"].split("\n\n") if x.strip()]):
            text = block.strip()
            qs = tags.get(str(p)) or tags.get(p)
            if not qs:
                body.append(para([run(text)], after=140, indent=140))
                md.append(f"{text}\n")
            elif len(qs) == 1:
                q = qs[0]
                body.append(para([run(f"Q{q}  ", INK[q - 1], 16, LABEL, space=True),
                                  run(text)],
                                 fill=FILL[q - 1], bar=INK[q - 1], after=140, indent=140))
                md.append(f"**[Q{q}]**  {text}\n")
            else:
                chips = [run(f"Q{q}  ", INK[q - 1], 16, LABEL, space=True) for q in qs]
                body.append(para(chips + [run(text)], fill=MIXFILL,
                                 bar=INK[qs[0] - 1], after=140, indent=140))
                md.append("**[" + " ".join(f"Q{q}" for q in qs) + "]**  " + text + "\n")

    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           "<w:body>" + "".join(body) +
           '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
           '<w:pgMar w:top="1134" w:right="1418" w:bottom="1134" w:left="1418"/>'
           "</w:sectPr></w:body></w:document>")

    types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.'
             'relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'
             '<Override PartName="/word/document.xml" ContentType="application/vnd.'
             'openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/'
            '2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')

    out = os.path.join(d, "view.docx")
    stamp = datetime.datetime.now().timetuple()[:6]
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in (("[Content_Types].xml", types), ("_rels/.rels", rels),
                           ("word/document.xml", doc)):
            info = zipfile.ZipInfo(name, stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data.encode("utf-8"))

    mdp = os.path.join(d, "view.md")
    open(mdp, "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
    print(f"{len(R)} calls -> {out} ({os.path.getsize(out)} bytes)")
    print(f"{len(R)} calls -> {mdp} ({os.path.getsize(mdp)} bytes)")
    return out


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else ".")
