"""Chinese · HSK 1: tools/zh_hsk1.tsv -> packs/zh-ru-hsk1.json + catalog.json.

python3 tools/build_zh_pack.py <graphics.txt> tools/zh_hsk1.tsv .

The word list is the new HSK 1 (2025 syllabus, key "newest-1") from
github.com/drkameleon/complete-hsk-vocabulary (MIT). Pinyin and Russian
translations in the TSV are written by hand: the dataset's first reading is
often a surname or a rare reading (百 Bǎi, 看 kān, 听 yǐn), so it is not used.

graphics.txt is Make Me a Hanzi (github.com/skishore/makemeahanzi, Arphic
Public License, tools/makemeahanzi/) and is not stored here (30 MB). Stroke
medians live on a 1024 grid with y up and an offset of 900; the app cell is
0..100: x*100/1024, (900 - y)*100/1024.

Each word gets "r" (reading: Pinyin, spec §23.4) and "s" (one drawing per
character, spec §18.7). Only this pack's entry in catalog.json is replaced.
"""
import hashlib
import json
import os
import sys

PACK_ID = 'zh-ru-hsk1'
PACK_VERSION = 1
PREVIEW = 12
REMOVED = {'zh-ru-hsk1-sample'}


def cell(v):
    return round(min(100.0, max(0.0, v * 100 / 1024)), 1)


def strokes_of(word, graphics):
    chars = []
    for ch in word:
        if ch not in graphics:
            sys.exit(f'no stroke data for {ch!r} in {word!r}')
        chars.append([
            [c for x, y in median for c in (cell(x), cell(900 - y))]
            for median in graphics[ch]
        ])
    return {'v': 1, 'c': chars}


def rows(path):
    for n, line in enumerate(open(path, encoding='utf-8'), 1):
        line = line.rstrip('\n')
        if not line.strip() or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) != 4 or not all(p.strip() for p in parts):
            sys.exit(f'{path}:{n}: expected deck, word, pinyin, translation')
        yield [p.strip() for p in parts]


def main():
    graphics = {}
    for line in open(sys.argv[1], encoding='utf-8'):
        d = json.loads(line)
        graphics[d['character']] = d['medians']
    items = list(rows(sys.argv[2]))
    out_dir = sys.argv[3]

    words = [w for _, w, _, _ in items]
    dups = {w for w in words if words.count(w) > 1}
    if dups:
        sys.exit(f'duplicate words: {sorted(dups)}')

    decks, cat_decks = [], []
    for title in dict.fromkeys(deck for deck, _, _, _ in items):
        entries = [
            {'w': w, 't': t, 'r': [{'l': 'Pinyin', 't': py}],
             's': strokes_of(w, graphics)}
            for deck, w, py, t in items if deck == title
        ]
        decks.append({'title': title, 'words': entries})
        cat_decks.append({'title': title, 'wordCount': len(entries),
                          'preview': [e['w'] for e in entries[:PREVIEW]]})

    pack = {'format': 1, 'id': PACK_ID, 'version': PACK_VERSION,
            'targetLang': 'zh', 'nativeLang': 'ru', 'decks': decks}
    body = json.dumps(pack, ensure_ascii=False, separators=(',', ':'))
    rel = f'packs/{PACK_ID}.json'
    os.makedirs(os.path.join(out_dir, 'packs'), exist_ok=True)
    with open(os.path.join(out_dir, rel), 'w', encoding='utf-8') as f:
        f.write(body)
    raw = body.encode()

    total = sum(d['wordCount'] for d in cat_decks)
    entry = {
        'id': PACK_ID, 'version': PACK_VERSION,
        'title': 'Chinese · HSK 1',
        'description': f'All {total} words of the new HSK 1 (2025) in '
                       f'{len(cat_decks)} topics: pinyin, Russian translations '
                       'and stroke order for every character to write by '
                       'hand. Word list: complete-hsk-vocabulary (MIT); '
                       'strokes: Make Me a Hanzi (Arphic Public License).',
        'targetLang': 'zh', 'nativeLang': 'ru', 'level': 'HSK 1',
        'wordCount': total, 'deckCount': len(cat_decks),
        'file': rel, 'bytes': len(raw),
        'sha256': hashlib.sha256(raw).hexdigest(),
        'decks': cat_decks,
    }
    cat_path = os.path.join(out_dir, 'catalog.json')
    catalog = json.load(open(cat_path, encoding='utf-8'))
    catalog['packs'] = [p for p in catalog['packs']
                        if p['id'] != PACK_ID and p['id'] not in REMOVED]
    catalog['packs'].append(entry)
    with open(cat_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=1)
    for old in REMOVED:
        path = os.path.join(out_dir, 'packs', f'{old}.json')
        if os.path.exists(path):
            os.remove(path)

    print('decks', len(decks), 'words', total, 'pack bytes', len(raw))


if __name__ == '__main__':
    main()
