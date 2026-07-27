# WormAtlas Architecture Decisions

## How to Use This File
Decisions logged here are binding. Before recommending any library,
framework, or architectural pattern, check this file first. If a request
conflicts with a logged decision, flag the conflict explicitly before
proceeding. Never silently override a prior decision. If a decision
genuinely needs to change, say so and offer to draft an updated entry.

Status key:
- DECIDED — Finalized, do not revisit without team sign-off
- PENDING — Not yet discussed or confirmed
- REJECTED — Considered and ruled out (reason logged)

---

## PLATFORM & HOSTING

### Decision: University of Illinois Hosting — DECIDED
- All server infrastructure runs through the University of Illinois
- All server-level decisions must be coordinated with IT admin Greg Parks
- Do not suggest third-party hosting solutions without flagging this constraint first
- Logged: Project start

### Decision: Version Control — ACES GitHub Instance — DECIDED
- Git hosting platform: University of Illinois ACES GitHub instance
- Greg Parks offered the ACES instance in June 2026; offer accepted
  in writing by Chris Crocker
- Action still required: follow up with Greg Parks to get the
  instance set up and team access provisioned — this has not
  yet happened as of the date of this entry
- Branch naming, commit message format, and all other Git conventions
  remain as documented in conventions.md
- Logged: June 2026

### Decision: Two-Environment Setup — DECIDED
- Production site: wormatlas.org
- Development site: dev.wormatlas.org
- All work is built and tested on dev before touching production
- Local development uses XAMPP on MacBook Pro
- Logged: Project start

---

## CMS

### Decision: Custom PHP/MySQL CMS Only — DECIDED
- No off-the-shelf CMS tools (WordPress, Drupal, etc.)
- Reason: Domain-specific scientific content requires custom data models
  that general CMS tools cannot accommodate without significant compromise
- The CMS must support: handbook chapters, media, image galleries,
  links, pages, references, anatomical entities
- User roles required: Admin, Editor, Contributor
- Logged: Project start

### Decision: CMS Must Support Non-Technical Editors — DECIDED
- All content editing workflows must be operable by non-technical users
- Every editing task must have an accompanying reference guide
- Non-technical team members: Laura Herndon, Cathy Wilkow,
  Eli Conklin, Malia Jennings
- Logged: Project start

---

## API

### Decision: REST API — DECIDED
- API style: RESTful (not GraphQL)
- Reason: PHP-based project serving a small team. REST is simpler to
  build, easier to maintain, better supported by the existing PHP stack,
  and does not require the overhead of a GraphQL layer
- All endpoints versioned: /api/v1/...
- All API responses follow a consistent envelope format:
  {
    "data": { },
    "meta": { "total": 100, "page": 1 },
    "error": null
  }
- Pagination required on all list endpoints — no unbounded queries
- HTTP status codes used correctly and consistently
- All error responses include a human-readable message and a
  machine-readable code
- GraphQL: REJECTED — unnecessary complexity for this stack and team size
- Logged: January 2026

---

## RAG SEARCH ASSISTANT

### Decision: RAG Search Is a Primary Deliverable — DECIDED
- The AI-powered anatomy search assistant is a core feature, not an add-on
- It must be treated with the same architectural priority as the CMS
- Any decision that affects data structure, annotations, or search pipeline
  must flag downstream RAG impact before proceeding
- Logged: Project start, confirmed by lab directors David Hall and Nate Schroeder

### Decision: Phased RAG Implementation — DECIDED
- Phase 1 (Foundation): Build clean structured data infrastructure
- Phase 2 (AI Integration): Deploy AI-powered search using Phase 1 foundation
- Phase 3 (Enhancement): Expand based on researcher feedback
- Phase 1 is not "instead of AI" — it is the prerequisite for AI
- Logged: Project start

### Decision: RAG Phase 1 Scope — Nervous System Cells First — DECIDED
- First meaningful RAG deployment targets nervous system cells (316 cells)
- Reason: Largest single organ system, most searched by researcher audience
- Other systems added in subsequent phases
- Logged: Spreadsheet analysis, January 2026

### Decision: RAG AI Assistant Scope and Guardrails — DECIDED
- The AI assistant answers questions grounded strictly in WormAtlas content only
- Every AI-generated answer must include source citations linking back
  to the specific WormAtlas page or document used for retrieval
- The assistant must refuse and explain when a query falls outside
  WormAtlas content scope
- Out of scope: general biology Q&A not in WormAtlas corpus, medical
  advice, anything outside nematode biology
- Reason: Scientific credibility requires transparency. Researchers
  cannot use unsourced AI answers
- Logged: January 2026

### Decision: Embeddings Service — voyage-3.5 — DECIDED
- Provider: Voyage AI
- Model: voyage-3.5
- Pricing: $0.06 per 1 million tokens (as of May 2026)
- Reason: Purpose-built for retrieval tasks; outperforms general-purpose
  models on domain-specific scientific vocabulary; same cost as
  voyage-3 but current-generation quality; integrates directly
  with ChromaDB (already selected for vector storage)
- voyage-3 (original candidate): REJECTED — now legacy generation;
  voyage-3.5 is the same price with better retrieval quality
- voyage-4: Considered; free tier available but pricing tier not yet
  confirmed for production; revisit if corpus grows significantly
  beyond initial 574 entities
- OpenAI embeddings: REJECTED — higher cost, general-purpose design,
  history of disruptive model deprecations
- Cohere: REJECTED — no meaningful advantage over Voyage AI for
  this use case
- Logged: May 2026

### Decision: Embeddings Model Upgrade Strategy — DECIDED
- The model name must be stored in a config variable or environment
  variable — never hardcoded across multiple files
- A re-indexing script must be written and documented as part of the
  initial build; it must accept the model name as a parameter so
  future upgrades require no new code
- When a newer model releases (e.g. voyage-4, voyage-5):
  - No action is required immediately — existing vectors remain valid
  - Upgrade is worthwhile when retrieval quality improvement is
    confirmed by Voyage AI benchmarks
  - Upgrade process: update model name in config → run re-indexing
    script → verify search quality → done
  - If vector dimensions change between model versions, the
    re-indexing script must drop and recreate the ChromaDB collection
    rather than overwriting in place
- When Voyage AI announces a deprecation (expected 6-12 months notice):
  - Treat as a scheduled maintenance window, not an emergency
  - Upgrade process is identical to above
- Estimated time for a full model upgrade at current corpus size: 2 hours
- Logged: May 2026

### Decision: Vector Storage — Two-Environment Approach — PROVISIONAL
- Local development (MacBook): ChromaDB
  - Reason: Free, runs locally, zero server dependency during build phase
  - No involvement from Greg Parks or university IT required
