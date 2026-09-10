# WormAtlas Coding Conventions

## How to Use This File
Before writing or reviewing any code, check this file. All code produced
for this project must follow these conventions. Consistency across a
9-month multi-person project depends on these rules being applied every
time without exception.

---

## GENERAL CODING PRINCIPLES

- Clarity over cleverness — code must be readable by someone unfamiliar
  with the codebase
- Every function does one thing only
- Name things clearly and explicitly — avoid abbreviations
- No dead code committed — remove it, never comment it out
- Fail loudly in development, gracefully in production
- No secrets, API keys, or credentials ever written into code files

---

## TERMINAL & COMMAND LINE

- Operating system: macOS
- Shell: zsh (Mac default since macOS Catalina)
- Preferred terminal: VS Code integrated terminal (View → Terminal)
- Always use python3, never python
- Always use pip3, never pip
- Always confirm working directory before running scripts using: pwd
- Always show the full Terminal command including which directory
  to be in before running it
- Never assume a Python package is installed — always show the
  pip3 install command first
- XAMPP install location on Mac: /Applications/XAMPP/
- XAMPP start via Terminal if needed:
  sudo /Applications/XAMPP/xamppfiles/xampp start
- Dev server path: /var/www/dev.wormatlas.org/html/
- Production server path: /var/www/wormatlas.org/html/

---

## GIT VERSION CONTROL

### Branch Naming
```
feature/short-description    → new functionality
fix/short-description        → bug fix
chore/short-description      → tooling or config changes
docs/short-description       → documentation only
a11y/short-description       → accessibility-specific fixes
rag/short-description        → AI/RAG pipeline work
```

### Commit Message Format
```
type(scope): short description (max 72 characters)

Optional: longer explanation of WHY, not what.
```

Types: feat, fix, docs, style, refactor, chore, a11y, rag

### Examples
```
feat(intestine-page): add entity markup to cell list
fix(wormbase-urls): correct missing IDs for 10 cells
a11y(nav): fix dropdown overflow on small screens
rag(embeddings): add ChromaDB indexing for nervous system cells
docs(decisions): log REST API decision
```

### Rules
- Never commit directly to main
- All work done on a branch, merged via pull request
- No console.log or debug print statements committed
- No API keys or secrets ever committed — use environment variables

---

## PHP

- File names: snake_case (e.g., database_connection.php)
- Function names: snake_case (e.g., get_entity_by_id())
- Class names: PascalCase (e.g., DatabaseConnection)
- All PHP files begin with <?php — no closing ?> tag at end of file
- All files begin with a standard header comment block:
  ```php
  <?php
  /**
   * [filename].php
   * [One line description of what this file does]
   *
   * Part of the WormAtlas CMS
   * wormatlas.org
   */
  ```
- Use prepared statements for all database queries — never
  concatenate user input directly into SQL
- No ORM layer — PHP prepared statements only
- Indentation: 4 spaces (not tabs)

---

## MYSQL / DATABASE

- The production database is MariaDB 10.5.29, not MySQL.
  MariaDB is a MySQL-compatible fork. All standard MySQL syntax,
  prepared statements, and data types work without modification.
  If a MySQL-specific feature is ever needed, verify MariaDB
  compatibility before using it. Do not assume parity for
  advanced or edge-case features.
- Table names: plural, lowercase, snake_case
  (e.g., anatomical_entities, article_figures)
- Primary keys: always named id, always INT AUTO_INCREMENT
- Foreign keys: [table_singular]_id (e.g., article_id, entity_id)
- Timestamps: use created_at and updated_at consistently
- updated_at always includes: ON UPDATE CURRENT_TIMESTAMP
- String fields: use VARCHAR for short strings, TEXT for long content,
  LONGTEXT for full article bodies
- Enums: use for fixed-value fields
  (e.g., status, entity_type, relationship_type)
- All tables must have indexes on frequently queried columns
- All foreign keys must have corresponding INDEX entries

---

## REST API

- All endpoints versioned: /api/v1/...
- All responses use this consistent envelope:
  ```json
  {
    "data": { },
    "meta": { "total": 100, "page": 1 },
    "error": null
  }
  ```
