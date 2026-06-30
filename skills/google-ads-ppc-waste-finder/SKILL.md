---
name: google-ads-ppc-waste-finder
description: >-
  Find wasted ad spend in a Google Ads account by pulling the last 7 days of
  search terms via the Optmyzr MCP, flagging terms that spent over a threshold
  (default $20) with zero conversions, grouping them into themes, estimating the
  monthly savings from adding them as negative keywords, and producing a ranked
  table plus a ready-to-paste negative keyword list. Use this skill whenever the
  user wants to find wasted spend, audit search terms, "find waste", surface
  zero-conversion queries, build a negative keyword list, clean up search terms,
  or run a weekly/recurring waste check on a Google Ads (or Bing/Yahoo) account.
  Trigger on phrases like "weekly waste finder", "find my wasted spend", "what's
  burning budget", "search term waste report", "negatives I should add", or
  "where am I losing money in [account]". Works for one named account per run.
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
the theme. Format so it pastes cleanly into Optmyzr's negative keyword tools or
Google Ads:

```
Exact negatives (one per term):
[google keyword planner]

Phrase negatives (theme-level, broader — review before applying):
"keyword planner"
```

Close with a one or two sentence summary: total projected monthly savings, how
many terms are clean waste vs. need review, and a reminder that brand/competitor
terms were deliberately excluded.

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
