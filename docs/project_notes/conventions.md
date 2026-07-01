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
- Relationship types always use established vocabulary:
  part_of | develops_from | adjacent_to | connected_to | expresses | contains
- Figure IDs follow the pattern [SystemAbbrev]FIG[Number]
  (e.g., IntFIG1, PharFIG2)
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
- Panel designations use capital letters: A, B, C — never
  lowercase
- Visibility levels use these values only:
  primary | secondary | labeled | visible
- Microscopy technique values use these terms only:
  DIC | TEM | epifluorescent | diagram | merged
- image_source format: [Photographer/Lab] + [archive reference]
  e.g., "[Hall] N510-R338"
- Gold standard template: IntFIG1 (intestine article)

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
