# Anki deck — AI-200

576 Notes (417 basic + 159 cloze) = 624 Cards in two TSV sources, built into one `AI-200.apkg`. Terms follow [CONTEXT.md](../CONTEXT.md): a **Note** is a TSV row, a **Card** is what Anki reviews.

- `ai200-basic.tsv` — Q/A + scenario Notes (Basic note type: Front, Back, Tags)
- `ai200-cloze.tsv` — command/SQL/code recall Notes (Cloze note type: Text, Back Extra, Tags)
- `build_apkg.py` → `AI-200.apkg` · `validate_deck.py` · `build_card_index.py` → [card-index-by-tag.md](card-index-by-tag.md) (the retake batch menu and the daily searches)

## Tags and format

- Tags: `ai200::<domain>` first (`containers`, `data`, `integration`, `ops`); cloze rows then carry `cloze`, then topic tags; `retake1` comes last on the retake batch (`mock01` marks the ten Mock-01 miss-fixers). Each retake batch starts with a banner comment `# ---------- retake batch: PREFIX (retake1) ----------`.
- Every `retake1` Note carries at least one sprint-day tag (`SPRINT_DAYS` in `validate_deck.py`, mirrored in [PLAN.md](../PLAN.md) Round 3), so each day's filtered-deck search reaches it.
- Rows have exactly 3 tab-separated fields; no field starts with `"`; cloze deletions sit side by side (`{{c1::…}}{{c2::…}}`), never nested; no `<br>`; only `b`, `i`, `code` HTML.
- A Note's identity is its text ([ADR 0002](../docs/adr/0002-content-derived-note-identity.md)): editing a Front/Back creates a new Note and leaves an Orphan after import; tag-only edits are safe.

## Check and rebuild

After any TSV change (from the repo root):

```bash
source .venv/bin/activate
python anki/validate_deck.py anki
python anki/validate_deck.py --mocks mocks/mock-02.md mocks/remediation-mock-02.md
python anki/build_apkg.py        # rewrites AI-200.apkg
python anki/build_card_index.py  # rewrites card-index-by-tag.md
```

## Import (Anki desktop)

1. File → Create Backup.
2. File → Import → `AI-200.apkg`. Notes Anki already has are matched by identity; new ones are added. In the import options (Anki 23.10+) set **Update notes → Never**: the old Notes are unchanged anyway, and updating a Note also refreshes its tags, which would drop local tags such as `leech` and `marked`.
3. Delete the Orphan (below).
4. Deck options for AI-200: new/day 15, learning steps under 1 day, leech threshold 4. FSRS: Deck options → Advanced; if it is on, set desired retention 0.92–0.93 and don't re-optimize mid-sprint.
5. Daily intake follows [PLAN.md](../PLAN.md) Round 3 (one filtered deck per day; ready-made searches in [card-index-by-tag.md](card-index-by-tag.md)). Weak-card searches: `tag:mock01`, `prop:lapses>=2`, `rated:1:1`, `tag:leech`.

Never import the TSVs into a collection that already holds the apkg: a TSV import assigns new identities and duplicates every Note. The TSV route is for a fresh collection only: File → Import → `ai200-basic.tsv` as **Basic** (Field 1 → Front, 2 → Back, 3 → Tags) and `ai200-cloze.tsv` as **Cloze** (Field 1 → Text, 2 → Back Extra, 3 → Tags), deck `AI-200`, separator Tab, allow HTML.

## Orphans

The 2026-11 apkg leaves one Orphan on top of the October one: the cloze Note "Build an image in ACR without a local Docker daemon…" (its nested cloze was fixed, so the corrected text is a new Note). In Browse, `deck:AI-200 "Build an image in ACR without a local Docker daemon"` shows two Notes; delete the one with a single Card.

After any later text edit, list Orphans by comparing the revision you last imported with the working tree (repo root, venv active):

```python
import csv, io, subprocess
from genanki.util import guid_for
OLD = "f164f6e"  # the revision you last imported (ad8f237 and 39e634c give the same result today)
rows = lambda t: [r for r in csv.reader(io.StringIO(t), delimiter="\t") if len(r) >= 3 and not r[0].startswith("#")]
sh = lambda *a: subprocess.run(a, capture_output=True, text=True, check=True).stdout
for f in ("anki/ai200-basic.tsv", "anki/ai200-cloze.tsv"):
    old = {guid_for(r[0], r[1]): r[0] for r in rows(sh("git", "show", f"{OLD}:{f}"))}
    new = {guid_for(r[0], r[1]) for r in rows(open(f, encoding="utf-8").read())}
    print(f, [t[:80] for g, t in old.items() if g not in new])
```
