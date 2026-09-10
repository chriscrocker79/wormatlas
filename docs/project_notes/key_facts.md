# WormAtlas Key Facts

## Team
- Project lead: Chris Crocker
- Lab directors: David Hall, Nate Schroeder
- Editors/researchers: Laura Herndon, Cathy Wolkow, Eli Conklin, Malia Jennings
- IT admin: Greg Parks (University of Illinois)

## URLs
- Production: https://wormatlas.org
- Development: https://dev.wormatlas.org
- Workflow manager: https://dev.wormatlas.org/workflow-manager.html

## Server Environment
- Host: University of Illinois
- IT admin: Greg Parks
- Local dev: XAMPP on MacBook Pro
- PHP version: 8.0.30
- Database: MariaDB 10.5.29 (MySQL-compatible)
- Dev server path: /var/www/dev.wormatlas.org/html/
- Production server path: /var/www/wormatlas.org/html/
- Python restrictions: None known; campus may flag unusual activity,
  resolved via exception request to Greg Parks
- API/networking: Webserver can communicate freely with database server.
  Cross-origin (CORS) is the primary networking concern to manage.
- Local project path (the real platform): /Users/christophercrocker/Desktop/sites/wormatlas
  — contains admin/, config/, content/, docs/, includes/, public/, rag_data/, scripts/.
- LOOK-ALIKE WARNING: a separate internal progress/workflow tracker lives at
  /Users/christophercrocker/Desktop/WA_workflowmanager. It is NOT the platform —
  it has no scripts/, config/, or schema. Do not run platform scripts there.
- Database names: local = `wormatlas_local` (XAMPP, this MacBook) — CONFIRMED
  September 2026; dev = `wormatlas_dev` (per config/database.php example, on
  cpsc-db-01.cropsci.illinois.edu); production = TBD — confirm with Greg Parks.
- Local .env configuration (this MacBook, CONFIRMED September 2026):
  DB_HOST=127.0.0.1, DB_PORT=3306, DB_NAME=wormatlas_local, DB_USER=root,
  DB_PASS= (empty — XAMPP default). The migration, schema, and import
  scripts all read these from .env via python-dotenv. .env is gitignored and
  must never be committed.

## Database Build State (as of September 2026)
- History / lesson: the schema was DECIDED in decisions.md but had NOT been
  built into any database as of early September 2026 — the local MySQL held only
  XAMPP's own system databases (information_schema, mysql, performance_schema,
  phpmyadmin, sys). This gap (schema decided vs. schema built) was not recorded
  and cost a full working session to discover; hence this note.
- LOCAL BUILD NOW COMPLETE (September 2026): `wormatlas_local` was built from
  scripts/create_schema.sql and populated by scripts/import_figures.py.
  Current contents: 10 figures, 36 rows in `figures`, 290 rows in
  `figure_entities`. All figure classification is on the split model
  (media_type / capture_technique / is_composite). figure_entities.entity_type
  is 'pending' for entities not yet in anatomical_entities (that table is empty;
  resolved at entity backfill).
- Fresh build method: scripts/create_schema.sql builds the full schema in one
  pass, with the Figure Type Axes Split already baked into `figures`
  (media_type / capture_technique / is_composite + the two lookup tables +
  the media-support columns) and `panel` as VARCHAR(20). On a fresh build, NO
  migration is required.
- scripts/migrate_figure_type_axes.py applies ONLY to an environment that
  already holds the OLD pre-split schema (the old image_type /
  microscopy_technique ENUMs). It is not used for a fresh local build.
- panel column width: VARCHAR(5) was too small for compound panel labels like
  `A-main`; corrected to VARCHAR(20) in create_schema.sql and in the local DB
  (see bugs.md 2026-09 and decisions.md Correction — September 2026). Any
  environment built on VARCHAR(5) needs:
    ALTER TABLE figures         MODIFY COLUMN panel VARCHAR(20) NOT NULL;
    ALTER TABLE figure_entities MODIFY COLUMN panel VARCHAR(20) NOT NULL;
- OPEN — confirm when dev access is available: do dev.wormatlas.org and
  production already have a pre-split `figures` table, or were they never built
  either? Run, on each, the information_schema check for a `figures` table.
  If never built, use create_schema.sql there too (and the migration script can
  be retired); if built on the old schema, run the migration AND the panel
  ALTERs (with Greg Parks for production, per the hosting decision).
- Deferred foreign keys stay DISABLED at build (enable later via ALTER TABLE):
  anatomical_entities.parent_entity_id self-FK, and figure_entities.entity_id →
  anatomical_entities(entity_id). See Known Data Gaps (parent_entity_id holds
  lineage) for the remediation sequence.

## Figure Cataloging — Standard Prompt
- Every new figure-cataloging chat should START from the standard prompt
  template: `FIGURE_CATALOGING_PROMPT_TEMPLATE.md` (kept in
  docs/project_notes/). Paste it, fill in the `[TEAMMATE NAME]` placeholder and
  the figure's source material, and let it run. Do not hand-write a fresh prompt
  each time — use this canonical copy so standards don't drift between chats.
  (Adjust the path here if the template is stored elsewhere.)
- The template enforces the current standards: the three-field figure type
  (media_type / capture_technique / is_composite; see decisions.md "Figure Type
  Axes Split"), the multimedia rules (movie / animation / interactive-3d / table,
  plus the media-support and accessibility columns), exact lookup-value spelling
  (e.g. epifluorescent), compound panel labels up to VARCHAR(20), the per-panel
  ai_summary / ai_answerable_questions rules, Type A / Type B entity resolution,
  and N/A-vs-blank / never-invent discipline.
- When a decision changes how figures are catalogued (new media_type, new
  capture_technique, changed field rules), UPDATE the template in the same pass
  so it never lags the decisions it depends on.

## Species & Taxonomy
- C. elegans: NCBITaxon:6239
- P. pacificus: NCBITaxon:54126
- S. stercoralis: NCBITaxon:34506
- Species names always italicized in display: <em>C. elegans</em>

