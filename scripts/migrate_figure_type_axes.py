#!/usr/bin/env python3
"""
migrate_figure_type_axes.py

One-time migration for the WormAtlas `figures` table.

WHAT THIS DOES (in plain terms)
-------------------------------
The old `figures` table stored a figure's classification in two columns that
held the SAME value on every row: `image_type` and `microscopy_technique`.
Both were MySQL/MariaDB ENUMs limited to: DIC, TEM, epifluorescent, diagram,
merged. That single list mixed three unrelated ideas together, which is why
movies, animations, 3D models and tables had nowhere to go.

Per the DECIDED decision "Figure Type Axes Split" (decisions.md, Sept 2026,
signed off by Chris Crocker), this migration replaces those two columns with:

  * media_type       -- WHAT KIND of asset it is
                        (image, diagram, table, movie, animation, interactive-3d)
  * capture_technique -- HOW it was imaged, when applicable
                        (DIC, TEM, SEM, epifluorescent, confocal, AFM; NULL = N/A)
  * is_composite      -- a yes/no flag that replaces the old "merged" value

The allowed values now live in two small "lookup tables" (media_types and
capture_techniques) instead of being baked into the column definition. A
lookup table is just a little table whose rows ARE the allowed values. Adding
a future technique (say cryo-EM) becomes inserting one row -- no schema change,
no developer migration -- which is exactly what the team asked for, because
imaging technology keeps evolving.

Section B (optional, controlled by --with-media-columns, ON by default) also
adds the columns a movie / animation / 3D model / image-only table needs in
order to be WCAG 2.1 AA compliant and actually playable:
  media_file, media_format, duration_seconds, poster_image,
  caption_file, transcript, text_alternative, autoplay, loops

IMPORTANT SAFETY NOTES
----------------------
1. Database credentials are read from ENVIRONMENT VARIABLES, never hardcoded
   (project Security decision). See the "HOW TO RUN" block below.
2. In MySQL/MariaDB, schema-changing statements (CREATE TABLE, ALTER TABLE)
   AUTO-COMMIT -- they CANNOT be rolled back. That is why:
     - `--dry-run` does not "try then undo"; it PRINTS the SQL and runs nothing.
     - the old columns are kept by default. They are only removed if you pass
       `--drop-legacy`, and only after the new columns are verified.
3. The script is idempotent: safe to run more than once. Re-running will not
   duplicate columns or lookup rows.

HOW TO RUN (macOS Terminal, from the project root)
--------------------------------------------------
    # 1. Install the two packages this script needs (do this once):
    cd ~/path/to/wormatlas
    pip3 install PyMySQL python-dotenv

    # 2. Put your DB credentials in the project's .env file (already gitignored):
    #      DB_HOST=127.0.0.1
    #      DB_PORT=3306
    #      DB_NAME=wormatlas
    #      DB_USER=your_user
    #      DB_PASS=your_password
    #    (XAMPP's default local user is usually "root" with an empty password.)

    # 3. FIRST run it as a dry run to see exactly what it will do -- changes NOTHING:
    python3 scripts/migrate_figure_type_axes.py --dry-run

    # 4. When the dry-run output looks right, run it for real:
    python3 scripts/migrate_figure_type_axes.py

    # 5. (LATER, only after you have verified the new columns in the app and
    #     re-pointed import_figures.py) remove the old columns:
    python3 scripts/migrate_figure_type_axes.py --drop-legacy
"""

import argparse
import os
import sys

try:
    import pymysql
except ImportError:
    sys.exit(
        "PyMySQL is not installed. Run this first:\n"
        "    pip3 install PyMySQL python-dotenv"
    )

# python-dotenv is optional. If present, it loads a local .env file so you do
# not have to export the variables by hand every time.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Not fatal -- we can still read real environment variables.


# ---------------------------------------------------------------------------
# The values we seed the two lookup tables with.
# Change these lists to add/retire types in the future.
# ---------------------------------------------------------------------------

# (code, label, is_time_based, is_interactive, requires_text_alternative, sort_order)
#   is_time_based            -> plays over time (needs pause/stop, reduced-motion)
#   is_interactive           -> user drives it (needs keyboard operability)
#   requires_text_alternative-> assistive tech cannot perceive it at all, so a
#                               full text equivalent MUST be stored in
#                               figures.text_alternative (this is stronger than
#                               ordinary alt text, which every image needs anyway)
MEDIA_TYPES = [
    ("image",          "Photomicrograph / still image", 0, 0, 0, 1),
    ("diagram",        "Diagram / illustration",        0, 0, 0, 2),
    ("table",          "Data table",                    0, 0, 0, 3),
    ("movie",          "Movie (recorded footage)",      1, 0, 1, 4),
    ("animation",      "Animation",                     1, 0, 1, 5),
    ("interactive-3d", "Interactive 3D model",          0, 1, 1, 6),
]

