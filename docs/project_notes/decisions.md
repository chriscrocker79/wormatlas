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
- RAG-specific fields required on every figure:
  - ai_summary: a plain-language description of what the figure
    shows overall, written for retrieval (50-150 words)
  - ai_answerable_questions: a list of questions this figure
    could help answer (minimum 3 questions per figure)
- These fields mirror the common_questions and key_concepts fields
  on entity records — figures must meet the same RAG-readiness
  standard as entities
- Panel-level fields: panel_id (A/B/C), description, image_type,
  view_orientation, magnification, source_reference
- Entity visibility fields: entity_id, wormbase_id, visibility
  level (primary/secondary/labeled/visible), panels the entity
  appears in
- Technical fields: microscopy_technique, specimen_stage,
  specimen_sex, strain, image_source, scale_bar
- Reason: figures are a primary retrieval target for researcher
  queries. Without structured metadata, the RAG pipeline cannot
  surface figures in response to visual or anatomical questions
- Gold standard template: IntFIG1 metadata (intestine article)
- Logged: [May 2026]

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
- David Hall and Nate Schroeder are non-UofI affiliates. University
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
