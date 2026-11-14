# Restaurant Performance Dashboard

Branch-level P&L for a multi-site restaurant group: revenue, food cost, labour, margin, and where each underperforming branch is losing money.

## What it does

- SQL schema and queries (`sql/`)
- Branch summary workbook, margin chart, HTML dashboard and a short memo in `outputs/`
- Diagnosis of each weak branch by cause (food cost vs labour)

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python generate_data.py
python -m restaurant_dashboard
```

Results are written to `outputs/`.

## Tests

```bash
ruff check . && pytest
```

## Notes

The data is synthetic. In the demo data, one branch loses money mainly through labour (about 11.8 points above the group) and another through food cost. No `.pbix` is included, see `powerbi/README.md` for how to build the Power BI version from the CSV and SQL.

MIT licensed. Built by Kesiya Ann Sony.