- Dev server and production: PostgreSQL + pgvector extension
  - Reason: Greg Parks is already setting up a PostgreSQL instance;
    storing vectors inside PostgreSQL means IT manages it identically
    to all other databases — no separate system required
  - pgvector adds semantic/vector search capability directly inside
    PostgreSQL; queries use SQL rather than the ChromaDB Python client
  - Requires PostgreSQL 12 or higher with pgvector extension installed
- Status: PROVISIONAL — pending confirmation from Greg Parks that the
  pgvector extension is available on the university PostgreSQL instance
  (under investigation by university IT as of June 2026)
- The reindex script (scripts/reindex_embeddings.py) will be written
  to support both backends via an environment variable — switching
  from ChromaDB to pgvector requires no new code, only a config change
- ChromaDB on any server environment: REJECTED — university IT is
  managing PostgreSQL; introducing a second separate database system
  on the server adds unnecessary maintenance burden
- Logged: Project start (original); updated June 2026

### Decision: PHP-Generated JSON Metadata Block on Content Pages — DECIDED
- Every content page includes a `<script type="application/json" id="page-metadata">`
  block containing structured machine-readable metadata about that page
- Fields included: content_id, content_type, species, sex, system, subsystem,
  primary_cells, primary_genes, figures, references, wormbase_terms
- This block is always PHP-generated from the database — it is never hand-authored
- Reason: Gives the RAG indexing script a clean, reliable extraction point for
  page-level structured data without parsing HTML. A Python script can locate
  `<script id="page-metadata">` in any page and extract valid JSON directly,
  with no HTML scraping logic required
- Rule: Because the block is generated by PHP, it is always in sync with the
  database. It is a read-only output of the CMS, not a second place where
  data is maintained
- This block is invisible to users and ignored by browsers (the type attribute
  prevents execution). It is for server-side indexing scripts only
- Logged: [May 2026]

### Decision: Standardized Figure Metadata Structure — DECIDED
- Each figure record includes a standard set of metadata fields
  covering panels, visible entities, technical imaging details,
  and RAG-specific fields
- RAG-specific fields required on every figure record:
  - ai_summary: a plain-language description of what that specific
    panel shows, written for retrieval (50-150 words)
  - ai_answerable_questions: a list of questions that specific panel
    could help answer (minimum 3 questions per figure record)
- "Per figure record" means per row in the figures table — since the
  corrected schema stores one row per panel, a multi-panel figure
  (e.g., IntFIG1 with panels A, B, C) requires a distinct ai_summary
  and ai_answerable_questions for each panel, not one shared summary
  copied across all of that figure's rows
- These fields mirror the common_questions and key_concepts fields
  on entity records — figures must meet the same RAG-readiness
  standard as entities
- Panel-level fields: panel_id (A, B, C, D...; any number of panels),
  description, image_type, view_orientation, magnification, source_reference
- Entity visibility fields: entity_id, wormbase_id, visibility
  level (primary/secondary/labeled/visible), panels the entity
  appears in
- Technical fields: microscopy_technique, specimen_stage,
  specimen_sex, strain, image_source, scale_bar
- Reason: figures are a primary retrieval target for researcher
  queries. Without structured metadata, the RAG pipeline cannot
  surface figures in response to visual or anatomical questions
- Gold standard template: IntFIG1 metadata (intestine article)
- Not all technical fields apply to every figure — many WormAtlas
  figures are diagrams/illustrations rather than photomicrographs,
  so fields like magnification, scale_bar, and strain are frequently
  not applicable. See conventions.md → Figure Metadata Conventions
  for the N/A-vs-blank distinction and the corresponding
  scripts/import_figures.py handling requirement (N/A → explicit
  NULL; genuinely blank required field → import warning, not a
  hard failure).
- Logged: [May 2026]

#### Correction — July 2026
- Original wording specified RAG fields "per figure," written before
  the figure_id UNIQUE constraint bug (see Figures Base Table entry →
  Correction — July 2026) was caught. With that bug fixed, a
  multi-panel figure is stored as multiple rows sharing one figure_id
  — one per panel. "Per figure" is now clarified as "per figure
  record" (i.e., per panel row).
- Rationale: IntFIG1's three panels (diagram, DIC, epifluorescent)
  show genuinely different content — a single blended summary would
  reduce retrieval precision and would need to be copy-pasted
  identically across all panel rows, creating drift risk if only one
  copy is later edited.
- Each panel's ai_summary should open with a brief anchor identifying
  it as part of the larger figure, e.g., "One of three panels in
  IntFIG1 depicting the intestine..." — so the panel's independent
  content is still traceable back to the full figure.
- Caught while drafting the IntFIG1 gold-standard row, July 2026.

---

## DATABASE

### Decision: MySQL Database — DECIDED
- All structured data stored in MySQL
- Database already exists at dev.wormatlas.org (workflow manager app)
- New WormAtlas CMS database to be built alongside existing workflow DB
- No ORM layer — use PHP prepared statements directly
- Logged: Project start

### Decision: Entity Data Pipeline — DECIDED
- Source of truth during editing phase: Google Sheets spreadsheet
- Flow: Google Sheets → CSV export → MySQL via Python import script
- 574 cells currently in spreadsheet, all C. elegans
- Other species to be added in later phase
- Logged: Spreadsheet analysis, January 2026

### Decision: `cell-group` Added as Entity Type — DECIDED
- The `entity_type` ENUM is extended to include `cell-group`
- Definition: a named grouping of cells that has its own biological identity,
  WormBase ID, and scientific significance, but is not itself a single cell
  and not large enough to be classified as an organ
- Example: intestinal ring I (contains int1DL, int1DR, int1VL, int1VR)
- Reason: cell groups are real anatomical concepts that researchers query by
  name. Classifying them as `cell` would be scientifically incorrect.
  The `parent_entity_id` field handles hierarchy; `entity_type` must
  accurately describe what kind of thing an entity is
- ENUM spelling uses hyphens: `cell-group` — matches the spreadsheet
  source of truth (never `cell_group` with an underscore in the schema)
- Full entity_type ENUM as of this decision:
  `cell`, `cell_group`, `organ`
  Planned additions (not yet built): `tissue`, `structure`, `gene`
- No existing spreadsheet records use this type yet — it is available
  for use when cell group entities are entered
- Logged: [May 2026]

### Decision: Entity Type Naming Uses Hyphens — DECIDED
- The `entity_type` ENUM in the database uses hyphens, not underscores
- Correct spelling: `cell-group` not `cell_group`
- For the current full ENUM, see: **Extended Entity Type ENUM — DECIDED**
- Reason: the spreadsheet (the source of truth during the editing phase)
  already uses hyphenated values. Matching the spreadsheet eliminates any
  transformation step in the Python import script — values can be written
  directly from spreadsheet to database without conversion
- The Python import script must never convert or normalize these values —
  what is in the spreadsheet column is what goes into the database
