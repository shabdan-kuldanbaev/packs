# Flashcards word packs

Ready-made word packs for the Flashcards app (Library tab).

- `catalog.json` — list of packs: title, language pair, word and deck counts, per-deck preview,
  file path, size and `sha256` of the pack file. The app loads it when the Library tab opens.
- `packs/<id>.json` — the pack itself. Downloaded only when the user taps **Add**; after the import
  the words live in the app's local database and the file is not needed anymore.

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
- Stroke order: [Make Me a Hanzi](https://github.com/skishore/makemeahanzi) `graphics.txt`, stroke
  medians, redistributed under the Arphic Public License — see `tools/makemeahanzi/`. The file is
  30 MB and is not stored here; download it first:

```
python3 tools/build_zh_pack.py path/to/graphics.txt tools/zh_hsk1.tsv .
```

It replaces only its own entry in `catalog.json`.
