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
  Current contents (2026-11-12): 16 figures, 57 rows in `figures` (one per panel), 393 rows in `figure_entities`, and 634 rows in `anatomical_entities`. All figure classification is on the split model
  (media_type / capture_technique / is_composite).
- ENTITY IMPORT DONE (2026-10-21): scripts/import_entities.py loaded the Entities
  tab export (exports/Entities.csv, 617 rows) into anatomical_entities, then set
  figure_entities.entity_type from it. Result: 252 figure_entities rows resolved
  (cell 210, cell-group 24, organ 16, organism 2). The 54 rows still 'pending'
  are exactly the PENDING-[name] placeholders (25 distinct Type A placeholders);
  no real entity_id is left pending. Before this import (2026-10-16) the
  anatomical_entities table was empty and all 139 distinct real entity_ids in
  the figures were 'pending'. The script is re-runnable; run it after every
  Entities-tab change, and re-run import_figures.py after figure changes.
- UPDATE after CePhaFIG8, the pm3 cell-group row and the nerve-ring structure row (2026-10-26): entities import and figures import re-run. figure_entities now resolves 257 rows (cell 212, cell-group 26, organ 16, organism 2, structure 1); the 59 still 'pending' are exactly the PENDING-[name] placeholders (25 distinct Type A placeholders); no real entity_id is left pending. The change from the 2026-10-21 run: +2 cell (pm1, panels A and B), +2 cell-group (pm3, panels C and D), +1 structure (nerve-ring, panel A), +5 pending (PENDING-buccal-cavity, PENDING-pharynx x2, PENDING-pharyngeal-epithelium x2). anatomical_entities is now 619 rows (pm3 and nerve-ring added since 2026-10-21).
- UPDATE after the pm4/pm5 migration (2026-10-29): `pm4` and `pm5` are now single `cell` entities and the six member rows were removed (decisions.md, "pm4 and pm5 Are Single Syncytial `cell` Entities"). Entities import and figures import re-run; the old rows were then deleted from the database by hand because the importers never delete (bugs.md, 2026-10). anatomical_entities is now 613 rows and figure_entities 312 rows (CePhaFIG1: 8 member rows replaced by 4 rows on pm4 and pm5). The PENDING- placeholder count was not affected.
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
  - `figure_aliases` (legacy figure ID -> new ID, per decisions.md "Legacy Figure-ID Alias Mechanism") is NOT built or populated by scripts/import_figures.py. Until it exists, legacy IDs such as PhaFIG 3E-G do not resolve in the database; translate them through the crosswalk (currently v1.1).

## Figure Cataloging — Standard Prompt
- Every new figure-cataloging chat should START from the standard prompt
  template: `FIGURE_CATALOGING_PROMPT_TEMPLATE.md` (kept in
  docs/project_notes/), (project-knowledge copy under claude/). Paste it, fill in the `[TEAMMATE NAME]` placeholder and
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
- Figure ID lookups use crosswalk v1.1 (2026-10-14, WormAtlas_figure_crosswalk_v1.1_2026-10-14_Master_List.csv): 695 figure rows, 660 unique IDs. v1.0 (2026-09-30) stays in the repo as history. Pharynx IDs from PhaMOVIE 2 onward are one higher than in v1.0 (see decisions.md "Figure Crosswalk v1.1"). 

