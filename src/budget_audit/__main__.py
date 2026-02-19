from __future__ import annotations

import argparse

from .db import fetch_expenses
from .reports import audit, by_category, make_summary, over_time_daily


def money(n: float) -> str:
    return f"${n:,.2f}"


def main():
    p = argparse.ArgumentParser(prog="budget-audit", description="Budget reports + audit checks.")
    p.add_argument("--db", required=True, help="Path to SQLite budget.db")
    p.add_argument("--days", type=int, default=None, help="Limit to last N days (optional)")

    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("summary")
    sub.add_parser("by-category")
    sub.add_parser("over-time")

    audit_p = sub.add_parser("audit")
    audit_p.add_argument("--min", type=float, default=100.0, help="Flag expenses >= this amount")

    args = p.parse_args()
    items = fetch_expenses(args.db, days=args.days)

    if args.cmd == "summary":
        s = make_summary(items)
        print(f"Range: {s.start} → {s.end}")
        print(f"Count: {s.count}")
        print(f"Total: {money(s.total)}")
        print(f"Avg:   {money(s.avg)}")

    elif args.cmd == "by-category":
        rows = by_category(items)
        if not rows:
            print("No data.")
            return
        for cat, total in rows:
            print(f"{cat:16} {money(total)}")

    elif args.cmd == "over-time":
        rows = over_time_daily(items)
        if not rows:
            print("No data.")
            return
        for d, total in rows:
            print(f"{d}  {money(total)}")

    elif args.cmd == "audit":
        result = audit(items, min_amount=float(args.min))

        large = result["large"]
        dups = result["duplicates"]

        print(f"Large expenses (>= {money(float(args.min))}): {len(large)}")
        for x in large[:10]:
            print(
                f"  - {x.created_at.date().isoformat()}  {x.name}  {money(x.amount)}  ({x.category})"
            )

        print(f"\nPotential duplicates: {len(dups)}")
        for a, b in dups[:10]:
            print(
                f"  - {a.created_at.date().isoformat()} {a.name} {money(a.amount)} (ids {a.id}, {b.id})"
            )


if __name__ == "__main__":
    main()
