Drafting figure metadata for the WormAtlas Figures tab (WormAtlas.org chapters).

This project uses a Claude Project with docs/project_notes/ as authoritative
knowledge — check these BEFORE proceeding with anything, and flag any conflict
rather than silently working around it:
  decisions.md, conventions.md, key_facts.md, GLOSSARY.md, bugs.md,
  ACCESSIBILITY_CHECKLIST.md, the Figures tab export CSV, the INSTRUCTIONS
  export CSV, and entities_export.csv (Entities tab) in /mnt/project/.

Source material for this figure was prepared by a teammate ([TEAMMATE NAME]),
not the team lead directly: their plain-language description of the figure, the
official figure legend, supporting text from the chapter, and possibly some example
ai_answerable_questions if they drafted. I'll paste all of this in below.

Please draft the panel rows following the established conventions and the
figures already in the database (IntFIG1–3, PhaFIG1–3, RectFIG1–2, AlimFIG1,
IntroFIG1) as style references:

FIGURE TYPE — three fields, not one (per decisions.md "Figure Type Axes Split"):
- media_type (REQUIRED) — what KIND of asset it is. Exactly one of:
  image | diagram | table | movie | animation | interactive-3d
- capture_technique — HOW it was imaged, if a microscope was used. Exactly one
  of: DIC | TEM | SEM | epifluorescent | confocal | AFM  — or N/A if it was
  drawn/built (diagram, animation, most 3D) rather than imaged.
  These values are foreign-key checked against a lookup table, so spelling must
  be exact (e.g. epifluorescent, NOT epiflourescent) — do not guess a spelling.
- is_composite — 1 if the panel overlays channels or stitches multiple
  images/timepoints together; else 0. This REPLACES the old "merged" value. A
  composite still records its real underlying technique in capture_technique
  where one exists; use N/A only when there genuinely isn't a single one.

MULTIMEDIA panels (movie / animation / interactive-3d / table) — special care:
- ai_summary must describe CHANGE OVER TIME (movie/animation) or the STRUCTURE
  the reader can rotate to (interactive-3d), not a single frozen frame.
- For interactive-3d, set view_orientation, magnification, and scale_bar to N/A
  (the reader controls view and zoom).
- media_type = table means a real HTML table; if only an image of a table
  exists, put its full contents in text_alternative.
- Fill the media-support columns when they apply (leave blank/N/A otherwise):
  media_file, media_format (e.g. mp4, webm, glb), duration_seconds,
  poster_image, caption_file, transcript, text_alternative, autoplay, loops.
- Accessibility (ACCESSIBILITY_CHECKLIST.md): movies/animations with speech need
  captions (caption_file); interactive-3d and image-only tables need
  text_alternative (also the RAG retrieval surface); autoplay stays 0 for
  anything with audio. Flag any multimedia panel that can't meet these.
- If the source material describes a figure type or imaging technique not in the
  lists above, STOP and flag it — new types are added to the lookup tables by
  decision, not invented in a draft.

PANEL & MULTI-ENTITY structure:
- One row per panel. Use sub-panel suffixes (A-main/A-inset, C-top/C-bottom) if
  a lettered panel actually contains multiple distinct images. Panel labels may
  be compound (up to 20 characters), e.g. A-main.
- If a panel shows more than one entity, ONLY the first row per figure_id+panel
  carries full panel content; additional entity rows get only entity_id and
  visibility.
- ai_summary and ai_answerable_questions are per panel, not blended across a
  multi-panel figure; each opens with an anchor line back to the parent figure.

ai_answerable_questions:
- [TEAMMATE NAME] has already drafted some — use these as a starting
  point/style reference rather than discarding them, but check they meet the
  minimum 3–4 count and full-question format, and flag anything off-target or
  duplicative.

ENTITY resolution:
- Before treating any entity as missing, check the actual Entities tab data
  (entities_export.csv in /mnt/project/) rather than assuming.
  Type A (unknown name) → PENDING-[descriptive-name].
  Type B (known name, missing row) → use the real entity_id directly, log as a
  gap. (Note: the entities table is not fully populated, so import currently
  marks entity_type as 'pending' for unresolved entities — expected, resolved at
  backfill. Still use the correct entity_id.)

DATA INTEGRITY:
- N/A vs blank: N/A = genuinely doesn't apply; blank = applies but unconfirmed —
  never guess.
- Never invent WormBase IDs, strains, magnifications, capture-technique
  spellings, entity_ids, or other scientific values.

Since this material was prepared by a teammate rather than the person I'm working
with directly, please flag anything ambiguous, inconsistent, or that conflicts
with existing Entities tab data (or with a logged decision) as a question — this
draft will go back to the team lead for review before it's finalized.

Pasting figure with teammate's material below.
--
