# FIGURE CATALOGING — STANDARD PROMPT TEMPLATE

**Version:** 2.1 — 2026-10-14 (merges v2.0 frozen-ID rules with the three-field figure type, multimedia rules, and crosswalk v1.1)
**Use:** Copy everything in the "PROMPT" block below into a new cataloguing chat, fill the
three placeholders ([chapter/section], [expected figure_id], [TEAMMATE NAME]), then paste the
teammate's source material and the figure image where marked. One figure per chat.

**What changed in v2.1:**
- MERGED two diverged copies. v2.0 (project knowledge) had the frozen figure-ID rules but
  lacked the media_type / capture_technique / is_composite and multimedia rules. The older
  repo copy had those rules but old IDs and the stale `entities_export.csv`. This version has both.
- Crosswalk reference updated from FROZEN v1.0 to **v1.1** (2026-10-14). Pharynx IDs from
  PhaMOVIE 2 onward are one higher than in v1.0. Any ID quoted from memory or an older
  crosswalk copy is suspect; always look it up in the v1.1 file.
- Output is now specified as rows for the 27-column Figures tab (exact header listed below).
- Added: "ask, don't infer" for symbols, colours and arrows not explained in the legend.
- Added: reuse an existing PENDING- placeholder before inventing a new one.
- Added: never put "(Type B)" in an entity_id; never use N/A as an entity_id for a visible structure.
- Added: when a legacy figure is split into several new figures, map old panel letters to the
  new panel letters and say so.
- Teammate name is a placeholder again, not hard-coded.
- Added 2026-10-27: region and landmark labels are not entities (no placeholder, no row); style-reference list now includes CePhaFIG8.

**Maintenance rule:** when a decision changes how figures are catalogued (new media_type,
new capture_technique, changed field rules, new crosswalk version), update this template in the
same pass so it never lags the decisions it depends on. Keep ONE copy: repo
`docs/project_notes/FIGURE_CATALOGING_PROMPT_TEMPLATE.md` and the project-knowledge copy
`FIGURE_CATALOGING_PROMPT_TEMPLATE.md` (top level) must be identical.

---

## PROMPT (copy from here)

Drafting figure metadata for the WormAtlas Figures tab ([chapter/section] — e.g. Alimentary — Rectum and Anus).

This project uses a Claude Project with docs/project_notes/ as authoritative knowledge — check these BEFORE proceeding with anything, and flag any conflict rather than silently working around it: decisions.md, conventions.md, key_facts.md, GLOSSARY.md, bugs.md, ACCESSIBILITY_CHECKLIST.md, the Figures tab export CSV ("...wormbase url checked - Figures.csv"), the INSTRUCTIONS export CSV, the Entities tab export CSV ("...wormbase url checked - Entities.csv"), and the figure crosswalk WormAtlas_figure_crosswalk_v1.1 (Master List). If any of these is missing or looks stale (for example a Figures export with image_type / microscopy_technique columns, or a crosswalk older than v1.1), say so BEFORE drafting.

Source material for this figure was prepared by a teammate ([TEAMMATE NAME]), not the team lead directly: their plain-language description of the figure, the official figure legend, supporting text from the chapter, and possibly some example ai_answerable_questions if they drafted. I'll paste all of this in below.

FIGURE ID & NAMING (crosswalk v1.1):
- Use the figure-ID format from decisions.md → Figure Identifier Format: [SpeciesCode][StageToken?][SectionToken]FIG[Number], no internal spaces (e.g. CeRectFIG1). Confirm the SectionToken against the ratified section-token vocabulary — do not invent or guess an abbreviation.
- The expected figure_id for this figure is [expected figure_id]. Confirm it in the v1.1 crosswalk Master List (new_id column). Do not assign or increment a number yourself. If you cannot find a matching row, or the ID in the crosswalk differs from the expected one, stop and flag it rather than guessing.
- Figure IDs appearing in the teammate's description, the legend, and the chapter text are almost certainly OLD-format (as on the live site, e.g. "PhaFIG 3E-G"). Treat every figure reference in the pasted material as old-format, translate it through the v1.1 crosswalk, and flag any you cannot resolve. Never copy an old-format ID (no Ce prefix) into the data, and never rely on an ID from memory.
- If the old figure was split into several new figures, the old panel letters may be re-lettered (A, B, C… per new figure). State the old-to-new panel mapping explicitly in your reply.

STYLE REFERENCES: use the figures already catalogued in the Figures tab (CeIntFIG1–3, CePhaFIG1–8, CeRectFIG1–2, CeAlimFIG1, CeIntroFIG1) as style and level-of-detail references. Do not rely on the older entities_export.csv anywhere.

OUTPUT FORMAT: draft the rows for the 27-column Figures tab, in exactly this column order:
figure_id, panel, entity_id, visibility, description_in_figure, media_type, capture_technique, is_composite, magnification, view_orientation, source_reference, specimen_stage, specimen_sex, strain, image_source, scale_bar, media_file, media_format, duration_seconds, poster_image, caption_file, transcript, text_alternative, autoplay, loops, ai_summary, ai_answerable_questions
Give them as CSV (or a table I can paste) with the header line, and no helper row. Do not add, rename or reorder columns.

