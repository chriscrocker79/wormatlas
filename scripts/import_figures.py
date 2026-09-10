#!/usr/bin/env python3
"""
import_figures.py

Imports the spreadsheet's "Figures" tab (exported as CSV) into the WormAtlas
database, into TWO tables: `figures` and `figure_entities`.

WHY TWO TABLES (the "un-merge")
-------------------------------
The Figures tab is a flat, human-friendly view of two different database tables
(see conventions.md -> "Figures tab - one spreadsheet, two tables"):

  * `figures`         holds ONE row per figure panel (the panel's content:
                      media_type, capture_technique, ai_summary, etc.).
  * `figure_entities` holds ONE row per entity visible in a panel (a panel can
                      show several entities).

So for a panel that shows three entities, the spreadsheet has three rows, but
only the FIRST carries the panel content. This script sends the first row of
each (figure_id + panel) group to `figures`, and EVERY row to `figure_entities`.

WHAT'S NEW SINCE THE AXES SPLIT
-------------------------------
Figure type is now three fields (decisions.md -> "Figure Type Axes Split"):
  media_type (required), capture_technique (N/A allowed), is_composite (0/1).
This script reads those columns. If the sheet still has the OLD single
`image_type` column instead, the script maps it automatically and warns you to
update the sheet.

KEY RULES THIS SCRIPT FOLLOWS
-----------------------------
  * N/A vs blank: an editor-typed "N/A" in any optional field becomes SQL NULL.
    A blank REQUIRED field (media_type, figure_id, panel, entity_id, visibility)
    produces a WARNING and that figure is skipped -- it does not crash the run.
  * Re-runnable: importing the same sheet again UPDATES existing rows instead of
    duplicating them (uses the UNIQUE keys on both tables).
  * Per-figure transaction: all panels + entities of one figure succeed together
    or not at all. A bad figure is rolled back and reported; the rest continue.
  * The foreign key on figure_entities.entity_id is DEFERRED (decisions.md),
    so PENDING- entity_ids are allowed and imported normally.
  * media_type / capture_technique are validated against the lookup tables
    BEFORE inserting, so you get a clear message instead of a raw FK error.

HOW TO RUN (macOS Terminal, from the project root)
--------------------------------------------------
    # 1. Install the packages (once):
    cd ~/path/to/wormatlas
    pip3 install PyMySQL python-dotenv

    # 2. Make sure your DB credentials are in the project .env (gitignored):
    #      DB_HOST=127.0.0.1
    #      DB_PORT=3306
    #      DB_NAME=wormatlas
    #      DB_USER=your_user
    #      DB_PASS=your_password

    # 3. Export the Figures tab from Google Sheets as CSV, then dry-run first
    #    (validates and reports, writes NOTHING):
    python3 scripts/import_figures.py path/to/figures.csv --dry-run

    # 4. When the dry-run looks right, import for real:
    python3 scripts/import_figures.py path/to/figures.csv

NOTE: the database schema (figures, figure_entities, and the two lookup tables)
must already exist. Run scripts/migrate_figure_type_axes.py first if it doesn't.
This script imports DATA only; it does not create tables.
"""

import argparse
import csv
import os
import sys
from collections import OrderedDict, defaultdict

try:
    import pymysql
except ImportError:
    sys.exit("PyMySQL is not installed. Run:\n    pip3 install PyMySQL python-dotenv")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# The descriptor row (row 2 of every tab) is guidance for editors, not data.
# We recognise and skip it by its figure_id cell.
DESCRIPTOR_MARKER = "Figure identifier"

# Values (lowercased) that mean "not applicable" -> stored as SQL NULL.
NA_VALUES = {"n/a", "na", "n\\a"}

# Values (lowercased) that mean "yes" for the 0/1 flag columns.
TRUE_VALUES = {"1", "yes", "y", "true", "t"}

# Fallback map if the sheet still has the OLD single image_type column.
# (media_type, capture_technique_or_None, is_composite)
LEGACY_IMAGE_TYPE_MAP = {
    "dic": ("image", "DIC", 0),
    "tem": ("image", "TEM", 0),
    "sem": ("image", "SEM", 0),
    "epifluorescent": ("image", "epifluorescent", 0),
    "confocal": ("image", "confocal", 0),
    "afm": ("image", "AFM", 0),
    "diagram": ("diagram", None, 0),
    "merged": ("image", None, 1),
}

