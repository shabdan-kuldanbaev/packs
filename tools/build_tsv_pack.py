"""A word pack from a hand-written TSV -> packs/<id>.json + its catalog.json entry.

python3 tools/build_tsv_pack.py <words.tsv> <pack id> <version> <title> <level> <description> [out_dir]

Accepted answers ("a") also get the word and each alternative without a trailing
.?! and without a leading article (a / an / the / to), as nobody types those.

TSV columns (tab-separated, '#' lines are comments):
  group, deck, word, translation, alternatives ('|'-separated, optional),
  example (optional), example translation (optional).
Decks keep the order they first appear in; titles get a "01 · " number.
Only this pack's entry in catalog.json is replaced.
"""
import hashlib
import json
import os
import re
import sys

PREVIEW = 12


def rows(path):
    for n, line in enumerate(open(path, encoding='utf-8'), 1):
        line = line.rstrip('\n')
        if not line.strip() or line.startswith('#'):
            continue
        parts = [p.strip() for p in line.split('\t')]
        parts += [''] * (7 - len(parts))
        if len(parts) != 7 or not all(parts[:4]):
            sys.exit(f'{path}:{n}: need group, deck, word, translation — got {parts}')
        if bool(parts[5]) != bool(parts[6]):
            sys.exit(f'{path}:{n}: example and its translation go together')
        yield n, parts


def main():
    tsv, pack_id, version, title, level, description = sys.argv[1:7]
    out_dir = sys.argv[7] if len(sys.argv) > 7 else '.'
    items = list(rows(tsv))
    seen = {}
    for n, p in items:
        key = p[2].lower()
        if key in seen:
            sys.exit(f'{tsv}:{n}: "{p[2]}" repeats line {seen[key]}')
        seen[key] = n

    order = list(dict.fromkeys((p[0], p[1]) for _, p in items))
    decks, cat_decks = [], []
    for i, (group, deck) in enumerate(order, 1):
        words = []
        for _, (g, d, w, t, a, ex, ext) in items:
            if (g, d) != (group, deck):
                continue
            entry = {'w': w, 't': t}
            alts = []
            # Ввод ответа (§4.1): точку в конце и артикль никто не печатает.
            for x in [*(x.strip() for x in a.split('|')), w]:
                for v in (x, re.sub(r'[.?!]+$', '', x)):
                    for c in (v, re.sub(r'^(a|an|the|to)\s+', '', v, flags=re.I)):
                        c = c.strip()
                        if c and c != w and c not in alts:
                            alts.append(c)
            if alts:
                entry['a'] = alts
            if ex:
                entry['ex'], entry['exT'] = ex, ext
            words.append(entry)
        deck_title = f'{i:02d} · {deck}'
        decks.append({'title': deck_title, 'group': group, 'words': words})
        cat_decks.append({'title': deck_title, 'group': group,
                          'wordCount': len(words),
                          'preview': [x['w'] for x in words[:PREVIEW]]})

    pack = {'format': 1, 'id': pack_id, 'version': int(version),
            'targetLang': 'en', 'nativeLang': 'ru', 'decks': decks}
    body = json.dumps(pack, ensure_ascii=False, separators=(',', ':'))
    rel = f'packs/{pack_id}.json'
    os.makedirs(os.path.join(out_dir, 'packs'), exist_ok=True)
    with open(os.path.join(out_dir, rel), 'w', encoding='utf-8') as f:
        f.write(body)
    raw = body.encode()
    entry = {
        'id': pack_id, 'version': int(version), 'title': title,
        'description': description, 'targetLang': 'en', 'nativeLang': 'ru',
        'level': level, 'wordCount': sum(d['wordCount'] for d in cat_decks),
        'deckCount': len(cat_decks), 'file': rel, 'bytes': len(raw),
        'sha256': hashlib.sha256(raw).hexdigest(), 'decks': cat_decks,
    }
    cat_path = os.path.join(out_dir, 'catalog.json')
    catalog = json.load(open(cat_path, encoding='utf-8'))
    catalog['packs'] = [p for p in catalog['packs'] if p['id'] != pack_id] + [entry]
    with open(cat_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=1)
    print('decks', len(decks), 'words', entry['wordCount'], 'bytes', len(raw))


if __name__ == '__main__':
    main()
