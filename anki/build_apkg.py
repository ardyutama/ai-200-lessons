# Builds anki/AI-200.apkg from the two TSV sources.
# Usage: python build_apkg.py   (requires: pip install genanki)
import csv, pathlib
import genanki

HERE = pathlib.Path(__file__).parent

BASIC_MODEL = genanki.Model(
    2001000001, "AI-200 Basic",
    fields=[{"name": "Front"}, {"name": "Back"}],
    templates=[{"name": "Card", "qfmt": "{{Front}}", "afmt": "{{Front}}<hr id='answer'>{{Back}}"}],
)
CLOZE_MODEL = genanki.Model(
    2001000002, "AI-200 Cloze",
    fields=[{"name": "Text"}, {"name": "Back Extra"}],
    model_type=genanki.Model.CLOZE,
    templates=[{"name": "Cloze", "qfmt": "{{cloze:Text}}", "afmt": "{{cloze:Text}}<br>{{Back Extra}}"}],
    css=".card { font-family: arial; font-size: 18px; } .cloze { font-weight: bold; color: #b02; }",
)

deck = genanki.Deck(2001000003, "AI-200")

def load(tsv, model):
    n = 0
    with open(HERE / tsv, encoding="utf-8") as f:
        for row in csv.reader(f, delimiter="\t"):
            if len(row) < 3 or row[0].startswith("#"):
                continue
            f1, f2, tags = row[0], row[1], row[2].split()
            deck.add_note(genanki.Note(model=model, fields=[f1, f2], tags=tags))
            n += 1
    print(f"{tsv}: {n} cards")

load("ai200-basic.tsv", BASIC_MODEL)
load("ai200-cloze.tsv", CLOZE_MODEL)
genanki.Package(deck).write_to_file(HERE / "AI-200.apkg")
print("Wrote AI-200.apkg — double-click to import into Anki.")
