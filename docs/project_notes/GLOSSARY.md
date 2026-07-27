# GLOSSARY.md
## WormAtlas Modernization — Scientific & Project Terminology

> Purpose: This file ensures Claude uses correct scientific terminology
> when generating code, documentation, API names, and database schemas.
> Do not abbreviate or rename these terms without team consensus.

---

## Part 1: C. elegans Scientific Terminology

### Organism

| Term | Definition | Notes |
|---|---|---|
| C. elegans | Caenorhabditis elegans — a free-living, transparent nematode ~1mm long | Always italicized: C. elegans |
| Nematode | A roundworm; the phylum Nematoda | |
| Hermaphrodite | The primary sex of C. elegans; produces both sperm and oocytes | Default organism in WormAtlas |
| Male | The minor sex; ~0.2% of wild-type population | Has distinct anatomy |
| L1–L4 | Larval stages 1 through 4 of C. elegans development | |
| Adult | The sexually mature stage following L4 | |
| Dauer | An alternative L3 larval stage; stress-induced, long-lived | |
| Developmental stage (database) | The `developmental_stage` column on
anatomical entity records uses exactly these values: `embryo`, `L1`,
`L2`, `L3`, `L4`, `dauer`, `adult`, `all`. `dauer` is an alternative L3
stage, not a separate numbered stage. `all` marks entities that are not
stage-specific. | See decisions.md → anatomical_entities Table Schema | |

---

### Nervous System

| Term | Definition | Notes |
|---|---|---|
| Neuron | An individual nerve cell | 302 neurons in hermaphrodite adult |
| Connectome | The complete map of neural connections | C. elegans has the first fully mapped connectome |
| Synapse | A connection between two neurons | |
| Chemical synapse | Synapse that releases neurotransmitter vesicles | |
| Gap junction | Electrical synapse; direct cytoplasmic connection | Also called electrical synapse |
| Neurite | Generic term for axon or dendrite of a neuron | |
| Axon | Neuronal process that transmits signals away from cell body | |
| Dendrite | Neuronal process that receives signals | |
| Ganglia | Clusters of neuron cell bodies | Plural of ganglion |
| Neuropil | Dense region of nerve fibers and synapses | |
| Nerve ring | The main brain-equivalent structure; circumesophageal ring | Located in the head |
| Ventral nerve cord (VNC) | Major longitudinal nerve tract along the ventral side | |
| Dorsal nerve cord (DNC) | Major longitudinal nerve tract along the dorsal side | |
| Commissure | A nerve tract crossing from one side of the body to the other | |
| Interneuron | Neuron that connects other neurons | |
| Motor neuron | Neuron that innervates muscle | |
| Sensory neuron | Neuron that detects external or internal stimuli | |
| Amphid | Pair of major chemosensory organs in the head | Contains ~12 neuron types |
| Phasmid | Pair of chemosensory organs in the tail | Hermaphrodite only |

---

### Body Regions & Anatomy

| Term | Definition |
|---|---|
| Anterior | Toward the head end |
| Posterior | Toward the tail end |
| Dorsal | Back side (away from substrate when crawling) |
| Ventral | Belly side (toward substrate when crawling) |
| Lateral | Side; left or right |
| Pharynx | The muscular feeding organ; processes food |
| Intestine | The digestive tube; also a major metabolic organ |
| Gonad | Reproductive organ; produces gametes |
| Hypodermis | The outer epithelial layer beneath the cuticle |
| Cuticle | The external exoskeleton-like covering; shed at each molt |
| Coelomocyte | Scavenger cells; part of the pseudocoelomic cavity |
| Pseudocoelom | The fluid-filled body cavity (not a true coelom) |
| Body wall muscle | The four quadrants of longitudinal muscle used for locomotion |
| Seam cell | Lateral hypodermal cells involved in cuticle synthesis |

---

### Cell Naming Convention

C. elegans uses a strict naming convention for all cells. Key rules:

- Neurons are named by position and function: e.g., ASEL, ASER, AWA, AWB
  - Letters indicate lineage origin and function; L/R suffix = left/right
- Muscles are named by position: e.g., BWM (body wall muscle), pm1-pm8 (pharyngeal muscles)
- Cell lineage is written as a path: e.g., AB.alaaapa

These names must be preserved exactly in the database, search index, and URL slugs.

---

### Imaging & Data Terms

| Term | Definition |
|---|---|
| TEM | Transmission Electron Microscopy — primary imaging method for connectome |
| DIC | Differential Interference Contrast microscopy — for live imaging |
| Fluorescence microscopy | Uses fluorescent markers to label specific cells |
| Serial section | Sequential thin slices through tissue for 3D reconstruction |
| Reconstruction | The 3D model built from serial sections |
| Atlas | A systematic mapping of anatomy with images and descriptions |

---

## Part 2: Project Terminology

### Project Structure
This project uses a single Claude Project for all development work.
All reference documents are maintained in docs/project_notes/.
See decisions.md, conventions.md, key_facts.md, and bugs.md.

### Technical Terms (Project-Specific)

