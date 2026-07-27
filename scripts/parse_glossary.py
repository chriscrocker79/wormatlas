"""
parse_glossary.py
Extract a structured inventory from the wormatlas.org glossary HTML pages
so an editor can classify which terms become new entity records.

This is step 1 (the "inventory pass") of the glossary backfill described in
decisions.md -> "Glossary Entity Backfill Runs in Parallel with Figure
Cataloguing". It does the MECHANICAL extraction only. It never decides what
is or is not an entity, and it never invents an entity_id -- it reports the
glossary anchor slug as the entity_id candidate per decisions.md ->
"entity_id Construction for Non-Cell Entities - Glossary Anchor Slug".

What it produces: one CSV with a row for every glossary term, with the
machine-extractable columns filled in and the human-judgment columns left
blank for an editor to complete.

Usage:
    python3 scripts/parse_glossary.py \
        --glossary-dir glossary_html \
        --entities entities_export.csv \
        --output glossary_inventory.csv

--entities is optional. If you leave it off, the "already_in_entities"
column is filled with UNKNOWN instead of TRUE/FALSE.
"""

import argparse
import csv
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup


# The entity_type ENUM as decided in decisions.md -> "Extended Entity Type
# ENUM". Used only to skip the spreadsheet's row-2 helper row when reading
# the existing Entities export (per conventions.md -> Spreadsheet Import
# Scripts: validate the row, don't count its position).
VALID_ENTITY_TYPES = {
    "cell", "cell-group", "organ", "tissue", "structure",
    "gene", "gene-family", "protein", "organism",
    "developmental-stage", "process",
}

# Column headers for the output inventory. The first block is filled in by
# this script; the second block is left blank for the editor to complete.
OUTPUT_COLUMNS = [
    # --- machine-extracted ---
    "source_page",
    "anchor",                     # entity_id candidate (the <a name="..."> value)
    "anchor_malformed_flag",      # TRUE if the anchor is not clean lowercase a-z0-9
    "cross_page_anchor_collision",  # TRUE if this anchor also appears on another page
    "term",                       # display name of the glossary term
    "abbreviation_or_cellname",   # column 2, non-synonym lines
    "synonyms_S",                 # column 2 lines marked "(S)"
    "lineage",                    # column 3
    "description",                # column 4 prose, so editors classify in-spreadsheet
    "has_wbbt_id",                # TRUE if a WormBase WBbt link is present
    "wbbt_ids",                   # the WBbt IDs found, if any
    "cross_reference_candidate",  # TRUE if the description is only a "See X" pointer
    "already_in_entities",        # TRUE / FALSE / UNKNOWN
    "match_basis",                # how the "already_in_entities" match was made
    # --- editor fills these in ---
    "is_entity",                  # editor: yes / no
    "proposed_entity_type",       # editor: one of the ENUM values
    "ambiguous_flag",             # editor: yes if unsure
    "editor_notes",               # editor: free text
]


