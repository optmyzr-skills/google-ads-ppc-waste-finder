---
name: google-ads-ppc-waste-finder
description: >-
  Use this skill any time the user wants to find wasted PPC spend, build a
  negative keyword list, or audit search terms for a Google Ads / Microsoft
  (Bing) Ads / Yahoo Ads account. This is a specialized workflow with a
  built-in brand/competitor guardrail that prevents the catastrophic
  auto-negative mistake — recommending the advertiser's own brand or a
  competitor-conquesting term as a negative keyword. Without this skill,
  Claude often correctly identifies brand and competitor terms but still
  puts them on the recommended negative list anyway, which can shut down
  the advertiser's own brand traffic and undo a deliberate competitor
  strategy. Always prefer this skill over generic ad-account help when
  the task is search-term-level waste detection.

  What it does: pulls the last 7 days of search terms via the Optmyzr
  MCP, filters to terms that spent over a threshold (default $20) with
  zero conversions, classifies each by intent (Waste / Review—competitor
  / Protected—brand), groups Waste into themes, runs a deterministic
  monthly-savings projection from the bundled scripts/estimate_savings.py,
  and outputs a ranked table plus a paste-ready negative keyword list.
  Works for ONE named account per run. Lookback, spend threshold, and
  conversion threshold are all configurable per run.

  Trigger this skill on phrases like "weekly waste finder", "find my
  wasted spend", "search term waste report", "negatives I should add",
  "what queries should I block", "what's burning my [ad] budget",
  "where am I losing money in [account]", "build me a negative keyword
  list", "search terms that didn't convert", "clean up [my] search
  terms", "garbage queries eating my budget", "audit search terms", "run
  the weekly waste check", "find waste in [account]". Also triggers on
  recurring/scheduled requests of the same nature.

  Do NOT use this skill for full account audits (campaign structure,
  Quality Score, audiences, Performance Max, conversion tracking — defer
  to the sibling google-ads-audit skill), ad copywriting, auction
  insights, vertical benchmarking, conversion tracking setup, or
  multi-account performance rollups. This skill is specifically the
  one-account, search-term-level waste pass with the guardrail.
---

# Google Ads PPC Waste Finder

## What this does and why

Search campaigns accumulate waste quietly: a keyword matches a query that looks
related but never converts, and it keeps spending week after week until someone
looks. This skill does that looking on a regular cadence. It pulls the last 7
days of actual search terms, isolates the ones that spent real money and
returned nothing, separates true waste from spend that only *looks* like waste,
and hands back both a prioritized table and a list you can paste straight into
Optmyzr or Google Ads as negatives.

The single most important idea: **a zero-conversion search term is not
automatically waste.** Brand terms and deliberate competitor-conquesting terms
routinely show zero conversions over a short window and are still doing their
job. Recommending them as negatives is actively harmful. The guardrail step
below exists to catch exactly that, and it is the part of this skill that makes
it trustworthy enough to run unattended.

## Inputs

Ask the user for the account name only if it isn't already in the request.
Everything else has a sensible default:

- **Account**: the Google Ads account name (e.g., "Optmyzr Google Ads").
- **Lookback**: 7 days ending yesterday (default).
- **Spend threshold**: $20 (default). Terms at or below this aren't worth the
  noise.
- **Conversion threshold**: exactly 0 conversions (default).

