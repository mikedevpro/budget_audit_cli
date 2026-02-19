from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Iterable

from .db import Expense

@dataclass(frozen=True)
class Summary:
    total: float
    count: int
    avg: float
    start: str
    end: str

def make_summary(items: list[Expense]) -> Summary:
    if not items:
        return Summary(total=0.0, count=0, avg=0.0, start="—", end="—")

    total = sum(x.amount for x in items)
    count = len(items)
    avg = total / count if count else 0.0
    start = min(x.created_at for x in items).date().isoformat()
    end = max(x.created_at for x in items).date().isoformat()
    return Summary(total=total, count=count, avg=avg, start=start, end=end)

def by_category(items: list[Expense]) -> list[tuple[str, float]]:
    m = defaultdict(float)
    for x in items:
        m[x.category or "General"] += float(x.amount)
    return sorted(m.items(), key=lambda t: t[1], reverse=True)

def over_time_daily(items: list[Expense]) -> list[tuple[str, float]]:
    m = defaultdict(float)
    for x in items:
        d = x.created_at.date().isoformat()
        m[d] += float(x.amount)
    return sorted(m.items(), key=lambda t: t[0])

def audit(items: list[Expense], min_amount: float = 100.0) -> dict:
    # Large expenses
    large = [x for x in items if x.amount >= min_amount]

    # Potential duplicates: same day + name + amount
    seen = {}
    dups = []
    for x in items:
        key = (x.created_at.date().isoformat(), x.name.strip().lower(), round(x.amount, 2))
        if key in seen:
            dups.append((seen[key], x))
        else:
            seen[key] = x

    return {
        "large": large,
        "duplicates": dups,
    }
