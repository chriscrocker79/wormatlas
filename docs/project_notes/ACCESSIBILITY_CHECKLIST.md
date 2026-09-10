# ACCESSIBILITY_CHECKLIST.md
## Wormatlas.org Modernization — WCAG 2.1 AA Checklist

> **How to use:** Run through this checklist for every new component, page, and feature before it is marked ready for review. Check off items as confirmed. Items marked 🔴 are blockers — do not merge until resolved.

---

## 1. Perceivable

### 1.1 Text Alternatives
- [ ] 🔴 All non-text content (images, diagrams, icons) has a text alternative via `alt`, `aria-label`, or `aria-labelledby`
- [ ] 🔴 Decorative images use `alt=""` so screen readers skip them
- [ ] 🔴 Scientific diagrams have detailed descriptions (either visible caption or `aria-describedby`)
- [ ] 🔴 Icon-only buttons have accessible names (`aria-label`)
- [ ] All microscopy images include descriptions of what is anatomically depicted

### 1.2 Time-Based Media
Applies to every figure whose media_type has is_time_based = 1 (movie, animation).
- [ ] 🔴 Movies/animations with meaningful audio have synchronized captions (auto-captions reviewed and corrected) — stored in figures.caption_file (WebVTT)
- [ ] Audio-only content has a transcript — stored in figures.transcript
- [ ] 🔴 No auto-playing audio (WCAG 1.4.2). figures.autoplay must be 0 for any figure with audio
- [ ] Silent animation may autoplay ONLY if it is ≤5s or can be paused, and it must still respect prefers-reduced-motion (see §2.3)
- [ ] A movie/animation whose visuals convey information not in the audio has an audio description OR an equivalent text description in figures.text_alternative (WCAG 1.2.5)
- [ ] Every movie/animation has a poster_image so a still preview renders before playback

### 1.3 Adaptable
- [ ] 🔴 Information is not conveyed by color alone (shape, pattern, or text also used)
- [ ] 🔴 Reading order makes sense when CSS is disabled
- [ ] 🔴 Semantic HTML used (`<nav>`, `<main>`, `<header>`, `<footer>`, `<section>`, `<article>`, `<aside>`)
- [ ] 🔴 Heading hierarchy is logical (h1 → h2 → h3, never skipped)
- [ ] Form fields have associated `<label>` elements (not just placeholder text)
- [ ] Tables have `<th>` headers with `scope` attributes
- [ ] Complex data tables have `<caption>` elements

### 1.4 Distinguishable
- [ ] 🔴 Text contrast ratio ≥ 4.5:1 for normal text (< 18pt or < 14pt bold)
- [ ] 🔴 Text contrast ratio ≥ 3:1 for large text (≥ 18pt or ≥ 14pt bold)
- [ ] 🔴 UI component contrast (borders, focus rings) ≥ 3:1 against adjacent colors
- [ ] Text can be resized up to 200% without loss of content or functionality
- [ ] No horizontal scrolling at 320px viewport width for vertically scrolling content
- [ ] Text spacing can be increased (line height 1.5×, letter spacing 0.12em, word spacing 0.16em) without losing content
- [ ] No content relies on hover or focus alone to be visible

---

## 2. Operable

### 2.1 Keyboard Accessible
- [ ] 🔴 All functionality is operable via keyboard alone
- [ ] 🔴 No keyboard traps (user can always navigate away using Tab/Escape)
- [ ] 🔴 Custom interactive components (dropdowns, modals, sliders) implement keyboard patterns from ARIA Authoring Practices Guide
- [ ] Keyboard shortcuts (if any) can be turned off or remapped
- [ ] 🔴 Interactive 3D models (is_interactive = 1) are fully operable by keyboard — rotate, zoom, and pan have keyboard equivalents, not mouse-drag only (WCAG 2.1.1)

### 2.2 Enough Time
- [ ] No time limits on core tasks (or user can extend/disable them)
- [ ] Moving or auto-updating content can be paused, stopped, or hidden
- [ ] Session timeouts warn the user and allow extension
- [ ] Any looping movie/animation (figures.loops = 1) can be paused, stopped, or hidden (WCAG 2.2.2)
- [ ] No figure animation flashes more than 3×/second (WCAG 2.3.1)
- [ ] Figure animations are disabled/reduced under prefers-reduced-motion

### 2.3 Seizures & Physical Reactions
- [ ] 🔴 No content flashes more than 3 times per second
- [ ] Animations can be disabled via `prefers-reduced-motion` media query
- [ ] Any looping movie/animation (figures.loops = 1) can be paused, stopped, or hidden (WCAG 2.2.2)
- [ ] No figure animation flashes more than 3×/second (WCAG 2.3.1)
- [ ] Figure animations are disabled/reduced under prefers-reduced-motion

