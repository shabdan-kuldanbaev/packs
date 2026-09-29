"""Китайский пак с рукописными эталонами (формат v1 + поле "s").

python3 tools/build_zh_pack.py <graphics.txt> tools/zh_hsk1_sample.json .

graphics.txt — из Make Me a Hanzi (github.com/skishore/makemeahanzi), Arphic
Public License: tools/makemeahanzi/. В репозиторий не кладётся (30 МБ).
Берутся медианы штрихов: сетка 1024, ось y вверх со сдвигом 900 —
в клетку 0..100 приложения: x*100/1024, (900 - y)*100/1024.
Пак дописывается в catalog.json; остальные паки каталога не трогаются.
"""
import hashlib
import json
import os
import sys

PACK_ID = 'zh-ru-hsk1-sample'
PACK_VERSION = 1
PREVIEW = 12


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


def main():
    graphics = {}
    for line in open(sys.argv[1], encoding='utf-8'):
        d = json.loads(line)
        graphics[d['character']] = d['medians']
    items = json.load(open(sys.argv[2], encoding='utf-8'))
    out_dir = sys.argv[3]

    decks, cat_decks = [], []
    for title in dict.fromkeys(x['deck'] for x in items):
        words = [{'w': x['w'], 't': x['t'], 's': strokes_of(x['w'], graphics)}
                 for x in items if x['deck'] == title]
        decks.append({'title': title, 'words': words})
        cat_decks.append({'title': title, 'wordCount': len(words),
                          'preview': [w['w'] for w in words[:PREVIEW]]})

    pack = {'format': 1, 'id': PACK_ID, 'version': PACK_VERSION,
            'targetLang': 'zh', 'nativeLang': 'ru', 'decks': decks}
    body = json.dumps(pack, ensure_ascii=False, separators=(',', ':'))
    rel = f'packs/{PACK_ID}.json'
    os.makedirs(os.path.join(out_dir, 'packs'), exist_ok=True)
    with open(os.path.join(out_dir, rel), 'w', encoding='utf-8') as f:
        f.write(body)
    raw = body.encode()

    entry = {
        'id': PACK_ID, 'version': PACK_VERSION,
        'title': 'Chinese · HSK 1 sample',
        'description': 'First Chinese words to write by hand, stroke by '
                       'stroke. Russian translations. Stroke data: Make Me '
                       'a Hanzi (Arphic Public License).',
        'targetLang': 'zh', 'nativeLang': 'ru', 'level': 'HSK 1',
        'wordCount': sum(d['wordCount'] for d in cat_decks),
        'deckCount': len(cat_decks),
        'file': rel, 'bytes': len(raw),
        'sha256': hashlib.sha256(raw).hexdigest(),
        'decks': cat_decks,
    }
    cat_path = os.path.join(out_dir, 'catalog.json')
    catalog = json.load(open(cat_path, encoding='utf-8'))
    catalog['packs'] = [p for p in catalog['packs'] if p['id'] != PACK_ID]
    catalog['packs'].append(entry)
    with open(cat_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=1)

    print('decks', len(decks), 'words', entry['wordCount'],
          'pack bytes', len(raw))


if __name__ == '__main__':
    main()
