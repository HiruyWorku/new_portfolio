---
name: Hiruy Worku Portfolio
description: A quiet editorial portfolio for engineering work and research.
colors:
  paper: "#f3f4f0"
  paperDeep: "#e6e8e2"
  ink: "#20221f"
  inkSoft: "#596269"
  rule: "#cbd1cf"
  accent: "#245b78"
  forest: "#3f6157"
typography:
  primary:
    fontFamily: "Avenir Next, Avenir, Segoe UI, sans-serif"
    fontWeight: 400
    lineHeight: 1.65
    letterSpacing: "0"
  label:
    fontFamily: "Azeret Mono, monospace"
    fontWeight: 400
rounded:
  default: "0px"
---

# Design System: Hiruy Worku

## Overview

**Creative North Star: "A well-edited working record"**

The portfolio behaves like a concise personal publication. It favors readable
prose, evidence-rich lists, direct links, and calm spacing over interface
spectacle. It should feel credible to recruiters, engineers, and researchers
without resembling a resume template or a product landing page.

## Principles

- Put work, research, and writing ahead of decoration.
- Let one typographic system organize the entire page.
- Use native disclosure controls only where they make dense information easier
  to scan.
- Keep photographs and project images small and documentary.
- Avoid animation, card grids, decorative effects, and app-like navigation.

## Color

The base is a cool off-white rather than pure white or cream. Charcoal carries
primary text. Muted blue marks interactive states and list markers. Evergreen
identifies technical metadata. Neither accent becomes a large field.

## Typography

Avenir Next carries names, prose, headings, and project titles, with a system
sans fallback. Azeret Mono is reserved for dates, navigation, technology, and
small organizational labels. Body copy stays within a readable measure.

## Layout

The desktop page uses a generous left margin and a focused reading column.
About opens with a small portrait beside the name and direct links below it;
Ventings, Experience, Projects, Research, Skills, and Contact use native disclosures so
the full record stays available without presenting one intimidating long page.
At smaller widths, the reading column uses the full available width.

## Components

### Project entry

A bordered editorial row containing a title, context, summary, evidence, stack,
and direct proof links. Selected entries may include one documentary image.

### Experience disclosure

The summary always shows date, organization, role, a plain-language account,
and a view-details cue. Opening the row reveals full bullet points and technologies.

### Photo record

A small circular, framed profile photograph appears beside the name. Three other static
photographs appear later in About. They do not rotate or behave like a gallery.

### Contact form

Plain labeled fields with bottom rules and a solid submit button. The form is
secondary to the direct email link but remains available.