FIGURE TYPE — three fields, not one (per decisions.md "Figure Type Axes Split"):
- media_type (REQUIRED) — what KIND of asset it is. Exactly one of: image | diagram | table | movie | animation | interactive-3d
- capture_technique — HOW it was imaged, if a microscope was used. Exactly one of: DIC | TEM | SEM | epifluorescent | confocal | AFM — or N/A if it was drawn/built (diagram, animation, most 3D) rather than imaged. These values are foreign-key checked against a lookup table, so spelling must be exact (e.g. epifluorescent, NOT epiflourescent) — do not guess a spelling.
- is_composite — 1 if the panel overlays channels or stitches multiple images/timepoints together; else 0. This REPLACES the old "merged" value. A composite still records its real underlying technique in capture_technique where one exists; use N/A only when there genuinely isn't a single one.
- If the source material describes a figure type or imaging technique not in the lists above, STOP and flag it — new types are added to the lookup tables by decision, not invented in a draft.

MULTIMEDIA panels (movie / animation / interactive-3d / table) — special care:
- ai_summary must describe CHANGE OVER TIME (movie/animation) or the STRUCTURE the reader can rotate to (interactive-3d), not a single frozen frame.
- For interactive-3d, set view_orientation, magnification, and scale_bar to N/A (the reader controls view and zoom).
- media_type = table means a real HTML table; if only an image of a table exists, put its full contents in text_alternative.
- Fill the media-support columns when they apply (leave blank/N/A otherwise): media_file, media_format (e.g. mp4, webm, glb), duration_seconds, poster_image, caption_file, transcript, text_alternative, autoplay, loops.
- Accessibility (ACCESSIBILITY_CHECKLIST.md): movies/animations with speech need captions (caption_file); interactive-3d and image-only tables need text_alternative (also the RAG retrieval surface); autoplay stays 0 for anything with audio. Flag any multimedia panel that can't meet these.

PANEL & MULTI-ENTITY structure:
- One row per panel. Use sub-panel suffixes (A-main/A-inset, C-top/C-bottom) if a lettered panel actually contains multiple distinct images. Panels are stored as clean letters (A, B, C…) plus any sub-panel suffix; labels may be compound (up to 20 characters). The reader-facing "FIG N / panel A" display label is generated separately and is NOT stored in these rows.
- If a panel shows more than one entity, ONLY the first row per figure_id+panel carries full panel content; additional entity rows get only entity_id and visibility.
- ai_summary (50–150 words) and ai_answerable_questions (minimum 3 complete questions) are per panel, not blended across a multi-panel figure. Each ai_summary opens with an anchor line back to the parent figure that uses the new Ce-prefixed figure_id (e.g. "One of three panels in CeRectFIG2, showing…"), never an old-format ID.
- Visibility values only: primary | secondary | labeled | visible. Apply the removal test from conventions.md ("if this entity were removed, would the panel lose its purpose?" → primary). More than one primary per panel is allowed only for genuine subjects.

ai_answerable_questions:
- [TEAMMATE NAME] may have drafted some — use these as a starting point/style reference rather than discarding them, but check they meet the minimum count and full-question format, and flag anything off-target or duplicative.

ENTITY resolution:
- Before treating any entity as missing, check the actual Entities tab export (the "…wormbase url checked - Entities.csv" file) rather than assuming. Confirm you are reading the Ce-prefixed version, not the older entities_export.csv.
- Type A (name genuinely unknown, no established identifier) → PENDING-[descriptive-name]. FIRST check key_facts.md → Known Data Gaps (the running PENDING- set) and reuse an existing placeholder where one fits; if a new name is close to an existing one (e.g. lumen vs pharyngeal-lumen), flag it as a question instead of silently adding a near-duplicate.
- Type B (known name, row simply missing) → use the real entity_id directly and log it as a gap. Never write a suffix such as "(Type B)" into an entity_id.
- Never use N/A as entity_id for a structure that is visible in the panel; use a Type A or Type B value so the structure stays findable by RAG.
- Exception: a label that only names a region or landmark of a larger structure (for example the anterior bulb or posterior bulb of the pharynx) is not an entity. Give it no entity_id, no PENDING- placeholder and no row; keep the label as text in description_in_figure and ai_summary. If you are unsure whether a label is a landmark or an entity, ask me before deciding (decisions.md → Region and Landmark Labels in Figures Are Not Entities).
- (The entities table is not fully populated, so import currently marks entity_type as 'pending' for unresolved entities — expected, resolved at backfill. Still use the correct entity_id.)

DATA INTEGRITY:
- N/A vs blank: N/A = genuinely doesn't apply (stored as NULL); blank = applies but unconfirmed — never guess.
- Never invent WormBase IDs, strains, magnifications, scale bars, specimen stages, capture-technique spellings, entity_ids, or other scientific values.
- Do not infer what symbols, arrows, stars, colours or labels mean from appearance alone. If the legend and the teammate's text do not explain them, ask. Count arrows or labelled structures only if I confirm the count.
- Do not carry over any claim from the legend or chapter text that you cannot support from the pasted material (for example a statement about what a signal "corresponds to"); flag such claims for Hall/Schroeder review.

Since this material was prepared by a teammate rather than the person I'm working with directly, please flag anything ambiguous, inconsistent, or that conflicts with existing Entities tab data (or with a logged decision) as a question — this draft will go back to the team lead for review before it's finalized. Ask your questions FIRST, grouped and numbered, and wait for answers before finalizing the rows. Also flag anything in the source material that references a figure by an old-format ID so the translation can be double-checked.

After the rows are final, list: (1) new PENDING- placeholders introduced, (2) Type B gaps, (3) anything needing Hall/Schroeder review, and end with: "This should be logged in [filename] — want me to draft the entry?"

Pasting figure with teammate's material below.
--

[PASTE TEAMMATE'S DESCRIPTION, OFFICIAL LEGEND, CHAPTER TEXT, DRAFT ai_answerable_questions, AND ATTACH THE FIGURE IMAGE HERE]

## (end of PROMPT)
