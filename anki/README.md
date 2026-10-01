# Anki deck — AI-200

Two source files, ~200 cards total, tagged `ai200::<domain>` (`containers`, `data`, `integration`, `ops`):

- `ai200-basic.tsv` — Q/A + scenario cards → import with **Basic** note type
- `ai200-cloze.tsv` — command/SQL/code recall cards → import with **Cloze** note type

## Option A — import TSV (zero tooling)

1. Anki → File → Import → `ai200-basic.tsv`
2. Note type: **Basic**; field mapping: Field 1 → Front, Field 2 → Back, Field 3 → **Tags**; deck: `AI-200`; field separator: Tab; allow HTML: ✅
3. Repeat for `ai200-cloze.tsv` with note type **Cloze** (Field 1 → Text, Field 2 → Back Extra, Field 3 → Tags)

## Option B — build .apkg (nicer)

```bash
source ../.venv/bin/activate   # from repo root: source .venv/bin/activate
python build_apkg.py           # writes AI-200.apkg — double-click to import
```

## Cram-mode usage (10 days)

Normal spaced repetition won't mature before Oct 10. Use: daily due cards → then **Custom Study** on the Domain tag for the next day's lab (`ai200::data` before Oct 1–3, `ai200::integration` before Oct 4, `ai200::ops` before Oct 5, `ai200::containers` before Oct 6). After Mock 01 (Oct 7), build a filtered deck of lapsed cards and run it twice daily.