- This is an exception to the general underscore convention for database
  fields. It applies only to ENUM values in the entity_type column,
  not to column names, table names, or any other database identifiers
- Logged: [original date]
- Updated: [May 2026] — full ENUM list moved to Extended Entity Type ENUM entry

### Decision: Extended Entity Type ENUM — DECIDED
- The `entity_type` ENUM is extended to include all confirmed entity
  types for WormAtlas
- Full ENUM as of this decision:
  `cell`, `cell-group`, `organ`, `tissue`, `structure`,
  `gene`, `gene-family`, `protein`,
  `organism`, `developmental-stage`, `process`
- All values use hyphens, never underscores — consistent with the
  "Entity Type Naming Uses Hyphens" decision
- All types are tracked in the `anatomical_entities` table (unified
  table — consistent with the "Unified Entities Table" decision)
- All types are tagged in HTML using `data-entity-type` with the
  exact ENUM value as the attribute value
- Definitions and examples for each type are in GLOSSARY.md
- Notes on specific types:
  - `gene-family`: a named group of related genes with collective
    biological significance (e.g., med genes). May or may not have
    a WormBase ID — include if available
  - `organism`: used when a species is itself the subject (e.g., a
    comparative anatomy page). Taxon IDs from key_facts.md are the
    canonical identifiers for this type
  - `developmental-stage`: named embryonic stages (E2, E4, E8, E16,
    E20), larval stages (L1–L4, dauer), and adult stages. These
    overlap with values in the `developmental_stage` column on entity
    records — this type is for when a stage is itself being discussed
    as a subject, not just as a filter value
  - `process`: a named biological process (gastrulation, cell
    intercalation, endoreduplication, defecation cycle). Not all
    processes have WormBase IDs — leave wormbase_id NULL if none exists
- Columns that don't apply to a given entity type are left NULL —
  sparse rows are acceptable (consistent with unified table decision)
- Logged: [May 2026]

### Decision: Unified Entities Table — DECIDED
- All entity types (cell, cell-group, organ, tissue, structure, gene, protein)
  are stored in a single `anatomical_entities` table with an `entity_type`
  column distinguishing them
- Separate tables per entity type: REJECTED
- Reason: the RAG indexing pipeline queries one table to build the complete
  entity index. A unified table means no UNION queries, no routing logic in
  the import script, and no pipeline updates when new entity types are added
- Reason: the spreadsheet (source of truth) already uses a unified structure
  with an entity_type column. The import script can write rows directly
  without routing them to different tables
- Columns that don't apply to a given entity type are left NULL — sparse rows
  are acceptable in this context
- Exception path: if gene-specific or protein-specific fields become numerous
  (more than five or six columns that only apply to that type), a separate
  `gene_details` or `protein_details` table with a one-to-one relationship
  to `anatomical_entities` may be added. This is a vertical partition, not
  a separate primary table
- This decision does not affect the `references`, `figures`, or `cell_lineage`
  tables — those are separate by nature, not by entity type
- Logged: [May 2026]

### Decision: RAG Readiness Standard for Entities — DECIDED
- An entity is considered RAG-ready when ALL of the following are true:
  - description is 50-200 words, written conversationally
  - function field is filled (not "Unknown")
  - synonyms are expanded beyond basic name variants
  - primary_figures field references at least one figure
  - status is set to "validated"
- Gold standard templates: int1DL and intestine records in Entities tab
- Logged: Spreadsheet analysis, January 2026

### Decision: Figure Cataloguing Begins Immediately — DECIDED
- Figure metadata entry begins alongside entity enrichment, not after
- Reason: RAG search cannot surface figures without this data
- Starting point: IntFIG1, IntFIG2, IntFIG3, IntFIG5
  (already referenced in validated entity records)
- Does not require CMS to be built first
- Logged: Spreadsheet analysis, January 2026

### Decision: Glossary Entity Backfill Runs in Parallel with Figure Cataloguing — DECIDED

- **Status:** DECIDED — signed off by Chris Crocker
- **Date drafted:** July 2026
- **Date decided:** July 2026
- **Relates to:** Figure Cataloguing Begins Immediately — DECIDED

#### Context
The Entities tab currently holds 574 records: 573 of type `cell` and 1
of type `organ`. There are zero records of type `structure`, `tissue`,
`gene`, `gene-family`, `protein`, `cell-group`, `organism`,
`developmental-stage`, or `process` (verified July 2026 against the
current export).

The first real figure catalogued, IntFIG1, immediately required an
entity that does not exist: gut granules, a `structure`. This is not an
edge case — every non-cellular feature encountered during figure
cataloguing (microvilli, basal lamina, terminal web, lumen) will hit the
same empty category.

#### Conflict considered
Completing the entity backfill BEFORE resuming figure cataloguing was
proposed and rejected: it conflicts with "Figure Cataloguing Begins
Immediately — DECIDED," which states figure metadata entry begins
"alongside entity enrichment, not after." Running the two in parallel is
consistent with that decision and is what it already anticipated.

#### Decision
- Glossary backfill begins now, with mechanical extraction scripted and
  classification assigned to a non-technical editor (Laura Herndon,
  Cathy Wolkow, Eli Conklin, or Malia Jennings).
- Figure cataloguing continues uninterrupted, using PENDING-
  placeholders freely as gaps appear.
- The PENDING-[descriptive-name] convention is NOT retired by this work.
  Figure cataloguing is what surfaces missing entities in the first
  place (see key_facts.md → Known Data Gaps); a glossary pass is an
  educated head start, not a complete solution. PENDING remains the
  permanent safety valve for structures the glossary did not anticipate.

#### Sequencing
1. Inventory pass (scoping). A Python parse script performs the
   mechanical extraction — for every wormatlas.org glossary term it
   pulls the term, its anchor slug (the entity_id candidate per the
   anchor-slug convention), any abbreviation/cell name, synonyms marked
   (S), lineage, whether the row links to a WormBase WBbt ID, whether
   the row is only a "See X" cross-reference, and whether a matching
   record already exists in the Entities tab. An editor then performs
   the classification the script cannot: confirming the proposed
   entity_type, flagging terms that are not entities at all (e.g.
   Ablation, Adaptation, Acentriolar on Glossary A), and flagging
   ambiguous cases. Ambiguous classifications are flagged, never
   guessed. Purpose: the size of this job is unknown until it is
   counted.
   (Refinement, July 2026: the original draft had the editor produce the
   list manually. The mechanical extraction is now scripted; the
   classification remains human. Scope is functionally identical.)
2. Record creation for everything the editor marked as a genuine,
   not-yet-present entity in step 1.
3. Figure cataloguing continues throughout steps 1 and 2.
4. PENDING- values replaced with real entity_ids once records exist. The
   real id comes from the term's glossary anchor (see entity_id
   Construction for Non-Cell Entities — Glossary Anchor Slug).
