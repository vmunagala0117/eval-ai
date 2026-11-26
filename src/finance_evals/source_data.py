"""Load the synthetic revenue transaction fixture into SQLite."""

import json
import sqlite3
from datetime import date
from pathlib import Path


_COLUMNS = (
    "transaction_id", "posting_date", "business_segment",
    "entry_type", "amount_cents", "currency",
)


def read_revenue_transactions(fixture_path: str | Path) -> list[tuple]:
    """Read and validate source records in schema column order."""
    transactions = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    if not isinstance(transactions, list):
        raise ValueError("Expected a JSON array of transactions")

    identifiers = set()
    rows = []
    for index, transaction in enumerate(transactions, start=1):
        if not isinstance(transaction, dict) or transaction.keys() != set(_COLUMNS):
            raise ValueError(f"Record {index} must contain exactly the transaction fields")
        identifier, posting_date, segment, entry_type, amount, currency = (
            transaction[column] for column in _COLUMNS
        )
        if not isinstance(identifier, str) or not identifier.strip():
            raise ValueError(f"Record {index}: transaction_id must be nonblank text")
        if identifier in identifiers:
            raise ValueError(f"Duplicate transaction_id: {identifier}")
        identifiers.add(identifier)

        try:
            canonical_date = date.fromisoformat(posting_date).isoformat()
        except (TypeError, ValueError):
            raise ValueError(f"{identifier}: posting_date must be a YYYY-MM-DD calendar date") from None
        if canonical_date != posting_date:
            raise ValueError(f"{identifier}: posting_date must be a YYYY-MM-DD calendar date")
        if not isinstance(segment, str) or not segment.strip():
            raise ValueError(f"{identifier}: business_segment must be nonblank text")
        if entry_type not in ("revenue", "credit"):
            raise ValueError(f"{identifier}: entry_type must be revenue or credit")
        if type(amount) is not int or not 0 <= amount <= 2**63 - 1:
            raise ValueError(f"{identifier}: amount_cents must be a nonnegative SQLite integer")
        if currency != "USD":
            raise ValueError(f"{identifier}: currency must be USD")

        rows.append((identifier, posting_date, segment, entry_type, amount, currency))
    return rows


def load_revenue_transactions(
    connection: sqlite3.Connection, fixture_path: str | Path
) -> None:
    """Create and populate the table atomically on a caller-owned connection.

    An existing revenue_transactions table causes the load to fail. To
    rebuild, pass a fresh connection to a new database. The loader leaves
    any surrounding transaction under the caller's control.
    """
    rows = read_revenue_transactions(fixture_path)
    connection.execute("SAVEPOINT load_revenue_transactions")
    try:
        connection.execute("""
            CREATE TABLE main.revenue_transactions (
                transaction_id TEXT NOT NULL PRIMARY KEY,
                posting_date TEXT NOT NULL,
                business_segment TEXT NOT NULL,
                entry_type TEXT NOT NULL CHECK (entry_type IN ('revenue', 'credit')),
                amount_cents INTEGER NOT NULL
                    CHECK (typeof(amount_cents) = 'integer' AND amount_cents >= 0),
                currency TEXT NOT NULL CHECK (currency = 'USD')
            )
        """)
        connection.executemany(
            """
            INSERT INTO main.revenue_transactions (
                transaction_id, posting_date, business_segment,
                entry_type, amount_cents, currency
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.execute("RELEASE load_revenue_transactions")
    except BaseException:
        connection.execute("ROLLBACK TO load_revenue_transactions")
        connection.execute("RELEASE load_revenue_transactions")
        raise
