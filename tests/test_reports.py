from datetime import datetime, timezone

from budget_audit.reports import make_summary, by_category, over_time_daily, audit
from budget_audit.db import Expense

def exp(id, name, amount, category, iso_dt):
    return Expense(
        id=id,
        name=name,
        amount=float(amount),
        category=category,
        created_at=datetime.fromisoformat(iso_dt).replace(tzinfo=timezone.utc),
    )

def test_make_summary_empty():
    s = make_summary([])
    assert s.total == 0.0
    assert s.count == 0
    assert s.avg == 0.0
    assert s.start == "—"
    assert s.end == "—"

def test_make_summary_non_empty():
    items = [
        exp("1", "Coffee", 4.50, "Food", "2026-02-01T10:00:00"),
        exp("2", "Gas", 35.10, "Transport", "2026-02-02T12:00:00"),
    ]
    s = make_summary(items)
    assert s.count == 2
    assert round(s.total, 2) == 39.60
    assert round(s.avg, 2) == 19.80
    assert s.start == "2026-02-01"
    assert s.end == "2026-02-02"

def test_by_category_sums_and_sorts():
    items = [
        exp("1", "Coffee", 4.50, "Food", "2026-02-01T10:00:00"),
        exp("2", "Lunch", 12.00, "Food", "2026-02-01T12:00:00"),
        exp("3", "Gas", 35.10, "Transport", "2026-02-02T12:00:00"),
    ]
    rows = by_category(items)
    # sorted desc by total
    assert rows[0][0] == "Transport"
    assert round(rows[0][1], 2) == 35.10
    assert rows[1][0] == "Food"
    assert round(rows[1][1], 2) == 16.50

def test_over_time_daily_groups_by_date():
    items = [
        exp("1", "Coffee", 4.50, "Food", "2026-02-01T10:00:00"),
        exp("2", "Lunch", 12.00, "Food", "2026-02-01T12:00:00"),
        exp("3", "Gas", 35.10, "Transport", "2026-02-02T12:00:00"),
    ]
    rows = over_time_daily(items)
    assert rows == [("2026-02-01", 16.5), ("2026-02-02", 35.1)]

def test_audit_large_and_duplicates():
    items = [
        exp("1", "Rent", 1200.00, "Utilities", "2026-02-01T10:00:00"),
        exp("2", "Coffee", 4.50, "Food", "2026-02-01T12:00:00"),
        exp("3", "Coffee", 4.50, "Food", "2026-02-01T18:00:00"),  # duplicate by name+amount+day
    ]
    result = audit(items, min_amount=100.0)

    large = result["large"]
    dups = result["duplicates"]

    assert len(large) == 1
    assert large[0].name == "Rent"

    assert len(dups) == 1
    a, b = dups[0]
    assert a.id == "2"
    assert b.id == "3"