5. Only then, the figure_entities foreign key is added (see
   anatomical_entities Table Schema → Constraint note).

#### Downstream RAG impact
PENDING entities are invisible to search. A researcher querying "gut
granules" retrieves nothing, even though IntFIG1 panel C shows them
clearly, because there is no entity record for the retrieval join to
land on. Every unbackfilled placeholder is a hole in retrieval coverage.
This is the primary reason the backfill starts now rather than after
cataloguing completes.

- **Logged by:** Claude (drafted) — signed off by Chris Crocker, July 2026.

### Decision: Stub Entity Records Permitted for Glossary Backfill — DECIDED

- **Status:** DECIDED — signed off by Chris Crocker. This entry creates
  an exception to guidance in key_facts.md; the matching amendment is in
  key_facts.md → Spreadsheet Editing Guidelines (stub exception) and
  → Known Data Gaps (stub tracking).
- **Date drafted:** July 2026
- **Date decided:** July 2026

#### Conflict declared
key_facts.md → Column Priority Tiers lists description, function, and
wormbase_id as REQUIRED — "never leave these blank." The
anatomical_entities schema permits all three to be NULL and provides
status='draft' precisely for incomplete records. The two documents
disagreed. This entry resolves the disagreement for one specific case
and does not otherwise relax the REQUIRED tier.

#### Decision
Entity records created during the glossary backfill may be entered as
stubs. A stub fills only:

    entity_id, entity_name, entity_type, species, taxon_id,
    data_source, curator_name, status='draft'

and leaves description, function, wormbase_id, and all HIGHLY
RECOMMENDED and OPTIONAL columns blank until enrichment.

#### Rationale
- Every NOT NULL column in the anatomical_entities schema is satisfied
  by a stub — this is schema-legal, not a workaround.
- status='draft' already communicates incompleteness. A stub is not a
  validated record pretending to be complete.
- The blocking problem is figure_entities.entity_type, which is NOT NULL
  and has no source when an entity record does not exist. A stub
  supplies entity_type at a fraction of the cost of a full record.
- Full records require a WormBase Ontology Browser lookup per term
  (never invented — see WormBase IDs Are the Canonical Identifier) plus
  50-200 words of prose each. Requiring that before figure cataloguing
  can proceed serialises the two largest remaining workstreams against a
  9-month deadline.
- The RAG Readiness Standard is unaffected: an entity still requires
  description, function, synonyms, primary_figures, and
  status='validated' to be RAG-ready. Stubs are explicitly not RAG-ready
  and are not counted as such.

#### Guardrails
- Stubs are permitted ONLY for glossary backfill entities created to
  unblock figure cataloguing. They are not a general licence to skip
  REQUIRED columns during normal enrichment — the Priority Rule in
  key_facts.md still stands.
- Every stub carries status='draft'. A stub must never be set to
  'review' or 'validated' until its REQUIRED columns are complete.
- Stub count is tracked in key_facts.md → Known Data Gaps alongside
  PENDING placeholders, so outstanding work stays visible.

- **Logged by:** Claude (drafted) — signed off by Chris Crocker, July 2026.

### Decision: entity_mentions Table — DECIDED
- A dedicated `entity_mentions` table tracks every occurrence of every
  entity across all articles
- Columns: article_id, entity_id, entity_type, mention_context
  (the surrounding sentence or passage), section_heading, mention_count
- Reason: enables the RAG pipeline to retrieve not just entity records
  but the specific article passages where each entity is discussed in
  context. A researcher asking about SKN-1 gets both the entity
  description and every relevant passage across the site
- Reason: enables "related content" features — articles that co-mention
  the same entities are likely scientifically related
- This table is populated by the Python import script when content
  pages are indexed — it is never hand-authored
- Logged: [May 2026]

### Decision: cell_lineage Table — DECIDED
- A dedicated `cell_lineage` table stores developmental relationships
  between cells
- Columns: cell_id (foreign key to anatomical_entities), parent_cell_id
  (foreign key to anatomical_entities), division_stage (e.g., E2, E4,
  E16), division_time_minutes, division_orientation
  (left-right / anterior-posterior / dorsal-ventral), fate
- Reason: developmental lineage is a primary research query type for
  C. elegans biology. "What does EMS give rise to?" and "What is the
  precursor of int1DL?" cannot be answered from entity records alone
- Reason: lineage data is structured and hierarchical — it belongs in
  a dedicated table, not embedded in prose descriptions
- This table is separate from the `anatomical_entities` table by nature,
  not by entity type — it models relationships between cells, not
  properties of cells
- Population of this table is deferred until after the core entities
  table is built and validated
- Logged: [May 2026]

### Decision: references and article_citations Tables — DECIDED
- A `references` table stores full bibliographic records for all
  academic papers cited across the site
- Columns: ref_id (e.g., Kimble1983 — matching the citation format
  in conventions.md), authors, year, title, journal, volume, pages,
  doi, pubmed_id, wormbase_paper_id (WBPaper format)
- An `article_citations` join table records which papers are cited
  in which articles, with citation context (surrounding passage)
  and citation count
- Reason: citations are evidence that must be structured and
  retrievable. The RAG pipeline must be able to surface source
  citations alongside retrieved content — unstructured citation
  strings in prose do not support this
- Reason: WormBase paper IDs (WBPaper format) link citations back
  to WormBase, consistent with the decision to use WormBase as the
  canonical identifier system
- The ref_id format follows conventions.md: Author + Year
  (e.g., Kimble1983, Sulston1983) — this is the primary key and
  must be applied consistently across all tables and HTML markup
- Logged: [May 2026]

### Decision: article_figures and figure_entities Tables — DECIDED
- An `article_figures` join table records which figures appear in
  which articles, with display order and section heading
- A `figure_entities` join table records which entities are visible
  in each figure, with panel designation (A, B, C), visibility level
  (primary / secondary / labeled / visible), and entity type
- Reason: figures cannot be connected to content or to entities
  without these join tables. The RAG pipeline cannot surface figures
  in response to entity queries without knowing which entities
  appear in which figures
- Reason: the Figures tab in the spreadsheet already captures
  figure_id, panel, entity_id, visibility, image_type, and
  magnification — these tables are the direct database counterpart
  of that spreadsheet structure
- Population of these tables begins immediately alongside entity
  enrichment, consistent with the logged decision that figure
  cataloguing begins immediately (see: Figure Cataloguing Begins
  Immediately — DECIDED)
- Priority figures for initial population: IntFIG1, IntFIG2,
  IntFIG3, IntFIG5 — already referenced in validated entity records
- Logged: [May 2026]

---

## FIGURES & CONTENT PAGES SCHEMA

### Decision: Figures Base Table, Join Tables, and Content Pages Table — DECIDED
- **Status:** DECIDED — signed off by Chris Crocker, David Hall, and
  Nate Schroeder, including the new `both`/`b` sex-abbreviation
  convention
