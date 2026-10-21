#!/usr/bin/env python3
"""
import_entities.py

Imports the spreadsheet's "Entities" tab (exported as CSV) into the WormAtlas
database table `anatomical_entities`, then fixes the `entity_type` of any
figure_entities rows that were imported as 'pending' before their entity existed.

WHY THIS SCRIPT EXISTS
----------------------
scripts/import_figures.py imports figures, but every real entity_id in a figure
is marked entity_type='pending' until that entity exists in `anatomical_entities`
(decisions.md -> anatomical_entities Table Schema; conventions.md -> Figure
Metadata Conventions). This script loads the entities so those 'pending'
markers can be resolved.

KEY RULES THIS SCRIPT FOLLOWS (all from conventions.md / decisions.md)
----------------------------------------------------------------------
  * Row 1 is the header; row 2 is a helper row for editors ("Unique ID (e.g.,
    int1DL)"). The helper row is skipped by recognising its content, not by
    counting position. Any other row that still contains template text is
    flagged and skipped (bugs.md -> Template/header rows leaked).
  * Header names are stripped of stray spaces before matching.
  * Duplicate entity_id values in the file STOP the whole import before anything
    is written. entity_id is UNIQUE and the upsert is last-write-wins, so a
    duplicate would silently overwrite a good record (bugs.md -> Duplicate int1DL).
  * N/A and blank both become SQL NULL for optional fields. A blank REQUIRED
    field (entity_id, entity_name, entity_type, species, taxon_id, data_source,
    curator_name) skips that row with a warning; it does not crash the run.
  * Values for entity_type, developmental_stage, sex and status are checked
    against the allowed lists BEFORE inserting, for a clear message instead of
    a raw database error.
  * Stub records (status='draft', description/function/wormbase_id blank) are
    allowed (decisions.md -> Stub Entity Records Permitted).
  * Re-runnable: importing the same sheet again UPDATES rows (no duplicates).
  * One transaction per entity row: a bad row is rolled back and reported, and
    the rest continue.
  * parent_entity_id is stored as written. The self-referencing foreign key is
    DEFERRED (decisions.md -> anatomical_entities Table Schema, Correction Aug
    2026), so lineage strings or not-yet-created parents do not block the import.
    They are reported as warnings so they stay visible.

HOW TO RUN (macOS Terminal, from the project root)
--------------------------------------------------
    # 1. Install the packages (once):
    cd /Users/christophercrocker/Desktop/sites/wormatlas
    pip3 install PyMySQL python-dotenv

    # 2. Your .env must hold DB_HOST, DB_PORT, DB_NAME, DB_USER (and DB_PASS if
    #    the user has a password). Same settings import_figures.py uses.

    # 3. Export the Entities tab from Google Sheets as CSV into exports/Entities.csv

    # 4. FIRST TIME ONLY, if the table does not exist yet (the script will tell
    #    you). This creates the table exactly as logged in decisions.md:
    python3 scripts/import_entities.py exports/Entities.csv --create-table --dry-run
    python3 scripts/import_entities.py exports/Entities.csv --create-table

    # 5. Normal use: dry-run first (checks everything, writes NOTHING), then live:
    python3 scripts/import_entities.py exports/Entities.csv --dry-run
    python3 scripts/import_entities.py exports/Entities.csv

This script imports DATA (and, with --create-table, the one table). It never
alters or drops anything.
"""

import argparse
import csv
import os
import sys
from collections import Counter

try:
    import pymysql
except ImportError:
    sys.exit("PyMySQL is not installed. Run:\n    pip3 install PyMySQL python-dotenv")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Constants (kept in one place so they are easy to review against decisions.md)
# ---------------------------------------------------------------------------

# Every column written to anatomical_entities, in table order.
COLUMNS = [
    "entity_id", "entity_name", "common_name", "entity_type", "parent_entity_id",
    "wormbase_id", "species", "taxon_id", "developmental_stage", "sex",
    "description", "function", "synonyms", "location_description",
    "size_description", "primary_figures", "wormbase_url", "data_source",
    "curator_name", "status", "common_questions", "key_concepts",
]

# Columns that must have a value (NOT NULL in the schema). status defaults to draft.
REQUIRED = ["entity_id", "entity_name", "entity_type", "species", "taxon_id",
            "data_source", "curator_name"]