### 2.4 Navigable
- [ ] 🔴 Skip navigation link ("Skip to main content") is the first focusable element on every page
- [ ] 🔴 All pages have a descriptive, unique `<title>` element
- [ ] 🔴 Focus indicator is visible on all interactive elements (never `outline: none` without replacement)
- [ ] Focus order is logical and matches reading order
- [ ] Link text is descriptive — no "click here" or "read more" without context
- [ ] Multiple ways to find pages (navigation, search, site map)
- [ ] Current location is indicated in navigation (breadcrumbs, `aria-current="page"`)

### 2.5 Input Modalities
- [ ] Touch targets are at least 44×44px (iOS) / 48×48dp (Android)
- [ ] No multi-point gestures required for functionality
- [ ] Functionality triggered by motion (shake, tilt) has a button alternative

---

## 3. Understandable

### 3.1 Readable
- [ ] 🔴 Page language declared: `<html lang="en">`
- [ ] Passages in other languages (e.g., Latin species names) marked with `lang` attribute
- [ ] Abbreviations explained on first use or via `<abbr>` with `title`
- [ ] Scientific jargon is defined or links to a glossary entry

### 3.2 Predictable
- [ ] 🔴 No unexpected context changes on focus or input (no auto-submit, no page jump)
- [ ] Navigation is consistent across pages
- [ ] Interactive components behave consistently

### 3.3 Input Assistance
- [ ] 🔴 Form errors are identified in text (not just color)
- [ ] 🔴 Error messages describe what went wrong and how to fix it
- [ ] 🔴 Required fields are indicated (not just by color)
- [ ] Search suggestions and autocomplete are keyboard navigable
- [ ] Important forms have a review step or can be corrected before submission

---

## 4. Robust

### 4.1 Compatible
- [ ] 🔴 HTML validates without errors (run through W3C validator)
- [ ] 🔴 ARIA roles, states, and properties are valid and used correctly
- [ ] 🔴 Status messages (loading, success, error) use `aria-live` regions or `role="status"`
- [ ] Component tested with at least two screen readers (e.g., NVDA + Chrome, VoiceOver + Safari)
- [ ] Component tested with keyboard only (no mouse)
- [ ] No accessibility errors in automated scan (axe-core / Lighthouse)

---

## 5. Scientific Content — Additional Requirements

These go beyond WCAG but are required for Wormatlas specifically:

- [ ] Microscopy images include zoom functionality that is keyboard accessible
- [ ] 🔴 Interactive 3D models have a text-based alternative representation stored in figures.text_alternative. This field is required whenever the figure's media_type.requires_text_alternative = 1, and it doubles as the RAG retrieval surface for media that has no readable frame.
- [ ] Data tables catalogued as figures use a native HTML <table> (media_type = table), not an image of a table. Where only an image exists, its full contents are entered in figures.text_alternative.
- [ ] Every time-based / interactive figure has been checked against §1.2 and §2.1 before its figure record is marked complete.
- [ ] Data tables (neuron connections, synaptic data) have summary descriptions
- [ ] Downloadable data files (CSV, JSON) are offered as an alternative to visual tables
- [ ] Mathematical notation uses MathML or has a plain-text alternative
- [ ] Cell names in Latin or scientific notation are wrapped in appropriate `lang` or `<abbr>` tags

---

## 6. Testing Tools Reference

| Tool | Use |
|---|---|
| axe DevTools (browser extension) | Automated accessibility scanning |
| Lighthouse | Performance + accessibility audit |
| WAVE | Visual accessibility checker |
| NVDA + Chrome | Screen reader testing (Windows) |
| VoiceOver + Safari | Screen reader testing (macOS/iOS) |
| TalkBack | Screen reader testing (Android) |
| Colour Contrast Analyser | Manual contrast ratio checking |
| Keyboard only | Tab through every interactive element manually |
| 320px viewport | Test reflow at smallest supported width |

---

## 7. Pre-Launch Accessibility Sign-Off

Before any page or major component goes to production:

- [ ] Automated scan complete (0 critical errors in axe-core)
- [ ] Manual keyboard test complete
- [ ] Screen reader test complete (NVDA + VoiceOver minimum)
- [ ] Color contrast verified for all text and UI components
- [ ] Mobile screen reader tested (VoiceOver iOS or TalkBack)
- [ ] Review against this checklist documented in PR

---

## Changelog

| Date | Change | Author |
|---|---|---|
| [DATE] | Initial document created | — |

| 2026-09-03 | Added time-based/interactive figure requirements (captions, transcript, audio description, keyboard-operable 3D, text alternatives) tied to new figures fields; see decisions.md → Figure Type Axes Split | Claude (draft), Chris Crocker (sign-off) |