# Panel-level columns that only the FIRST row of a (figure_id, panel) group
# carries. Kept here so the mapping to `figures` is explicit and readable.
PANEL_COLUMNS = [
    "description_in_figure", "view_orientation", "magnification",
    "source_reference", "specimen_stage", "specimen_sex", "strain",
    "image_source", "scale_bar", "media_file", "media_format",
    "duration_seconds", "poster_image", "caption_file", "transcript",
    "text_alternative", "ai_summary", "ai_answerable_questions",
]

REQUIRED_ENTITY_FIELDS = ["figure_id", "panel", "entity_id", "visibility"]


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


def as_bool(value):
    """Turn a flag cell into 0/1. Blank or unrecognised -> 0."""
    v = (value or "").strip().lower()
    return 1 if v in TRUE_VALUES else 0


def as_int_or_none(value):
    """Turn a numeric cell into int, or None if blank/N/A/non-numeric."""
    v = clean(value)
    if v is None:
        return None
    try:
        return int(float(v))
    except ValueError:
        return None


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


def column_exists(cur, table, column):
    cur.execute(
        """SELECT COUNT(*) FROM information_schema.columns
           WHERE table_schema=%s AND table_name=%s AND column_name=%s""",
        (os.environ["DB_NAME"], table, column),
    )
    return cur.fetchone()[0] > 0


def load_lookup_codes(cur, table):
    cur.execute(f"SELECT code FROM {table} WHERE active = 1")
    return {row[0] for row in cur.fetchall()}


def figures_columns(cur):
    """The columns the `figures` table actually has, so we never write to a
    column that doesn't exist (e.g. if the migration ran with --no-media-columns)."""
    cur.execute(
        """SELECT column_name FROM information_schema.columns
           WHERE table_schema=%s AND table_name='figures'""",
        (os.environ["DB_NAME"],),
    )
    return {row[0] for row in cur.fetchall()}


def preflight(cur):
    """Fail early with clear messages if the schema isn't ready."""
    for tbl in ("figures", "figure_entities", "media_types", "capture_techniques"):
        if not table_exists(cur, tbl):
            sys.exit(
                f"Required table `{tbl}` does not exist. Build the schema first:\n"
                f"    - fresh/empty database:  import scripts/create_schema.sql\n"
                f"    - existing pre-split DB: python3 scripts/migrate_figure_type_axes.py"
            )
    if not column_exists(cur, "figures", "media_type"):
        sys.exit(
            "The `figures` table exists but has no `media_type` column, so it is "
            "the OLD pre-split schema. Convert it first:\n"
            "    python3 scripts/migrate_figure_type_axes.py"
        )


# ---------------------------------------------------------------------------
# Figure-type resolution (new three-field model, with legacy fallback)
# ---------------------------------------------------------------------------

def resolve_figure_type(row, warnings):
    """
    Return (media_type, capture_technique, is_composite) for a panel row.
    Prefers the new columns; falls back to a legacy image_type column.
    """
    media_type = clean(row.get("media_type"))
    if media_type is not None:
        capture = clean(row.get("capture_technique"))       # None if N/A/blank
        is_comp = as_bool(row.get("is_composite"))
        return media_type, capture, is_comp

    # Fallback: old single image_type column still in the sheet.
    legacy = clean(row.get("image_type"))
    if legacy is not None:
        mapped = LEGACY_IMAGE_TYPE_MAP.get(legacy.lower())
        if mapped:
            warnings.append(
                f"  [legacy] {row.get('figure_id')} {row.get('panel')}: sheet still "
                f"uses image_type='{legacy}'. Mapped to media_type='{mapped[0]}'. "
                f"Please update the sheet to the media_type/capture_technique columns."
            )
            return mapped
        warnings.append(
            f"  [warn] {row.get('figure_id')} {row.get('panel')}: unknown "
            f"image_type '{legacy}' -- cannot map. Panel skipped."
        )
    return None, None, 0