## WormBase
- Anatomy term URL pattern: https://wormbase.org/species/all/anatomy_term/[WBbt:ID]
- Gene URL pattern: https://wormbase.org/species/c_elegans/gene/[WBGeneID]
- WBbt IDs identify anatomical structures (e.g., WBbt:0005772 = intestine)
- WBGene IDs identify genes (e.g., WBGene00004804 = skn-1)
- Ontology Browser (use to look up WBbt IDs for any anatomical term):
  https://wormbase.org/tools/ontology_browser
  Never invent or assume a WBbt ID — always verify here before entering it


## Embeddings Service
- Provider: Voyage AI
- Selected model: voyage-3.5
- Pricing: $0.06 per 1 million tokens (verified May 2026)
- Free tier: Not available on voyage-3.5 (free tier applies to
  voyage-4 series — 200M tokens; revisit if corpus grows)
- Estimated total cost for 9-month build + first year of queries:
  under $5.00 at current corpus size and expected academic traffic
- Model name must be stored in environment variable: VOYAGE_MODEL
- API key must be stored in environment variable: VOYAGE_API_KEY
- Re-indexing script location (once written): scripts/reindex_embeddings.py
- ChromaDB collection name convention: wormatlas_[system]_[model]
  e.g. wormatlas_nervous_voyage35
  (includes model slug so collections are never accidentally mixed)
- Input type for indexing documents: "document"
- Input type for search queries: "query"
  (these are different — using the wrong one degrades retrieval quality)

## Entity Data Standards
- Taxon ID for C. elegans: NCBITaxon:6239
- Validated record examples: int1DL (WBbt:0004361), intestine (WBbt:0005772)
- These two records are the gold standard templates for all enrichment work
- Total entities currently in spreadsheet: 574
- Status values: draft / review / validated
- Developmental stage values: embryo / L1 / L2 / L3 / L4 / dauer / adult / all
(Full C. elegans life cycle: embryonic stage, four larval stages L1–L4,
dauer as an alternative L3, and adulthood. all is reserved for entities
that are not stage-specific, e.g. a gene expressed across all stages.
This value set is DECIDED — see decisions.md → anatomical_entities Table
Schema.)
- Sex values: hermaphrodite / male / both
- Entity types permitted in spreadsheet: cell, cell-group, organ, tissue,
  structure, gene, protein
- Entity types confirmed in use (have records): cell, organ
- Entity types permitted but not yet populated: cell-group, tissue,
  structure, gene, protein
- entity_id construction:
  - Cells: entity_id = cell name, exactly as in the spreadsheet
    (e.g. int1DL).
  - Non-cell entities (created via glossary backfill): entity_id = the
    term's wormatlas.org glossary anchor slug — the `<a name="...">`
    value on that term's row (e.g. adherensjunction, axoneme). See
    decisions.md → entity_id Construction for Non-Cell Entities —
    Glossary Anchor Slug. Malformed anchors are flagged in the inventory
    pass and corrected under review; never bake a typo into an entity_id.
  - Terminology: "glossary anchor", "entity_id", "stub", and the
    "PENDING-" placeholder are defined in GLOSSARY.md → Technical Terms
    (reconciled with the backfill work, July 2026). GLOSSARY.md also notes
    the distinction between this project's internal terminology file and
    the wormatlas.org public glossary used as the backfill source.

## Entity Counts by Organ System (as of January 2026)
- Nervous system: 316 cells
- Alimentary: 98 cells
- Somatic muscle: 95 cells
- Seam: 21 cells
- Reproductive: 11 cells
- Hypodermis: 11 cells
- Coelomocyte: 6 cells
- Excretory: 4 cells

## Relationship Types (established)
part_of | develops_from | adjacent_to | connected_to | expresses | contains

## Spreadsheet Data Status (as of January 2026)
Source file: wormatlas_entities_WITH_WORMFINDR_DATA_01-2026

### Entities tab
- Total records: 574
- Validated (complete): 2 — int1DL, intestine
- Status "review" (imported, needs enrichment): 572
- Has WormBase ID: 564/574
- Has WormBase URL: 564/574
- Has real description: 574/574 (quality varies — WormFindr imports are thin)
- Has function: 2/574
- Has primary_figures: 2/574
- Has common_questions (RAG field): 2/574
- Has key_concepts (RAG field): 2/574
- Species: all C. elegans — no other species entered yet

### Relationships tab
- Total records: 3
- All usable, all C. elegans intestine examples
- Target for Phase 1: 100-150 relationships

### Figures tab
- Total records: 4 rows covering 1 figure — IntFIG1, panels A/B/C.
  Panel C carries a second entity-only row (PENDING-gut-granules).
- Column structure: COMPLETE as of July 2026. All 17 columns required
  by the DECIDED `figures` schema are present, the microscopy_technique
  header typo is corrected, and header whitespace has been cleaned.
- IntFIG1 is the validated gold-standard reference — match its format
  and level of detail for all subsequent figure rows. Verified against
  the schema and Figure Metadata Conventions, July 2026.
- 800+ figures on the site need cataloguing
- Priority figures to enter next: IntFIG2, IntFIG3, IntFIG5
  (already referenced in validated entity records)
- Figure cataloguing does not require the CMS to be built first

### Figures Pipeline — Status Update (July 2026)
- Database schema for figures is now fully DECIDED: `figures`,
  `article_figures`, `figure_entities`, `content_pages`, and
  `anatomical_entities` tables are all logged in decisions.md with
  signed-off CREATE TABLE statements (Chris Crocker, David Hall,
  Nate Schroeder)
- All previously open schema questions are resolved:
  - `anatomical_entities` schema — DECIDED
  - `content_id` article-identity / `both`-`b` sex convention — DECIDED
  - `ai_answerable_questions` column type — DECIDED as TEXT
- `scripts/import_figures.py` is no longer blocked by any undecided
  schema and can be written against the current, authoritative schema
- Spreadsheet Figures tab column update: COMPLETE (July 2026).
  No remaining blockers. Figure cataloguing is unblocked and IntFIG1
  is entered and verified.

### Validation tab
- Total records: 0
- 564 WormBase URLs need testing
- URL testing can and should be automated with a Python script

## Known Data Gaps
- int-ring-1 (Int ring 1, the four-cell anteriormost intestinal ring)
  referenced in Relationships tab but missing from Entities tab.
  Corrected July 2026 from an earlier mislabeling as "int-ring-I" —
  see bugs.md for details.
