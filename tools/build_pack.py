"""items + собственные переводы -> catalog.json + packs/<id>.json (формат v1)."""
import hashlib
import itertools
import json
import os
import re
import sys

PACK_ID = 'en-ru-intermediate-3000'
PACK_VERSION = 1
PREVIEW = 12

CYR = re.compile(r'[А-Яа-яЁё]')
ARTICLE = re.compile(r'^(a|an|the|to)\s+', re.I)

def strip_parens(s):
    s = re.sub(r'\s+', ' ', re.sub(r'\([^)]*\)?', ' ', s)).strip()
    return re.sub(r'\s+([,.?!/])', r'\1', s)


def split_top(s, sep):
    return [x.strip() for x in s.split(sep) if x.strip()]


def expand_slashes(phrase):
    """«to lock/unlock one's phone» -> два варианта; не больше 8 комбинаций."""
    tokens = phrase.split(' ')
    choices = [t.split('/') if '/' in t.strip('/') and
               all(len(x) > 1 for x in t.split('/')) else [t] for t in tokens]
    n = 1
    for c in choices:
        n *= len(c)
    if n == 1 or n > 8:
        return [phrase]
    return [' '.join(c) for c in itertools.product(*choices)]


def answers(word):
    """Допустимые ответы при вводе (кроме самого word)."""
    base = strip_parens(word)
    variants = []
    sentence = bool(re.search(r'[.?!]$', base)) or (
        base[:1].isupper() and len(base.split()) > 4)
    for part in ([base] if sentence else split_top(base, ',')):
        for sub in split_top(part, ' / '):
            variants.extend(expand_slashes(sub))
    if len(variants) > 1 or base != word:
        variants.append(base)
    out = []
    for v in variants:
        v = v.strip()
        for cand in (v, re.sub(r'[.?!…]+$', '', v)):
            for c in (cand, ARTICLE.sub('', cand)):
                c = c.strip()
                if c and c != word and c not in out and not CYR.search(c):
                    out.append(c)
    return out


def main():
    """python build_pack.py <items.json> <translations.json> <out_dir>"""
    items = json.load(open(sys.argv[1]))
    tr = json.load(open(sys.argv[2]))
    out_dir = sys.argv[3]
    groups = {}
    for x in items:
        groups[x['deck']] = (x['group'], x['topic'])

    decks, cat_decks = [], []
    for n in sorted(groups):
        group, topic = groups[n]
        words = []
        for x in items:
            if x['deck'] != n:
                continue
            w = {'w': x['w'], 't': tr[str(x['i'])]}
            a = answers(x['w'])
            if a:
                w['a'] = a
            words.append(w)
        title = f"{n:02d} · {topic}"
        decks.append({'title': title, 'group': group, 'words': words})
        cat_decks.append({
            'title': title, 'group': group, 'wordCount': len(words),
            'preview': [x['w'] for x in words[:PREVIEW]],
        })

    pack = {'format': 1, 'id': PACK_ID, 'version': PACK_VERSION,
            'targetLang': 'en', 'nativeLang': 'ru', 'decks': decks}
    body = json.dumps(pack, ensure_ascii=False, separators=(',', ':'))
    os.makedirs(os.path.join(out_dir, 'packs'), exist_ok=True)
    rel = f'packs/{PACK_ID}.json'
    with open(os.path.join(out_dir, rel), 'w') as f:
        f.write(body)
    raw = body.encode()

    total = sum(d['wordCount'] for d in cat_decks)
    catalog = {'format': 1, 'packs': [{
        'id': PACK_ID, 'version': PACK_VERSION,
        'title': 'English 3000 · Intermediate',
        'description': '3000 words and phrases for the Intermediate level: '
                       f'{len(cat_decks)} topics in 12 chapters. '
                       'Russian translations.',
        'targetLang': 'en', 'nativeLang': 'ru', 'level': 'B1',
        'wordCount': total, 'deckCount': len(cat_decks),
        'file': rel, 'bytes': len(raw),
        'sha256': hashlib.sha256(raw).hexdigest(),
        'decks': cat_decks,
    }]}
    with open(os.path.join(out_dir, 'catalog.json'), 'w') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=1)

    print('decks', len(decks), 'words', total, 'pack bytes', len(raw),
          'catalog bytes', os.path.getsize(os.path.join(out_dir, 'catalog.json')))
    with_a = sum(1 for d in decks for w in d['words'] if 'a' in w)
    print('with alternatives', with_a)


if __name__ == '__main__':
    main()