- **Date drafted:** July 2026
- **Date decided:** July 2026
- **Context:** Figure cataloguing (IntFIG1, IntFIG2, IntFIG3, IntFIG5 first)
  is already DECIDED to begin immediately (see: Figure Cataloguing Begins
  Immediately). The `article_figures` and `figure_entities` join tables were
  named in the Standardized Figure Metadata Structure decision, but no
  CREATE TABLE statements were ever logged, and no base table for figure
  content itself (ai_summary, microscopy_technique, etc.) had been named.
  This entry proposes concrete schema for all of this so
  `scripts/import_figures.py` can be written against something authoritative.

#### Proposed schema

```sql
-- Base table for figure content and metadata
CREATE TABLE figures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    figure_id VARCHAR(50) NOT NULL,               -- e.g. "IntFIG1", matches spreadsheet exactly — no longer UNIQUE alone, see compound key below
    panel VARCHAR(5) NOT NULL,                     -- capital letters (A, B, C, D...); no limit on number of panels (per conventions.md)
    description_in_figure TEXT,
    image_type ENUM('DIC','TEM','epifluorescent','diagram','merged') NOT NULL,
    view_orientation VARCHAR(100),
    magnification VARCHAR(50),
    source_reference VARCHAR(255),
    microscopy_technique ENUM('DIC','TEM','epifluorescent','diagram','merged'),
    specimen_stage VARCHAR(50),
    specimen_sex VARCHAR(50),
    strain VARCHAR(100),
    image_source VARCHAR(255),                    -- format: "[Photographer/Lab] archive_ref", e.g. "[Hall] N510-R338"
    scale_bar VARCHAR(50),
    ai_summary TEXT,                              -- 50-150 words, required per RAG readiness standard
    ai_answerable_questions TEXT,                 -- minimum 3 questions; type TBD, see open items
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_figure_id (figure_id),
    UNIQUE KEY uq_figure_id_panel (figure_id, panel)
    -- One figure_id can have multiple rows (one per panel), but the same
    -- figure_id + panel combination cannot repeat. Corrects the original
    -- figure_id-only UNIQUE constraint, which made it structurally
    -- impossible to store multi-panel figures like IntFIG1 (A/B/C).
);

-- Join table: which figures appear in which articles
CREATE TABLE article_figures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT NOT NULL,
    figure_id INT NOT NULL,
    display_order INT NOT NULL,
    section_heading VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES content_pages(id),
    FOREIGN KEY (figure_id) REFERENCES figures(id),
    INDEX idx_article_id (article_id),
    INDEX idx_figure_id (figure_id)
);

-- Join table: which entities are visible in which figures
CREATE TABLE figure_entities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    figure_id INT NOT NULL,
    entity_id VARCHAR(50) NOT NULL,               -- string business key, matches anatomical_entities.entity_id (see rationale)
    panel VARCHAR(5) NOT NULL,      -- capital letters (A, B, C, D...); no limit on number of panels
    visibility ENUM('primary','secondary','labeled','visible') NOT NULL,
    entity_type VARCHAR(30) NOT NULL,             -- mirrors entity_type ENUM values, hyphenated (e.g. cell-group)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (figure_id) REFERENCES figures(id),
    INDEX idx_figure_id (figure_id),
    INDEX idx_entity_id (entity_id)
);

-- Content pages ("articles") table
CREATE TABLE content_pages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content_id VARCHAR(100) NOT NULL UNIQUE,      -- matches existing data-content-id attribute already used in HTML
                                                    -- e.g. "elegans-h-intestine" (see conventions.md HTML section)
    content_type VARCHAR(50) NOT NULL,             -- e.g. "anatomical-handbook", matches data-content-type
    species VARCHAR(50) NOT NULL,
    sex ENUM('hermaphrodite','male','both') NOT NULL,  -- values per key_facts.md; NOT NULL so the compound
                                                         -- constraint below can enforce uniqueness reliably
    system VARCHAR(50) NOT NULL,
    subsystem VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_content_id (content_id),
    UNIQUE KEY uq_species_sex_system_subsystem (species, sex, system, subsystem)
    -- Safety net independent of content_id string construction: guarantees the database
    -- itself cannot hold two rows for the same species+sex+system+subsystem combination,
    -- even if a content_id is ever mistyped, duplicated, or doesn't follow the slug
    -- convention correctly. See "content_id / multi-sex article identity" note in Rationale.
);
```

#### Rationale

- **`content_id` as the identifying column for `content_pages`:** conventions.md
  already shows this exact attribute in production HTML
  (`data-content-id="elegans-h-intestine"`), and the PHP-Generated JSON
  Metadata Block decision confirms it's already how the CMS identifies a
  page internally. Using it here requires no new naming scheme.

- **Compound `UNIQUE` constraint on `(species, sex, system, subsystem)`:**
  The one existing `content_id` example (`elegans-h-intestine`) implies a
  species+sex+subsystem naming pattern, but that pattern was never formally
  documented anywhere prior to this entry — see the matching addition to
  GLOSSARY.md drafted alongside this decision. Rather than rely solely on
  editors and the CMS constructing `content_id` correctly by convention
  across 800+ pages, this constraint enforces species/sex/system/subsystem
  uniqueness at the database level as a backstop. `sex` is changed to an
  `ENUM` (matching the `hermaphrodite | male | both` values already
  established in key_facts.md) rather than a free-text `VARCHAR`, and
  `sex`, `system`, and `subsystem` are all made `NOT NULL` — MariaDB
  treats `NULL` values in a unique key as distinct from one another, so
  a nullable column would silently defeat this safety net.

- **`entity_id` as VARCHAR business key in `figure_entities` (not an
  artificial integer FK):** Three independent parts of the existing
  knowledge base already treat the string `entity_id` (e.g. `int1DL`) as
  the de facto join key across the system:
  1. Live HTML markup (conventions.md) uses `data-entity-id="int1DL"` —
     called out as a fixed attribute name, never to be substituted.
  2. The already-DECIDED `entity_mentions` table uses `entity_id` as a
     plain column, implying the same string is matched against page
     content during indexing.
  3. key_facts.md and conventions.md both state entity IDs must match
     the spreadsheet exactly, and the Entity Data Pipeline decision says
     spreadsheet values are written to MySQL without transformation.
  Introducing a different, artificial PK for `figure_entities` alone
  would break this existing pattern and require an extra translation
  step nowhere else in the pipeline needs. Recommendation: `figures`
  and `content_pages` keep standard `INT AUTO_INCREMENT` PKs per
  conventions.md's general rule (this rule governs a table's own PK,
  not what others use as a foreign key to reach it), while
  `anatomical_entities` — once its own CREATE TABLE is formally logged
  — should expose `entity_id VARCHAR(50) NOT NULL UNIQUE` as the
  column everything else joins against, alongside its own internal
  `id INT AUTO_INCREMENT PRIMARY KEY`.

