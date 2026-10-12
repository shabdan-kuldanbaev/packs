"""Turn the Google Doc "Frontend — interview questions (full)" (exported as Markdown) into
the TSV that build_tsv_pack.py reads.

python3 tools/doc2tsv.py doc.md tools/frontend_interview.tsv

Part 1 · Base: "**N. Question**" then a one-line answer      -> word = question, translation = answer.
Part 2 · Senior: "### **N. Question**", spoken answer, *Russian gist*
                                                            -> word = question, translation = gist,
                                                               example = spoken answer, example translation = gist.
"## Section" headings become decks.
"""
import re
import sys

src, dst = sys.argv[1:3]


def clean(s):
    s = s.strip()
    s = re.sub(r'\\([^0-9A-Za-z\s])', r'\1', s)
    s = re.sub(r'^\*+|\*+$', '', s).strip()
    return s.replace('\t', ' ')


def question(s):
    return re.sub(r'^\d+\.\s*', '', clean(s.lstrip('#').strip()))


lines = [l.rstrip('\n') for l in open(src, encoding='utf-8')]
part, deck, out, i = None, None, [], 0
paras = []
# Group lines into paragraphs; a "  " line break keeps question and answer apart.
buf = []
for l in lines + ['']:
    if not l.strip():
        if buf:
            paras.append(buf)
            buf = []
        continue
    buf.append(l)

for p in paras:
    head = p[0]
    if head.startswith('# '):
        t = clean(head[2:])
        part = 'Base' if 'Part 1' in t else 'Senior' if 'Part 2' in t else None
        continue
    if head.startswith('## '):
        deck = clean(head[3:])
        continue
    if not part:
        continue
    if part == 'Base' and re.match(r'^\*\*\d+\\?\.', head):
        if len(p) != 2:
            sys.exit(f'base card needs question + answer: {p}')
        out.append(['Base', deck, question(head), clean(p[1]), '', '', ''])
    elif part == 'Senior' and head.startswith('### '):
        out.append(['Senior', deck, question(head), None, '', None, None])
    elif part == 'Senior' and out and out[-1][3] is None:
        text = clean(' '.join(p))
        if out[-1][5] is None:
            out[-1][5] = text
        else:
            out[-1][3] = out[-1][6] = text

bad = [r for r in out if None in r or not r[1]]
if bad:
    sys.exit(f'incomplete cards: {bad[:2]}')
with open(dst, 'w', encoding='utf-8') as f:
    f.write(f'# generated from {src} by tools/doc2tsv.py — edit the Google Doc, then re-export\n')
    f.write('\n'.join('\t'.join(r) for r in out) + '\n')
print(sum(r[0] == 'Base' for r in out), 'base,', sum(r[0] == 'Senior' for r in out), 'senior')