- Prompt template v2.1 (2026-10-14) merges the two diverged copies. v2.0 (project knowledge) had the frozen figure-ID rules but lacked the media_type / capture_technique / is_composite and multimedia rules; the older repo copy had those rules but old IDs and the stale entities_export.csv. v2.1 has both, points at crosswalk v1.1 and the current Entities file, specifies output as the exact 27-column Figures tab header, and adds: no "(Type B)" suffix or N/A in entity_id, reuse an existing PENDING- placeholder before creating a new one, ask rather than infer what unexplained symbols/arrows/colours mean, and ask all questions before finalizing rows. Teammate name is a [TEAMMATE NAME] placeholder. The repo copy (docs/project_notes/FIGURE_CATALOGING_PROMPT_TEMPLATE.md) and the project-knowledge copy (FIGURE_CATALOGING_PROMPT_TEMPLATE.md, top level) must stay identical; update both in the same pass whenever a decision or the crosswalk version changes.


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
- Total entities currently in spreadsheet: 634
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
- Entity types confirmed in use (have records): cell, cell-group, organ, organism, structure
- Entity types permitted but not yet populated: tissue, gene, gene-family, protein, developmental-stage, process
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
- Total (2026-11-12): 16 figures, 57 panels, 393 rows (one row per entity per panel).Figures v4 CSV is the current file. Panel-level content is on the first row of each figure + panel; extra entity rows carry only entity_id and visibility.
- Column structure: 27 columns on the split model (media_type, capture_technique, is_composite and the media-support columns; see decisions.md "Figure Type Axes Split"). The helper row's figure_id cell is exactly "Figure identifier". Any export with image_type or microscopy_technique columns is stale.
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
    (Update 2026-10-21: founder cells E, MS, EMS, ABa, ABp and the AB, K and
    PDA rows now exist in the Entities tab; check each row's wormbase_id.)
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
- SUPERSEDED for pm4 and pm5 (applied 2026-10-29; decisions.md, "pm4 and pm5 Are Single Syncytial `cell` Entities"): pm4 and pm5 are single `cell` entities (WBbt:0003739 and WBbt:0003737 kept, parent PENDING-pharynx). The six member rows pm4DL-pm4DR, pm4L-pm4VL, pm4R-pm4VR, pm5DL-pm5DR, pm5L-pm5VL and pm5R-pm5VR were retired and their ids are never reused; the labels that were on them (for example pm4DL-DR and pm4DL-pm4DR) are synonyms on pm4 and pm5; relationships rel-004 to rel-009 were removed (the numbering gap is deliberate). The statements in the bullets above about 9 member cells, 9 part_of rows (rel-004..rel-012) and the 3 cell-group rows now apply to mc3 only (mc3DL, mc3DR, mc3V; rel-010 to rel-012). The WBbt lookups owed on member cells no longer apply to the six retired pm4/pm5 members. Still owed: the single-nucleus names (for example pm4L, pm4VL) as synonyms once the team confirms them. Also SUPERSEDED for mc3 (applied 2026-11-12, CePhaFIG12 cataloguing): mc3 is now a single cell entity too, and mc3DL, mc3DR and mc3V were retired; see the mc3 retype bullet in the CePhaFIG12 entry and decisions.md.
- The 3 cell-group rows pm4/pm5/mc3 need parent_entity_id=PENDING-pharynx set
  (organ-level structural parent) if not already done during retype.
- data_source/curator_name on the 9 drafts were set to "PhaFIG1 cataloguing
  (Aug 2026)" / "[PhaFIG1 cataloguing - draft]" — align with the string the
  IntFIG3-created cells used, for consistency.
- Pre-existing cell-group gap (surfaced, not yet done): pm2, pm3, mc1, mc2
  are stored only as member cells with NO cell-group parent. Each needs the
  same treatment pm4/pm5/mc3 just got — a cell-group parent, member part_of
  rows, and organ-level parent_entity_id. Not blocking. Update 2026-11-12: closed. pm3 and pm2 were done earlier, and mc1 and mc2 now have cell-group parents (CePhaFIG12). The earlier "mc1 and mc2 still need" reminders in the CePhaFIG8 and CePhaFIG9 entries are superseded.
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
  - Update 2026-10-21: both group rows were added to the Entities tab as
    draft stubs, and the five part_of rows (virL, virR, rect_D, rect_VL, rect_VR)
    were added to the Relationships tab. Class-level WBbt lookups remain owed
    where the wormbase_id cell is still blank.

- alimentary-system entity row owed (approved 2026-08-31): created so it is a
  real structural parent, resolving the dangling intestine -> alimentary-system
  reference and serving the new valve/gland groups. WBbt looked up
  individually; NULL if none. See bugs.md (2026-08 parent_entity_id integrity).
  Update 2026-10-21: the row now exists in the Entities tab (draft stub,
  entity_type organ). wormbase_id lookup still owed if blank.

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

- CePhaFIG7 (Pharynx chapter, legacy PhaFIG 3E-G) catalogued October 2026: 3 panels (A diagram, B TEM, C TEM at higher magnification than B), 16 figure_entities rows, all seven entities Type A. Image source Hall archive. Panel B shows six black and three white arrows. Panel A's page legend should read "left, middle, right". New PENDING- placeholders: PENDING-blastopore (CePhaFIG6 panel B), PENDING-pharyngeal-lumen, PENDING-marginal-cells, PENDING-intermediate-filaments, PENDING-basal-lamina, PENDING-pharyngeal-muscle, PENDING-pharyngeal-channels. Reused: PENDING-adherensjunction, PENDING-pharynx. Check whether PENDING-pharyngeal-lumen duplicates the existing PENDING-lumen. Stub count unaffected.
- CePhaFIG8 (Pharynx chapter, legacy PhaFIG 4A-D) catalogued October 2026: 4 panels, 10 figure_entities rows. Panel A epifluorescent (pm1, 400x); B merged DIC + epifluorescence, same animal as A (400x); C epifluorescent (pm3 and pharyngeal epithelium, 600x); D merged DIC + epifluorescence, same animal as C (600x). Legend gives magnification for A and C only; the B and D values were assigned by Chris Crocker. Crosswalk v1.1 maps PhaFIG 4A-D to CePhaFIG8 with no split, so old and new panel letters are identical. Panel-level metadata: strain = "PENDING — strain not yet confirmed"; image_source, specimen_stage, specimen_sex, scale_bar and view_orientation left blank (outstanding); source_reference = N/A. By Chris Crocker's decision image_source is blank, so the legend's strain-source credit (Z-W. Wang and B. Chen) is not recorded anywhere in the rows (RectFIG2 recorded it in image_source); revisit if that credit should be captured. Panel D has no on-image labels, so its entity rows (pm3, PENDING-pharyngeal-epithelium, PENDING-pharynx) rest on panel C and the legend. The teammate's description said the panel D overlay came from "PhaFIG4B"; it is panel C, so correct that wherever the description text is reused. Panel B labels "Anterior bulb" and "Posterior bulb" are pharyngeal landmarks, not entities, so they have no entity rows and no placeholders; the labels are kept only as text in panel B's description_in_figure and ai_summary (decisions.md → Region and Landmark Labels in Figures Are Not Entities). An earlier draft of this figure had 12 rows including PENDING-anterior-bulb and PENDING-posterior-bulb; those two were removed on 2026-10-26.
- CePhaFIG8 entities: real ids `pm1` (existing row, cell, WBbt:0003744), `pm3` (Type B, added as a cell-group, see the pm3 bullet) and `nerve-ring` (Type B, added as the first `structure` record, see the nerve-ring bullet). No new Type A placeholders were introduced. Reused: PENDING-buccal-cavity, PENDING-pharyngeal-epithelium, PENDING-pharynx. PENDING-nerve-ring was used in the first draft and has been replaced by `nerve-ring` in panel A. Running PENDING- set is now 25 distinct placeholders: PENDING-uterus, PENDING-gut-granules, PENDING-pharynx, PENDING-rectum, PENDING-adherensjunction, PENDING-vulva, PENDING-preanal-ganglion, PENDING-lumen, PENDING-pharyngeal-epithelium, PENDING-pharyngeal-intestinal-valve, PENDING-buccal-cavity, PENDING-radial-channels, PENDING-sieve, PENDING-grinder, PENDING-anus, PENDING-embryo, PENDING-proximal-gonad, PENDING-distal-gonad, PENDING-blastopore, PENDING-pharyngeal-lumen, PENDING-marginal-cells, PENDING-intermediate-filaments, PENDING-basal-lamina, PENDING-pharyngeal-muscle, PENDING-pharyngeal-channels. Still open from CePhaFIG7: check whether PENDING-pharyngeal-lumen duplicates PENDING-lumen. Stub count unaffected.
- pm3 cell-group created (CePhaFIG8 cataloguing, October 2026): panel C labels the bare muscle class "pm3", which had no cell-group row — the same pre-existing gap as pm6/pm7 (resolved in PhaFIG2). Actioned: 1 cell-group row `pm3` added to the Entities tab (status=draft, parent_entity_id=PENDING-pharynx, data_source "CePhaFIG8 cataloguing (Oct 2026)"), and 3 part_of rows added to the Relationships tab (pm3DL-pm3DR, pm3L-pm3VL and pm3R-pm3VR part_of pm3, numbered rel-024, rel-025 and rel-026 respectively). Member cells needed no change (already parent_entity_id=PENDING-pharynx with their own WBbt IDs). The class-level WBbt lookup is DONE: wormbase_id WBbt:0003740, looked up by Chris Crocker in the WormBase Ontology Browser on 2026-10-26 (distinct from the three member IDs, not inferred from them), wormbase_url set to the standard pattern. STILL OWED before pm3 leaves draft: function/common_questions/key_concepts enrichment. Pre-existing gap now narrowed: pm2, mc1 and mc2 still need the same treatment (this supersedes the earlier "pm2, pm3, mc1, mc2" reminders above). Not blocking.
- nerve-ring entity created (CePhaFIG8 cataloguing, October 2026): panel A labels the nerve ring ("NR"), which had no Entities-tab row and no glossary anchor (confirmed by Chris Crocker). By decision (decisions.md → Nerve Ring entity_id Is the Descriptive Hyphenated Form `nerve-ring`) it was added as a draft stub: entity_id `nerve-ring`, entity_name "Nerve ring", entity_type `structure` (the FIRST `structure` record), wormbase_id WBbt:0006749 (looked up by Chris Crocker, 2026-10-26, recorded as supplied), parent_entity_id NULL (no nervous-system entity exists yet; none invented), data_source "CePhaFIG8 cataloguing (Oct 2026)". The panel A figure row now uses `nerve-ring` in place of PENDING-nerve-ring. STILL OWED before it leaves draft: function, common_questions, key_concepts and a Hall/Schroeder check of the description; a structural parent once a nervous-system entity exists. This is a one-entity exception to the glossary-anchor-slug rule, not a new general rule.
- CePhaFIG9 (Pharynx chapter, legacy PhaFIG 4E-I) catalogued October 2026: 5 lettered panels, 6 panel rows (A; B-main and B-inset; C; D; E), 20 figure_entities rows. Old-to-new panel mapping: E to A, F to B (the larval inset is B-inset), G to C, H to D, I to E. Crosswalk v1.1 row still flagged "re-confirm after renumber". Source material prepared by Nate Schroeder. Panel A epifluorescent (hyp1, 400x, adult); B-main merged DIC + epifluorescence, same animal as A (400x, adult); B-inset epifluorescent, larval animal, same strain, magnification not given; C epifluorescent (arcade cells, pm3, 600x); D the same image as C, magnified, magnification not given; E DIC with WormAtlas colour overlay (image, DIC, is_composite 1). Magnification 400x for B-main and E was supplied by Chris Crocker (the legend gives 400x for the E/F pair only; none for I). Panel-level metadata: strain "PENDING — strain not yet confirmed" on all panels; image_source blank (the legend's strain-source credit, Z-W. Wang and B. Chen, is not recorded); scale_bar N/A; view_orientation "anterior to the left"; specimen_sex blank; specimen_stage A and B-main adult (legend), B-inset larval (legend, stage not named), E adult (supplied by Chris Crocker), C and D blank (not stated). Panel E colour key supplied by Chris Crocker: hyp1 dcc3ac, arcade cccc00, pharyngeal epithelium 996699, pharyngeal muscle 33cc00. No new PENDING- placeholders; reused PENDING-buccal-cavity (visible in A, B-main, C, D) and PENDING-pharyngeal-epithelium (E). Running PENDING- set stays at 25 distinct placeholders. Source-text corrections to make when the chapter text is migrated: "4E-1" should read "4E-I"; "adultanterior" needs a space; the bare "PhaFIG 5" in the associated text is ambiguous (5A-C is CePhaFIG10, 5D-E is CePhaFIG11); legacy InterFIG 3 is CeInterFIG4 in v1.1.
- Entities added by CePhaFIG9 (13 rows, all status draft; Entities 613 to 626):
  - `pm2` (cell-group, WBbt:0003742 supplied by Chris Crocker, not verified by Claude; parent PENDING-pharynx), with part_of rows rel-027 to rel-029 (pm2DL-pm2DR, pm2L-pm2VL, pm2R-pm2VR). This closes the pm2 gap; pm2 no longer needs a parent. mc1 and mc2 still need cell-group parents.
  - `arcade-cells`, `anterior-arcade`, `posterior-arcade` (cell-group, parent alimentary-system, wormbase_id blank), and nine arcade `cell` rows (parent alimentary-system) with WBbt ids supplied by Chris Crocker, not verified by Claude: arc ant DL WBbt:0004572, arc ant DR WBbt:0004571, arc ant V WBbt:0004573, arc post D WBbt:0004565, arc post DL WBbt:0004570, arc post DR WBbt:0004569, arc post V WBbt:0004567, arc post VL WBbt:0004568, arc post VR WBbt:0004566. Membership rows rel-030 to rel-040. See decisions.md, "Arcade Cells Are Modelled as cell-group Entities". (The first message gave arc ant DL and DR the same id, 0004572; DR was corrected to 0004571 on 2026-10-30.)
  - STILL OWED before any of these leave draft: class-level WBbt lookups for `arcade-cells`, `anterior-arcade`, `posterior-arcade` and a check of the supplied ids; description, function, synonyms, common_questions and key_concepts for the cells; Hall/Schroeder confirmation of the cell-group classification; primary_figures for hyp1, pm3 and the new rows.
- Relationships tab now holds rel-001 to rel-003 and rel-010 to rel-051. The gap rel-004 to rel-009 is deliberate.
- After the CePhaFIG9 import (confirmed 2026-11-02): anatomical_entities 626; 13 figures and 49 panel rows; figure_entities 332; 64 figure_entities rows still pending, all PENDING-[name] placeholders. CePhaFIG9 itself resolves as 6 cell, 9 cell-group and 5 pending rows.
- CePhaFIG10 (Pharynx chapter, legacy PhaFIG 5A-C) catalogued November 2026: 3 lettered panels, 4 panel rows (A-main diagram, A-inset DIC, B TEM, C TEM), 18 figure_entities rows. Crosswalk v1.1 maps PhaFIG 5A-C to CePhaFIG10 with no split, so old and new panel letters are identical (the crosswalk row still says "re-confirm after renumber"). Source material prepared by Nate Schroeder. A-main: diagram, adult, source_reference Albertson1976 (the legend says "Based on Albertson and Thomson, 1976"), image_source blank; e1, e2 and e3 are purple (996699) and e3 is a greyish purple with a slight hue shift for visibility (colour key supplied by Chris Crocker). A-inset: DIC micrograph that locates the levels of B and C, no labels, scale_bar N/A (matching CePhaFIG9), image_source blank. B: TEM, transverse section, transition between the posterior arcade cells and the pharyngeal epithelium, [MRC] N2T A60-8, scale bar 1 μm. C: TEM, transverse section, e1 and e2 cells, [MRC] N2T A60-22, scale bar 1 μm assigned by Chris Crocker (same scale as B; the bar is drawn only in B). Strain "PENDING — strain not yet confirmed" on A-inset, B and C; stage and sex blank except A-main stage adult; magnification blank on B and C (outstanding). The buccal cavity row on A-inset uses the legend wording "encircle the anterior of the pharynx". The "short clockwise turn in front of pm1" is viewed from the front (mouth) of the worm, per Chris Crocker; the legend does not say so.
- Entities added by CePhaFIG10 (3 rows, all status draft; Entities 626 to 629): `e1`, `e2`, `e3` (cell-group, parent PENDING-pharynx), with WBbt ids supplied by Chris Crocker and NOT verified by Claude: e1 WBbt:0003718, e2 WBbt:0003716, e3 WBbt:0003714 (update 2026-11-09: e1, e2 and e3 all confirmed by Chris Crocker). Membership via part_of, rel-041 to rel-049 (e1D, e1VL, e1VR to e1; e2DL, e2DR, e2V to e2; e3D, e3VL, e3VR to e3). The nine existing member cells had a blank parent_entity_id; it is now PENDING-pharynx. Their descriptions are still the WormFindr stubs.
- Placeholders for CePhaFIG10: no new PENDING- placeholders (still 25 distinct). Reused PENDING-pharyngeal-epithelium, PENDING-pharyngeal-lumen, PENDING-pharynx, PENDING-buccal-cavity and PENDING-adherensjunction. (Chris Crocker wrote "PENDING-adherens-junctions"; the existing PENDING-adherensjunction was used to avoid a near-duplicate.) Still open: whether PENDING-pharyngeal-lumen duplicates PENDING-lumen. After the CePhaFIG10 import (confirmed 2026-11-04): anatomical_entities 629; 14 figures and 53 panel rows; figure_entities 350; 73 pending, all PENDING-[name] placeholders; CePhaFIG10 itself resolves as 9 cell-group and 9 pending rows. Backup taken first (~/Desktop/wormatlas_local_backup_2026-11-04.sql, outside the repo, never commit). Dev and production were not touched.
- Owed review (CePhaFIG10): Hall/Schroeder to confirm the e1/e2/e3 cell-group classification and the parent (PENDING-pharynx here; the arcade groups use alimentary-system); the clockwise-turn viewpoint; the legend's cell-body distances (about 30, 20 and 35 μm for e1, e2 and e3, from Albertson and Thomson 1976, not checked); the three WBbt ids (confirmed by Chris Crocker, 2026-11-09). Outstanding: strain, stage and sex on all imaged panels, magnification on B and C, description/function/synonyms/common_questions/key_concepts for the nine e-cells, and primary_figures on them. Source-text corrections when the chapter text is migrated: the bare "PhaFIG 5" is ambiguous (5A-C is CePhaFIG10, 5D-E is CePhaFIG11); "PhaFIG5 D&E" is CePhaFIG11; PhaFIG 4A-D is CePhaFIG8 and 4E-I is CePhaFIG9; InterFIG 1 is CeInterFIG1; InterFIG 3 is CeInterFIG4; DCutFIG4 is CeDauerCutFIG4.
- Owed review (CePhaFIG8): the CePhaFIG8 crosswalk row is marked verified (CC, 09/30) but still carries "re-confirm after renumber". Hall/Schroeder confirmed the `structure` classification and the id `nerve-ring` (received 2026-10-27; decided by Chris Crocker, 2026-10-26).
- wormbase_id corrections (2026-11-04): four Entities rows had a wrong wormbase_id and were corrected in the Sheet, then re-exported and re-imported into wormatlas_local. ILshR changed from WBbt:0004531 (the same id as ILshDR, so a duplicate) to WBbt:0004527. ILsoVR changed from WBbt:000450 to WBbt:0004501. OLQVR changed from WBbt:000443 to WBbt:0004431. RIH changed from WBbt:000392 to WBbt:0003928. ILsoVR, OLQVR and RIH had truncated six-digit ids; each new id matches the row's existing wormbase_url, and no other entity uses any of the four. The new ids were supplied by Chris Crocker and NOT verified by Claude against the WormBase Ontology Browser; check them there when convenient. The problem surfaced while reviewing the exports diff for the CePhaFIG10 pull request (OLQVR first, then a scan of the export for the other three). That scan covered only rows that have both a wormbase_id and a wormbase_url; at the time it found no other id that was not seven digits or that disagreed with its URL. Entities with a blank wormbase_url were not scanned. Local database only; dev and production were not touched.
- OLQ synonym edits by a teammate (2026-11-04): a teammate edited ten OLQ rows in the Entities tab between the 2026-11-02 export and the CePhaFIG10 export: OLQshDL, OLQshDR, OLQshVL, OLQshVR, OLQsoDL, OLQsoDR, OLQsoVL, OLQsoVR, OLQVL and OLQVR. Per Chris Crocker these are synonym edits. The rows were imported with the CePhaFIG10 batch and committed in the CePhaFIG10 pull request (the commit message names them). They were not compared column by column, so the claim that only synonyms changed rests on Chris Crocker's account.
- CePhaFIG11 (Pharynx chapter, legacy PhaFIG 5D-E) catalogued November 2026: 3 panels (A-main, A-inset, B), 16 figure_entities rows (A-main 8, A-inset 2, B 6). Crosswalk v1.1 maps PhaFIG 5D-E to CePhaFIG11 (the row still says "re-confirm after renumber"; it was CePhaFIG10 in v1.0). The crosswalk is per figure and carries no panel letters, so the old-to-new panel mapping was confirmed by Chris Crocker: legacy D to A-main, legacy E to B, and the DIC micrograph is A-inset. Source material prepared by Nate Schroeder. A-main: TEM, transverse section, [MRC] N2T A61-11, scale bar 1 μm. A-inset: DIC, anterior to the left (supplied by Chris Crocker), locates the approximate levels of A-main and B, scale_bar N/A, image_source blank. B: TEM, transverse section, [MRC] N2T A63-4, scale bar 1 μm assigned by Chris Crocker (B shares the scale of A-main; the bar is drawn only in A-main). Strain "PENDING — strain not yet confirmed" on all three panels; stage, sex and magnification blank; source_reference N/A; is_composite 0. Marker key confirmed by Chris Crocker: white arrowheads = adherens junctions, black arrows = intermediate filaments, black arrowheads = half-desmosomes (the legend gives "arrowheads" for half-desmosomes without a colour). The legend's three cuticular flaps are recorded as three; arrow and label counts are not stated. The legend sentence "(Top inset) Section level." was read as describing the DIC inset (neither EM panel has an inset of its own); correct the legend text at chapter migration.
- Entities for CePhaFIG11: real ids e2, e3, pm1 and I2; the e2 and e3 WBbt ids (WBbt:0003716 and WBbt:0003714) were confirmed by Chris Crocker on 2026-11-09. posterior-arcade was deliberately not used (see the owed review below). Reused placeholders: PENDING-pharyngeal-epithelium, PENDING-adherensjunction, PENDING-intermediate-filaments, PENDING-pharyngeal-lumen, PENDING-basal-lamina, PENDING-pharynx and PENDING-buccal-cavity. Two NEW Type A placeholders: PENDING-hemidesmosome (the legend says "half-desmosome", the chapter text "hemidesmosome") and PENDING-cuticular-flaps. The running PENDING- set is now 27 distinct placeholders. Stub count unaffected. The lumenal cuticle has no row.
- I2 cell-group created (CePhaFIG11 cataloguing, November 2026): panel B labels the bare class "I2", and only I2L and I2R existed. Same pre-existing gap as pm3 and pm6, resolved under the binding cell-group rule; no new decision. Entities 629 to 630. `I2`: cell-group, parent PENDING-pharynx, status draft, WBbt:0003645 supplied and confirmed by Chris Crocker (2026-11-09; not independently checked by Claude), wormbase_url standard pattern, developmental_stage and sex copied from I2L and I2R (L1, hermaphrodite), description taken from the I2L and I2R records, primary_figures CePhaFIG11, data_source "CePhaFIG11 cataloguing (Nov 2026)". Membership via part_of: rel-050 (I2L to I2) and rel-051 (I2R to I2). I2L and I2R had a blank parent_entity_id; it is now PENDING-pharynx (their WBbt ids WBbt:0004744 and WBbt:0004743 are unchanged). Panel B carries `I2` (labeled), not I2L, as confirmed by Chris Crocker.
- After the CePhaFIG11 import (confirmed 2026-11-05 by query on wormatlas_local): anatomical_entities 630; 15 figures and 56 panel rows; figure_entities 366; 83 pending, all PENDING-[name] placeholders (27 distinct); CePhaFIG11 itself resolves as 5 cell-group, 1 cell and 10 pending rows. The Sheet export came back re-sorted, so the commit shows many moved rows; compare_entities_export.py and compare_figures_export.py confirmed that apart from the new rows only I2L and I2R changed. Dev and production were not touched.
- Owed review (CePhaFIG11): resolved 2026-11-09. Chris Crocker confirmed the I2 cell-group classification, I2's parent (PENDING-pharynx), that the black arrowheads mark the half-desmosomes, and the WBbt ids for I2 (WBbt:0003645), e2 (WBbt:0003716) and e3 (WBbt:0003714); the ids were not independently checked by Claude. Source-text conflicts, all resolved in the data by following the legend: Nate Schroeder's description says both EM panels are "from the buccal cavity" while the legend says pharyngeal epithelium (Chris Crocker's note is that the pharyngeal epithelium is part of the buccal cavity; not encoded in the data, check against the chapter text, which says the epithelial cells secrete the cuticle that lines the buccal cavity); the chapter text puts the prominent adherens junctions where the epithelium meets the posterior arcade cells (PhaFIG5 D&E) whereas the legend says the A-main junctions join e2 and e3 and no arcade cells are labelled; the chapter text says the filaments are anchored to apical and basal membranes by hemidesmosomes whereas the legend only says lumenal cuticle to basal lamina. The ai_summary text follows the legend only.
- Outstanding (CePhaFIG11): strain on all three panels; stage, sex and magnification on the imaged panels (all recorded as unknown on 2026-11-09: not obtainable from the source material, so left as is); common_questions and key_concepts for I2 (the description and function for I2, I2L and I2R were written on 2026-11-10, and CePhaFIG11 was added to primary_figures on I2L and I2R); primary_figures on e2, e3 and pm1 (add CePhaFIG11). The AI questions follow the Nate Schroeder drafts with these edits: his question about the basal lamina and "buccal cavity lumen" was reworded to ask what anchors the pharyngeal epithelial cells to the basal lamina; his "pharyngeal flaps" question was reworded to "cuticular flaps" to match the legend; his adherens-junction question was made panel-specific; each panel has at least 3 questions.
- Source-text corrections when the chapter text is migrated: "Associated test" should read "Associated text"; the bare "PhaFIG 5" is ambiguous (5A-C is CePhaFIG10, 5D-E is CePhaFIG11); "Level slightly posterior to C" in the 5D legend refers to CePhaFIG10 panel C; PhaFIG 4A-D is CePhaFIG8 and 4E-I is CePhaFIG9; InterFIG 1 is CeInterFIG1; InterFIG 3 is CeInterFIG4; DCutFIG4 is CeDauerCutFIG4.
- I2 classification and function update (2026-11-10): Nate Schroeder and David Hall replied (2026-11-09 and 2026-11-10) that most pharyngeal neurons are now considered polymodal (structural evidence for most; solid functional data for I2), that assignments in earlier publications have changed and WormAtlas should reflect that, and that the legacy I2 page should state that I2 regulates light-induced inhibition of feeding (Bhatla et al., 2015). The legacy WormAtlas I2 page lists the type as "Pharyngeal interneuron (also anterior sensory?)". The Entities rows I2, I2L and I2R were updated: the description now says I2 is a pair of pharyngeal neurons, classed as interneurons in earlier publications and now understood as polymodal (the embryonic lineage strings on I2L and I2R are unchanged); function is "Regulates light-induced inhibition of feeding (pharyngeal pumping) (Bhatla et al., 2015)."; primary_figures CePhaFIG11 was added to I2L and I2R; synonyms were extended. I2 stays draft and I2L and I2R stay review. The mechanism (GUR-3, PRDX-2, glutamate release acting through AVR-15) was seen only in a conference abstract, so it was deliberately not entered; add it once the full 2015 paper has been checked. Owed: other pharyngeal neuron pages, and WormFindr-imported records, may still carry older interneuron or sensory labels; check each as it is reached, and update the legacy WormAtlas I2 page with the function statement. Imported to wormatlas_local on 2026-11-10: anatomical_entities 630 (unchanged), figure_entities 366, 83 pending. Backup taken first (~/Desktop/wormatlas_local_backup_2026-11-09.sql, outside the repo, never commit). Dev and production were not touched.
- Synonym enrichment by Bridget Brokaw (2026-11-10), 24 Entities rows: PDB, PHAL, PHAR, PHBL, PHBR, PHCL, PHCR, PHshL, PHshR, PHso1L, PHso1R, PHso2L, PHso2R, PLML, PLMR, PLNL, PLNR, pm1, pm2, pm2DL-pm2DR, pm2L-pm2VL, pm2R-pm2VR, pm3DL-pm3DR and pm3L-pm3VL. On the phasmid and posterior neurons, the third synonym (a copy of the entity_id in capitals) was replaced by the cell's full name; on the pharyngeal muscle rows, descriptive names such as "first layer pharyngeal muscle cell" were added. Before import, Chris Crocker restored five synonyms that the edits had dropped (pm2DL-pm2DR, pm2L-pm2VL, pm2R-pm2VR, pm3DL-pm3DR, pm3L-pm3VL) and removed two trailing spaces (PHCR, PHshL); the names for PDB ("Preanal Cell Body Dorsal Axon B") and PLNL/PLNR ("Posterior Lateral N Left/Right") were confirmed by Chris Crocker. A read-only check found no old synonym dropped, and compare_entities_export.py showed only the synonyms column changed on these 24 rows. The Sheet-to-export compare is order-insensitive; a new compare_entities_export.py (keyed on entity_id) was written on 2026-11-10 because the earlier copy was not on the Desktop.
- CePhaFIG12 (Pharynx chapter, legacy PhaTABLE 1, "Characteristics of pharyngeal muscle cells and marginal cells") catalogued November 2026: 1 panel row (panel A), 28 figure_entities rows. Crosswalk v1.1 maps PhaTABLE 1 to CePhaFIG12 (media TABLE; in v1.0 it was CePhaFIG11, which is now legacy PhaFIG 5D-E). media_type table, capture_technique N/A, is_composite 0 (confirmed by Chris Crocker: the table does not combine sources). magnification, view_orientation, scale_bar and strain N/A; specimen_stage and specimen_sex left blank (outstanding); image_source ©WormAtlas; source_reference lists Albertson and Thomson 1976, Bhatla et al. 2015, Cook et al. 2019 and Harry et al. 2022. The teammate who prepared the source material is not recorded. Nate Schroeder confirmed (2026-11-10) that the pm5 "I3" superscript is a typo for footnote c, that "apm4" in the legend is footnote a plus "pm4 and pm5" (the footnote a text is stated once), and that pm1 as a single six-nucleus syncytium is correct (no explanation exists because it goes back to Albertson and Thomson 1976).
- CePhaFIG12 entity rows: pm1-pm8, mc1, mc2 and mc3 primary (11); neuron classes M1, M2, M3, M4, M5, MI, NSM, I1, I2, I3, I4, I5, I6 and MC labeled (14); PENDING-pharyngeal-muscle, PENDING-marginal-cells and PENDING-pharynx visible (3). No new PENDING- placeholders; the running set stays at 27 distinct placeholders.
- The table is an image only. Its full contents, with footnote letters in square brackets and footnotes a-e, are in text_alternative (the retrieval surface). Footnote e ("Leon Avery, pers. comm.") sits on pm4's MC and pm6's M4 only (confirmed). The new site will use a native HTML table (decisions.md); media_file and media_format are N/A. Synaptic input is not modelled as relationships (the Relationships tab has only part_of and adjacent_to); see decisions.md.
- Entities added by CePhaFIG12 (7 rows, all status draft, parent PENDING-pharynx; Entities 627 to 634): cell-group rows mc1 (WBbt:0003709), mc2 (WBbt:0003708), M2 (WBbt:0003634), M3 (WBbt:0003754), NSM (WBbt:0003666), MC (WBbt:0003638) and I1 (WBbt:0003649). WBbt ids supplied by Chris Crocker, not verified by Claude in the Ontology Browser. Relationships rel-052 to rel-067 (16 part_of rows, evidence_source CePhaFIG12): mc1DL/mc1DR/mc1V, mc2DL/mc2DR/mc2V, M2L/M2R, M3L/M3R, NSML/NSMR, MCL/MCR and I1L/I1R. This closes the mc1/mc2 cell-group gap. Descriptions were built only from the existing member rows and the table; the neuron classes are described as "pharyngeal neurons" without the old interneuron/motor labels (Hall: assignments have changed).
- mc3 retyped (applies decisions.md, "pm4 and pm5 Are Single Syncytial 'cell' Entities", to mc3): `mc3` changed from cell-group to cell (WBbt:0003707 and parent PENDING-pharynx kept); mc3DL, mc3DR and mc3V retired and never reused, with the three labels now synonyms on mc3; rel-010 to rel-012 removed. CePhaFIG1 edited to match: panel A mc3DL became mc3 and panel B mc3DR became mc3 with mc3V deleted (3 rows became 2); the on-image labels mc3DL, mc3DR and mc3V stay in the panel descriptions. The old database rows were deleted by hand because the importers never delete (bugs.md, 2026-10).
- After the CePhaFIG12 import (confirmed 2026-11-12): anatomical_entities 634; 16 figures and 57 panel rows; figure_entities 393; 86 figure_entities rows pending, all PENDING-[name] placeholders (27 distinct). Relationships tab: 58 rows (rel-001 to rel-003, rel-013 to rel-051, rel-052 to rel-067); next id rel-068; the gap rel-004 to rel-012 is deliberate.
- Pharynx figures not yet catalogued: CePhaFIG3, 4, 5 (movies; multimedia and accessibility rules apply), CePhaFIG13 and CePhaFIG14.
- Source-text corrections for chapter migration (associated text of PhaTABLE 1): remove the statement that most pharyngeal muscle segments are made up of three two-nucleus cells (Chris Crocker's instruction; the table shows pm1, pm4 and pm5 as single six-nucleus syncytia, and no source explains pm1 beyond Albertson and Thomson 1976, confirmed by Nate); "apm4 and pm5" in the legend is footnote a plus "pm4 and pm5"; the stray full stop before MC in the pm4 row is a comma; the bare "PhaFIG 3" (3A-D is CePhaFIG6, 3E-G is CePhaFIG7) and bare "PhaFIG 6" (6A-C is CePhaFIG13, 6D is CePhaFIG14) are ambiguous and need resolving; the other references translate as PhaFIG 2 = CePhaFIG2, PhaFIG 6A-C = CePhaFIG13, PhaFIG 6D = CePhaFIG14, PhaFIG 7A = CePhaFIG15.
- STILL OWED for the 7 new cell-groups: function, common_questions, key_concepts, primary_figures (mc1 and mc2 are primary in CePhaFIG12), WBbt checks in the Ontology Browser, and Hall/Schroeder confirmation of the cell-group classification. Open question: whether the 10 neuron member cells (M2L, M2R, M3L, M3R, NSML, NSMR, MCL, MCR, I1L, I1R) should get parent PENDING-pharynx like I2L and I2R. The crosswalk v1.1 row for PhaTABLE 1 still says "re-confirm after renumber".

- Owed review: Hall/Schroeder to confirm the CeIntFIG2 panel C-bottom summary's claim that the nuclear GFP signal "corresponds to the nucleolus" (unverified).
- Owed cleanup: the int1DL primary_figures still cites the bare legacy "IntFIG5", which now splits into more than one figure. An editor needs to pick the right new ID.

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



