#!/usr/bin/env python3
"""Validator for AI-200 Anki TSV decks (repo deck + retake batches).

Encodes the loader rules from anki/build_apkg.py plus the retake-batch
conventions from the handoff (section 4):

Loader rules (build_apkg.py):
  - csv.reader, tab-delimited
  - rows with <3 fields or whose first field starts with '#' are skipped

Batch rules:
  - exactly 3 fields per non-skipped row
  - no field may start with a double quote (csv.reader would strip it and
    Anki import mangles the field)
  - cloze Text uses {{cN::...}} ordinals, no nesting, no empty clozes
  - no duplicate Front (basic) / Text (cloze) across the whole corpus
  - batch rows: first tag is a domain tag ai200::{containers,data,integration,ops},
    last tag is 'retake1'
  - HTML: no <br>; only <b>, </b>, <i>, </i>, <code>, </code> tags allowed;
    a raw '<' outside those tags is an error (tag-parsing hazard in Anki);
    a raw '>' is allowed (renders literally; repo-deck KQL convention)

Usage:
  validate_deck.py REPO_DECK_DIR [BATCH_TSV...]
  validate_deck.py --mocks MOCK.md...      (mock format checks, section 6)

Exit code 0 = no issues; 1 = issues found. Prints one line per issue.
"""
import csv
import re
import sys
from pathlib import Path

DOMAIN_TAGS = {"ai200::containers", "ai200::data", "ai200::integration", "ai200::ops"}
ALLOWED_TAGS = {"<b>", "</b>", "<i>", "</i>", "<code>", "</code>"}
CLOZE_RE = re.compile(r"\{\{c(\d+)::(.+?)\}\}")


def rows_of(path: Path):
    """Yield (lineno, row) exactly as the repo loader sees them."""
    with open(path, encoding="utf-8") as f:
        for lineno, row in enumerate(csv.reader(f, delimiter="\t"), start=1):
            yield lineno, row


def check_html(path: Path, lineno: int, field: str, issues: list):
    for m in re.finditer(r"<[^>]*>", field):
        if m.group(0) not in ALLOWED_TAGS:
            issues.append(f"{path.name}:{lineno}: disallowed HTML tag {m.group(0)!r}")
    # raw '<' not part of an allowed tag parses as HTML in Anki and eats text;
    # raw '>' renders literally, so it is allowed (repo deck uses it in KQL code spans)
    stripped = field
    for tag in ALLOWED_TAGS:
        stripped = stripped.replace(tag, "")
    if "<" in stripped:
        issues.append(f"{path.name}:{lineno}: raw '<' outside allowed tags (use &lt;)")


def validate_tsvs(repo_dir: Path, batch_paths: list) -> int:
    issues: list = []
    seen: dict = {}  # front/text -> first file:lineno

    def check_file(path: Path, is_batch: bool, is_cloze: bool):
        # raw-line pass: csv.reader silently strips a leading quote, so detect
        # quoted fields before parsing (the ai200-basic.tsv:40 bug class)
        with open(path, encoding="utf-8") as raw:
            for lineno, line in enumerate(raw, start=1):
                line = line.rstrip("\n")
                if not line or line.startswith("#"):
                    continue
                if line.startswith('"') or '\t"' in line:
                    issues.append(f"{path.name}:{lineno}: field starts with a raw double quote "
                                  f"(csv.reader will mangle it)")
        for lineno, row in rows_of(path):
            if len(row) < 3 or row[0].startswith("#"):
                if len(row) not in (0,) and not row[0].startswith("#") and len(row) < 3:
                    issues.append(f"{path.name}:{lineno}: skipped by loader (<3 fields): {row!r}")
                continue
            if len(row) != 3:
                issues.append(f"{path.name}:{lineno}: {len(row)} fields, expected exactly 3")
                continue
            f1, f2, tagfield = row
            for i, fld in enumerate(row):
                if fld.startswith('"'):
                    issues.append(f"{path.name}:{lineno}: field {i} starts with a double quote")
                check_html(path, lineno, fld, issues)
            if is_cloze:
                clozes = CLOZE_RE.findall(f1)
                if not clozes:
                    issues.append(f"{path.name}:{lineno}: cloze row without any {{{{cN::}}}}")
                # nesting: a '{{' inside a cloze body
                for _, body in clozes:
                    if "{{" in body or "}}" in body:
                        issues.append(f"{path.name}:{lineno}: nested cloze in {body!r}")
                # every cloze ordinal group must be non-empty and well-formed
                if re.search(r"\{\{c\d+::\s*\}\}", f1):
                    issues.append(f"{path.name}:{lineno}: empty cloze body")
                # stray braces not part of a cloze
                leftover = CLOZE_RE.sub("", f1)
                if "{{" in leftover or "}}" in leftover:
                    issues.append(f"{path.name}:{lineno}: stray braces outside clozes: {leftover!r}")
            key = f1.strip()
            if key in seen:
                issues.append(f"{path.name}:{lineno}: duplicate of {seen[key]}")
            else:
                seen[key] = f"{path.name}:{lineno}"
            tags = tagfield.split()
            if is_batch:
                if not tags or tags[0] not in DOMAIN_TAGS:
                    issues.append(f"{path.name}:{lineno}: first tag not a domain tag: {tags[:1]}")
                if not tags or tags[-1] != "retake1":
                    issues.append(f"{path.name}:{lineno}: last tag is not 'retake1': {tags[-1:]}")

    # repo deck (baseline; known-bug rows are reported, not hidden)
    check_file(repo_dir / "ai200-basic.tsv", is_batch=False, is_cloze=False)
    check_file(repo_dir / "ai200-cloze.tsv", is_batch=False, is_cloze=True)
    for p in batch_paths:
        check_file(Path(p), is_batch=True, is_cloze="cloze" in Path(p).name)

    for i in issues:
        print(i)
    print(f"\n{len(issues)} issue(s); {len(seen)} unique notes checked")
    return 1 if issues else 0


