import json
import sqlite3
import subprocess
import sys
from contextlib import closing
from datetime import date
from pathlib import Path

import pytest

from finance_evals.contracts import evaluate
from finance_evals.reference_calculations import (
    PeriodRevenue,
    ReportingPeriod,
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


@pytest.mark.parametrize(
    ("reporting_date", "expected"),
    [
        ("2026-11-18", ("2026-09-01", "2026-10-01", "2026-11-01")),
        ("2027-01-01", ("2026-11-01", "2026-12-01", "2027-01-01")),
        ("2024-03-01", ("2024-01-01", "2024-02-01", "2024-03-01")),
    ],
)
def test_completed_months(reporting_date, expected):
    start, middle, end = map(date.fromisoformat, expected)
    assert completed_months(date.fromisoformat(reporting_date)) == (
        ReportingPeriod(start, middle),
        ReportingPeriod(middle, end),
    )


def calculate_both(fixture, segment, periods):
    with closing(sqlite3.connect(":memory:")) as connection:
        load_revenue_transactions(connection, fixture)
        sql = tuple(aggregate_revenue_sql(connection, segment, period) for period in periods)
    python = tuple(reconcile_revenue_python(fixture, segment, period) for period in periods)
    assert sql == python
    return sql


def test_marketplace_reconciles_to_manual_totals_and_boundary_ids():
    periods = completed_months(date(2026, 11, 18))
    prior, current = calculate_both(FIXTURE, "Marketplace", periods)
    assert prior == PeriodRevenue(
        2, 1_100_000_000, 100_000_000, 1_000_000_000, ("TX-001", "TX-002")
    )
    assert current == PeriodRevenue(
        2, 950_000_000, 50_000_000, 900_000_000, ("TX-003", "TX-004")
    )
    assert compare_revenue(prior.net_cents, current.net_cents) == RevenueComparison(
        -100_000_000, "-10.00", None
    )


def test_direct_zero_revenue_differs_from_missing_wholesale():
    periods = completed_months(date(2026, 11, 18))
    prior, current = calculate_both(FIXTURE, "Direct", periods)
    assert current == PeriodRevenue(2, 15_000_000, 15_000_000, 0, ("TX-007", "TX-008"))
    assert compare_revenue(prior.net_cents, current.net_cents) == RevenueComparison(
        -25_000_000, "-100.00", None
    )
    missing = PeriodRevenue(0, None, None, None, ())
    assert calculate_both(FIXTURE, "Wholesale", periods) == (missing, missing)


@pytest.mark.parametrize(
    ("prior_type", "prior_amount", "expected_net", "expected"),
    [
        ("revenue", 0, 0, RevenueComparison(200, None, "Prior net revenue is zero.")),
        ("credit", 50, -50, RevenueComparison(250, None, "Prior net revenue is negative.")),
        (None, None, None, RevenueComparison(None, None, "Missing revenue in one or both periods.")),
    ],
)
def test_comparisons_with_nonpositive_or_missing_prior(
    tmp_path, prior_type, prior_amount, expected_net, expected
):
    current = dict(
        transaction_id="current", posting_date="2026-10-01", business_segment="Test",
        entry_type="revenue", amount_cents=200, currency="USD",
    )
    rows = [current]
    if prior_type is not None:
        rows.append(dict(
            current, transaction_id="prior", posting_date="2026-09-30",
            entry_type=prior_type, amount_cents=prior_amount,
        ))
    path = tmp_path / "comparison.json"
    path.write_text(json.dumps(rows), encoding="utf-8")

    periods = completed_months(date(2026, 11, 18))
    prior, present = calculate_both(path, "Test", periods)
    assert prior.net_cents == expected_net
    assert present.net_cents == 200
    assert compare_revenue(prior.net_cents, present.net_cents) == expected


def test_missing_current_period_makes_comparison_unavailable():
    assert compare_revenue(100, None) == RevenueComparison(
        None, None, "Missing revenue in one or both periods."
    )


@pytest.mark.parametrize(("current", "expected"), [(20001, "0.01"), (19999, "-0.01"), (20000, "0.00")])
def test_percentage_rounds_half_away_from_zero_and_formats_two_places(current, expected):
    assert compare_revenue(20000, current) == RevenueComparison(current - 20000, expected, None)


def test_reference_artifact_matches_verified_generation_and_lesson00_contract():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/generate_lesson01_reference.py")],
        check=True,
        capture_output=True,
    )
    assert ARTIFACT.read_bytes() == result.stdout.replace(b"\r\n", b"\n")
    artifact = json.loads(result.stdout)
    assert artifact["review_status"] == "demo_authored"
    assert artifact["dataset_version"] == artifact["business_rule_version"] == "1"

    answers = json.loads((ROOT / "evals/cases/lesson00_answers.json").read_text(encoding="utf-8"))
    checks = evaluate(answers[0], artifact["reference"])["checks"]
    assert checks["numbers_correct"] == checks["scope_and_period_correct"] == "pass"
