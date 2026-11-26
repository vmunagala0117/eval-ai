import json
import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from finance_evals.source_data import load_revenue_transactions


FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "evals" / "source" / "revenue_transactions_v1.json"
)


def read_rows(connection):
    return connection.execute("""
        SELECT transaction_id, posting_date, business_segment, entry_type,
               amount_cents, currency
        FROM revenue_transactions
        ORDER BY transaction_id
    """).fetchall()


def test_loads_fixture_into_sqlite(tmp_path):
    database = tmp_path / "transactions.sqlite3"
    with closing(sqlite3.connect(database)) as connection:
        load_revenue_transactions(connection, FIXTURE)

    with closing(sqlite3.connect(database)) as connection:
        rows = read_rows(connection)

    assert len(rows) == 8
    assert rows[:5] == [
        ("TX-001", "2026-09-01", "Marketplace", "revenue", 1100000000, "USD"),
        ("TX-002", "2026-09-30", "Marketplace", "credit", 100000000, "USD"),
        ("TX-003", "2026-10-01", "Marketplace", "revenue", 950000000, "USD"),
        ("TX-004", "2026-10-31", "Marketplace", "credit", 50000000, "USD"),
        ("TX-005", "2026-11-01", "Marketplace", "revenue", 200000000, "USD"),
    ]
    assert rows[5:] == [
        ("TX-006", "2026-09-15", "Direct", "revenue", 25000000, "USD"),
        ("TX-007", "2026-10-12", "Direct", "revenue", 15000000, "USD"),
        ("TX-008", "2026-10-25", "Direct", "credit", 15000000, "USD"),
    ]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("transaction_id", "TX-001"),
        ("entry_type", "refund"),
        ("amount_cents", -1),
        ("amount_cents", 2.5),
        ("amount_cents", 2.0),
        ("amount_cents", True),
        ("amount_cents", "100"),
        ("amount_cents", None),
        ("amount_cents", 2**63),
        ("posting_date", "2026-09-31"),
        ("posting_date", "20260930"),
        ("business_segment", " "),
        ("currency", "EUR"),
    ],
)
def test_rejects_invalid_fixture_without_creating_table(tmp_path, field, value):
    transactions = json.loads(FIXTURE.read_text(encoding="utf-8"))
    transactions[1][field] = value
    invalid_fixture = tmp_path / "invalid.json"
    invalid_fixture.write_text(json.dumps(transactions), encoding="utf-8")

    with closing(sqlite3.connect(tmp_path / "transactions.sqlite3")) as connection:
        with pytest.raises(ValueError, match=field):
            load_revenue_transactions(connection, invalid_fixture)
        assert connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall() == []


def test_fresh_rebuilds_match_and_existing_table_is_preserved(tmp_path):
    with closing(sqlite3.connect(tmp_path / "first.sqlite3")) as first:
        load_revenue_transactions(first, FIXTURE)
        original_rows = read_rows(first)

        with pytest.raises(sqlite3.OperationalError, match="already exists"):
            load_revenue_transactions(first, FIXTURE)
        assert read_rows(first) == original_rows

    with closing(sqlite3.connect(tmp_path / "second.sqlite3")) as second:
        load_revenue_transactions(second, FIXTURE)
        assert read_rows(second) == original_rows