MOCK_Q_RE = re.compile(r"^\*\*Q(\d+)\.\*\*", re.M)
MOCK_KEY_ROW_RE = re.compile(r"^\|\s*Q?(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\w+)\s*\|", re.M)
VALID_DOMAINS = {"containers", "data", "integration", "ops"}


def validate_mocks(paths: list) -> int:
    issues: list = []
    for p in paths:
        text = Path(p).read_text(encoding="utf-8")
        name = Path(p).name
        qs = [int(n) for n in MOCK_Q_RE.findall(text)]
        if qs != list(range(1, len(qs) + 1)):
            issues.append(f"{name}: question numbering gap/dup: {qs}")
        keys = {int(n): (ans.strip(), dom.strip()) for n, ans, dom in MOCK_KEY_ROW_RE.findall(text)}
        if set(keys) != set(qs):
            issues.append(f"{name}: key/table mismatch — {len(qs)} questions vs {len(keys)} key rows; "
                          f"missing keys for {sorted(set(qs) - set(keys))}")
        for n, (ans, dom) in keys.items():
            if dom not in VALID_DOMAINS:
                issues.append(f"{name}: Q{n} key domain {dom!r} not in {VALID_DOMAINS}")
            stem_start = text.find(f"**Q{n}.**")
            stem_end = text.find(f"**Q{n + 1}.**") if n < len(qs) else text.find("## Answer", stem_start)
            stem = text[stem_start:stem_end if stem_end > 0 else len(text)]
            freeform = any(m in stem for m in ("(Dropdown)", "(Fill-in)", "(Code", "(CLI", "(Free-form"))
            if "(Ordering)" in stem and "->" not in ans and "\u2192" not in ans:
                issues.append(f"{name}: Q{n} is Ordering but key {ans!r} has no arrow")
            if re.search(r"\(Select (TWO|THREE)\)", stem) and "," not in ans:
                issues.append(f"{name}: Q{n} is Select-N but key {ans!r} has no comma")
            if "(Matching)" in stem and not re.fullmatch(r"\d+-[A-Z](,\s*\d+-[A-Z])*(\s*\([A-Z](,\s*[A-Z])* unused\))?", ans):
                issues.append(f"{name}: Q{n} is Matching but key {ans!r} is not 'N-Letter' pairs")
            if not freeform and "(Ordering)" not in stem and "(Matching)" not in stem and "," not in ans:
                if not re.fullmatch(r"[A-E]|Yes|No", ans):
                    issues.append(f"{name}: Q{n} single-answer key {ans!r} is not A-E/Yes/No")
            # options referenced by the key must exist in the stem
            if not freeform and "(Matching)" not in stem and "(Ordering)" not in stem:
                for letter in re.findall(r"[A-E]", ans):
                    if f"{letter})" not in stem and f"{letter}." not in stem:
                        issues.append(f"{name}: Q{n} key references option {letter} not present in stem")
    for i in issues:
        print(i)
    print(f"\n{len(issues)} issue(s) across {len(paths)} mock file(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mocks":
        sys.exit(validate_mocks(sys.argv[2:]))
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(validate_tsvs(Path(sys.argv[1]), sys.argv[2:]))