# ---------------------------------------------------------------------------
# Row reading + grouping
# ---------------------------------------------------------------------------

def read_rows(csv_path):
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            if (raw.get("figure_id") or "").strip() == DESCRIPTOR_MARKER:
                continue  # skip the editor descriptor row
            if not any((v or "").strip() for v in raw.values()):
                continue  # skip fully-blank rows
            yield raw


def group_by_figure(rows):
    """OrderedDict: figure_id (str) -> list of its rows, in sheet order."""
    groups = OrderedDict()
    for row in rows:
        fid = (row.get("figure_id") or "").strip()
        groups.setdefault(fid, []).append(row)
    return groups


# ---------------------------------------------------------------------------
# Upsert one figure (all its panels + entities) in a single transaction
# ---------------------------------------------------------------------------

def entity_type_for(cur, entity_id, has_entities_table, cache, warnings):
    """Resolve figure_entities.entity_type (NOT NULL) by lookup; 'pending' if unknown."""
    if entity_id in cache:
        return cache[entity_id]
    result = "pending"
    if has_entities_table and not entity_id.startswith("PENDING-"):
        cur.execute(
            "SELECT entity_type FROM anatomical_entities WHERE entity_id=%s",
            (entity_id,),
        )
        found = cur.fetchone()
        if found and found[0]:
            result = found[0]
        else:
            warnings.append(
                f"  [pending] entity '{entity_id}' not found in anatomical_entities "
                f"yet -- entity_type set to 'pending' (fix at backfill)."
            )
    cache[entity_id] = result
    return result