- Cataloguing IntFIG2 surfaced a distinct type of gap from the
  gut-granules case in IntFIG1: cells with known, unambiguous names
  that are simply missing rows in the Entities tab, as opposed to
  structures with no established identifier yet. These do NOT need
  a PENDING- placeholder, since there is nothing ambiguous to
  resolve — the entity_id is already certain. Confirmed missing as
  of July 2026: int1DR (sibling cells int1DL/VL/VR already exist),
  Z2, Z3 (germline precursor cells), K (partner cell K' already
  exists), PDA (neuron; precursor cell Y already exists). These
  should be added to the Entities tab directly under their real
  names once WormBase IDs are looked up — tracked here so they
  aren't lost, not because their naming is in question.
- uterus was also found missing while cataloguing IntFIG2 (inset,
  postembryonic intestinal arrangement). Unlike the cells above,
  this is a non-cell structure — treated as a PENDING-uterus
  placeholder per the standard glossary-backfill process, since its
  entity_type and confirmed glossary anchor still need editor
  classification, consistent with how gut granules was handled.
- Figure cataloguing is surfacing anatomical structures visible in
  figures that do not yet have entity_id records in the Entities tab
  (e.g., gut granules, seen in IntFIG1 panel C). The WormAtlas.org
  glossary will be used as the source to backfill these missing
  entities. Until backfilled, figure rows needing an unrecorded
  entity use a temporary placeholder: entity_id = "PENDING-[descriptive
  name]" (e.g., PENDING-gut-granules), to be corrected once the real
  entity_id exists.
 - Entity types with zero records as of July 2026: cell-group, tissue,
  structure, gene, gene-family, protein, organism,
  developmental-stage, process. The tab currently holds 573 `cell`
  and 1 `organ` record. Every non-cellular structure encountered
  during figure cataloguing (gut granules, microvilli, basal lamina,
  terminal web, lumen) will require a new record.
- Entity backfill from the WormAtlas.org glossary runs IN PARALLEL
  with figure cataloguing, not after it. See decisions.md → Glossary
  Entity Backfill Runs in Parallel with Figure Cataloguing.
- FOREIGN KEY on figure_entities.entity_id must NOT be added until
  every PENDING- placeholder has been replaced with a real entity_id.
  See decisions.md → anatomical_entities Table Schema → Constraint —
  figure_entities foreign key is DEFERRED, not optional. 
- 10 cells missing WormBase IDs: AC, ADLL, ADLR, P12.pa,
  PVDL, PVDR, SML, SMR, VD12, VD13
- Relationships table is early stage — only 3 entries, target is 100-150
- Figures tab is empty — largest data gap relative to RAG requirements
- No P. pacificus or S. stercoralis entities exist yet
- FK constraint on figure_entities.entity_id must not be added until
  every PENDING- placeholder is backfilled. See decisions.md →
  anatomical_entities Table Schema → Constraint note.
- Glossary backfill stub records: entity records entered as stubs during
  the glossary backfill (see decisions.md → Stub Entity Records
  Permitted for Glossary Backfill) are tracked here alongside PENDING-
  placeholders so outstanding enrichment work stays visible. Running
  count: 0 as of July 2026 — update as stubs are created. A stub is
  complete only when its REQUIRED columns are filled and status is
  promoted from 'draft'.
- PENDING- placeholder resolution uses the glossary anchor: when a
  PENDING-[name] value is replaced with a real entity_id, the real id is
  the term's glossary anchor slug (e.g. PENDING-gut-granules →
  gutgranules), NOT a de-hyphenated version of the placeholder. See
  decisions.md → entity_id Construction for Non-Cell Entities.
- Glossary backfill inventory pass COMPLETE (July 2026), via
  scripts/parse_glossary.py against all 26 wormatlas.org glossary pages
  (A-Z). Results: 1,619 glossary terms total; 107 already match existing
  Entities records; 1,512 not yet matched. Of those 1,512: 117 are "See X"
  cross-references (synonym data, not new records); 38 carry a WBbt ID and
  10 carry a lineage path (both high-confidence real entities to create);
  the remaining ~1,347 are a mix of genuine new entities (structure,
  process, tissue) and non-entities (methods, concepts, adjectives) that
  the editor classification pass must separate. True records-to-create
  count is therefore not yet known — floor ~48, upper bound ~1,395 —
  pending classification. 0 cross-page anchor collisions (all 1,619
  anchors globally unique). 9 malformed anchors flagged for editor review.
  412 rows carry synonym data for routing into target entities' synonyms
  column. See decisions.md -> Glossary Entity Backfill Runs in Parallel
  with Figure Cataloguing.
- Glossary backfill classification pass: guide COMPLETE and shared with
  the editors; classification IN PROGRESS, results not yet returned
  (July 2026). Editor guide (glossary_classification_guide.docx / .md)
  covers the four columns to complete (is_entity, proposed_entity_type,
  ambiguous_flag, editor_notes), the entity-vs-not-entity test, an
  entity/anchor explainer, worked examples, and the 9 malformed-anchor
  cases (including the cell-name-vs-slug rule for P0/E/intI/MCM/SR).
  Work is organized as 10 claimable chunks by letter with NO fixed
  per-person assignment — editors claim a chunk via a "Chunk sign-up"
  tab (seeded from chunk_signup.csv) and complete only their claimed
  rows. Working method: a single shared Google Sheet edited by all
  editors together (Google Sheets is already the entity-data source of
  truth per decisions.md -> Entity Data Pipeline), exported back to CSV
  for the import script. The description column was added to
  scripts/parse_glossary.py so editors classify entirely in-spreadsheet.
  Record creation and stub counting begin only after classification is
  complete; stub count remains 0 (see the stub-records bullet above).