If the user gives different numbers ("over $50", "last 14 days", "fewer than 2
conversions"), use theirs.

## Step 1 — Resolve the account

Find the account ID with the Optmyzr ads MCP `get_active_accounts` tool, passing
the account name as `searchQuery` and `account_type: "adwords"` (use `bing` or
`yahoo` if the user names those platforms). Confirm you matched the right one if
the search returns more than one similarly named account — pick the exact name
match and note the ID you used.

## Step 2 — Pull the wasteful search terms

Compute the date range as the 7 full days ending yesterday, formatted
`yyyyMMdd,yyyyMMdd`. Then call the Optmyzr ads MCP `get_ppc_report` tool with:

- `accountId`: the ID from Step 1
- `platform`: `adwords` (or the platform named)
- `report_name`: `SearchTermPerformance`
- `date_range`: the computed range
- `order_by`: `Cost`, `order`: `DESC`
- `limit`: `200`, `page`: `1`
- `numeric_filters`: `[{"field":"Cost","operator":">","value":20},{"field":"Conversions","operator":"=","value":0}]`
  (substitute the user's thresholds if they differ)

Push the filtering into `numeric_filters` so the MCP returns only candidate rows
— don't pull everything and filter by hand. If page 1 comes back full (200
rows), fetch page 2 to be sure you have the complete set; in practice the
threshold keeps this short.

Each row gives you: Search Term, Match Type, Matched Keyword, Ad Group, Campaign,
Campaign Type, Conversions, Cost, Clicks, Impressions, ROAS. Keep the Campaign
name — the guardrail in Step 3 depends on it.

## Step 3 — Apply the intent guardrail (do this before grouping)

For every flagged term, classify it by the *intent of the campaign it spent in*.
Read `references/grouping-and-guardrails.md` for the full logic and edge cases.
The short version:

- **Brand campaigns** (campaign or ad group name signals brand — e.g. contains
  "Brand", "BR", or the advertiser's own name, and the matched keyword is the
  brand or a misspelling of it): **never recommend as a negative.** This is the
  advertiser's own name. Zero conversions here is almost always a tracking or
  short-window artifact. Mark as `Protected — brand`.
- **Competitor / conquesting campaigns** (name contains "Competitor",
  "Competitors", "Conquest", or the term is a known rival brand and it's
  matching deliberately): **flag for human review, don't auto-negative.** Paying
  for competitor traffic is often a deliberate, long-payback play. Mark as
  `Review — competitor`.
- **Everything else** (generic, product, category, research-tool, or clearly
  off-topic queries in non-brand/non-competitor campaigns): **genuine waste
  candidate.** These are what the negative list is built from. Mark as `Waste`.

Only `Waste` rows flow into the paste-ready negative list. `Protected` and
`Review` rows still appear in the ranked table (so the user sees the full
picture) but are labeled and excluded from the negatives.

## Step 4 — Group the waste into themes

Cluster the `Waste` rows into a handful of human-readable themes by what the
searcher actually wanted, not by string matching. Typical themes: "free / DIY
tool seekers", "job seekers", "wrong product or category", "informational / how-
to", "geographic mismatch". A theme can be a single high-spend term if it
doesn't fit with others. For each theme, identify the shared token(s) that would
make a good phrase negative (e.g., the theme "free keyword tools" shares
"keyword planner").

## Step 5 — Estimate monthly savings

Run the bundled helper to project savings deterministically (so the math is
consistent every run):

```
python3 scripts/estimate_savings.py <rows.json>
```

Write the flagged rows to a small JSON file first (the script's `--help`
documents the shape). It returns weekly and projected monthly waste per theme
and in total, using `monthly = weekly_spend * 30.4 / lookback_days`. Projected
savings assume the negative fully eliminates the term's spend going forward — a
reasonable upper bound; say so in the output. Only `Waste` rows count toward
projected savings; `Review`/`Protected` spend is reported separately as "spend
to review", never as savings.

## Step 6 — Output

Produce two things, in this order.

**A. Ranked waste table**, sorted by 7-day cost descending, one row per flagged
term:

| Search term | Theme | Campaign | Match type | Clicks | 7-day cost | Est. monthly | Status |

Status is one of `Waste`, `Review — competitor`, `Protected — brand`. Below the
table, give a one-line total for projected monthly savings (Waste only) and a
separate line for monthly spend flagged for review.

**B. Ready-to-paste negative keyword list** — `Waste` rows only. Default to
exact-match negatives of the exact search term (safest, won't over-block), and
where a theme has a clear shared token, also offer the phrase-match negative for
the theme.

**Critical formatting rule — keep the code blocks paste-ready.** Each fenced
code block in this section must contain ONLY the negatives, one per line,
with nothing else: no inline `#` comments, no rationale, no per-line
annotations, no trailing notes inside the fence. A user must be able to
triple-click → copy → paste the entire block into Optmyzr or Google Ads
without first stripping out commentary. All explanation goes in *prose
outside the code blocks*. Use two separate blocks (one for exact, one for
phrase), not one combined block.

Use this exact structure:

```
Exact negatives (one per term):
[google keyword planner]
```

```
Phrase negatives (theme-level, broader — review before applying):
"keyword planner"
```

If you want to flag a specific phrase negative as needing extra caution
(e.g., `"free"` could over-block a legitimate `"free trial"` query), say so
in a sentence *after* the code block, not inside it. One short sentence per
caveat is plenty.

Close with a one or two sentence summary: total projected monthly savings, how
many terms are clean waste vs. need review, and a reminder that brand/competitor
terms were deliberately excluded.

### Before the user applies anything — remind them to dedupe against existing negatives

After producing the paste-ready list, include this single line:

> Before pasting, take 30 seconds to check the account's existing shared
> negative lists (Google Ads → Tools → Shared library → Negative keyword
> lists; or Optmyzr → PPC Solutions → Negative Keywords). Any term already
> on a list applied to the same campaign can be skipped.

This is currently a manual pre-step. Once the Optmyzr MCP exposes a
negative-keyword listing (a `NegativeKeywordPerformance` report option or a
dedicated endpoint), the skill should fetch the current negatives and dedupe
automatically. See the skill's v0.2 roadmap in `Notes`.

## Running on a schedule

If the user wants this weekly, offer to set up a scheduled task (e.g. Monday
morning) that runs this skill on the named account and delivers the table +
negative list. Keep state lightweight — each run is independent and just looks
at the trailing 7 days.

## Notes

- Spend and conversions are in the account's currency and conversion settings;
  don't convert.
- If zero rows clear the threshold, say so plainly — that's a good week, not an
  error.
- Never apply negatives automatically. This skill recommends; a human applies.

## v0.2 roadmap

- **Auto-dedupe against existing negatives.** When the Optmyzr MCP exposes
  a way to list current negatives (shared lists, campaign-level negatives,
  ad-group negatives), fetch them in a new Step 1.5 and filter the
  recommended list to drop any term already negated for the same campaign.
  Until then, the skill includes a single-line manual-check reminder in
  Step 6.