- Pagination required on all list endpoints — no unbounded queries
- HTTP status codes used correctly (200, 201, 400, 401, 404, 500)
- All error responses include:
  - message: human-readable explanation
  - code: machine-readable error identifier

---

## HTML

- All HTML must be semantically correct
- Use article, section, nav, header, footer appropriately
- Every image must have a descriptive alt attribute
  Exception: purely decorative images use alt=""
- All interactive elements must be keyboard-accessible
- Page-level metadata stored in data attributes on the main
  article element:
  ```html
  <article
    data-content-id="elegans-h-intestine"
    data-content-type="anatomical-handbook"
    data-species="c-elegans"
    data-sex="hermaphrodite"
    data-system="alimentary"
    data-subsystem="intestine">
  ```

---

## HTML DATA ATTRIBUTES (Entity Markup)

These attribute names are fixed — never invent alternatives:

- Entity identification: data-entity-id
- WormBase linking: data-wormbase-id
- Entity classification: data-entity-type
- Taxon identification: data-taxon-id
- Parent entity: data-parent

Example of correct entity markup:
```html
<span
  class="entity cell"
  data-entity-id="int1DL"
  data-wormbase-id="WBbt:0004361"
  data-entity-type="cell"
  data-taxon-id="NCBITaxon:6239"
  data-parent="int-ring-I">
  int1DL
</span>
```

---

## CSS

- Class names: kebab-case (e.g., .entity-card, .figure-legend)
- Entity classes follow the pattern: .entity.[type]
  (e.g., .entity.cell, .entity.gene, .entity.organ)
- No inline styles — all styles in external CSS files
- Mobile-first: write base styles for small screens,
  use min-width media queries to scale up
- CSS custom properties (variables) used for all colors and
  repeated values

---

## JAVASCRIPT

- Variable and function names: camelCase
- Constants: UPPER_SNAKE_CASE
- No inline JavaScript in HTML files — all JS in external files
- Use addEventListener, never inline onclick attributes in HTML

---

## PYTHON

- File names: snake_case (e.g., prepare_rag.py, validate_urls.py)
- Function names: snake_case
- Class names: PascalCase
- All scripts begin with a docstring explaining purpose and usage:
  ```python
  """
  [script_name].py
  [What this script does]

  Usage: python3 scripts/[script_name].py
  """
  ```
- All file paths use Python's pathlib.Path, not string concatenation
- All API keys loaded from environment variables, never hardcoded

## EMBEDDINGS (VOYAGE AI)

- Model name loaded from environment variable: VOYAGE_MODEL
  Never hardcode the model name string in any script
- API key loaded from environment variable: VOYAGE_API_KEY
- Always pass input_type explicitly — never omit it:
  - input_type="document" when embedding content for the index
  - input_type="query" when embedding a user search query
- All embedding calls wrapped in try/except — the API is external
  and must fail gracefully in production
- ChromaDB collection names follow the pattern:
  wormatlas_[system]_[model_slug]
  e.g. wormatlas_nervous_voyage35
- The re-indexing script (scripts/reindex_embeddings.py) is the
  single source of truth for all indexing operations —
  never embed content inline in other scripts

---

## SECURITY

- No secrets, API keys, or credentials committed to the repository — ever
- All secrets stored in environment variables
- All user inputs validated and sanitized server-side
- CORS policy explicitly configured — no wildcard * in production
- Permitted CORS origins: https://wormatlas.org and
  https://dev.wormatlas.org only
- CMS login authentication only — all research content is publicly
  accessible without login

---

## FILE & FOLDER STRUCTURE

```
wormatlas_project/
├── docs/
│   └── project_notes/
│       ├── decisions.md
│       ├── bugs.md
│       ├── key_facts.md
│       └── conventions.md
├── public/
│   ├── index.php
│   ├── css/
│   ├── js/
│   └── uploads/
├── admin/
│   ├── login.php
│   ├── dashboard.php
│   └── manage-articles.php
├── includes/
│   ├── Database.php
│   ├── Auth.php
│   └── functions.php
├── config/
│   └── database.php
├── scripts/
│   ├── prepare_rag.py
│   ├── validate_urls.py
│   └── import_to_database.py
├── content/
│   └── [HTML handbook pages]
└── rag_data/
    └── chromadb/
```
- Dev server path: /var/www/dev.wormatlas.org/html/
- Production server path: /var/www/wormatlas.org/html/