# (code, label, category, sort_order)
CAPTURE_TECHNIQUES = [
    ("DIC",            "Differential Interference Contrast", "light",         1),
    ("epifluorescent", "Epifluorescence",                    "fluorescence",  2),
    ("confocal",       "Confocal",                           "fluorescence",  3),
    ("TEM",            "Transmission Electron Microscopy",   "electron",      4),
    ("SEM",            "Scanning Electron Microscopy",       "electron",      5),
    ("AFM",            "Atomic Force Microscopy",            "scanning-probe", 6),
]

# How each OLD image_type value maps onto the THREE new fields.
#   (media_type, capture_technique_or_None, is_composite)
LEGACY_MAP = {
    "DIC":            ("image",   "DIC",            0),
    "TEM":            ("image",   "TEM",            0),
    "SEM":            ("image",   "SEM",            0),
    "epifluorescent": ("image",   "epifluorescent", 0),
    "confocal":       ("image",   "confocal",       0),
    "AFM":            ("image",   "AFM",            0),
    "diagram":        ("diagram", None,             0),
    # "merged" was never a technique -- it means "a composite panel". We record
    # that fact (is_composite=1) and leave the true technique blank for an
    # editor to fill in, because it cannot be recovered from the word "merged".
    "merged":         ("image",   None,             1),
}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def get_connection():
    """Open a DB connection using credentials from environment variables."""
    required = ["DB_HOST", "DB_NAME", "DB_USER"]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        sys.exit(
            "Missing database environment variable(s): " + ", ".join(missing) +
            "\nSet them in your .env file or export them, then re-run.\n"
            "Never hardcode credentials in this script (project Security decision)."
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


def run(cursor, sql, params=None, dry_run=False, label=None):
    """Execute one statement, or just print it in dry-run mode."""
    pretty = " ".join(sql.split())  # collapse whitespace for readable printing
    if label:
        print(f"  - {label}")
    if dry_run:
        shown = pretty if len(pretty) < 300 else pretty[:297] + "..."
        print(f"      SQL> {shown}")
        return None
    cursor.execute(sql, params or ())
    return cursor


def column_exists(cursor, table, column):
    cursor.execute(
        """SELECT COUNT(*) FROM information_schema.columns
           WHERE table_schema = %s AND table_name = %s AND column_name = %s""",
        (os.environ["DB_NAME"], table, column),
    )
    return cursor.fetchone()[0] > 0


def fk_exists(cursor, table, constraint_name):
    cursor.execute(
        """SELECT COUNT(*) FROM information_schema.table_constraints
           WHERE table_schema = %s AND table_name = %s
             AND constraint_name = %s AND constraint_type = 'FOREIGN KEY'""",
        (os.environ["DB_NAME"], table, constraint_name),
    )
    return cursor.fetchone()[0] > 0


# ---------------------------------------------------------------------------
# Migration steps
# ---------------------------------------------------------------------------

def step_create_lookup_tables(cur, dry_run):
    print("\n[1/6] Creating lookup tables (media_types, capture_techniques)...")
    run(cur, """
        CREATE TABLE IF NOT EXISTS media_types (
            code                      VARCHAR(30)  PRIMARY KEY,
            label                     VARCHAR(100) NOT NULL,
            is_time_based             TINYINT(1)   NOT NULL DEFAULT 0,
            is_interactive            TINYINT(1)   NOT NULL DEFAULT 0,
            requires_text_alternative TINYINT(1)   NOT NULL DEFAULT 0,
            sort_order                INT          NOT NULL DEFAULT 0,
            active                    TINYINT(1)   NOT NULL DEFAULT 1
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """, dry_run=dry_run, label="media_types")
    run(cur, """
        CREATE TABLE IF NOT EXISTS capture_techniques (
            code       VARCHAR(30)  PRIMARY KEY,
            label      VARCHAR(150) NOT NULL,
            category   VARCHAR(50),
            sort_order INT          NOT NULL DEFAULT 0,
            active     TINYINT(1)   NOT NULL DEFAULT 1
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """, dry_run=dry_run, label="capture_techniques")


def step_seed_lookup_tables(cur, dry_run):
    print("\n[2/6] Seeding lookup values (safe to re-run)...")
    # ON DUPLICATE KEY UPDATE makes this idempotent: re-running refreshes the
    # label/flags but never creates duplicate rows.
    for code, label, tb, inter, txt, order in MEDIA_TYPES:
        run(cur, """
            INSERT INTO media_types
                (code, label, is_time_based, is_interactive,
                 requires_text_alternative, sort_order, active)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
                label=VALUES(label), is_time_based=VALUES(is_time_based),
                is_interactive=VALUES(is_interactive),
                requires_text_alternative=VALUES(requires_text_alternative),
                sort_order=VALUES(sort_order)
        """, (code, label, tb, inter, txt, order), dry_run=dry_run,
             label=f"media_type: {code}")
    for code, label, category, order in CAPTURE_TECHNIQUES:
        run(cur, """
            INSERT INTO capture_techniques
                (code, label, category, sort_order, active)
            VALUES (%s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
                label=VALUES(label), category=VALUES(category),
                sort_order=VALUES(sort_order)
        """, (code, label, category, order), dry_run=dry_run,
             label=f"capture_technique: {code}")


def step_add_axis_columns(cur, dry_run):
    print("\n[3/6] Adding the three new columns to `figures`...")
    # MariaDB supports "ADD COLUMN IF NOT EXISTS", which keeps this idempotent.
    run(cur, """
        ALTER TABLE figures
            ADD COLUMN IF NOT EXISTS media_type VARCHAR(30) NULL AFTER description_in_figure,
            ADD COLUMN IF NOT EXISTS capture_technique VARCHAR(30) NULL AFTER media_type,
            ADD COLUMN IF NOT EXISTS is_composite TINYINT(1) NOT NULL DEFAULT 0 AFTER capture_technique
    """, dry_run=dry_run, label="media_type, capture_technique, is_composite")


def step_backfill(cur, dry_run):
    print("\n[4/6] Backfilling new columns from old image_type values...")
    if not dry_run and not column_exists(cur, "figures", "image_type"):
        print("      Old column image_type not found -- assuming already migrated. Skipping backfill.")
        return
    # Only touch rows not yet migrated (media_type still NULL), so re-runs are safe.
    for old_value, (mt, ct, comp) in LEGACY_MAP.items():
        run(cur, """
            UPDATE figures
               SET media_type = %s, capture_technique = %s, is_composite = %s
             WHERE image_type = %s AND media_type IS NULL
        """, (mt, ct, comp, old_value), dry_run=dry_run,
             label=f"map '{old_value}' -> media_type={mt}, "
                   f"capture_technique={ct or 'NULL'}, is_composite={comp}")


def step_verify_and_constrain(cur, dry_run):
    print("\n[5/6] Verifying, then locking down (NOT NULL + foreign keys)...")
    if dry_run:
        print("      (dry-run) would check for unmapped rows, then add NOT NULL + FKs.")
        run(cur, """ALTER TABLE figures MODIFY COLUMN media_type VARCHAR(30) NOT NULL""",
            dry_run=True, label="media_type NOT NULL")
        run(cur, """ALTER TABLE figures
                    ADD CONSTRAINT fk_figures_media_type
                    FOREIGN KEY (media_type) REFERENCES media_types(code)""",
            dry_run=True, label="FK figures.media_type -> media_types.code")
        run(cur, """ALTER TABLE figures
                    ADD CONSTRAINT fk_figures_capture_technique
                    FOREIGN KEY (capture_technique) REFERENCES capture_techniques(code)""",
            dry_run=True, label="FK figures.capture_technique -> capture_techniques.code")
        return

    # Safety check: no figure may be left without a media_type.
    cur.execute("SELECT COUNT(*) FROM figures WHERE media_type IS NULL")
    unmapped = cur.fetchone()[0]
    if unmapped:
        raise RuntimeError(
            f"{unmapped} figure row(s) still have NULL media_type -- an old value "
            f"was not in LEGACY_MAP. Fix the mapping before adding NOT NULL. "
            f"Nothing destructive has run."
        )

    run(cur, """ALTER TABLE figures MODIFY COLUMN media_type VARCHAR(30) NOT NULL""",
        label="media_type -> NOT NULL")

    if not fk_exists(cur, "figures", "fk_figures_media_type"):
        run(cur, """ALTER TABLE figures
                    ADD CONSTRAINT fk_figures_media_type
                    FOREIGN KEY (media_type) REFERENCES media_types(code)""",
            label="add FK figures.media_type")
    if not fk_exists(cur, "figures", "fk_figures_capture_technique"):
        run(cur, """ALTER TABLE figures
                    ADD CONSTRAINT fk_figures_capture_technique
                    FOREIGN KEY (capture_technique) REFERENCES capture_techniques(code)""",
            label="add FK figures.capture_technique")


def step_media_columns(cur, dry_run):
    print("\n[B] Adding media-support columns (movies / 3D / animations / tables)...")
    # These are what a time-based or interactive figure needs to be both
    # PLAYABLE and WCAG 2.1 AA COMPLIANT. All nullable -- a plain still image
    # simply leaves them empty.
    run(cur, """
        ALTER TABLE figures
            ADD COLUMN IF NOT EXISTS media_file       VARCHAR(255) NULL,
            ADD COLUMN IF NOT EXISTS media_format     VARCHAR(30)  NULL,
            ADD COLUMN IF NOT EXISTS duration_seconds INT          NULL,
            ADD COLUMN IF NOT EXISTS poster_image     VARCHAR(255) NULL,
            ADD COLUMN IF NOT EXISTS caption_file     VARCHAR(255) NULL,
            ADD COLUMN IF NOT EXISTS transcript       TEXT         NULL,
            ADD COLUMN IF NOT EXISTS text_alternative TEXT         NULL,
            ADD COLUMN IF NOT EXISTS autoplay         TINYINT(1)   NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS loops            TINYINT(1)   NOT NULL DEFAULT 0
    """, dry_run=dry_run,
         label="media_file, media_format, duration_seconds, poster_image, "
               "caption_file, transcript, text_alternative, autoplay, loops")


def step_report_review_rows(cur, dry_run):
    print("\n[6/6] Rows an editor must review...")
    if dry_run:
        print("      (dry-run) would list every is_composite=1 row for technique review.")
        return
    cur.execute("""
        SELECT id, figure_id, panel FROM figures
         WHERE is_composite = 1 AND (capture_technique IS NULL)
         ORDER BY figure_id, panel
    """)
    rows = cur.fetchall()
    if not rows:
        print("      None. (No composite rows need a technique filled in.)")
        return
    print("      These were old 'merged' rows. is_composite=1 was set, but the")
    print("      underlying technique(s) could not be recovered automatically and")
    print("      must be filled in by an editor (or left N/A if truly composite):")
    for _id, fig, panel in rows:
        print(f"         figures.id={_id}  {fig} panel {panel}")


def step_drop_legacy(cur, dry_run):
    print("\n[DROP] Removing the old image_type / microscopy_technique columns...")
    run(cur, """
        ALTER TABLE figures
            DROP COLUMN IF EXISTS image_type,
            DROP COLUMN IF EXISTS microscopy_technique
    """, dry_run=dry_run, label="drop image_type, microscopy_technique")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Split figure type axes migration.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the SQL and change NOTHING.")
    parser.add_argument("--drop-legacy", action="store_true",
                        help="Remove the old image_type/microscopy_technique columns. "
                             "Run this only AFTER verifying the new columns.")
    parser.add_argument("--no-media-columns", action="store_true",
                        help="Skip Section B (the movie/3D/animation support columns).")
    args = parser.parse_args()

    mode = "DRY RUN (no changes will be made)" if args.dry_run else "LIVE RUN"
    print("=" * 68)
    print(f"WormAtlas figure type axes migration -- {mode}")
    print(f"Target database: {os.environ.get('DB_NAME', '(unset)')} "
          f"on {os.environ.get('DB_HOST', '(unset)')}")
    print("=" * 68)

    conn = get_connection()
    try:
        cur = conn.cursor()

        if args.drop_legacy:
            # Destructive path is deliberately separate and explicit.
            step_drop_legacy(cur, args.dry_run)
            if not args.dry_run:
                conn.commit()
            print("\nDone. Legacy columns removed." if not args.dry_run
                  else "\nDone (dry run). Nothing was dropped.")
            return

        step_create_lookup_tables(cur, args.dry_run)
        step_seed_lookup_tables(cur, args.dry_run)
        if not args.dry_run:
            conn.commit()

        step_add_axis_columns(cur, args.dry_run)
        step_backfill(cur, args.dry_run)
        if not args.dry_run:
            conn.commit()

        step_verify_and_constrain(cur, args.dry_run)
        if not args.no_media_columns:
            step_media_columns(cur, args.dry_run)
        if not args.dry_run:
            conn.commit()

        step_report_review_rows(cur, args.dry_run)

        print("\n" + "=" * 68)
        if args.dry_run:
            print("DRY RUN complete. Re-run without --dry-run to apply.")
        else:
            print("MIGRATION complete. Old columns were KEPT.")
            print("Next: verify the new columns, update import_figures.py, then")
            print("run with --drop-legacy to remove image_type/microscopy_technique.")
        print("=" * 68)

    except Exception as exc:
        conn.rollback()  # rolls back any pending DML; DDL already auto-committed
        print(f"\nERROR: {exc}", file=sys.stderr)
        print("Any schema changes already made are NOT rolled back (DDL auto-commits "
              "in MariaDB). Read the message above, fix, and re-run -- the script is "
              "idempotent and will skip work already done.", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
