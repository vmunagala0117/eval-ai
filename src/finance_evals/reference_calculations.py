"""Completed-month revenue calculations for the synthetic reference case."""

import json
import sqlite3
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal, localcontext
from pathlib import Path

from .source_data import read_revenue_transactions


@dataclass(frozen=True)
class ReportingPeriod:
    start: date
    end: date

    @property
    def label(self) -> str:
        return self.start.isoformat()[:7]


def completed_months(reporting_date: date) -> tuple[ReportingPeriod, ReportingPeriod]:
    """Return the prior and current completed periods with exclusive ends."""
    incomplete_start = reporting_date.replace(day=1)
    current_start = (incomplete_start - timedelta(days=1)).replace(day=1)
    prior_start = (current_start - timedelta(days=1)).replace(day=1)
    return (
        ReportingPeriod(prior_start, current_start),
        ReportingPeriod(current_start, incomplete_start),
    )


@dataclass(frozen=True)
class PeriodRevenue:
    record_count: int
    revenue_cents: int | None
    credit_cents: int | None
    net_cents: int | None
    transaction_ids: tuple[str, ...]


def aggregate_revenue_sql(
    connection: sqlite3.Connection, segment: str, period: ReportingPeriod
) -> PeriodRevenue:
    """Aggregate a USD segment and collect its evidence in one SQL snapshot."""
    count, revenue, credits, net, evidence = connection.execute(
        """
        WITH totals AS (
            SELECT COUNT(*) AS record_count,
                   SUM(CASE WHEN entry_type = 'revenue' THEN amount_cents ELSE 0 END)
                       AS revenue_cents,
                   SUM(CASE WHEN entry_type = 'credit' THEN amount_cents ELSE 0 END)
                       AS credit_cents,
                   json_group_array(transaction_id) AS transaction_ids
            FROM main.revenue_transactions
            WHERE business_segment = ? AND currency = ?
              AND posting_date >= ? AND posting_date < ?
        )
        SELECT record_count, revenue_cents, credit_cents,
               revenue_cents - credit_cents, transaction_ids
        FROM totals
        """,
        (segment, "USD", period.start.isoformat(), period.end.isoformat()),
    ).fetchone()
    return PeriodRevenue(count, revenue, credits, net, tuple(sorted(json.loads(evidence))))


def reconcile_revenue_python(
    fixture_path: str | Path, segment: str, period: ReportingPeriod
) -> PeriodRevenue:
    """Reconcile the original fixture independently of the database."""
    ids = []
    revenue = credits = 0
    for identifier, posting_date, business_segment, entry_type, amount, currency in (
        read_revenue_transactions(fixture_path)
    ):
        if business_segment != segment or currency != "USD":
            continue
        if not period.start <= date.fromisoformat(posting_date) < period.end:
            continue
        ids.append(identifier)
        if entry_type == "revenue":
            revenue += amount
        else:
            credits += amount

    if not ids:
        return PeriodRevenue(0, None, None, None, ())
    return PeriodRevenue(len(ids), revenue, credits, revenue - credits, tuple(sorted(ids)))


@dataclass(frozen=True)
class RevenueComparison:
    change_cents: int | None
    change_pct: str | None
    reason: str | None


def compare_revenue(prior_cents: int | None, current_cents: int | None) -> RevenueComparison:
    """Compare net cents and round percentage ties away from zero."""
    if prior_cents is None or current_cents is None:
        return RevenueComparison(None, None, "Missing revenue in one or both periods.")

    change = current_cents - prior_cents
    if prior_cents == 0:
        return RevenueComparison(change, None, "Prior net revenue is zero.")
    if prior_cents < 0:
        return RevenueComparison(change, None, "Prior net revenue is negative.")

    with localcontext() as context:
        context.prec = 64
        context.rounding = ROUND_HALF_UP
        percentage = (Decimal(change) * 100 / Decimal(prior_cents)).quantize(Decimal("0.01"))
    return RevenueComparison(change, format(percentage, ".2f"), None)
