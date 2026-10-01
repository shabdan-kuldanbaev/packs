# Flashcards word packs

Ready-made word packs for the Flashcards app (Library tab).

- `catalog.json` — list of packs: title, language pair, word and deck counts, per-deck preview,
  file path, size and `sha256` of the pack file. The app loads it when the Library tab opens.
- `packs/<id>.json` — the pack itself. Downloaded only when the user taps **Add**; after the import
  the words live in the app's local database and the file is not needed anymore. Related packs may
  sit in a subfolder (`packs/interview-prep/`); the app only follows the `file` path from the catalog.

## Pack format (v1)

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

## Rebuilding

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

### Topic packs from a TSV (`packs/interview-prep/`)

Hand-written word lists live in `tools/*.tsv` (group, deck, word, translation, alternatives,
example, example translation). Build one; a folder in the pack id puts the file in that subfolder
of `packs/`:

```
python3 tools/build_tsv_pack.py tools/en_js_interview_day1.tsv interview-prep/en-ru-js-interview-day1 1 \
  "JS Interview · Day 1 · Core" B2 "<description>" .
python3 tools/build_tsv_pack.py tools/interview_vocab.tsv interview-prep/en-ru-fullstack-interview-vocab 1 \
  "Full-stack Interview · Vocabulary" B2 "<description>" .
```

Accepted answers automatically include each variant without a trailing `.?!` and without a leading
article. Bump the version argument when the content changes.

- **JS Interview · Day 1 · Core** — 162 words and phrases from the Day 1 lesson, with its examples.
- **Full-stack Interview · Vocabulary** — the "Vocabulary (flashcards)" section of each of the 12
  day files of the full-stack prep plan (Google Drive › interview-prep): 128 terms and interview
  phrases, one deck per day (JS core, async JS, TypeScript, React ×2, web basics & algorithms,
  Node.js, NestJS, databases, API & security, testing & DevOps, architecture & behavioral).
  Translations by meaning; every card has an interview-style example sentence.