def read_html_file(path):
    """Read a glossary HTML file, tolerating its old Latin-1 encoding.

    The pages declare charset=iso-8859-1. We try UTF-8 first (in case a file
    was re-saved) and fall back to Latin-1, which can decode any byte.
    """
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def get_page_letter(filename):
    """Work out which glossary letter a file represents, from its name.

    Handles names like 'WA_glossary_A.txt', 'aglossary.htm', 'glossary_b.html'.
    Falls back to the file's stem if no single letter can be found.
    """
    stem = Path(filename).stem
    match = re.search(r"glossary[_\s]*([A-Za-z])\b", stem, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    match = re.search(r"\b([A-Za-z])[_\s]*glossary", stem, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return stem


def clean_text(node, separator=" "):
    """Return normalized visible text from a BeautifulSoup node."""
    if node is None:
        return ""
    text = node.get_text(separator=separator)
    text = text.replace("\xa0", " ")          # &nbsp; -> normal space
    if separator == "\n":
        # collapse spaces within each line, keep line breaks
        lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
        return "\n".join(ln for ln in lines if ln)
    return re.sub(r"\s+", " ", text).strip()


def get_lines(node):
    """Return the visible text of a node as a list of logical lines.

    Logical line breaks come only from <br> and </p> tags. The source HTML
    wraps text mid-sentence across many lines, so we must NOT treat source
    newlines as line breaks (that would split "See Anchor cell" into three
    lines). We convert <br> and </p> to sentinels, then split on those.
    """
    if node is None:
        return []
    inner_html = node.decode_contents()
    inner_html = re.sub(r"(?i)<br\s*/?>", "\n", inner_html)
    inner_html = re.sub(r"(?i)</p>", "\n", inner_html)
    fragment = BeautifulSoup(inner_html, "html.parser")
    text = fragment.get_text(separator=" ").replace("\xa0", " ")
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            lines.append(line)
    return lines


def is_data_row(tds):
    """A glossary data row has 4 columns and an <a name> anchor in column 1."""
    if len(tds) < 4:
        return False
    return tds[0].find("a", attrs={"name": True}) is not None


def get_anchor(first_td):
    """Return the anchor slug from a row's first cell (the entity_id candidate)."""
    tag = first_td.find("a", attrs={"name": True})
    if tag and tag.get("name"):
        return tag["name"].strip()
    tag = first_td.find("a", attrs={"id": True})
    if tag and tag.get("id"):
        return tag["id"].strip()
    return ""


def anchor_is_malformed(anchor):
    """Flag anchors that are not clean lowercase letters/digits.

    This catches things like 'ACVUdecison' (uppercase + typo). It cannot
    catch an all-lowercase typo -- that is what editor review in step 1 is
    for -- but it surfaces the obvious cases per decisions.md clarification 1.
    """
    if not anchor:
        return True
    return not re.fullmatch(r"[a-z0-9]+", anchor)


def split_column_two(lines):
    """Split column 2 into (abbreviation/cell name, synonyms, antonyms).

    Lines marked '(S)' are synonyms; lines marked '(A)' are antonyms;
    anything else is treated as the abbreviation or cell name.
    """
    abbreviations, synonyms, antonyms = [], [], []
    for line in lines:
        if re.search(r"\(S\)\s*$", line):
            synonyms.append(re.sub(r"\s*\(S\)\s*$", "", line).strip())
        elif re.search(r"\(A\)\s*$", line):
            antonyms.append(re.sub(r"\s*\(A\)\s*$", "", line).strip())
        else:
            abbreviations.append(line)
    return " | ".join(abbreviations), " | ".join(synonyms), " | ".join(antonyms)


def find_wbbt_ids(row):
    """Return any WormBase WBbt anatomy-term IDs referenced anywhere in the row."""
    return sorted(set(re.findall(r"WBbt:\d+", str(row))))


def find_cell_names(row):
    """Return any WormBase cell names referenced via cell.cgi?name= links."""
    return sorted(set(re.findall(r"cell\.cgi\?name=([^;&\"]+)", str(row))))


def is_cross_reference(description_lines):
    """True if the description is only a 'See X' pointer, not a real definition."""
    if not description_lines:
        return False
    return description_lines[0].lower().startswith("see ")


def load_existing_entities(csv_path):
    """Load the Entities export into lookup sets for the 'already exists' check.

    Skips the row-2 helper row (and any junk) by requiring a valid entity_type,
    per conventions.md -> Spreadsheet Import Scripts.
    Returns a dict of sets, or None if no path was given.
    """
    if csv_path is None:
        return None

    path = Path(csv_path)
    if not path.exists():
        sys.exit(f"ERROR: entities file not found: {path}")

    wbbt_ids, entity_ids, entity_names = set(), set(), set()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for record in reader:
            entity_type = (record.get("entity_type") or "").strip()
            if entity_type not in VALID_ENTITY_TYPES:
                continue  # skips the helper row and any blank/invalid rows
            wbbt = (record.get("wormbase_id") or "").strip()
            if wbbt:
                wbbt_ids.add(wbbt)
            entity_id = (record.get("entity_id") or "").strip()
            if entity_id:
                entity_ids.add(entity_id.lower())
            name = (record.get("entity_name") or "").strip()
            if name:
                entity_names.add(name.lower())
    return {"wbbt": wbbt_ids, "ids": entity_ids, "names": entity_names}


def match_existing(existing, anchor, term, wbbt_ids, cell_names, abbreviation):
    """Decide whether this glossary term already has a record, and how it matched."""
    if existing is None:
        return "UNKNOWN", ""

    if set(wbbt_ids) & existing["wbbt"]:
        return "TRUE", "wormbase_id"
    if anchor.lower() in existing["ids"]:
        return "TRUE", "entity_id == anchor"

    candidate_names = [name.strip().lower() for name in cell_names]
    candidate_names += [
        part.strip().lower()
        for part in re.split(r"[|,/]", abbreviation)
        if part.strip()
    ]
    for candidate in candidate_names:
        if candidate and candidate in existing["ids"]:
            return "TRUE", "entity_id == cell name"
    if term.lower() in existing["names"]:
        return "TRUE", "entity_name"
    return "FALSE", ""


def parse_page(path, existing):
    """Parse one glossary HTML file into a list of inventory row dicts."""
    letter = get_page_letter(path.name)
    soup = BeautifulSoup(read_html_file(path), "html.parser")
    rows = []

    for tr in soup.find_all("tr"):
        tds = tr.find_all("td", recursive=False)
        if not is_data_row(tds):
            continue

        anchor = get_anchor(tds[0])

        # Column 1 term name, minus the empty anchor element's text.
        term = clean_text(tds[0])

        col2_lines = get_lines(tds[1])
        abbreviation, synonyms, antonyms = split_column_two(col2_lines)

        lineage = clean_text(tds[2])
        description_lines = get_lines(tds[3])
        description = " ".join(description_lines)

        wbbt_ids = find_wbbt_ids(tr)
        cell_names = find_cell_names(tr)

        already, basis = match_existing(
            existing, anchor, term, wbbt_ids, cell_names, abbreviation
        )

        rows.append({
            "source_page": letter,
            "anchor": anchor,
            "anchor_malformed_flag": "TRUE" if anchor_is_malformed(anchor) else "FALSE",
            "cross_page_anchor_collision": "FALSE",  # filled in later, across all pages
            "term": term,
            "abbreviation_or_cellname": abbreviation,
            "synonyms_S": synonyms,
            "lineage": lineage,
            "description": description,
            "has_wbbt_id": "TRUE" if wbbt_ids else "FALSE",
            "wbbt_ids": " | ".join(wbbt_ids),
            "cross_reference_candidate": "TRUE" if is_cross_reference(description_lines) else "FALSE",
            "already_in_entities": already,
            "match_basis": basis,
            "is_entity": "",
            "proposed_entity_type": "",
            "ambiguous_flag": "",
            "editor_notes": "",
        })
    return rows


def flag_cross_page_collisions(rows):
    """Mark anchors that appear on more than one glossary page.

    entity_id must be globally unique (it is the join key), but glossary
    anchors are only guaranteed unique within a single letter page --
    decisions.md clarification 3.
    """
    seen_pages = {}
    for row in rows:
        seen_pages.setdefault(row["anchor"], set()).add(row["source_page"])
    collisions = {anchor for anchor, pages in seen_pages.items() if len(pages) > 1}
    for row in rows:
        if row["anchor"] in collisions:
            row["cross_page_anchor_collision"] = "TRUE"
    return collisions


def write_inventory(rows, output_path):
    """Write the inventory rows to a CSV file."""
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(rows, collisions, wrote_to):
    """Print a plain-language summary of what was found."""
    total = len(rows)
    already = sum(1 for r in rows if r["already_in_entities"] == "TRUE")
    unknown = sum(1 for r in rows if r["already_in_entities"] == "UNKNOWN")
    new_candidates = sum(1 for r in rows if r["already_in_entities"] == "FALSE")
    cross_refs = sum(1 for r in rows if r["cross_reference_candidate"] == "TRUE")
    malformed = sum(1 for r in rows if r["anchor_malformed_flag"] == "TRUE")

    print("")
    print("Glossary inventory complete.")
    print(f"  Total glossary terms found:        {total}")
    print(f"  Already in Entities tab:           {already}")
    if unknown:
        print(f"  Match status UNKNOWN (no --entities): {unknown}")
    print(f"  New-entity candidates (not found): {new_candidates}")
    print(f"  'See X' cross-reference candidates: {cross_refs}")
    print(f"  Malformed anchors to review:       {malformed}")
    print(f"  Cross-page anchor collisions:      {len(collisions)}")
    if collisions:
        print(f"    -> {', '.join(sorted(collisions))}")
    print("")
    print(f"Wrote: {wrote_to}")
    print("Next: an editor fills in is_entity, proposed_entity_type, and")
    print("ambiguous_flag. The script has intentionally left those blank.")


def main():
    parser = argparse.ArgumentParser(
        description="Extract an inventory from wormatlas.org glossary HTML pages."
    )
    parser.add_argument(
        "--glossary-dir", required=True,
        help="Folder containing the glossary HTML files (one per letter).",
    )
    parser.add_argument(
        "--entities", default=None,
        help="Optional CSV export of the Entities tab, for the 'already exists' check.",
    )
    parser.add_argument(
        "--output", default="glossary_inventory.csv",
        help="Where to write the inventory CSV (default: glossary_inventory.csv).",
    )
    args = parser.parse_args()

    glossary_dir = Path(args.glossary_dir)
    if not glossary_dir.is_dir():
        sys.exit(f"ERROR: glossary folder not found: {glossary_dir}")

    files = sorted(
        p for p in glossary_dir.iterdir()
        if p.suffix.lower() in {".htm", ".html", ".txt"}
    )
    if not files:
        sys.exit(f"ERROR: no .htm/.html/.txt files found in {glossary_dir}")

    existing = load_existing_entities(args.entities)

    all_rows = []
    for path in files:
        page_rows = parse_page(path, existing)
        print(f"  parsed {path.name}: {len(page_rows)} terms")
        all_rows.extend(page_rows)

    collisions = flag_cross_page_collisions(all_rows)

    output_path = Path(args.output)
    write_inventory(all_rows, output_path)
    print_summary(all_rows, collisions, output_path)


if __name__ == "__main__":
    main()