#### Open items — all resolved
All three open items originally raised by this decision have now been resolved:
Item 1 (anatomical_entities schema) — see anatomical_entities Table Schema — DECIDED, below
Item 2 (content_id article identity / both-b sex convention) — resolved as part of this entry's DECIDED status (see Rationale above)
Item 3 (ai_answerable_questions column type) — see ai_answerable_questions Column Type — TEXT — DECIDED, below

| # | Question | Notes |
|---|----------|-------|

Item 2 (`content_id` article identity / compound `UNIQUE(species, sex,
system, subsystem)` constraint / `both`-`b` sex convention) is resolved
as part of this DECIDED status — see Rationale above and the companion
GLOSSARY.md addition.

#### Correction — July 2026
- Original schema defined `figure_id` as `UNIQUE` alone, which would
  have made it impossible to store more than one row per figure_id —
  incompatible with real multi-panel figures (e.g., IntFIG1 has panels
  A, B, and C, each with different image_type, magnification, and
  content). Corrected to a compound `UNIQUE(figure_id, panel)` key.
  Caught while cataloguing IntFIG1, the first real figure entered.

- **Logged by:** Claude (drafted) — signed off by Chris Crocker, David
  Hall, and Nate Schroeder, July 2026.

### Decision: figure_entities Uniqueness Constraint — DRAFTED, AWAITING SIGN-OFF

- **Status:** DRAFTED — awaiting sign-off from Chris Crocker, David Hall,
  and Nate Schroeder. This entry MODIFIES a previously signed-off
  CREATE TABLE statement and must not be applied before sign-off.
- **Date drafted:** July 2026
- **Modifies:** Figures Base Table, Join Tables, and Content Pages Table
  — DECIDED (signed off July 2026)

#### Conflict declared
The `figure_entities` CREATE TABLE in the entry above was signed off
with no UNIQUE constraint. This entry proposes adding one. It is a
design change to signed-off schema, not a typo correction, and is
logged separately rather than edited into the original entry.

#### Proposed change
Add to CREATE TABLE figure_entities:

    UNIQUE KEY uq_figure_entity_panel (figure_id, entity_id, panel)

#### Rationale
- scripts/import_figures.py must be safely re-runnable — the Figures tab
  will be imported many times as cataloguing proceeds across 800+
  figures (see conventions.md → Spreadsheet Import Scripts).
- Re-running is achieved with INSERT ... ON DUPLICATE KEY UPDATE, which
  requires a unique key to detect the duplicate. Without one, every
  re-import appends a complete second set of entity rows, silently.
- (figure_id, entity_id, panel) is the natural business key: an entity
  appears in a given panel of a given figure once. The same entity
  legitimately appears in multiple panels (intestine appears in IntFIG1
  A, B, and C) and in multiple figures, so no narrower constraint is
  correct.
- Mirrors the existing UNIQUE(figure_id, panel) on `figures`, added in
  the July 2026 correction for the same class of reason.

#### Note
`figure_id` here is the INT foreign key to figures(id), not the string
figure identifier — see conventions.md → "figure_id means two different
things."

- **Logged by:** Claude (drafted for review)


### Decision: anatomical_entities Table Schema — DECIDED
- **Status:** DECIDED — signed off by Chris Crocker
- **Date drafted:** July 2026
- **Context:** decisions.md had repeatedly described this table's properties
  across multiple entries (Unified Entities Table, Extended Entity Type
  ENUM, RAG Readiness Standard, Entity Data Pipeline) but no CREATE TABLE
  had ever been logged. The "Figures Base Table, Join Tables, and Content
  Pages Table" decision assumed `anatomical_entities` exposes
  `entity_id VARCHAR(50) NOT NULL UNIQUE` as its join key — this entry
  confirms that assumption formally.
  
  #### Constraint — figure_entities foreign key is DEFERRED, not optional

- This entry states that figure_entities.entity_id "can now reference
  this table's entity_id column with a proper FOREIGN KEY." That FK
  must NOT be created until the PENDING entity backfill is complete.

- Reason: the PENDING-[descriptive-name] convention (conventions.md →
  Figure Metadata Conventions) deliberately creates entity_id values
  for structures visible in figures that have no record in the
  Entities tab yet — e.g. PENDING-gut-granules in IntFIG1 panel C.
  A FOREIGN KEY enforces that a value already exists in the
  referenced table. Adding it now would cause every PENDING row to
  be rejected at import, blocking figure cataloguing entirely.

- Current state: the logged CREATE TABLE figure_entities does NOT
  include this FK. Nothing is broken today. This note exists to
  prevent it being "helpfully" added later by someone reading the
  anatomical_entities entry in isolation.

- Sequence that must be followed:
  1. Complete figure cataloguing, using PENDING- placeholders freely
  2. Backfill real entity records from the WormAtlas.org glossary
  3. Replace every PENDING- value with its real entity_id
  4. Verify zero remaining PENDING- values in figure_entities
  5. Only then add the FOREIGN KEY constraint

- Step 4 is a hard gate. Adding the FK with even one PENDING- value
  remaining will fail, and the error message will not explain why.

#### Schema

```sql
CREATE TABLE anatomical_entities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity_id VARCHAR(50) NOT NULL UNIQUE,        -- business key, e.g. "int1DL" — matches spreadsheet exactly
    entity_name VARCHAR(255) NOT NULL,
    common_name VARCHAR(255),
    entity_type ENUM('cell','cell-group','organ','tissue','structure',
                      'gene','gene-family','protein','organism',
                      'developmental-stage','process') NOT NULL,
    parent_entity_id VARCHAR(50),                 -- self-referencing FK to entity_id, nullable
    wormbase_id VARCHAR(50),                       -- nullable: 10 cells confirmed missing this per key_facts.md
    species VARCHAR(50) NOT NULL,
    taxon_id VARCHAR(50) NOT NULL,                 -- e.g. "NCBITaxon:6239"
    developmental_stage ENUM('embryo','L1','L2','L3','L4','dauer','adult','all'),
                                                    -- full C. elegans life cycle: embryo, four larval
                                                    -- stages, dauer (alternative L3), adulthood.
                                                    -- 'all' reserved for stage-independent entities
                                                    -- (e.g. a gene expressed across all stages)
    sex ENUM('hermaphrodite','male','both'),
    description TEXT,                              -- 50-200 words per RAG Readiness Standard when status='validated'
    function TEXT,
    synonyms TEXT,
    location_description TEXT,
    size_description VARCHAR(255),
    primary_figures TEXT,                          -- raw import field from spreadsheet; see note below
    wormbase_url VARCHAR(255),
    data_source VARCHAR(100) NOT NULL,
    curator_name VARCHAR(100) NOT NULL,
    status ENUM('draft','review','validated') NOT NULL DEFAULT 'draft',
    common_questions TEXT,
    key_concepts TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_entity_id) REFERENCES anatomical_entities(entity_id),
    INDEX idx_entity_id (entity_id),
    INDEX idx_entity_type (entity_type),
    INDEX idx_parent_entity_id (parent_entity_id)
);
```

