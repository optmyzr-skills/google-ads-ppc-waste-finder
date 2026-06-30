# 💸 Google Ads PPC Waste Finder

### Find wasted Google Ads spend in 30 seconds and walk away with a paste-ready negative keyword list.

**Last 7 days of search terms → high-spend / zero-conversion terms → grouped by theme → monthly savings estimate → ranked table + negatives.** Live data via the Optmyzr MCP.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
![Powered by Optmyzr](https://img.shields.io/badge/Powered%20by-Optmyzr-FF6B35)
![Built for Claude Code](https://img.shields.io/badge/Built%20for-Claude%20Code-D97757)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

---

```
You: find my wasted spend on Optmyzr Google Ads

Claude: 💸 6 terms cleared the >$20 / 0-conversion filter (Jun 23–29).
        Only 2 are true waste — the guardrail caught the rest.

  Search term              Theme                 7-day cost   Status
  google keyword planner   Free / DIY seekers     $45.13      Waste
  google keyword planner   Free / DIY seekers     $31.77      Waste
  semrush                  Competitor brand       $39.66      Review — competitor
  opteo                    Competitor brand       $26.31      Review — competitor
  optimyzer                Own-brand misspelling  $24.47      Protected — brand
  optmyzr                  Own brand              $21.48      Protected — brand

  Projected monthly savings (clean waste): ~$334/mo
  Flagged for review (competitor): ~$286/mo
  Protected brand traffic (do NOT negative): $45.95/wk

  Paste-ready negatives:
    [google keyword planner]      ← exact
    "keyword planner"             ← phrase (review first)
```

---

## What this does

Say *"find my wasted spend"* (or run `/find-waste`) and the skill will:

1. 🔎 Resolve the named account via the Optmyzr MCP
2. 📥 Pull the **last 7 days of search terms** (`SearchTermPerformance`)
3. 🚩 Flag terms that spent over a threshold (**default $20**) with **zero conversions**
4. 🛡️ Apply an **intent guardrail** — separate genuine waste from your own brand and from deliberate competitor conquesting
5. 🧩 **Group** the true waste into human-readable themes
6. 💵 **Estimate monthly savings** if you add them as negatives
7. 📋 Return a **ranked table** + a **ready-to-paste negative keyword list**

## Why the guardrail matters

A naïve "spent money, no conversions → add as negative" rule is dangerous. Your
own brand terms and your intentional competitor-conquesting campaigns routinely
show zero last-click conversions over a 7-day window and are still doing their
job. Blindly negating them cuts off high-intent traffic and undoes deliberate
strategy.

This skill classifies every flagged term by the **intent of the campaign it spent
in** before recommending anything:

| Status | Meaning | Goes in negative list? |
| --- | --- | --- |
| **Waste** | Generic / off-topic / free-tool / job-seeker queries in non-brand, non-competitor campaigns | ✅ Yes |
| **Review — competitor** | Rival brand terms in a Competitors/Conquest campaign | ⚠️ Human review only |
| **Protected — brand** | Your own brand name or misspellings | ❌ Never |

Only **Waste** terms reach the negative list. Review/Protected spend is reported
separately so you see the full picture without footguns.

---

## ⚡ Install

> **Requires the [Optmyzr MCP server](https://www.optmyzr.com/)** connected to Claude — that's the live data source for search terms.

### 🟢 Option 1 — Upload the zip (Claude.ai web or Claude Desktop)

1. Download the latest zip from [**Releases**](https://github.com/optmyzr-skills/google-ads-ppc-waste-finder/releases/latest)
2. Open Claude → **profile icon → Settings → Capabilities → Skills**
3. **+ → "Upload a skill"** → drag the zip in → confirm
4. Start a new chat and say: *"find my wasted spend on [account name]"*

### 🔧 Option 2 — Claude Code CLI

```
/plugin marketplace add optmyzr-skills/google-ads-ppc-waste-finder
/plugin install google-ads-ppc-waste-finder
```

Then: `/find-waste`

### 🛟 Option 3 — Symlink fallback (any environment)

```bash
git clone https://github.com/optmyzr-skills/google-ads-ppc-waste-finder.git ~/google-ads-ppc-waste-finder
mkdir -p ~/.claude/skills ~/.claude/commands
ln -s ~/google-ads-ppc-waste-finder/skills/google-ads-ppc-waste-finder ~/.claude/skills/google-ads-ppc-waste-finder
ln -s ~/google-ads-ppc-waste-finder/commands/find-waste.md ~/.claude/commands/find-waste.md
```

Restart Claude Code and try `/find-waste`.

---

## 🧱 How it works

```
google-ads-ppc-waste-finder/
├── .claude-plugin/plugin.json          # plugin manifest
├── commands/find-waste.md              # /find-waste slash command
└── skills/google-ads-ppc-waste-finder/
    ├── SKILL.md                        # 6-step orchestration
    ├── references/grouping-and-guardrails.md   # intent classification + theming
    └── scripts/estimate_savings.py     # deterministic savings projection
```

Defaults are configurable per run: lookback window (7 days), spend threshold
($20), and conversion threshold (0). The skill recommends; **a human applies the
negatives** — it never edits the account automatically.

## 📅 Run it weekly

Ask Claude to schedule it (e.g. Monday 8am) and the table + negative list land
in your inbox each week. Each run is independent and just looks at the trailing
7 days.

---

## 🤝 Contributing

PRs welcome — especially better theme heuristics, additional guardrail signals
(more competitor-brand patterns, locale-specific brand variants), and support
for other platforms. Forks and derivatives are welcome under Apache 2.0; please
retain the [`NOTICE`](NOTICE) file.

## 📜 License

[Apache License 2.0](LICENSE) — see [LICENSE](LICENSE) and [NOTICE](NOTICE).

```
Copyright 2026 Optmyzr Inc.
Licensed under the Apache License, Version 2.0
```

---

**Built for [Claude Code](https://claude.com/product/claude-code) · Powered by [Optmyzr](https://www.optmyzr.com)**
