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

## Rebuilding

```
python3 tools/build_pack.py tools/items.json tools/translations.json .
```

`tools/items.json` is the word list (deck, topic, word), `tools/translations.json` maps item id →
translation. Edit them, rebuild, bump `PACK_VERSION` in `tools/build_pack.py` when the content
changes, commit and push. Users who already added the pack keep their copy untouched.