# decisions.md -> Extended Entity Type ENUM
ENTITY_TYPES = {
    "cell", "cell-group", "organ", "tissue", "structure", "gene", "gene-family",
    "protein", "organism", "developmental-stage", "process",
}
# decisions.md -> anatomical_entities Table Schema
DEV_STAGES = {"embryo", "L1", "L2", "L3", "L4", "dauer", "adult", "all"}
SEXES = {"hermaphrodite", "male", "both"}
STATUSES = {"draft", "review", "validated"}

# Values (lowercased) that mean "not applicable" -> stored as SQL NULL.
NA_VALUES = {"n/a", "na", "n\\a"}

# Text that only appears in the editor helper row / template (bugs.md, Aug 2026).
TEMPLATE_ENTITY_ID_PREFIX = "Unique ID"
TEMPLATE_PARENT_TEXT = "Parent structure ID"

# The table, exactly as logged in decisions.md -> anatomical_entities Table Schema.
# The parent_entity_id self-reference is intentionally NOT a foreign key (deferred).
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS anatomical_entities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity_id VARCHAR(50) NOT NULL UNIQUE,
    entity_name VARCHAR(255) NOT NULL,
    common_name VARCHAR(255),
    entity_type ENUM('cell','cell-group','organ','tissue','structure',
                      'gene','gene-family','protein','organism',
                      'developmental-stage','process') NOT NULL,
    parent_entity_id VARCHAR(50),
    wormbase_id VARCHAR(50),
    species VARCHAR(50) NOT NULL,
    taxon_id VARCHAR(50) NOT NULL,
    developmental_stage ENUM('embryo','L1','L2','L3','L4','dauer','adult','all'),
    sex ENUM('hermaphrodite','male','both'),
    description TEXT,
    `function` TEXT,
    synonyms TEXT,
    location_description TEXT,
    size_description VARCHAR(255),
    primary_figures TEXT,
    wormbase_url VARCHAR(255),
    data_source VARCHAR(100) NOT NULL,
    curator_name VARCHAR(100) NOT NULL,
    status ENUM('draft','review','validated') NOT NULL DEFAULT 'draft',
    common_questions TEXT,
    key_concepts TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_entity_id (entity_id),
    INDEX idx_entity_type (entity_type),
    INDEX idx_parent_entity_id (parent_entity_id)
)
"""

MAX_LISTED = 25  # how many items of a long warning list to print


# ---------------------------------------------------------------------------
# Value cleaning helpers
# ---------------------------------------------------------------------------

def clean(value):
    """Trim whitespace; turn '' or 'N/A' into None (SQL NULL)."""
    if value is None:
        return None
    v = value.strip()
    if v == "" or v.lower() in NA_VALUES:
        return None
    return v


# ---------------------------------------------------------------------------
# Reading and validating the CSV (no database needed for this part)
# ---------------------------------------------------------------------------

def read_rows(csv_path):
    """Return (rows, skipped_notes). Each row is a dict with stripped headers."""
    rows, notes = [], []
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        try:
            header = [h.strip() for h in next(reader)]
        except StopIteration:
            sys.exit(f"{csv_path} is empty.")
        missing = [c for c in COLUMNS if c not in header]
        if missing:
            sys.exit("The CSV is missing expected column(s): " + ", ".join(missing) +
                     "\nIs this the Entities tab export?")
        for line_no, cells in enumerate(reader, start=2):
            row = dict(zip(header, cells))
            if not any((c or "").strip() for c in cells):
                continue  # fully blank row
            ent = (row.get("entity_id") or "").strip()
            if ent.startswith(TEMPLATE_ENTITY_ID_PREFIX):
                notes.append(f"  [template] line {line_no}: helper/template row skipped.")
                continue
            if (row.get("parent_entity_id") or "").strip() == TEMPLATE_PARENT_TEXT:
                notes.append(f"  [template] line {line_no}: row '{ent}' contains template "
                             f"text and was skipped.")
                continue
            row["_line"] = line_no
            rows.append(row)
    return rows, notes


def find_duplicates(rows):
    """entity_id values that appear more than once (case-sensitive, as in the DB key)."""
    counts = Counter((r.get("entity_id") or "").strip() for r in rows)
    return sorted(e for e, n in counts.items() if e and n > 1)


def validate_row(row):
    """Return (clean_values_dict, problem_or_None) for one row."""
    values = {c: clean(row.get(c)) for c in COLUMNS}
    line = row["_line"]
    label = values["entity_id"] or "(blank entity_id)"

    for field in REQUIRED:
        if values[field] is None:
            return None, f"line {line} '{label}': missing required field '{field}'. Row skipped."

    if len(values["entity_id"]) > 50:
        return None, f"line {line} '{label}': entity_id longer than 50 characters. Row skipped."
    if values["entity_type"] not in ENTITY_TYPES:
        return None, (f"line {line} '{label}': entity_type '{values['entity_type']}' is not "
                      f"in the allowed list. Row skipped.")
    if values["developmental_stage"] is not None and values["developmental_stage"] not in DEV_STAGES:
        return None, (f"line {line} '{label}': developmental_stage "
                      f"'{values['developmental_stage']}' is not allowed. Row skipped.")
    if values["sex"] is not None and values["sex"] not in SEXES:
        return None, (f"line {line} '{label}': sex '{values['sex']}' is not allowed. Row skipped.")

    if values["status"] is None:
        values["status"] = "draft"
    elif values["status"] not in STATUSES:
        return None, (f"line {line} '{label}': status '{values['status']}' is not allowed. "
                      f"Row skipped.")
    return values, None


def check_parents(valid_rows):
    """Names used as parent_entity_id that are not an entity_id in this file."""
    ids = {v["entity_id"] for v in valid_rows}
    dangling = {}
    for v in valid_rows:
        p = v["parent_entity_id"]
        if p and p not in ids and not p.startswith("PENDING-"):
            dangling.setdefault(p, []).append(v["entity_id"])
    return dangling


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_connection():
    required = ["DB_HOST", "DB_NAME", "DB_USER"]
    missing = [n for n in required if not os.environ.get(n)]
    if missing:
        sys.exit(
            "Missing database environment variable(s): " + ", ".join(missing) +
            "\nSet them in your .env file or export them, then re-run. "
            "Never hardcode credentials (project Security decision)."
        )
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ["DB_USER"],
        password=os.environ.get("DB_PASS", ""),
        database=os.environ["DB_NAME"],
        charset="utf8mb4",
        autocommit=False,
    )


def table_exists(cur, table):
    cur.execute(
        """SELECT COUNT(*) FROM information_schema.tables
           WHERE table_schema=%s AND table_name=%s""",
        (os.environ["DB_NAME"], table),
    )
    return cur.fetchone()[0] > 0


def upsert_sql():
    cols = ", ".join(f"`{c}`" for c in COLUMNS)
    marks = ", ".join(["%s"] * len(COLUMNS))
    updates = ", ".join(f"`{c}`=VALUES(`{c}`)" for c in COLUMNS if c != "entity_id")
    return (f"INSERT INTO anatomical_entities ({cols}) VALUES ({marks}) "
            f"ON DUPLICATE KEY UPDATE {updates}")


def resolve_pending_figure_entities(cur):
    """Give figure_entities rows their real entity_type now that the entity exists.
    Returns the number of rows updated."""
    cur.execute(
        """UPDATE figure_entities fe
           JOIN anatomical_entities ae ON ae.entity_id = fe.entity_id
           SET fe.entity_type = ae.entity_type
           WHERE fe.entity_type = 'pending'"""
    )
    return cur.rowcount


def still_pending(cur):
    """Real (non-PENDING-) entity_ids in figure_entities still marked 'pending'."""
    cur.execute(
        """SELECT DISTINCT entity_id FROM figure_entities
           WHERE entity_type = 'pending' AND entity_id NOT LIKE 'PENDING-%'
           ORDER BY entity_id"""
    )
    return [r[0] for r in cur.fetchall()]


def print_limited(items, indent="    "):
    for item in items[:MAX_LISTED]:
        print(f"{indent}{item}")
    if len(items) > MAX_LISTED:
        print(f"{indent}... and {len(items) - MAX_LISTED} more")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Import the Entities tab CSV.")
    parser.add_argument("csv_path", help="Path to the exported Entities tab CSV.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate and report only; write nothing.")
    parser.add_argument("--create-table", action="store_true",
                        help="Create anatomical_entities (as logged in decisions.md) "
                             "if it does not exist yet.")
    args = parser.parse_args()

    mode = "DRY RUN (nothing will be written)" if args.dry_run else "LIVE IMPORT"
    bar = "=" * 68
    print(bar)
    print(f"WormAtlas entities import -- {mode}")
    print(f"CSV: {args.csv_path}")
    print(f"Database: {os.environ.get('DB_NAME', '(unset)')} on "
          f"{os.environ.get('DB_HOST', '(unset)')}")
    print(bar)

    # ---- 1. Read and validate the file (no database needed) ----
    rows, notes = read_rows(args.csv_path)
    for n in notes:
        print(n)
    print(f"\nRead {len(rows)} entity row(s) from the sheet.")

    dupes = find_duplicates(rows)
    if dupes:
        print("\nERROR: duplicate entity_id values found. Nothing was imported.")
        print("An import would silently overwrite one record with the other.")
        print("Fix these in the Google Sheet (sort by entity_id to see them together):")
        print_limited(dupes)
        sys.exit(1)

    valid, problems = [], []
    for row in rows:
        values, problem = validate_row(row)
        if problem:
            problems.append(f"  [skip] {problem}")
        else:
            valid.append(values)
    dangling = check_parents(valid)

    # ---- 2. Database checks ----
    conn = get_connection()
    cur = conn.cursor()

    if not table_exists(cur, "anatomical_entities"):
        if args.create_table:
            if args.dry_run:
                print("\nTable `anatomical_entities` does not exist. A live run with "
                      "--create-table would create it.")
            else:
                cur.execute(CREATE_TABLE_SQL)
                conn.commit()
                print("\nCreated table `anatomical_entities`.")
        else:
            sys.exit("\nTable `anatomical_entities` does not exist. Re-run with "
                     "--create-table (first time only).")

    existing = set()
    if table_exists(cur, "anatomical_entities"):
        cur.execute("SELECT entity_id FROM anatomical_entities")
        existing = {r[0] for r in cur.fetchall()}
    new_ids = [v["entity_id"] for v in valid if v["entity_id"] not in existing]
    upd_ids = [v["entity_id"] for v in valid if v["entity_id"] in existing]
    print(f"Valid rows: {len(valid)}  ->  {len(new_ids)} to insert, {len(upd_ids)} to update.")

    # ---- 3. Write (live only) ----
    errors = []
    written = 0
    if not args.dry_run:
        sql = upsert_sql()
        for v in valid:
            try:
                cur.execute(sql, [v[c] for c in COLUMNS])
                conn.commit()
                written += 1
            except pymysql.MySQLError as exc:
                conn.rollback()
                errors.append(f"  [error] {v['entity_id']}: {exc}")
        print(f"Wrote {written} row(s).")

        updated = resolve_pending_figure_entities(cur)
        conn.commit()
        print(f"Resolved entity_type on {updated} figure_entities row(s) that were 'pending'.")
        left = still_pending(cur)
    else:
        left = None

    # ---- 4. Report ----
    print("\n" + "-" * 68)
    if problems:
        print(f"SKIPPED ROWS ({len(problems)}):")
        for p in problems:
            print(p)
    if errors:
        print(f"DATABASE ERRORS ({len(errors)}):")
        for e in errors:
            print(e)
    if dangling:
        print(f"WARNING: {len(dangling)} parent_entity_id value(s) are not an entity_id in "
              f"this sheet (expected until the lineage cleanup in key_facts.md -> Known "
              f"Data Gaps is done):")
        print_limited([f"{p}  (used by {', '.join(users[:3])}"
                       f"{'...' if len(users) > 3 else ''})" for p, users in sorted(dangling.items())])
    if left:
        print(f"WARNING: {len(left)} real entity_id(s) in figure_entities are still "
              f"'pending' because they are not in the Entities tab:")
        print_limited(left)
    if not (problems or errors or dangling or left):
        print("No warnings, no errors.")
    print("-" * 68)
    print("Dry run complete -- re-run without --dry-run to import."
          if args.dry_run else "Import complete.")
    conn.close()
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
