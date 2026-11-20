# Connectome Explorer: handoff notes

> Save as `docs/project_notes/connectome-explorer-handoff.md`. This file REPLACES the earlier "Worm Wiring Explorer: handoff notes" (version 3 era), which is out of date and must not be reused: it used a name that cannot be used, described a dark-first design that is no longer the default, and restated facts that belong in key_facts.md.
>
> Last updated: 2026-11-20. Facts about people, data and counts are NOT repeated here. Read them in key_facts.md → Connectome Explorer (prototype) and decisions.md → CONNECTOME EXPLORER. (bugs.md, May 2026: a handoff that restated facts led to invented details.)

## What it is
A prototype interactive map of the *C. elegans* hermaphrodite connectome with a linked body model. A proof of concept built by Chris Crocker in his free time. It is not on the 9-month plan, David Hall and Nate Schroeder did not request it, and it is not linked from wormatlas.org. "Connectome Explorer" is a placeholder title; "Worm Wiring" must not be used.

## Where things are
- Review copy: https://claude.ai/artifact/5xLQVSkkbhTugkB9pmzdLu (private; Version 12 as of 2026-11-20). Update it in place: read it, edit, republish to the same URL. Only one chat edits it at a time.
- Standalone dev copy: `connectome-explorer.html` (noindex). Upload method for dev.wormatlas.org is not recorded.
- Source data and rules: key_facts.md and decisions.md (see above). Do not commit the .cys, the connectome data or the body-model SVG to the public repository (Open Question 17).

## What the prototype does today (Version 12)
- Network map on a canvas, using the original Cytoscape layout; search, Chemical and Gap toggles, group chips, "lines shown" slider.
- Selecting a cell shows its sends, receives and gap links in a side panel, with hover wording "Sends to / Receives from / Gap junction with", and highlights the cell on a left-side body model and a head-detail inset. Left/right pairs share one dot.
- Cell information in levels: summary and chips; an About tab (collapsible sections, citations); "Full profile page: coming soon" as plain text. Only ADA (ADAL, ADAR) has content, pasted verbatim from the legacy page, with the legacy JPGs as placeholders.
- Light theme by default, dark only if chosen. Keyboard arrows move among body-model dots.

## Standing rules from the owner
- Light background by default; no +/- on connection hovers; a white arrow keyboard indicator that appears only after an arrow key; unselected dots at 87% opacity; the zoom buttons keep their original behaviour.
- The source line is a placeholder until Nate and David supply wording.
- Never invent WormBase IDs, taxonomy identifiers, transmitters, citations or people. If a fact is needed and is not in the project notes, ask.
- WCAG 2.1 AA and mobile responsiveness apply to anything that goes to production. The prototype's known gaps are listed in decisions.md.

## Phase plan (proposed; see decisions.md → phased-work entry)
| Phase | Goal | Done when |
|---|---|---|
| 0 Triage and gate | One backlog of team ideas; yes/no and a time limit from Hall and Schroeder; source wording and permission | Open Questions 14 to 17 answered |
| 1 Data foundations | neuron_details, connections and figures decisions; graph-to-entity mapping; missing class rows; reviewed content and references | Open Questions 18 to 20 decided; mapping built |
| 2 Prototype features | Keyboard and table/CSV alternatives, mobile layout, animation controls, team-requested features | Accessibility gaps in decisions.md closed |
| 3 Production build | PHP page, /api/v1/ endpoints, external CSS/JS, self-hosted fonts, cell profile pages, SVG images | Passes ACCESSIBILITY_CHECKLIST.md |
| 4 Link, stories, launch | RAG link, guided stories, dev then production with Greg Parks | Live |

Rules: one phase per chat; each chat starts by reading this file, decisions.md, key_facts.md, conventions.md, bugs.md; each chat ends with log entries drafted ("This should be logged in [filename] — want me to draft the entry?").

## Backlog (fill in from the team; columns only)
| # | Idea | Asked by | Why (what problem it solves) | Size (S/M/L) | Phase | Status |
|---|---|---|---|---|---|---|
| | | | | | | |

No ideas are listed here because none have been recorded in the project. Add rows as the team sends them.

## Starter prompts (copy into a new chat in the project)

Phase 0:
"Read docs/project_notes/connectome-explorer-handoff.md and the CONNECTOME EXPLORER section of decisions.md. I have the team's feedback: [paste]. Help me turn it into the backlog table, size each item, and prepare the go/no-go question for David Hall and Nate Schroeder. Do not change the Artifact in this chat."

Phase 1:
"Read the handoff, decisions.md (Open Questions 17 to 20) and key_facts.md → Connectome Explorer. Help me decide neuron_details, the connections table and the figure question, and write the graph-to-entity mapping script as a dry run first. Show every command with the directory to run it from."

Phase 2:
"Read the handoff and the Artifact at [URL]. Work on [one named feature]. Update the Artifact in place, keep light theme default, and test at 390px width and with the keyboard before saying it is done."

Phase 3:
"Read the handoff, conventions.md (Interactive Visualisation Conventions) and ACCESSIBILITY_CHECKLIST.md. Plan the production page and API endpoints for [named piece], mobile-first, with no inline CSS or JS."

Phase 4:
"Read the handoff and the RAG decisions in decisions.md. Plan how the assistant and the explorer link to each other, and which questions go to the database versus RAG."

## Open items (as of 2026-11-20)
Source wording and data version; final name; production go/no-go; reuse permission; neuron_details, connections and figure decisions; WormWiring URL pattern check; how the dev copy is deployed; ADA summary sentence review. See Open Questions 14 to 20 in decisions.md.
