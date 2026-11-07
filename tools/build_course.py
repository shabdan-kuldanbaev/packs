"""A ready-made course from its parts -> courses/<id>.json + its catalog.json entry.

python3 tools/build_course.py courses/src/<course id> [out_dir]

The source folder holds course.json (id, version, title, basedOn, description {en, ru},
targetLang, nativeLang, level, parts, chapters) and the part files it lists: each part is
a Jattap course file (format 1, kind "course") whose lessons are appended in order.
Lesson ids must be unique across the parts: the app finds a lesson by its id when the
course is updated, so a repeated id would merge two lessons into one.

A chapter is a section of the book: {"title": ..., "units": [first, last]}. A lesson
belongs to the chapter of its unit number, read from the id ("u19-…" or a review
"r025-…" → unit 25 → the chapter of the last unit it reviews).

Only this course's entry in catalog.json's "courses" list is replaced.
"""
import hashlib
import json
import os
import re
import sys

UNIT = re.compile(r'^[ur]0*(\d+)-')


def fail(msg):
    sys.exit(f'build_course: {msg}')


def main():
    src = sys.argv[1].rstrip('/')
    out_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    meta = json.load(open(os.path.join(src, 'course.json'), encoding='utf-8'))
    for key in ('id', 'version', 'title', 'description', 'targetLang', 'nativeLang',
                'level', 'parts', 'chapters'):
        if key not in meta:
            fail(f'course.json: no "{key}"')
    if not isinstance(meta['description'], dict) or 'en' not in meta['description']:
        fail('course.json: "description" must be {"en": ..., "ru": ...}')

    lessons, seen = [], {}
    for part in meta['parts']:
        d = json.load(open(os.path.join(src, part), encoding='utf-8'))
        if d.get('format') != 1 or d.get('kind') != 'course':
            fail(f'{part}: not a Jattap course file')
        for lesson in d['lessons']:
            if lesson['id'] in seen:
                fail(f'{part}: lesson id "{lesson["id"]}" repeats {seen[lesson["id"]]}')
            seen[lesson['id']] = part
            lessons.append(lesson)

    def chapter_of(lesson):
        m = UNIT.match(lesson['id'])
        if not m:
            fail(f'lesson "{lesson["id"]}": id must start with the unit number (u12-… / r12-…)')
        unit = int(m.group(1))
        for ch in meta['chapters']:
            first, last = ch['units']
            if first <= unit <= last:
                return ch['title']
        fail(f'lesson "{lesson["id"]}": unit {unit} is in no chapter')

    chapters = []
    for ch in meta['chapters']:
        entry = {'title': ch['title'], 'lessons': []}
        chapters.append(entry)
    by_title = {c['title']: c for c in chapters}
    for lesson in lessons:
        row = {'id': lesson['id'], 'title': lesson['title']}
        if lesson.get('subtitle'):
            row['subtitle'] = lesson['subtitle']
        by_title[chapter_of(lesson)]['lessons'].append(row)
    empty = [c['title'] for c in chapters if not c['lessons']]
    if empty:
        fail(f'chapters without lessons: {empty}')

    course = {
        'format': 1, 'kind': 'course', 'id': meta['id'], 'title': meta['title'],
        'targetLang': meta['targetLang'], 'nativeLang': meta['nativeLang'],
        'level': meta['level'], 'lessons': lessons,
    }
    body = json.dumps(course, ensure_ascii=False, separators=(',', ':'))
    rel = f'courses/{meta["id"]}.json'
    os.makedirs(os.path.join(out_dir, 'courses'), exist_ok=True)
    with open(os.path.join(out_dir, rel), 'w', encoding='utf-8') as f:
        f.write(body)
    raw = body.encode()

    points = [p for l in lessons for p in l['points']]
    sentences = sum(len(p.get('practice', [])) + len(p.get('review', [])) for p in points)
    entry = {
        'id': meta['id'], 'version': int(meta['version']), 'title': meta['title'],
        'basedOn': meta.get('basedOn'), 'description': meta['description'],
        'targetLang': meta['targetLang'], 'nativeLang': meta['nativeLang'],
        'level': meta['level'], 'lessonCount': len(lessons), 'ruleCount': len(points),
        'sentenceCount': sentences, 'file': rel, 'bytes': len(raw),
        'sha256': hashlib.sha256(raw).hexdigest(), 'chapters': chapters,
    }
    if entry['basedOn'] is None:
        del entry['basedOn']
    cat_path = os.path.join(out_dir, 'catalog.json')
    catalog = json.load(open(cat_path, encoding='utf-8'))
    courses = [c for c in catalog.get('courses', []) if c['id'] != meta['id']]
    catalog['courses'] = courses + [entry]
    with open(cat_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=1)
    print('lessons', len(lessons), 'rules', len(points), 'sentences', sentences,
          'bytes', len(raw))


if __name__ == '__main__':
    main()