#### Notes

- **`developmental_stage` ENUM confirmed July 2026:** key_facts.md previously
  listed `embryo / L1 / adult / dauer / all`, while GLOSSARY.md separately
  documented the full `L1–L4` larval range — an inconsistency between the
  two files. Resolved: full life cycle is embryonic stage, four larval
  stages (L1–L4), dauer (alternative L3), and adulthood. `all` is retained
  from key_facts.md's original list for stage-independent entities. Both
  key_facts.md and GLOSSARY.md should be updated to match this ENUM so the
  three files stay consistent.
- **`primary_figures` retained as TEXT, flagged for future deprecation:**
  This field may become redundant once `figure_entities` (DECIDED in the
  Figures Base Table entry above) is populated, since that table tracks
  entity-to-figure relationships with panel and visibility detail that
  `primary_figures` cannot capture. Kept as-is for now because it is the
  current spreadsheet source of truth and no migration has happened yet.
  Do not remove this column until `figure_entities` is confirmed to be a
  complete replacement — revisit after Phase 1 figure cataloguing.
- **`entity_id` as business key confirmed:** resolves open item #1 from the
  Figures Base Table, Join Tables, and Content Pages Table decision.
  `figure_entities.entity_id` can now reference this table's `entity_id`
  column with a proper FOREIGN KEY, rather than an unconfirmed assumption.

---

### Decision: ai_answerable_questions Column Type — TEXT — DECIDED
- **Status:** DECIDED — signed off by Chris Crocker
- **Date drafted:** July 2026
- **Context:** Resolves open item #3 from the Figures Base Table, Join
  Tables, and Content Pages Table decision — whether `ai_answerable_questions`
  on the `figures` table should be `TEXT` (delimited) or native `JSON`.

#### Decision
`ai_answerable_questions` is stored as `TEXT`, not `JSON`.

#### Rationale
- MariaDB's `JSON` type is not a distinct binary-optimized type — it is
  implemented as `LONGTEXT` with an automatic `CHECK (JSON_VALID(...))`
  constraint. Choosing JSON here would not provide a storage or query
  performance advantage over TEXT.
- The sibling entity fields performing the same function —
  `common_questions` and `key_concepts` on `anatomical_entities` — are
  documented in key_facts.md as free text, "separated by spaces or line
  breaks," filled in directly by non-technical editors in the spreadsheet.
  Making `ai_answerable_questions` JSON while these remain TEXT would be
  an inconsistency with no real benefit.
- Requiring valid JSON syntax in a spreadsheet cell would create friction
  for non-technical team members (Laura Herndon, Cathy Wolkow, Eli Conklin,
  Malia Jennings) — inconsistent with the project's non-technical-editor
  support requirement.
- The "minimum 3 questions" requirement (per the Standardized Figure
  Metadata Structure decision) is enforced at the Python import-script
  level — counting delimited entries and flagging rows below the minimum —
  not as a database constraint. This matches how required-field rules are
  already enforced elsewhere in the pipeline (spreadsheet convention +
  import validation, not DB-level constraints).
- **Logged by:** Claude (drafted) — signed off by Chris Crocker, July 2026.

---

## URL STRUCTURE

### Decision: Hierarchical Clean URLs — DECIDED
- URL pattern: /species/sex/system/subsystem
- Example: /c-elegans/hermaphrodite/alimentary/intestine
- Database-driven routing — no static file extensions in URLs
- Old URLs must redirect to new pattern (301 redirects)
- Logged: Project start

---

## ACCESSIBILITY & RESPONSIVENESS

### Decision: WCAG 2.1 AA Compliance Is Non-Negotiable — DECIDED
- Every feature must meet WCAG 2.1 AA standards
- No exceptions, no deferrals
- Lighthouse score target: 90+ on all pages
- Logged: Project start

### Decision: Mobile-First Development — DECIDED
- All templates designed mobile-first, then scaled up
- Known issue: navbar dropdown menus overflow on small screens — must fix
- Logged: Project start

---

## SCIENTIFIC DATA INTEGRITY

### Decision: WormBase IDs Are the Canonical Identifier — DECIDED
- Every anatomical entity, gene, and protein must be linked to its WormBase ID
- WBbt IDs for anatomy terms, WBGene IDs for genes
- Never invent or assume a WormBase ID — look it up or flag it as missing
- Logged: Project start

### Decision: entity_id Construction for Non-Cell Entities — Glossary Anchor Slug — DECIDED

- **Status:** DECIDED — signed off by Chris Crocker
- **Date drafted:** July 2026
- **Date decided:** July 2026
- **Relates to:** Glossary Entity Backfill Runs in Parallel with Figure
  Cataloguing; Stub Entity Records Permitted for Glossary Backfill;
  Entity Data Pipeline; WormBase IDs Are the Canonical Identifier

#### Context
Cells have always had an obvious entity_id: the cell name itself
(int1DL), matched to the spreadsheet exactly (conventions.md →
Scientific Content Conventions). Non-cell entities — the structures,
processes, tissues, and other terms created during the glossary
backfill — had no defined entity_id convention. The
PENDING-[descriptive-name] placeholder (conventions.md → Figure
Metadata Conventions) is a temporary stand-in, not a real entity_id,
and does not define one. This entry defines the real convention.

#### Decision
The entity_id for a non-cell entity created during the glossary backfill
is the term's existing HTML anchor slug on the wormatlas.org glossary
page — the value inside `<a name="...">` on that term's row.

Examples (from Glossary A):
- Adherens junction → `adherensjunction`
- Axoneme        → `axoneme`
- A band         → `aband`
- Axon guidance  → `axonguidance`

#### Scope
- This convention governs entity_id construction for NON-CELL entities
  only. Cells retain their existing convention (entity_id = cell name,
  e.g. int1DL) unchanged.
- The anchor slug becomes the value written into the spreadsheet's
  entity_id column, so conventions.md's "entity IDs match the
  spreadsheet exactly" rule is preserved — the spreadsheet value simply
  is the anchor.

#### Clarifications (must be applied)

1. Malformed anchors are flagged, not blindly used. Some anchors carry
   typos or inconsistent casing — e.g. the AC/VU decision row on
   Glossary A has the anchor `ACVUdecison` (misspelled). Rule: use the
   anchor exactly as written by default, but the inventory pass (see
   Glossary Backfill decision, step 1) flags any anchor that appears
   malformed for editor review. Where a malformed anchor is corrected,
   the editor records a deliberate, reviewed slug in the inventory — the
   correction is documented, never silently auto-generated. A typo must
   not be baked into a permanent join key.

