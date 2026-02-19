from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Expense:
    id: str
    name: str
    amount: float
    category: str
    created_at: datetime


def _parse_dt(value: str) -> datetime:
    # your API uses ISO-like strings; SQLite might store as text
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def fetch_expenses(db_path: str, days: int | None = None) -> list[Expense]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    if days is None:
        cur.execute("""
            SELECT id, name, amount, category, created_at
            FROM expenses
            ORDER BY created_at DESC
        """)
    else:
        # SQLite: compare as datetime string; works fine with ISO text
        cur.execute(
            """
            SELECT id, name, amount, category, created_at
            FROM expenses
            WHERE datetime(created_at) >= datetime('now', ?)
            ORDER BY created_at DESC
        """,
            (f"-{int(days)} days",),
        )

    rows = cur.fetchall()
    con.close()

    out: list[Expense] = []
    for r in rows:
        out.append(
            Expense(
                id=str(r["id"]),
                name=str(r["name"]),
                amount=float(r["amount"]),
                category=str(r["category"] or "General"),
                created_at=_parse_dt(str(r["created_at"])),
            )
        )
    return out