| Term | Definition |
|---|---|
| RAG | Retrieval-Augmented Generation — AI answers grounded in retrieved source documents |
| Vector database | A database that stores and searches high-dimensional embeddings |
| Embedding | A numerical vector representation of text used for semantic search |
| Chunking | Breaking long documents into smaller pieces for embedding and retrieval |
| Re-ranking | A second-pass sorting of retrieved results by relevance |
| Design token | A named variable for a design value (color, spacing, font size) |
| Content model | The structured schema defining a content type in the CMS |
| API envelope | The standard JSON wrapper around all API responses |
| WCAG | Web Content Accessibility Guidelines — target: 2.1 AA |
| a11y | Shorthand for accessibility (a + 11 letters + y) |
| i18n | Shorthand for internationalization |
| WBbt ID | WormBase anatomy term identifier (e.g., WBbt:0005772 = intestine) |
| WBGene ID | WormBase gene identifier (e.g., WBGene00004804 = skn-1) |
| NCBITaxon ID | NCBI taxonomy identifier for species (e.g., NCBITaxon:6239 = C. elegans) |
| Entity | Any discrete, identifiable scientific object: cell, gene, organ,
tissue, structure, gene family, organism, developmental stage, or
biological process. Entities have unique identifiers, appear across
multiple pages, have properties and relationships, and benefit from
consistent representation. **Plain-language test:** If you would make
a dedicated page for it, it's an entity. If it has a WormBase ID,
it's almost certainly an entity that should be tagged. |
| Relationship type | Controlled vocabulary for entity connections: part_of, develops_from, adjacent_to, connected_to, expresses, contains |
| voyage-3.5 | The selected Voyage AI embedding model for WormAtlas RAG.
Optimized for retrieval tasks on specialized text |
| input_type | A required Voyage API parameter. Must be "document" when
embedding content for storage, and "query" when embedding a
user's search question. Mixing these degrades search quality |

### Entity Types in WormAtlas

| Entity Type | Definition | Example |
|---|---|---|
| cell | An individual named cell | int1DL, EMS, ASEL |
| cell-group | A named grouping of cells with its own biological identity and WormBase ID | intestinal ring I |
| organ | A major anatomical structure composed of multiple cells | intestine, pharynx |
| tissue | A tissue category | hypodermis, muscle |
| structure | A sub-cellular or non-cellular anatomical feature | gut granules, microvilli, basal lamina |
| gene | An individual gene | SKN-1, POP-1 |
| gene-family | A named group of related genes | med genes |
| protein | A protein or protein complex | hemicentin, laminin α |
| organism | A species being studied | C. elegans, P. pacificus |
| developmental-stage | A named life or embryonic stage | L1, dauer, E4, E16 |
| process | A named biological process | gastrulation, endoreduplication |

**Not entities (do not tag):** common words, generic directional terms
(anterior, posterior), adjectives (large, small), verbs, plain numbers.

---

Example URL patterns:
```
/c-elegans/hermaphrodite/nervous/neurons/ASEL
/c-elegans/hermaphrodite/alimentary/intestine
/c-elegans/hermaphrodite/alimentary/pharynx
/figures/IntFIG1
/references/Kimble1983
```

### content_id Construction (data-content-id attribute)

`content_id` is the internal identifier stored on every content page's
root `<article>` element (`data-content-id`) and in the `content_pages`
database table. It is distinct from the URL path (see URL patterns above)
though built from the same underlying values.

**Pattern:**
```
[species-abbreviation]-[sex-abbreviation]-[subsystem]
```

**Species abbreviations:**
| Species | Abbreviation |
|---|---|
| C. elegans | elegans |
| P. pacificus | ppacificus |
| S. stercoralis | sstercoralis |

**Sex abbreviations:**
| Sex | Abbreviation |
|---|---|
| hermaphrodite | h |
| male | m |
| both (sex-independent content) | b |

**Examples:**
```
elegans-h-intestine        → C. elegans, hermaphrodite, intestine
elegans-m-intestine        → C. elegans, male, intestine
elegans-b-nerve-ring       → C. elegans, sex-independent, nerve ring
ppacificus-h-pharynx       → P. pacificus, hermaphrodite, pharynx
```

**Rules:**
- Every content page must have a `content_id` following this exact
  pattern — no ad hoc variations.
- A subsystem that genuinely differs by sex (anatomy is not identical
  between male and hermaphrodite) gets separate pages with separate
  `content_id`s, one per sex.
- A subsystem with sex-independent content gets a single page using
  the `b` (both) abbreviation — do not create duplicate `h` and `m`
  pages with identical content.
- This pattern is enforced at the database level by a compound
  `UNIQUE(species, sex, system, subsystem)` constraint on the
  `content_pages` table (see decisions.md → Figures Base Table, Join
  Tables, and Content Pages Table) — a mistyped or duplicated
  `content_id` cannot silently create a second row for the same
  species/sex/system/subsystem combination.
- If a new species or subsystem naming need arises that this pattern
  doesn't cover, flag it for team discussion before inventing a new
  abbreviation — do not guess.