# Grouping and guardrails

This file explains how to classify a zero-conversion, high-spend search term
before it ever reaches the negative keyword list. The classification matters
more than the grouping: a wrong negative can cut off brand traffic or undo a
deliberate competitor strategy, which is far costlier than a few dollars of
genuine waste left running one extra week.

## The core question

For each flagged term, ask: **was this campaign *trying* to capture this kind of
query?** If yes, zero conversions over a short window is a signal to investigate,
not to block. If no, it's waste.

## Classification rules

Evaluate in this order; first match wins.

### 1. Protected — brand
Signals (any combination):
- Campaign or ad group name contains "Brand", "BR", "Branded", or the
  advertiser's own company/product name.
- The matched keyword or the search term is the advertiser's brand name or a
  misspelling/variant of it (e.g. for Optmyzr: "optmyzr", "optimyzer",
  "optmizer", "optmyzr ppc").

Action: **exclude from negatives entirely.** People searching your brand are
high-intent; a 7-day zero-conversion blip is almost always tracking lag, a
short window, or assisted conversions landing elsewhere. Negating your own
brand is one of the most expensive mistakes in PPC. Label `Protected — brand`.

### 2. Review — competitor
Signals:
- Campaign or ad group name contains "Competitor", "Competitors", "Conquest",
  "Conquesting", or "vs".
- The search term is a recognizable rival brand (for Optmyzr's space, e.g.
  "semrush", "opteo", "adalysis", "spyfu") and it's matching through a keyword
  that targets that rival on purpose.

Action: **flag for human review; do not auto-negative.** Competitor conquesting
often has a long, indirect payback (brand consideration, multi-touch journeys)
and zero last-click conversions in a week doesn't mean it failed. Surface the
spend so the user can decide. Label `Review — competitor`.

### 3. Waste
Everything else: generic, informational, free/DIY-tool, job-seeker, wrong-
category, or plainly off-topic queries appearing in non-brand, non-competitor
campaigns.

Action: **this is the negative list.** Label `Waste`.

A useful tell for the most clear-cut waste: queries that signal the searcher
wants something free, manual, or unrelated to a paid product — "free", "diy",
"template", "how to", "jobs", "salary", "login" (when you're not the brand),
"google keyword planner" (a free Google tool, not your paid software), etc.

## Grouping the Waste rows into themes

Group by searcher *intent*, not by string overlap. The goal is themes a human
recognizes at a glance and that map to a sensible phrase negative.

Common themes:
- **Free / DIY tool seekers** — want a no-cost or build-it-yourself option.
- **Job / career seekers** — "jobs", "careers", "salary", "hiring".
- **Wrong product or category** — adjacent product the account doesn't sell.
- **Informational / how-to** — research intent, not buying intent.
- **Geographic mismatch** — locations you don't serve.

For each theme, pick the shared token(s) that make a safe phrase negative. The
phrase negative is broader than the exact negative, so always present it as
"review before applying" rather than paste-and-go.

## Match type guidance for the negative list

- **Exact-match negative of the full search term**: safest. Blocks only that
  exact query. Default for every `Waste` term.
- **Phrase-match negative of a theme token**: broader reach, blocks variations.
  Offer it at the theme level, clearly labeled as needing a quick human check so
  it doesn't accidentally block a valuable query that happens to share the word.
- Avoid broad-match negatives unless the user asks — they over-block.