- Enrichment flags during classification: an optional `enrichment_note`
  column was added to the classification sheet (July 2026) so editors can
  record content problems they notice in passing — e.g. descriptions with
  C. elegans-specific counts or measurements that won't hold for other
  species (first raised by Nate Schroeder on the amphid, ~12 neuron types).
  These are NOT acted on during classification; they are collected for the
  later enrichment pass, where species-scoped descriptions are written to
  the RAG Readiness Standard. Classification itself stays at the four
  columns (is_entity, proposed_entity_type, ambiguous_flag, editor_notes).
  The column was also added to scripts/parse_glossary.py so a regenerated
  inventory keeps it.
  - Cataloguing AlimFIG1 (alimentary overview figure) surfaced a batch of
  missing entities across its anatomy and lineage panels. Only `intestine`
  (the one existing organ record) was already present; everything else in
  the figure is a gap:
  - Type B (known name, missing row — use the real entity_id directly): the
    embryonic founder cells E, MS, AB, EMS, ABa, ABp, from lineage panels B
    and C. All are `cell` entities, NOT cell-group (see decisions.md →
    Founder/Blast Cells Are `cell`, Not `cell-group`). Each needs a row
    added directly under its real name plus a cell-level WBbt lookup in the
    Ontology Browser (never invented; NULL if none exists). Their naming is
    not in question — tracked here so they are not lost, same as the
    int1DR / Z2 / Z3 / K / PDA Type B cells above.
  - Type A (non-cell structure, glossary anchor slug not yet confirmed —
    PENDING- placeholder per the standard backfill process): pharynx and
    rectum, entered in the AlimFIG1 figure rows as PENDING-pharynx and
    PENDING-rectum. To be replaced with their real glossary-anchor
    entity_ids once the backfill resolves them (the anchor slug, NOT a
    de-hyphenated form of the placeholder — see decisions.md → entity_id
    Construction for Non-Cell Entities). Note: pharynx is the anterior
    analog of the intestine organ, but its entity_id is still unconfirmed
    and must NOT be assumed to be "pharynx".
  - Pending Nate Schroeder's classification (NOT yet committed as gaps — see
    AlimFIG1 classification email): foregut / midgut / hindgut (panel A
    region labels — distinct entities, or shorthand for pharynx / intestine
    / rectum?); the unenumerated "specific tissues" labels below panel A
    (need the actual list before rows can be created); and whether panel C's
    lineage tree shows EMS as a discrete node.
  - Running PENDING- set now includes PENDING-pharynx and PENDING-rectum
    alongside the earlier PENDING-uterus and PENDING-gut-granules. Stub
    count unaffected (these are figure-surfaced placeholders, not glossary
    stubs).

