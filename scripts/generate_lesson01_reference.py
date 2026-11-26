"""Explicitly generate the evaluator-owned Lesson 01 reference."""

import argparse
import json
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path

from finance_evals.reference_calculations import (
    PeriodRevenue,
    RevenueComparison,
    aggregate_revenue_sql,
    compare_revenue,
    completed_months,
    reconcile_revenue_python,
)
from finance_evals.source_data import load_revenue_transactions


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "evals/source/revenue_transactions_v1.json"
ARTIFACT = ROOT / "evals/reference/lesson01_marketplace_revenue_v1.json"


def build_reference() -> dict:
    reporting_date = date(2026, 11, 18)
    segment = "Marketplace"
    periods = completed_months(reporting_date)
    manual = (
        PeriodRevenue(2, 1_100_000_000, 100_000_000, 1_000_000_000, ("TX-001", "TX-002")),
        PeriodRevenue(2, 950_000_000, 50_000_000, 900_000_000, ("TX-003", "TX-004")),
    )
    if tuple((period.start.isoformat(), period.end.isoformat()) for period in periods) != (
        ("2026-09-01", "2026-10-01"), ("2026-10-01", "2026-11-01")
    ):
        raise ValueError("Reporting periods disagree with the manual case")

    with closing(sqlite3.connect(":memory:")) as connection:
        load_revenue_transactions(connection, FIXTURE)
        sql = tuple(aggregate_revenue_sql(connection, segment, period) for period in periods)
    python = tuple(reconcile_revenue_python(FIXTURE, segment, period) for period in periods)
    if sql != manual or python != manual:
        raise ValueError(f"SQL, Python, and manual reconciliation disagree: {sql=}, {python=}, {manual=}")

    prior, current = sql
    comparison = compare_revenue(prior.net_cents, current.net_cents)
    if comparison != RevenueComparison(-100_000_000, "-10.00", None):
        raise ValueError(f"Comparison disagrees with the manual case: {comparison}")

    return {
        "case_id": "lesson01_marketplace_revenue",
        "version": "1",
        "dataset_version": "1",
        "source_fixture": FIXTURE.relative_to(ROOT).as_posix(),
        "business_rule_version": "1",
        "fixed_today": reporting_date.isoformat(),
        "review_status": "demo_authored",
        "reference": {
            "scope": segment,
            "metric": "net_revenue",
            "prior_period": periods[0].label,
            "current_period": periods[1].label,
            "prior_cents": prior.net_cents,
            "current_cents": current.net_cents,
            "change_cents": comparison.change_cents,
            "change_pct": comparison.change_pct,
        },
        "source_record_ids": {
            periods[0].label: prior.transaction_ids,
            periods[1].label: current.transaction_ids,
        },
        "evidence_limit": "Posting records establish the amount of the decline. They do not establish its business cause.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write the verified JSON to the reference path.")
    args = parser.parse_args()
    output = json.dumps(build_reference(), indent=2) + "\n"
    if args.write:
        ARTIFACT.write_text(output, encoding="utf-8", newline="\n")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
