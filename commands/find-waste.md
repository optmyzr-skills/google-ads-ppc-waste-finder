---
description: Find wasted Google Ads spend in the last 7 days and build a negative keyword list
---

Run the **Google Ads PPC Waste Finder** skill on the user's Google Ads account.

Ask for the account name if it isn't already given. Then pull the last 7 days of
search terms via the Optmyzr MCP (`get_active_accounts` to resolve the account,
`get_ppc_report` with `report_name=SearchTermPerformance`), flag terms that spent
over the threshold (default $20) with zero conversions, apply the brand /
competitor intent guardrail before recommending anything, group the true waste
into themes, estimate monthly savings, and return a ranked table plus a
ready-to-paste negative keyword list.

Follow the skill's `SKILL.md` for the orchestration and
`references/grouping-and-guardrails.md` for the classification logic. Use the
bundled `scripts/estimate_savings.py` for the savings projection so the math is
deterministic. Never apply negatives automatically — the skill recommends, a
human applies.