---

## SCIENTIFIC CONTENT CONVENTIONS

- Species names always italicized: <em>C. elegans</em>
- WormBase IDs never invented or assumed — always verified
- Entity IDs match the Google Sheets spreadsheet exactly
  (e.g., int1DL not Int1DL or int-1-DL)
- Organism entities: entity_id = the established species slug — the same
  value used in the `species` column and the `data-species` attribute
  (e.g. c-elegans, p-pacificus, s-stercoralis). One organism record per
  species; stage and sex are never encoded in the id (they live in the
  developmental_stage / sex columns). See decisions.md → Organism Entities —
  Species-Level Modeling and entity_id Construction.
- Relationship types always use established vocabulary:
  part_of | develops_from | adjacent_to | connected_to | expresses | contains
- Figure IDs follow the pattern [SystemAbbrev]FIG[Number]
  (e.g., IntFIG1, PhaFIG1, RectFIG1, AlimFIG1, IntroFIG1)
  Sanctioned chapter abbreviations: Int (Intestine), Pha (Pharynx — not
  Phar), Rect (Rectum), Alim (Alimentary), Intro (Introduction). Intro is
  distinct from Int and confirmed not to collide with it (Chris Crocker,
  September 2026). Chapter abbreviations must be confirmed before use — see
  the Pha (not Phar) precedent logged in decisions.md.
- Citation format: Author Year (e.g., Kimble1983)
- DOI links always use https://doi.org/ prefix

## CELL DESCRIPTION WRITING STANDARD

These rules apply whenever writing or reviewing enhanced descriptions
for anatomical entity records (cells, neurons, organs, etc.).
They were established during the enhanced cell descriptions project
(January–March 2026) with director feedback from David Hall incorporated.

### Template Structure
All cell descriptions are written as a single prose paragraph
following this order:

  [CELL_NAME(s)] ([Full Name]) - [Type]. Located in [location].
  Born from [lineage] (exact AB lineages). [Morphological/developmental
  details]. [Neurotransmitter info with citations]. Express receptors
  [list with citations] and innexins [list with citations].
  [Detailed functional information with all citations preserved exactly].
  Important model for understanding [research significance].

### Formatting Rules (Non-Negotiable)
- Length: ~200–300 words per description
- Format: single paragraph — no bullet points, no section headers,
  no numbered lists, no bold text
- Lineage placement: EARLY in description, immediately after location —
  never at the end
- Lineage format: "Born from AB lineage (AB alapaappaa for ALML,
  AB alapppppaa for ALMR)"
- Bilateral pairs: described together, e.g., "AWCL/R (Amphid Wing C
  left/right)"
- Final sentence: ALWAYS ends with "Important model for understanding
  [research significance]."
- Citations: preserved exactly as they appear in the source WormAtlas
  data — never paraphrased or reformatted

### Required Content by Cell Type

Touch neurons:
- Include 15-protofilament microtubule detail
- Include MEC genes: MEC-2, MEC-4, MEC-6, MEC-10
- Include mechanotransduction mechanism

Chemosensory neurons:
- Include DEX-1/DYF-7 dendrite anchoring process
- Note whether dendrite protrudes through socket cell
- Include receptor expression (GPCRs, chemoreceptors)
- Include behavioral functions (chemotaxis, avoidance)
- Note AWC stochastic left/right asymmetry where applicable

Motor neurons:
- Include neurotransmitters (acetylcholine, GABA, or betaine)
- Include connectivity: chemical synapses to/from, gap junctions
- Specify locomotion role (forward/backward)
- Note postembryonic birth for: VA, VB, VD, AS classes

Command interneurons:
- Specify role: forward (AVB, PVC) vs. backward (AVA, AVD, AVE)
- Distinguish

## FIGURE METADATA CONVENTIONS