- IntFIG3 cataloguing (August 2026) added 28 new rows to the Entities tab,
  all status='draft' with blank wormbase_id. 28 WBbt Ontology Browser
  lookups are therefore owed before any of these leave draft — look each up
  individually (never infer int1DR's WBbt from its siblings), and leave NULL
  only where a term genuinely has no WBbt. None of the 28 are RAG-ready
  (drafts lack the full description/function/validated status the RAG
  Readiness Standard requires). Breakdown:
  - int1DR (cell, parent_entity_id=int-ring-1) — dorsal right cell of
    intestinal ring 1. RESOLVES the previously-logged Type B gap for int1DR.
  - int-ring-1 through int-ring-9 (cell-group, parent_entity_id=intestine),
    per decisions.md → cell-group Added as Entity Type, using the int-ring-1
    (arabic) identifier. RESOLVES the previously-logged int-ring-1 gap;
    int-ring-2..9 are newly created.
  - 18 embryonic lineage cells (all entity_type=cell, developmental_stage=
    embryo, sex=both, parent_entity_id NULL per decisions.md → Founder/Blast
    Cells Are `cell`): E, EMS, MS, P2, ABa, ABp, ABal, ABar, ABpl, ABpr, C,
    D, P3, P4, Ea, Ep, Z2, Z3. Of these, E, EMS, MS, ABa, ABp (previously
    logged from AlimFIG1) and Z2, Z3 (previously logged) are now RESOLVED as
    draft rows; the other 11 (P2, ABal, ABar, ABpl, ABpr, C, D, P3, P4, Ea,
    Ep) are newly surfaced by IntFIG3.
  - Developmental parentage of these cells (EMS→E/MS, AB→ABa/ABp, E→Ea/Ep,
    P2→C/P3, P3→D/P4, P4→Z2/Z3) belongs in the cell_lineage table (DECIDED,
    not yet built), NOT in parent_entity_id (left NULL for founder cells).
    Deferred until cell_lineage exists.
  - Still OPEN, not created by IntFIG3: AB, P0, P1 (2-cell/founder cells not
    labeled in IntFIG3, skipped by decision); K, PDA (from the earlier
    int1DR/Z2/Z3 batch); and the E4 daughters Eal/Ear/Epl/Epr (named in the
    IntFIG3 caption but not individually diagram-labeled — deliberately not
    created).

- IntFIG3 PENDING- figure placeholders (figure-row values only, not entity
  rows): PENDING-adherensjunction and PENDING-vulva are new; PENDING-uterus
  (already logged from IntFIG2) also appears. Running PENDING- set is now:
  PENDING-uterus, PENDING-gut-granules, PENDING-pharynx, PENDING-rectum,
  PENDING-adherensjunction, PENDING-vulva. Adherens junction's glossary
  anchor is already documented (adherensjunction, per GLOSSARY.md), so that
  one resolves trivially in the backfill. Stub count unaffected — these are
  figure-surfaced placeholders, not glossary stubs.

- Binucleate-cell synonym enrichment owed (IntFIG3, RAG impact): IntFIG3
  panel B labels the anterior/posterior NUCLEI of binucleate intestinal
  cells (int3Da/int3Dp, int3Va, int4Da/int4Dp, int4Va/int4Vp, int5La,
  int5Ra). These are nuclei, not cells — no entity rows were created for
  them. To let RAG match a query on a nucleus label, add these labels to the
  synonyms field of the PARENT cell records (int3D, int3V, int4D, int4V,
  int5L, int5R). This edit to existing rows is outstanding.

- int1DL duplicate — salvaged lineage (holding note, August 2026): the
  Entities tab briefly held two int1DL rows — one validated (gold standard)
  and one WormFindr 'review' import. The review duplicate is being deleted
  (see bugs.md). Its lineage data is preserved here because there is nowhere
  yet to file it (the cell_lineage table is DECIDED but not built):
  - int1DL sublineage recorded by WormFindr: Ealaad (immediate parent Ealaa).
  - UNVERIFIED — sourced from the WormFindr import, whose quality varies (the
    source description even carries the typo "Emrbyonic"). Must be checked
    against the canonical Sulston lineage before it is ever entered into
    cell_lineage. Do not treat as confirmed.
  - Modeling note for when cell_lineage is built: Ealaa is a deep
    intermediate blastomere that is NOT an entity in the tab (and not one we
    are creating). cell_lineage.parent_cell_id is meant to reference a real
    entity, so a choice is needed then — store the lineage as a plain-text
    path, or create the intermediate blastomeres. Table-design question,
    deferred.
  - Companion fix (see bugs.md): the kept validated int1DL row's
    parent_entity_id is being changed from int-ring-I (old mislabeled form)
    to int-ring-1.

  - parent_entity_id holds embryonic lineage, not structural parent
  (RESOLVED 2026-08-31 for parent_entity_id itself — lineage strings removed
  project-wide, DB7 final straggler deleted, live Google Sheet confirmed
  authoritative. Downstream cell_lineage migration and self-FK remain; see
  RESOLUTION NOTE at the end of this entry. Originally discovered August 2026
  during the int1DL duplicate fix; see bugs.md for the discovery record). 564 of the 565 Entities-tab rows that have a
  parent_entity_id set store an embryonic CELL-LINEAGE PATH there, not the
  cell's structural parent — e.g. int1VR → Earaa, int2D → Earp,
  ADAL → ABplapaaaap, ADEsoL → H2L.a. Only 1 row (the validated int1DL, after
  its fix) uses a real structural parent (int-ring-1). The problem is
  project-wide, not intestine-specific: it spans the entire WormFindr
  Information Cards import (Nov 2024) across all organ systems, because that
  import mapped each cell's lineage path into parent_entity_id. This
  contradicts the agreed model (decisions.md → Founder/Blast Cells Are `cell`;
  cell_lineage Table): structural parentage belongs in parent_entity_id,
  developmental parentage belongs in cell_lineage.
    - RESOLUTION NOTE (2026-08-31): the parent_entity_id lineage cleanup is
    complete — the last straggler (DB7 -> ABprppaapp) has been deleted, so no
    parent_entity_id still holds a lineage path. The entities_export.csv used
    for RectFIG2 cataloguing was confirmed to match the live Google Sheet, so
    the post-cleanup state is current (no stale snapshot). Embryonic lineages
    now live almost entirely in the DESCRIPTION field as the interim single
    copy — the guardrail above still holds: description enrichment must not
    drop them before cell_lineage is built.    ... parent_entity_id will be populated with real structural designations
    over time (still-blank rows are awaiting that assignment, not an error).
    DESTINATION: the eventual home for lineage is already decided — decisions.md
    -> "cell_lineage Table" (May 2026: cell_id, parent_cell_id, division_stage,
    division_time_minutes, division_orientation, fate), which explicitly states
    lineage belongs in that table, NOT in prose. The current descriptions-holding
    is therefore an INTERIM deviation pending that table's build; the strip-and-
    hold step was decided in a separate chat session (date to confirm). No new
    binding decision is needed since the destination is logged — but if the
    interim + the "don't drop lineage from descriptions before migration"
    guardrail should themselves be binding, add them as a short addendum to the
    cell_lineage decision rather than as a standalone entry.

  - Consequence for schema: the anatomical_entities self-FK
    FOREIGN KEY (parent_entity_id) REFERENCES anatomical_entities(entity_id)
    must NOT be enabled yet. The lineage values (Earaa, ABplapaaaap, H2L.a…)
    are not entity_ids in the table, so enabling the FK now would reject all
    564 rows at import. This is the exact parallel of the figure_entities FK
    deferral noted above — same guardrail, different table.
  - Consequence for RAG: structural hierarchy queries ("what ring/organ is
    int2D part of?") cannot be answered from parent_entity_id in its current
    state.
  - The IntFIG3 lineage-cell batch (August 2026) already follows the correct
    convention — founder cells were added with parent_entity_id NULL — so this
    cleanup targets the pre-existing WormFindr rows only, not the new ones.
  - Fix (not yet done; sequence, after cell_lineage is built): (1) move each
    cell's lineage path into cell_lineage, verified against the canonical
    Sulston lineage (WormFindr lineage is unverified — see the int1DL holding
    note); (2) set parent_entity_id to the cell's real structural parent
    (ring/organ/tissue), or NULL where none applies; (3) only then enable the
    self-FK. Scope ~564 rows — batch/scripted correction, not a hand edit.
    A solved-bug entry goes in bugs.md when this pass runs, and this gap is
    marked resolved at the same time.  
    - STATUS UPDATE (August 2026): Step 2 executed early and project-wide —
    embryonic-lineage strings removed from parent_entity_id on ALL ~564
    affected rows. Structural parents assigned so far: pharyngeal cells
    (pm4/pm5/mc3 groups + their 9 member cells) -> PENDING-pharynx; int1DL ->
    int-ring-1 (prior fix). All other cleared rows now have parent_entity_id
    NULL/blank (real structural parent still to be assigned).
  - CONSEQUENCE — lineage is now SINGLE-COPY: it previously sat in BOTH
    parent_entity_id and the description; after the clear it survives ONLY in
    the description field. Steps 1 (migrate to cell_lineage) and 3 (enable
    self-FK) are still not done; cell_lineage is not built.
  - NEW RISK / GUARDRAIL: the description is now the sole surviving copy of
    every cell's lineage. The "Enhanced Cell Descriptions" enrichment pass
    MUST NOT drop the lineage string when rewriting a description, OR the
    cell_lineage build + migration must run BEFORE enrichment touches these
    rows. Losing the description string before migration = permanent lineage
    loss (no backup). Sequence cell_lineage migration ahead of WormFindr-row
    enrichment.
  - Self-FK: still deferred — no longer because of lineage strings (gone),
    but because PENDING-pharynx (and any other PENDING placeholder used as a
    structural parent) is not yet a real entity_id and would be rejected.
    Enable only after those placeholders are backfilled.

    - STATUS UPDATE (August 2026): Step 2 executed early and project-wide —
    embryonic-lineage strings removed from parent_entity_id on ALL ~564
    affected rows. Structural parents assigned so far: pharyngeal cells
    (pm4/pm5/mc3 groups + their 9 member cells) -> PENDING-pharynx; int1DL ->
    int-ring-1 (prior fix). All other cleared rows now have parent_entity_id
    NULL/blank (real structural parent still to be assigned).
  - CONSEQUENCE — lineage is now SINGLE-COPY: it previously sat in BOTH
    parent_entity_id and the description; after the clear it survives ONLY in
    the description field. Steps 1 (migrate to cell_lineage) and 3 (enable
    self-FK) are still not done; cell_lineage is not built.
  - NEW RISK / GUARDRAIL: the description is now the sole surviving copy of
    every cell's lineage. The "Enhanced Cell Descriptions" enrichment pass
    MUST NOT drop the lineage string when rewriting a description, OR the
    cell_lineage build + migration must run BEFORE enrichment touches these
    rows. Losing the description string before migration = permanent lineage
    loss (no backup). Sequence cell_lineage migration ahead of WormFindr-row
    enrichment.
  - Self-FK: still deferred — no longer because of lineage strings (gone),
    but because PENDING-pharynx (and any other PENDING placeholder used as a
    structural parent) is not yet a real entity_id and would be rejected.
    Enable only after those placeholders are backfilled.

 - PhaFIG1 (Pharynx chapter, figure 1) catalogued August 2026: 2 `figures`
  rows (panels A/B), 69 `figure_entities` rows. Primary entity = existing
  PENDING-pharynx placeholder (reused, no new placeholder).
- pm4/pm5/mc3 cell-group conversion COMPLETE (decisions.md — Pharyngeal
  pm4/pm5/mc3; and Cell-Group Membership via part_of): pm4, pm5, mc3 retyped
  cell -> cell-group; 9 member cells created (status=draft) with
  parent_entity_id=PENDING-pharynx; 9 part_of relationship rows added
  (rel-004..rel-012 — verify numbering didn't collide). STILL OWED on the 9
  drafts before they leave draft/reach RAG-readiness: individual WBbt lookups
  (wormbase_id + wormbase_url currently blank; never infer from siblings),
  embryonic lineage into cell_lineage, and function/size_description/
  common_questions/key_concepts enrichment.
- The 3 cell-group rows pm4/pm5/mc3 need parent_entity_id=PENDING-pharynx set
  (organ-level structural parent) if not already done during retype.
- data_source/curator_name on the 9 drafts were set to "PhaFIG1 cataloguing
  (Aug 2026)" / "[PhaFIG1 cataloguing - draft]" — align with the string the
  IntFIG3-created cells used, for consistency.
- Pre-existing cell-group gap (surfaced, not yet done): pm2, pm3, mc1, mc2
  are stored only as member cells with NO cell-group parent. Each needs the
  same treatment pm4/pm5/mc3 just got — a cell-group parent, member part_of
  rows, and organ-level parent_entity_id. Not blocking.
- int-ring structural migration (follow-on): int1DR etc. currently put the
  cell-group in parent_entity_id (int-ring-1); per the Aug 2026 membership
  decision, membership becomes part_of and parent_entity_id moves to the
  organ (intestine — already an entity). Reconcile the int-ring-1 / int-ring-I
  id-format issue (bugs.md 2026-07) in the same pass.
- Lineage for the 9 pharyngeal member cells rides with the whole WormFindr
  set under the "parent_entity_id holds lineage" gap above (see its August
  2026 status update): parent_entity_id cleared, lineage now description-only,
  cell_lineage migration owed, enrichment must preserve lineage.
- pm2L-pmVL -> pm2L-pm2VL entity_id typo corrected in the live Entities tab.
- Pharynx chapter enrichment: text says "4 gland cells" but there are 5
  gland nuclei (g1AL, g1AR, g1P, g2L, g2R), all present as entities. Carry
  the "5 gland cells" fix into the chapter prose.
- Pharynx figure-ID abbreviation is PhaFIG (e.g. PhaFIG1), NOT PharFIG;
  conventions.md's Figure ID example was corrected from "PharFIG2" to
  "PhaFIG1" (Aug 2026).

- pm6 and pm7 cell-group creation (PhaFIG2 cataloguing, Aug 2026): PhaFIG2
  panel F labels the bare muscle class "pm6", which had no cell-group row —
  the first bare-class pharyngeal-muscle callout (PhaFIG1 only ever labeled
  the individual nuclei). pm6 and pm7 are the same pre-existing cell-group
  gap as pm2/pm3/mc1/mc2, but were OMITTED from that earlier list; both are
  multi-member classes (pm6D/pm6VL/pm6VR; pm7D/pm7VL/pm7VR) that under the
  cell-group rule need a class parent. Actioned:
  - 2 cell-group rows created (status=draft): pm6, pm7. entity_id = class
    name; parent_entity_id = PENDING-pharynx; data_source "PhaFIG2
    cataloguing (Aug 2026)".
  - 6 part_of rows added (rel-013..rel-018): pm6D/pm6VL/pm6VR part_of pm6;
    pm7D/pm7VL/pm7VR part_of pm7.
  - Member cells needed NO change — they already carried
    parent_entity_id=PENDING-pharynx and their own WBbt IDs (status review).
  - STILL OWED before pm6/pm7 leave draft: class-level WBbt lookups in the
    WormBase Ontology Browser (wormbase_id + wormbase_url currently blank;
    never infer from members, NULL only if the class genuinely has none),
    and function/common_questions/key_concepts enrichment.
  - Pre-existing gap reminder: pm2, pm3, mc1, mc2 still need the same
    treatment (cell-group parent + part_of rows); not blocking.

- PhaFIG2 (Pharynx chapter, figure 2) catalogued Aug 2026: 7 figures rows
  (panels A-G), 15 figure_entities rows. 6 new PENDING- placeholders
  introduced (Type A structures, glossary anchors to confirm on backfill):
  PENDING-pharyngeal-epithelium, PENDING-pharyngeal-intestinal-valve,
  PENDING-buccal-cavity, PENDING-radial-channels, PENDING-sieve,
  PENDING-grinder. Reused existing PENDING-pharynx. Running PENDING- set is
  now: PENDING-uterus, PENDING-gut-granules, PENDING-pharynx, PENDING-rectum,
  PENDING-adherensjunction, PENDING-vulva, PENDING-preanal-ganglion,
  PENDING-lumen, PENDING-pharyngeal-epithelium,
  PENDING-pharyngeal-intestinal-valve, PENDING-buccal-cavity,
  PENDING-radial-channels, PENDING-sieve, PENDING-grinder. Stub count
  unaffected (figure-surfaced placeholders, not glossary stubs). Note: the
  ventral gland openings (labeled generically "Gl" in panel D) were NOT
  mapped to specific gland cells (g1AL/g1AR/g1P/g2L/g2R all exist) — pending
  Hall/Schroeder confirmation of which cells the two openings correspond to.

- RectFIG2 (Rectum/Anus chapter) cataloguing status (2026-08-31): drafted
  and pending review before import. 5 Figures-tab rows (panels A-main,
  A-inset, B, C, D) + 19 figure_entities rows. Panel A split into A-main /
  A-inset (the inset is a magnified view of the valve). Strain: only strain
  SOURCES given (people), no genotype — strain = "PENDING — strain not yet
  confirmed", source in image_source as "[Wang/Chen strain source]
  wormatlas.org" (A/B) and "[Land/Rubin strain source] wormatlas.org" (C/D).

- PENDING-anus (new Type A placeholder, surfaced by RectFIG2): anus is labeled
  in the figure (panel A "Anus" arrowhead; panel B arrowhead) but has no
  Entities-tab row and no glossary anchor. Figure-row value only. Distinct
  from the cells "mu anal" / "mu sph" (anal muscles, not the opening). Running
  PENDING- set is now: PENDING-uterus, PENDING-gut-granules, PENDING-pharynx,
  PENDING-rectum, PENDING-adherensjunction, PENDING-vulva, PENDING-anus.

- Two new anatomical-grouping cell-groups owed (surfaced by RectFIG2; entity
  rows NOT yet created — figure rows reference them as Type B):
  - intestinal-rectal-valve — members virL + virR (Dave Hall: "collectively,
    as a cell group, they make up the intestinal rectal valve"). Synonym: vir.
    entity_id is the descriptive, hyphenated, no-space form matching
    int-ring-1 (not the "vir" class-name form, not a glossary slug).
  - rectal-gland — members rect_D + rect_VL + rect_VR ("a group of cells that
    make up the rectal gland structure"). Same entity_id format.
  - Each group needs its own class-level WBbt, looked up individually; NULL if
    none.
  - Containment (decisions.md -> Aug 2026 model, affirmed 2026-08-31,
    Option A): members are part_of their group AND parent_entity_id =
    alimentary-system; each group's parent_entity_id = alimentary-system.
    part_of = membership, parent_entity_id = structural parent — non-redundant,
    not mirrored.

- alimentary-system entity row owed (approved 2026-08-31): created so it is a
  real structural parent, resolving the dangling intestine -> alimentary-system
  reference and serving the new valve/gland groups. WBbt looked up
  individually; NULL if none. See bugs.md (2026-08 parent_entity_id integrity).

- Containment model — SETTLED (2026-08-31, Option A): the Aug 2026 decision
  (part_of = membership; parent_entity_id = single structural parent;
  non-redundant) is affirmed, not superseded. The int-ring consistency
  migration it owed is scheduled and tracked in bugs.md. See decisions.md ->
  "Aug 2026 Containment Model Affirmed; int-ring Migration, alimentary-system
  Entity, and Valve/Gland Cell-Groups".

- virL description lineage typo: "Abprpappppp" -> "ABprpappppp" (matches virR
  "ABprpappppa"; sister cells from ABprpapppp). To be applied on next
  Entities-tab edit.

- IntroFIG1 (Introduction chapter, "Anatomy of an adult hermaphrodite")
  cataloguing (September 2026): 9 figure_entities rows across 2 panels
  (A: DIC whole animal; B: schematic). Surfaced the following gaps.
  - c-elegans organism entity row OWED (Type B — id known and certain, row
    simply missing; NOT a PENDING- placeholder). This is the FIRST
    `organism`-type record (the type was previously zero-record). Create per
    decisions.md → Organism Entities — Species-Level Modeling and entity_id
    Construction: entity_id `c-elegans`, entity_name "Caenorhabditis elegans",
    common_name "C. elegans", entity_type `organism`, parent_entity_id NULL,
    species `c-elegans`, taxon_id `NCBITaxon:6239`, developmental_stage `all`,
    sex `both`, status `draft`. wormbase_id: Ontology Browser lookup owed;
    NULL if no organism-level term exists — do not invent. Referenced as the
    primary entity on IntroFIG1 panels A and B; the interim placeholder
    PENDING-celegans-adult-hermaphrodite is now RESOLVED to `c-elegans` and is
    therefore NOT added to the PENDING- set. The animal's adult/hermaphrodite
    specificity is carried on the figure rows (specimen_stage=adult,
    specimen_sex=hermaphrodite), not in the entity.
  - Three new Type A PENDING- placeholders (figure-row values only, glossary
    anchors to confirm on backfill): PENDING-embryo (the two ovoid eggs in
    panel A, present in the image but omitted from the official legend),
    PENDING-proximal-gonad, PENDING-distal-gonad. Note: the existing `Gonad`
    record (entity_type=cell, WBbt:0005785) is correctly a separate thing and
    is NOT a match for these adult gonad regions — confirmed with Chris Crocker.
  - Reused existing placeholders (no new gap): PENDING-pharynx, PENDING-uterus,
    PENDING-anus. Real entity reused: intestine.
  - Running PENDING- set RECONCILED (the PhaFIG2 note and the later RectFIG2
    note had drifted — RectFIG2's list silently dropped the six PhaFIG2
    pharyngeal placeholders, PENDING-preanal-ganglion, and PENDING-lumen).
    Correct union as of IntroFIG1: PENDING-uterus, PENDING-gut-granules,
    PENDING-pharynx, PENDING-rectum, PENDING-adherensjunction, PENDING-vulva,
    PENDING-preanal-ganglion, PENDING-lumen, PENDING-pharyngeal-epithelium,
    PENDING-pharyngeal-intestinal-valve, PENDING-buccal-cavity,
    PENDING-radial-channels, PENDING-sieve, PENDING-grinder, PENDING-anus,
    PENDING-embryo, PENDING-proximal-gonad, PENDING-distal-gonad. Stub count
    unaffected (figure-surfaced placeholders, not glossary stubs).


## Enhanced Cell Descriptions — Status (as of March 2026)
- 70 nervous system cells have completed enhanced descriptions
- All follow the writing standard in conventions.md
- All descriptions were reviewed against director feedback from David Hall
- These descriptions are WRITTEN but may not yet be entered into the
  spreadsheet — confirm import status before beginning duplicate work

### Completed cells (70 total):
Touch neurons (6): ALM (ALML/R), AVM, PLM (PLML/R), PVM,
  FLP (FLPL/R), PVD (PVDL/R)
Chemosensory neurons (15): AWC (AWCL/R), AWA (AWAL/R),
  ASH (ASHL/R), ASE (ASEL/R), ASI (ASIL/R), ADF (ADFL/R),
  ASG (ASGL/R), AQR, AFD (AFDL/R), URX (URXL/R), PQR,
  AWB (AWBL/R), ASJ (ASJL/R), ASK (ASKL/R), ADL (ADLL/R)
Sensory neurons (5): IL1 (IL1L/R, IL1DL/DR, IL1VL/VR),
  IL2 (IL2L/R, IL2DL/DR, IL2VL/VR), OLQ (OLQDL/DR, OLQVL/VR),
  CEP (CEPDL/DR, CEPVL/VR), ADE (ADEL/R)
Command interneurons (8): AVAL/R, AVBL/R, AVDL/R, AVEL/R
Interneurons (6): AIBL/R, AIYL/R, AIZL/R, RIML/R, RIAL/R, RIS
Motor neurons (21): DB1–DB7, DD1–DD6, VA1–VA12, VB1–VB11,
  DA1–DA9, VD1–VD13, RMD (RMDDL/DR, RMDL/R, RMDVL/VR),
  RME (RMED, RMEL/R, RMEV), SMD (SMDDL/DR, SMDVL/VR),
  SMB (SMBDL/DR, SMBVL/VR), RIV (RIVL/R), AS1–AS11
Special function (9): PVCL/R, PVPL/R, PVQL/R, DVA

## Verified Neurotransmitter Corrections
These corrections were confirmed during the enhanced descriptions
project and override any earlier or imported data:

- IL2: Acetylcholine + unknown monoamine — NOT glutamatergic
- AVE: Acetylcholine + FLP-1 — NOT glutamatergic
- RMD: Acetylcholine — NOT glutamatergic
- ASJ: NLP-3 — NOT glutamatergic
- DVA: Cholinergic — DVC is NOT cholinergic (these two are distinct)

## Verified Cell Biology Facts
These distinctions were confirmed during the enhanced descriptions
project and must not be contradicted in content or database entries:

- DD neurons: undergo synaptic remodeling during late L1
- AS neurons: all commissures to the dorsal cord occur on the
  right side; AS11 has a different anatomy in males
  (part of the preanal ganglion)
- VA/VB connectivity: VA1, VA3, VA5 and VB1, VB4, VB7 have
  slightly different connectivity than the rest of their classes
- IL2 neurons: display neuroplasticity and stage-specific
  synaptic remodeling during the dauer stage
- AWC asymmetry: AWCL and AWCR differentiation is stochastic,
  not deterministic — this must be noted in descriptions

  ## Spreadsheet Editing Guidelines (for Non-Technical Team Members)

This section is for contributors working directly in
the Google Sheets spreadsheet. It explains which columns must be filled,
which are strongly recommended, and which are optional.

### Column Priority Tiers

**REQUIRED — never leave these blank:**
- entity_id, entity_name, entity_type, wormbase_id
- species, taxon_id
- description, function
- data_source, curator_name, status

**Exception — glossary backfill stubs:** entity records created during
the WormAtlas.org glossary backfill may be entered as stubs, filling
only entity_id, entity_name, entity_type, species, taxon_id,
data_source, curator_name, and status='draft'. description, function,
and wormbase_id are left blank until enrichment. See decisions.md →
Stub Entity Records Permitted for Glossary Backfill. This exception
applies ONLY to glossary backfill — normal enrichment work still fills
every REQUIRED column.

**HIGHLY RECOMMENDED — fill these whenever possible:**
- synonyms (critical: RAG cannot match alternate names without this)
- location_description (used for spatial queries like "where is X?")
- primary_figures (RAG cites visual evidence from these)
- parent_entity_id (tells the system what larger structure this belongs to)

**OPTIONAL — helpful for RAG but not blocking:**
- common_questions (see examples below — focus on top entities first)
- key_concepts (see examples below — focus on top entities first)
- size_description

### How to Write common_questions

Think: what will a researcher type into the search bar about this entity?
Write 4-6 complete questions, separated by spaces or line breaks.

Example for **int1DL**:

What is the function of int1DL? Where is int1DL located?
What structures are visible in int1DL? What genes are expressed in
int1DL? How does int1DL differ from other intestinal cells?

Example for **intestine**:

What is the function of the intestine? How does the intestine develop?
Why does the intestine show left-right asymmetry? What genes regulate
intestinal development? How many cells make up the intestine?

Example for **EMS** (embryonic cell):

What does EMS develop into? What genes regulate EMS fate? How does EMS
divide? What signals EMS to divide asymmetrically? When does EMS appear
during development?

### How to Write key_concepts

Think: what topics, processes, or systems is this entity associated with?
Write a comma-separated list of terms. These help the search system
connect related entities even when the exact name isn't used.

Example for **int1DL**:

digestion, nutrient absorption, apical-basal polarity, microvilli,
gut granules, yolk production

Example for **intestine**:

digestion, nutrient absorption, development, morphogenesis,
left-right asymmetry, immunity, metabolism, yolk production, gut granules

Example for **EMS**:

embryonic development, cell fate specification, asymmetric division,
Wnt signaling, SKN-1, med genes, mesendoderm, gastrulation

### Priority Rule
Do not skip REQUIRED columns to fill OPTIONAL ones.
If time is limited, a complete required set on 10 entities is more
valuable than partially filled records on 50 entities.
The gold standard for a complete record is int1DL — use it as your
reference when uncertain about what "done" looks like.