2. PENDING- placeholders resolve to the anchor, not the placeholder
   name. When a PENDING- value is replaced with a real entity_id
   (backfill sequence step 4), the replacement comes from the term's
   glossary anchor, NOT by de-hyphenating the placeholder. Example:
   PENDING-gut-granules resolves to the gut granules anchor (e.g.
   `gutgranules`), not to `gut-granules`. Do not guess the real id from
   the placeholder text.

3. Anchors are unique per page only — cross-page collisions must be
   caught. entity_id must be globally unique because it is the join key
   used by figure_entities, entity_mentions, and cell_lineage. Glossary
   anchors are only guaranteed unique within a single letter page. The
   parse script must check for the same anchor appearing on two
   different pages and flag any collision for resolution before records
   are created.

#### Casing note
Anchor slugs are lowercase with spaces removed (`adherensjunction`),
which differs from cell entity_ids, which preserve mixed-case cell names
(int1DL). This difference is intentional and acceptable — entity_id only
needs to be unique and stable, and the two entity classes never share
ids. Do not "normalize" casing across entity types; doing so would break
existing joins on cell records.

#### Downstream RAG impact
entity_id is the permanent key every retrieval join lands on. Fixing the
convention before mass record creation means figure_entities,
entity_mentions, and cell_lineage all point at stable values from day
one. A convention chosen after hundreds of records exist would require
rewriting every join.

- **Logged by:** Claude (drafted) — signed off by Chris Crocker, July 2026.

### Decision: Species and Taxonomy Use NCBI Taxon IDs — DECIDED
- C. elegans: NCBITaxon:6239
- P. pacificus: NCBITaxon:54126
- S. stercoralis: NCBITaxon:34506
- All entity records must include taxon_id
- Logged: Project start

### Decision: All Data Must Remain Freely Accessible — DECIDED
- WormAtlas is an open-access platform
- No paywalls, no login requirements for research content
- Authentication is for CMS editing only, never for content viewing
- Logged: Project start

---

## SECURITY

### Decision: Secrets Management — DECIDED
- No API keys, passwords, or secrets ever committed to the repository
- All secrets stored in environment variables
- All user inputs validated and sanitized server-side
- CORS policy explicitly configured — no wildcard * in production
- Logged: January 2026

---

## TIMELINE

### Decision: 9-Month Project Deadline — DECIDED
- All primary deliverables (CMS + RAG search) must be complete within 9 months
- Project spearheaded by Chris Crocker
- Logged: Project start

---

### Decision: Git Hosting Platform — GitHub — DECIDED

- **Status:** DECIDED
- **Date logged:** July 2026

#### Decision
GitHub (github.com) is the version control and code hosting platform
for the WormAtlas redevelopment project.

- Repository: https://github.com/chriscrocker79/wormatlas
- Visibility: Public
- Account: chriscrocker79

#### Rationale
- The bioinformatics and C. elegans research community uses GitHub
  as standard. WormBase and most related projects are hosted there.
  External collaborators will expect to find WormAtlas code on GitHub.
- Nate Schroeder are non-UofI affiliates. University
  of Illinois GitLab cannot reliably grant accounts to external
  collaborators, which ruled out university Git hosting.
- GitHub free plan covers all project needs with no maintenance
  burden on Greg Parks or university IT infrastructure.
- Public visibility was chosen after GitHub's free plan was found
  to not enforce branch protection rules on private repositories.
  Public code is consistent with WormAtlas's open-access mission.
  Credentials are protected by .gitignore regardless of visibility.
- GitLab.com: REJECTED — smaller community, higher complexity,
  no meaningful advantage for this stack and team size.
- University GitLab: REJECTED — cannot grant accounts to non-UofI
  team members including lab directors.

#### Repository structure
- `main` branch is protected via branch protection rule
- All work done on feature branches, merged via pull request
- Branch naming, commit message format, and merge rules are
  documented in conventions.md
- Required approvals set to 1 — solo developer self-approves
  pull requests before merging to main

#### Files committed in initial scaffold
- `.gitignore` — prevents secrets, credentials, ChromaDB data,
  and local config from ever being committed
- `README.md` — project overview, setup instructions, team list,
  Git workflow summary
- `.env.example` — safe template for environment variables
  (Voyage AI key, database credentials)
- `config/database.example.php` — safe template for database
  credentials
- `.vscode/extensions.json` — recommended VS Code extensions
  for all team members
- `docs/project_notes/` — all project knowledge files
  (decisions.md, bugs.md, key_facts.md, conventions.md,
  GLOSSARY.md, ACCESSIBILITY_CHECKLIST.md)

#### Security conventions established
- `config/database.php` is gitignored — never committed
- `.env` is gitignored — never committed
- `.sql` database dumps are gitignored — never committed
- All secrets live in environment variables only
- See conventions.md → Security section for full policy

#### Team access
- Chris Crocker: Owner (full access)
- David Hall: Read access (visibility into project progress)
- Nate Schroeder: Read access (visibility into project progress)
- Additional team members to be added as needed

#### Open questions resolved
- Open question #1 (Git hosting platform) is now DECIDED
  and can be removed from the Open Questions table

---

## OPEN QUESTIONS
These items need a decision but have not yet been discussed.
Each must be logged as a DECIDED entry before work begins on that area.

| # | Question | Priority | Notes |
|---|----------|----------|-------|
| 2 | Authentication approach for CMS login | High | Sessions? JWT? |
| 3 | Breakpoints for responsive design | Medium | Mobile / tablet / desktop values |
| 4 | Typography choices | Medium | Must render scientific notation and Latin names clearly |
| 5 | Color system | Medium | All combos must meet WCAG AA contrast ratios |
| 6 | RAG architecture pattern | High | Naive RAG vs Advanced RAG with re-ranking. Candidate approach: a query classifier that routes factual queries (exact cell name, WormBase ID lookups) to the structured MySQL database, and explanatory or conceptual queries ("how does X work", "what is the role of Y") to the RAG pipeline, with hybrid results combined for ambiguous queries. This is not a decision yet — log here when discussed with David Hall and Nate Schroeder. |
| 7 | Chunking strategy for RAG content | High | By section? By paragraph? Overlap? |
| 8 | Rate limiting on API and AI assistant | Medium | Prevent abuse |
| 9 | GDPR compliance approach | Medium | International academic audience |
| 10 | Expected traffic volume post-launch | Medium | Affects hosting and API cost planning |
| 11 | Will 3D anatomical models be in Version 1 or deferred? | Medium | |
| 12 | Is multilingual support required? | Low | |
| 13 | Accessibility testing tooling | Medium | axe-core confirmed candidate |
