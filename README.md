# budget-audit-cli

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Package type](https://img.shields.io/badge/type-CLI-informational)](./pyproject.toml)
[![Status](https://img.shields.io/badge/status-prototype-orange)](./README.md)

Small, dependency-free CLI for budget reporting and anomaly checks on a SQLite `expenses` table.

## Quickstart

1. Install in editable mode:

```bash
python -m pip install -e .
```

2. Create a demo database:

```bash
sqlite3 budget.db "
CREATE TABLE IF NOT EXISTS expenses (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  amount REAL NOT NULL,
  category TEXT,
  created_at TEXT NOT NULL
);
INSERT INTO expenses (id, name, amount, category, created_at) VALUES
  ('1', 'Coffee', 6.50, 'Food', '2026-02-12T08:20:00Z'),
  ('2', 'Groceries', 87.44, 'Food', '2026-02-12T19:10:00Z'),
  ('3', 'Groceries', 87.44, 'Food', '2026-02-12T19:12:00Z'),
  ('4', 'Rent', 1500.00, 'Housing', '2026-02-01T09:00:00Z');
"
```

3. Run commands:

```bash
budget-audit --db budget.db summary
budget-audit --db budget.db by-category
budget-audit --db budget.db over-time
budget-audit --db budget.db audit --min 100
```

## What It Does

- `summary`: total spend, count, average, and covered date range
- `by-category`: totals grouped by category
- `over-time`: daily totals
- `audit`: flags large expenses (`amount >= --min`, default `100.0`) and potential duplicates (same day + normalized name + amount)

## Command Reference

Base command:

```bash
budget-audit --db path/to/budget.db <command> [options]
```

Global options:

- `--db`: path to SQLite DB (required)
- `--days N`: limit analysis to last `N` days

Subcommands:

```bash
budget-audit --db budget.db summary
budget-audit --db budget.db by-category
budget-audit --db budget.db over-time
budget-audit --db budget.db audit
budget-audit --db budget.db audit --min 250
```

## Example Output

```text
$ budget-audit --db budget.db summary
Range: 2026-02-01 → 2026-02-12
Count: 4
Total: $1,681.38
Avg:   $420.35
```

```text
$ budget-audit --db budget.db audit --min 100
Large expenses (>= $100.00): 1
  - 2026-02-01  Rent  $1,500.00  (Housing)

Potential duplicates: 1
  - 2026-02-12 groceries $87.44 (ids 2, 3)
```

## Data Expectations

The CLI reads from a table named `expenses` with columns:

- `id`
- `name`
- `amount`
- `category`
- `created_at` as ISO-like text (`2026-02-18T15:04:05Z`)

If `category` is missing/empty, it is treated as `General`.

## Development

Run directly from source without installing entrypoints:

```bash
PYTHONPATH=src python3 -m budget_audit --db budget.db summary
```