def upsert_figure(conn, figure_id, rows, valid_media, valid_capture,
                  has_entities_table, existing_cols, type_cache, dry_run,
                  warnings, errors):
    cur = conn.cursor()

    # Group this figure's rows by panel; first row per panel carries content.
    panels = OrderedDict()
    for r in rows:
        panel = (r.get("panel") or "").strip()
        panels.setdefault(panel, []).append(r)

    # ---- validate before writing anything ----
    for panel, panel_rows in panels.items():
        first = panel_rows[0]
        for field in REQUIRED_ENTITY_FIELDS:
            if clean(first.get(field)) is None:
                errors.append(f"  [skip] {figure_id} panel '{panel}': missing "
                              f"required field '{field}'. Figure skipped.")
                return
        media_type, capture, _ = resolve_figure_type(first, warnings)
        if media_type is None:
            errors.append(f"  [skip] {figure_id} panel '{panel}': no media_type "
                          f"(and no mappable image_type). Figure skipped.")
            return
        if media_type not in valid_media:
            errors.append(f"  [skip] {figure_id} panel '{panel}': media_type "
                          f"'{media_type}' is not in the media_types lookup. Figure skipped.")
            return
        if capture is not None and capture not in valid_capture:
            errors.append(f"  [skip] {figure_id} panel '{panel}': capture_technique "
                          f"'{capture}' is not in the capture_techniques lookup. Figure skipped.")
            return
        for erow in panel_rows:
            if clean(erow.get("entity_id")) is None:
                errors.append(f"  [skip] {figure_id} panel '{panel}': an entity row "
                              f"has a blank entity_id. Figure skipped.")
                return

    if dry_run:
        n_panels = len(panels)
        n_entities = sum(len(pr) for pr in panels.values())
        print(f"  would import {figure_id}: {n_panels} panel(s) -> figures, "
              f"{n_entities} row(s) -> figure_entities")
        return

    # ---- write, all-or-nothing for this figure ----
    try:
        for panel, panel_rows in panels.items():
            first = panel_rows[0]
            media_type, capture, is_comp = resolve_figure_type(first, warnings)

            fields = {
                "figure_id": figure_id,
                "panel": panel,
                "media_type": media_type,
                "capture_technique": capture,
                "is_composite": is_comp,
                "autoplay": as_bool(first.get("autoplay")),
                "loops": as_bool(first.get("loops")),
                "duration_seconds": as_int_or_none(first.get("duration_seconds")),
            }
            for col in PANEL_COLUMNS:
                if col == "duration_seconds":
                    continue
                fields[col] = clean(first.get(col))

            # Only keep columns that actually exist in this database's figures
            # table (media-support columns may be absent if the migration ran
            # with --no-media-columns). figure_id/panel/media_type always exist.
            fields = {k: v for k, v in fields.items() if k in existing_cols}

            # Manual upsert on UNIQUE(figure_id, panel): SELECT then INSERT/UPDATE,
            # so we always know the integer figures.id to link entities to.
            cur.execute(
                "SELECT id FROM figures WHERE figure_id=%s AND panel=%s",
                (figure_id, panel),
            )
            existing = cur.fetchone()
            cols = list(fields.keys())
            if existing:
                figures_id = existing[0]
                assignments = ", ".join(f"{c}=%s" for c in cols if c not in ("figure_id", "panel"))
                params = [fields[c] for c in cols if c not in ("figure_id", "panel")]
                cur.execute(
                    f"UPDATE figures SET {assignments} WHERE id=%s",
                    params + [figures_id],
                )
            else:
                placeholders = ", ".join(["%s"] * len(cols))
                cur.execute(
                    f"INSERT INTO figures ({', '.join(cols)}) VALUES ({placeholders})",
                    [fields[c] for c in cols],
                )
                figures_id = cur.lastrowid

            # Every row of this panel -> figure_entities (idempotent on its UNIQUE key).
            for erow in panel_rows:
                entity_id = clean(erow.get("entity_id"))
                visibility = clean(erow.get("visibility"))
                etype = entity_type_for(cur, entity_id, has_entities_table,
                                        type_cache, warnings)
                cur.execute(
                    """
                    INSERT INTO figure_entities
                        (figure_id, entity_id, panel, visibility, entity_type)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        visibility=VALUES(visibility),
                        entity_type=VALUES(entity_type)
                    """,
                    (figures_id, entity_id, panel, visibility, etype),
                )

        conn.commit()
        print(f"  imported {figure_id}: {len(panels)} panel(s), "
              f"{sum(len(pr) for pr in panels.values())} entity row(s)")
    except Exception as exc:
        conn.rollback()
        errors.append(f"  [error] {figure_id} rolled back: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Import the Figures tab CSV.")
    parser.add_argument("csv_path", help="Path to the exported Figures tab CSV.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate and report only; write nothing.")
    args = parser.parse_args()

    if not os.path.isfile(args.csv_path):
        sys.exit(f"CSV file not found: {args.csv_path}")

    mode = "DRY RUN (nothing will be written)" if args.dry_run else "LIVE IMPORT"
    print("=" * 68)
    print(f"WormAtlas figures import -- {mode}")
    print(f"CSV: {args.csv_path}")
    print(f"Database: {os.environ.get('DB_NAME', '(unset)')} "
          f"on {os.environ.get('DB_HOST', '(unset)')}")
    print("=" * 68)

    conn = get_connection()
    warnings, errors = [], []
    type_cache = {}
    try:
        cur = conn.cursor()
        preflight(cur)
        valid_media = load_lookup_codes(cur, "media_types")
        valid_capture = load_lookup_codes(cur, "capture_techniques")
        existing_cols = figures_columns(cur)
        has_entities_table = table_exists(cur, "anatomical_entities")
        if not has_entities_table:
            warnings.append("  [note] anatomical_entities table not present -- all "
                            "figure_entities.entity_type set to 'pending'.")

        groups = group_by_figure(read_rows(args.csv_path))
        print(f"\nFound {len(groups)} figure(s) across the sheet.\n")

        for figure_id, rows in groups.items():
            upsert_figure(conn, figure_id, rows, valid_media, valid_capture,
                          has_entities_table, existing_cols, type_cache,
                          args.dry_run, warnings, errors)

        print("\n" + "-" * 68)
        if warnings:
            print(f"WARNINGS ({len(warnings)}):")
            for w in warnings:
                print(w)
        if errors:
            print(f"\nSKIPPED / ERRORS ({len(errors)}):")
            for e in errors:
                print(e)
        if not warnings and not errors:
            print("No warnings, no errors.")
        print("-" * 68)
        print("Dry run complete -- re-run without --dry-run to import."
              if args.dry_run else "Import complete.")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
