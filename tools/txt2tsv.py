"""Convert a 4-line card file (tools/*.txt) into the TSV that build_tsv_pack.py reads.

python3 tools/txt2tsv.py tools/frontend_senior.txt tools/frontend_senior.tsv "Senior questions"

"## Deck" lines start a deck; a card is 4 consecutive lines: question, one-line answer,
spoken answer (example), Russian gist (example translation). Blank lines separate cards.
"""
import sys

src, dst, group = sys.argv[1:4]
deck, buf, out = None, [], []
for line in list(open(src, encoding='utf-8')) + ['\n']:
    line = line.rstrip('\n')
    if line.startswith('#') and not line.startswith('##'):
        continue
    if line.startswith('## '):
        deck = line[3:].strip()
        continue
    if line.strip():
        buf.append(line.strip())
        continue
    if buf:
        if len(buf) != 4 or not deck:
            sys.exit(f'bad card near: {buf[0][:60]!r} ({len(buf)} lines, deck={deck})')
        q, short, spoken, ru = buf
        out.append('\t'.join([group, deck, q, short, '', spoken, ru]))
        buf = []
with open(dst, 'w', encoding='utf-8') as f:
    f.write(f'# generated from {src} by tools/txt2tsv.py — edit the .txt, not this file\n')
    f.write('\n'.join(out) + '\n')
print(len(out), 'cards')
