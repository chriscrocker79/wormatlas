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
- Developmental stage values: embryo / L1 / adult / dauer / all
- Sex values: hermaphrodite / male / both
- Entity types permitted in spreadsheet: cell, cell-group, organ, tissue,
  structure, gene, protein
- Entity types confirmed in use (have records): cell, organ
- Entity types permitted but not yet populated: cell-group, tissue,
  structure, gene, protein

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
- Total records: 0
- Column structure is ready: figure_id, panel, entity_id,
  visibility, description_in_figure, image_type, magnification
- 800+ figures on the site need cataloguing
- Priority figures to enter first: IntFIG1, IntFIG2, IntFIG3, IntFIG5
  (already referenced in validated entity records)
- Figure cataloguing can begin immediately — does not require
  CMS to be built first

### Validation tab
- Total records: 0
- 564 WormBase URLs need testing
- URL testing can and should be automated with a Python script

## Known Data Gaps
- int-ring-I referenced in Relationships tab but missing from Entities tab
- 10 cells missing WormBase IDs: AC, ADLL, ADLR, P12.pa,
  PVDL, PVDR, SML, SMR, VD12, VD13
- Relationships table is early stage — only 3 entries, target is 100-150
- Figures tab is empty — largest data gap relative to RAG requirements
- No P. pacificus or S. stercoralis entities exist yet

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