- Every figure requires the following RAG fields before it is
  considered complete:
  - ai_summary: plain-language description of what the figure
    shows (50-150 words, written conversationally)
  - ai_answerable_questions: minimum 3 questions this figure
    could help answer
  - ai_summary and ai_answerable_questions are written per panel, not
  blended across a multi-panel figure. Each panel of a figure (e.g.,
  IntFIG1's panels A, B, and C) gets its own ai_summary describing
  only what that panel shows, and its own set of at least 3
  ai_answerable_questions about that panel specifically.
   - Open each panel's ai_summary with a brief anchor to the parent
    figure, e.g., "One of three panels in IntFIG1 depicting the
    intestine..." so the RAG system and readers can still tell it's
    part of a set
   - Do not copy-paste one shared summary across all panel rows of the
    same figure_id — this creates drift risk if one copy is edited
    later and the others aren't
- Panel designations use capital letters (A, B, C, D, E...) — never
  lowercase. Figures may have any number of panels; the letter
  sequence is not limited to three.
- Visibility levels use these values only:
  primary | secondary | labeled | visible

  These describe how much a figure panel is *about* a given entity.
  This field is a ranking signal for the RAG search pipeline — when a
  researcher searches for an entity, figures where it is `primary`
  should outrank figures where it merely appears. If most entities
  are marked `primary`, that ranking collapses and every figure looks
  equally relevant to everything.

  | Value | Meaning | Test to apply |
  |---|---|---|
  | primary | The panel exists to show this entity | "If you removed this entity, would the panel lose its purpose?" |
  | secondary | Prominent and relevant, but not why the panel was made | Significant context, not the subject |
  | labeled | Has a visible text label or callout, but isn't a focus | Objective — is there a label pointing at it? |
  | visible | Discernible in the image, unlabeled, not a focus | Present but incidental |

  Note that these four values are not a single clean scale: `primary`
  and `secondary` describe prominence, while `labeled` and `visible`
  describe presentation. When an entity is both prominent and
  labeled, prominence wins — use `primary` or `secondary`.

- More than one entity may be marked `primary` in the same panel.
  This is permitted and sometimes correct: IntFIG1 panel C marks both
  `intestine` and `PENDING-gut-granules` as primary, because the
  epifluorescent panel exists specifically to show the granules
  within the intestine — both are genuinely the subject.
  `primary` is for genuine subjects, however, not a default. If in
  doubt, apply the removal test above.
Figure type is recorded on three fields, not one. The old single image_type / microscopy_technique pair is retired. Every figure panel now carries:
Field	Question it answers	Allowed values
media_type (required)	What KIND of asset is this?	image, diagram, table, movie, animation, interactive-3d
capture_technique (optional)	HOW was it imaged?	DIC, TEM, SEM, epifluorescent, confocal, AFM, or N/A
is_composite (yes/no)	Is it an overlay/composite of channels or sources?	0 or 1
Allowed values live in lookup tables, not in code. media_type and capture_technique are validated against the media_types and capture_techniques tables (foreign keys), NOT hardcoded ENUMs. To add a new figure type in future (e.g. a new imaging method), insert one row into the relevant lookup table — never alter the figures table and never edit a script. This is deliberate: figure types evolve with imaging technology, so the list must be editable without a schema migration.
media_type is always required; capture_technique is often N/A. A hand-drawn diagram, an animation, or an interactive-3d model usually has no capture technique — set capture_technique to N/A (written to the database as NULL). A movie or a still image that WAS imaged does carry a technique (e.g. a movie shot under DIC). Follow the existing N/A-vs-blank rule below: N/A = considered and not applicable (→ NULL); blank = still outstanding.
merged is no longer a type — it became the is_composite flag. A panel that overlays channels (e.g. DIC + GFP) or compiles multiple sources/timepoints sets is_composite = 1 AND records its real underlying technique in capture_technique where one exists. This keeps the true technique visible to search instead of hiding it behind the word "merged." When a composite has no single technique (e.g. a developmental timeline built from several papers), leave capture_technique N/A and set is_composite = 1.
media_type = table means a real HTML <table>, not a picture of one. A table rendered as a flat image is invisible to screen readers and unusable by the RAG pipeline. Catalogue tables as native HTML wherever possible. If a legacy table exists only as an image, its full contents MUST be entered in the text_alternative field (see ACCESSIBILITY_CHECKLIST.md). This is the one case where the accessibility-first and RAG-first requirements point at the same fix.
view_orientation, magnification, and scale_bar are N/A for interactive-3d. The reader controls the view and zoom, so there is no fixed value — set all three to N/A (→ NULL). For movie and animation, magnification/scale bar apply only if the footage is calibrated microscopy; otherwise N/A.
ai_summary for time-based and interactive media must describe change or structure, not a frozen frame. A movie / animation summary describes what happens over time; an interactive-3d summary describes the structure the reader can rotate to. A summary written like a still-image caption will retrieve poorly. All other ai_summary rules (50–150 words, per-panel, parent-figure anchor) still apply.
- Not every field applies to every figure — many WormAtlas figures
  are illustrations/diagrams rather than photomicrographs, and fields
  like magnification, scale_bar, and strain do not apply to them.
  Use this rule to distinguish "doesn't apply" from "not yet filled in":
  - Type N/A if the field genuinely does not apply to this figure
    (e.g., magnification for a schematic diagram)
  - Leave the cell blank only if the field applies but the value is
    still unknown or not yet entered
  - A blank cell always means outstanding work; N/A always means
    the field was considered and intentionally does not apply
  - This distinction matters most for: magnification, scale_bar,
    strain, specimen_stage, specimen_sex — fields that are meaningful
    for photographic/microscopy figures but often not applicable to
    diagrams and illustrations
  - image_source and view_orientation still apply to diagrams — for
    illustrations, image_source may reference an illustrator or the
    source publication a diagram was adapted from, rather than a lab
    archive reference
- Multi-entity panels: when more than one entity is visible in the
  same panel, only the FIRST row for that figure_id + panel
  combination carries panel-level content (description_in_figure, media_type, capture_technique, is_composite, magnification, view_orientation, source_reference, specimen_stage, specimen_sex, strain, image_source, scale_bar, media_file, media_format, duration_seconds, poster_image, caption_file, transcript, text_alternative, autoplay, loops, ai_summary, ai_answerable_questions).
  - Additional rows for the same figure_id + panel: fill in only
    entity_id and visibility. Leave every panel-level field blank
    on these rows — they exist solely to record that another entity
    is visible in that panel, not to duplicate panel content.
  - This keeps the figures table's UNIQUE(figure_id, panel) constraint
    intact (see decisions.md → Figures Base Table correction) while
    still letting figure_entities capture every entity visible in a
    panel, not just the primary one.
  - Example: IntFIG1 panel C has two rows — one for "intestine"
    (primary row, fully filled in) and one for "PENDING-gut-granules"
    (entity-only row, all panel-level fields blank).
  - Missing entity placeholder: if a visible structure does not yet
    have an entity_id in the Entities tab, use entity_id =
    "PENDING-[descriptive-name]" (e.g., PENDING-gut-granules) rather
    than leaving the cell blank or guessing a value. See key_facts.md
  - Two different kinds of "missing entity" exist, and they are
    handled differently:
    - Type A (name genuinely undetermined): a structure with no
      established identifier — e.g., gut granules. Use
      PENDING-[descriptive-name] until the glossary backfill
      resolves it.
    - Type B (name already known, row simply missing): a cell with
      an unambiguous, standard name that just hasn't been entered
      into the Entities tab yet — e.g., Z2, Z3, int1DR. Use the real
      entity_id directly; do NOT wrap it in PENDING-. Log it in
      key_facts.md → Known Data Gaps as a cell needing a new row,
      not as a naming question.
    → Known Data Gaps for tracking these until the WormAtlas glossary
    review backfills them with real entity_id values.
- image_source format: [Photographer/Lab] + [archive reference]
  e.g., "[Hall] N510-R338"
- Gold standard template: IntFIG1 (intestine article)

---

## SPREADSHEET IMPORT SCRIPTS

These rules apply to every script that reads the Google Sheets export
(scripts/import_figures.py, scripts/import_to_database.py, and any
future tab importer).

### Rules that apply to every tab

- Row 1 is the column header row. Row 2 is a human-readable helper row
  describing what each column should contain (e.g. "Figure identifier",
  "e.g., 400x", "draft/review/validated"). Row 2 is guidance for
  editors, not data. Every tab has one — Entities, Figures,
  Relationships, and Validation. A script reading the file naively will
  treat it as a record and import it.
  - Skip it by validating the row, not by counting position: skip any
    row whose key identifier column does not match its expected pattern
    (figure_id must match [SystemAbbrev]FIG[Number]; entity_type must be
    one of the ENUM values). Pattern validation also catches stray notes
    and blank rows anywhere in the file, not only at the top.
  - Skipping "the first two lines" works today and breaks the moment
    anyone inserts a row.

- Strip leading and trailing whitespace from every column header before
  matching headers to database columns. Spreadsheet headers have carried
  accidental spaces in practice ("    view_orientation"), and
  "    view_orientation" and "view_orientation" are different strings to
  a script. The mismatch fails silently — the field simply never maps.

- N/A and blank are not interchangeable (see Figure Metadata
  Conventions): N/A is written to the database as an explicit NULL; a
  blank cell on a field that should have a value is logged as an import
  warning, not a hard failure.

- Every import runs inside a transaction, one per logical record (per
  figure, per entity). A transaction means "do all of this or none of
  it." Without one, a script that fails partway through a multi-panel
  figure leaves some panels in the database and others missing, and
  re-running duplicates the ones that succeeded.

- Every import must be safely re-runnable. The spreadsheet is imported
  repeatedly as it grows; a second run must update existing rows, not
  create duplicates. Use INSERT ... ON DUPLICATE KEY UPDATE against the
  table's unique key.

### Figures tab — one spreadsheet, two tables

The Figures tab is a flat, merged view of two different database tables.
scripts/import_figures.py must un-merge it. Inserting every spreadsheet
row into `figures` will fail on the UNIQUE(figure_id, panel) constraint
the first time a panel contains more than one entity.

Grouping rule:

- `figures` receives the FIRST row of each figure_id + panel group.
  This row carries all panel-level content (description_in_figure,
  media_type, capture_technique, is_composite, magnification, view_orientation, source_reference, specimen_stage, specimen_sex, strain, image_source, scale_bar, media_file, media_format, duration_seconds, poster_image, caption_file, transcript, text_alternative, autoplay, loops, ai_summary, ai_answerable_questions).
- `figure_entities` receives EVERY row, including additional
  entity-only rows for the same panel.

Worked example — IntFIG1 (4 spreadsheet rows):

| Spreadsheet row | → figures | → figure_entities |
|---|---|---|
| A / intestine | yes | yes |
| B / intestine | yes | yes |
| C / intestine | yes | yes |
| C / PENDING-gut-granules | no | yes |

Result: 3 rows in `figures`, 4 rows in `figure_entities`.

### figure_id means two different things — read before writing the insert

The name `figure_id` appears in three places and does not hold the same
kind of value in all three:

| Location | Type | Example |
|---|---|---|
| Spreadsheet `figure_id` column | text | IntFIG1 |
| `figures.figure_id` | text | IntFIG1 |
| `figure_entities.figure_id` | integer | 7 |

`figure_entities.figure_id` is a FOREIGN KEY referencing `figures.id` —
the auto-increment number the database assigns when the panel row is
inserted. It does NOT hold the string "IntFIG1".

Required sequence for each panel:
1. INSERT the panel row into `figures`
2. Retrieve the id the database just assigned (PDO: $pdo->lastInsertId())
3. Use that integer as figure_entities.figure_id for every entity row
   belonging to that panel

Writing the string "IntFIG1" into figure_entities.figure_id will either
raise a type error or silently link rows to the wrong figure.

---

## ACCESSIBILITY CONVENTIONS

- Every page must pass WCAG 2.1 AA
- Lighthouse score target: 90+ on all pages
- All form inputs must have associated label elements
- Color is never the only means of conveying information
- Focus indicators must never be removed — style them, don't hide them
- All navigation must be keyboard-accessible
- Skip navigation link at top of every page
- Heading hierarchy must be logical (h1 → h2 → h3, no skipping)
- Use semantic HTML first — ARIA only when native semantics are insufficient


## REVISION HISTORY 

2026-09-03 — Figure classification moved from the single image_type / microscopy_technique ENUM pair to three fields (media_type, capture_technique, is_composite) backed by lookup tables. Adds movie, animation, interactive-3d, table, SEM, confocal, AFM. See decisions.md → "Figure Type Axes Split." Companion media-support columns and accessibility fields added; see ACCESSIBILITY_CHECKLIST.md.