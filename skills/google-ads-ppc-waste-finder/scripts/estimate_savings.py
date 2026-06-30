#!/usr/bin/env python3
"""Project monthly ad-spend waste from a week of flagged search terms.

The grouping and intent-classification are judgment calls made by the model;
this script just does the arithmetic deterministically so the numbers are the
same every run.

Input: a JSON file — either a list of row objects, or an object with a "rows"
key and optional "lookback_days" (default 7).

Each row object:
{
  "search_term": "google keyword planner",
  "theme": "Free / DIY tool seekers",
  "campaign": "Optmyzr | NB | PPC Solutions | ...",
  "match_type": "Exact",
  "clicks": 19,
  "cost": 45.13,
  "status": "Waste"          # one of: Waste | Review - competitor | Protected - brand
}

Only rows with status "Waste" count toward projected savings. "Review" and
"Protected" spend is reported separately and never counted as savings.

Usage:
  python3 estimate_savings.py rows.json
  python3 estimate_savings.py rows.json --lookback-days 7 --days-per-month 30.4
"""
import argparse
import json
import sys
from collections import defaultdict

DAYS_PER_MONTH = 30.4


def is_waste(status: str) -> bool:
    return (status or "").strip().lower() == "waste"


def is_review(status: str) -> bool:
    return (status or "").strip().lower().startswith("review")


def project_monthly(weekly_cost: float, lookback_days: int, days_per_month: float) -> float:
    if lookback_days <= 0:
        return 0.0
    return weekly_cost * days_per_month / lookback_days


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("rows_json", help="Path to JSON file of flagged rows.")
    p.add_argument("--lookback-days", type=int, default=None,
                   help="Days the cost figures cover (default 7, or 'lookback_days' in the file).")
    p.add_argument("--days-per-month", type=float, default=DAYS_PER_MONTH,
                   help="Days per month used for projection (default 30.4).")
    args = p.parse_args()

    with open(args.rows_json) as f:
        data = json.load(f)

    if isinstance(data, dict):
        rows = data.get("rows", [])
        file_lookback = data.get("lookback_days")
    else:
        rows = data
        file_lookback = None

    lookback = args.lookback_days or file_lookback or 7

    theme_weekly = defaultdict(float)
    theme_terms = defaultdict(int)
    waste_weekly = 0.0
    review_weekly = 0.0
    protected_weekly = 0.0

    for r in rows:
        cost = float(r.get("cost", 0) or 0)
        status = r.get("status", "Waste")
        if is_waste(status):
            waste_weekly += cost
            theme = r.get("theme", "Uncategorized")
            theme_weekly[theme] += cost
            theme_terms[theme] += 1
        elif is_review(status):
            review_weekly += cost
        else:
            protected_weekly += cost

    result = {
        "lookback_days": lookback,
        "days_per_month": args.days_per_month,
        "themes": [
            {
                "theme": theme,
                "terms": theme_terms[theme],
                "weekly_waste": round(weekly, 2),
                "projected_monthly_savings": round(
                    project_monthly(weekly, lookback, args.days_per_month), 2),
            }
            for theme, weekly in sorted(theme_weekly.items(), key=lambda kv: -kv[1])
        ],
        "total_weekly_waste": round(waste_weekly, 2),
        "total_projected_monthly_savings": round(
            project_monthly(waste_weekly, lookback, args.days_per_month), 2),
        "weekly_spend_to_review": round(review_weekly, 2),
        "monthly_spend_to_review": round(
            project_monthly(review_weekly, lookback, args.days_per_month), 2),
        "weekly_spend_protected": round(protected_weekly, 2),
        "note": ("Projected savings assume each negative fully eliminates the "
                 "term's future spend (upper bound). Review/Protected spend is "
                 "never counted as savings."),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
