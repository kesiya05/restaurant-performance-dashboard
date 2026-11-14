import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def connect(csv_path: str | Path = ROOT / "data" / "monthly_pnl.csv") -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.executescript((ROOT / "sql" / "schema.sql").read_text())
    with open(csv_path, newline="") as f:
        rows = [(r["month"], r["branch"], float(r["revenue"]), float(r["food_cost"]), float(r["labour_cost"]),
                 float(r["rent"]), float(r["utilities"]), float(r["other_costs"])) for r in csv.DictReader(f)]
    con.executemany("INSERT INTO monthly_pnl VALUES (?,?,?,?,?,?,?,?)", rows)
    con.commit()
    return con
