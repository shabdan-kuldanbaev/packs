# Jattap packs and courses

Ready-made content for the Jattap app (Flashcards).

- `catalog.json` — one list for everything ready-made:
  - `courses` — grammar courses (spec.md §29): title, `basedOn`, description in `en` and `ru`,
    level, lesson / rule / sentence counts, chapters with their lessons, file path, size and
    `sha256`. The app ships a copy of this list and of every course file in its assets
    (`assets/catalog/`, synced by `tool/sync_catalog.sh` in the app repository): the app has
    no network, so a new or updated course reaches users with the next app release.
  - `packs` — word packs from the former Library tab (removed from the app 2026-10-26). They
    stay here as files: the app still opens them via **New → Add ready-made → Choose a .json
    file**.
- `courses/<id>.json` — a course file in the app's lesson format (`format: 1`, `kind: "course"`),
  built from `courses/src/<id>/` — see below.
- `packs/<id>.json` — a word pack. Related packs may sit in a subfolder (`packs/interview-prep/`).

## Courses

### English Grammar in Use (`courses/en-ru-grammar-in-use.json`)

All 145 units of Raymond Murphy's *English Grammar in Use*, 5th edition, in the book's order,
plus 15 review lessons: 160 lessons, 469 rules, 7 355 sentences. The text is Jattap's own:
Russian explanations and freshly written practice sentences follow the units' topics, nothing is
copied from the book. Every unit is one lesson (`u12-…`); a review lesson (`r18-…`) closes a
group of units.

Source: `courses/src/en-ru-grammar-in-use/` — `course.json` (id, version, title, description,
chapters = sections of the book with their unit ranges) and ten part files, each a course file
of its own, kept small enough to edit. To change a lesson, edit its part file, then rebuild:

```
python3 tools/build_course.py courses/src/en-ru-grammar-in-use .
```

The builder concatenates the parts into `courses/<id>.json`, checks that lesson ids are unique
(the app matches lessons by id when a course is updated, keeping the learner's progress), puts
every lesson into the chapter of its unit and replaces the course's entry in `catalog.json`.
Bump `version` in `course.json` when the content changes.

The lesson format, the prompt for neural networks and the JSON schema live in the app
repository: `docs/lessons/`.

## Word packs

### Pack format (v1)

```json
{
  "format": 1, "id": "en-ru-intermediate-3000", "version": 1,
  "targetLang": "en", "nativeLang": "ru",
  "decks": [
    { "title": "01 · Appearance", "group": "People",
      "words": [ { "w": "a scar", "t": "шрам", "a": ["scar"] } ] }
  ]
}
```

`w` — word or phrase as shown on the card, `t` — translation, `a` — other accepted answers for the
typing test (synonyms split apart, variants without the article / `to`, without usage labels).

Optional, per word:

- `r` — readings, how the word sounds: `[{"l": "Pinyin", "t": "ài hào"}]`. Shown under the word,
  never accepted as an answer. `t` must be a non-empty string, `l` an optional string.
- `s` — handwriting reference to write the word by hand, in the app's own format
  `{"v":1,"c":[[[x,y,x,y,…],…],…]}`: characters → strokes → flat polyline, coordinates in a `0..100`
  cell, top-left is `0,0`.

The app rejects the whole pack if `r` or `s` is broken or `s` leaves the cell.

### Rebuilding

```
python3 tools/build_pack.py tools/items.json tools/translations.json .
```

`tools/items.json` is the word list (deck, topic, word), `tools/translations.json` maps item id →
translation. Edit them, rebuild, bump `PACK_VERSION` in `tools/build_pack.py` when the content
changes, commit and push. Users who already added the pack keep their copy untouched.

### Chinese · HSK 1

All 294 words of the new HSK 1 (2025 syllabus) in 20 topics.

- Word list: [complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary) (MIT),
  key `newest-1`.
- Topics, pinyin and Russian translations are written by hand in `tools/zh_hsk1.tsv`. The
  dataset's first reading is often a surname or a rare reading (百 Bǎi, 看 kān), so it is not used.
- Drawings are turned into a print-like (Hei) skeleton (`tools/stroke_clean.py`): the medians of a
  brush font have entry ticks, end presses, waves and a flat "foot" on 捺. Lines are simplified
  (Ramer-Douglas-Peucker, 4.0), ticks on long strokes dropped, near-horizontal (12°) / vertical (6°)
  segments snapped, the 捺 foot merged into one diagonal. Real hooks stay. Stroke order is the
  data's own — the standard one (horizontal before vertical: 十 = 一 then 丨).
- Stroke order: [Make Me a Hanzi](https://github.com/skishore/makemeahanzi) `graphics.txt`, stroke
  medians, redistributed under the Arphic Public License — see `tools/makemeahanzi/`. The file is
  30 MB and is not stored here; download it first:

```
python3 tools/build_zh_pack.py path/to/graphics.txt tools/zh_hsk1.tsv .
```

It replaces only its own entry in `catalog.json`.

### Frontend Interview · Questions (`tools/frontend_interview.tsv`)

One pack, built from a single source: the Google Doc "Frontend — interview questions (full)"
(Google Drive › interview-prep). 181 question cards in 29 decks.

- Group "Base": 67 common questions. Front: the question, back: a short spoken answer in simple English.
- Group "Senior": 114 senior deep-dive questions. Front: the question, back: the Russian gist;
  the spoken answer in simple English is the example, the gist its translation.

To update: edit the Google Doc, export it as Markdown (File › Download › Markdown), then

```
python3 tools/doc2tsv.py doc.md tools/frontend_interview.tsv
python3 tools/build_tsv_pack.py tools/frontend_interview.tsv en-ru-frontend-interview <version> \
  "Frontend Interview · Questions" C1 "<description>" .
```

`build_tsv_pack.py` reads a hand-written or generated TSV (group, deck, word, translation,
alternatives, example, example translation) and replaces only its own entry in `catalog.json`.
A folder in the pack id puts the file in that subfolder of `packs/`. Bump the version when the
content changes.
