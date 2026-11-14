import sqlite3

import pytest

from generate_data import generate, write_csv
from restaurant_dashboard.db import connect
from restaurant_dashboard.metrics import diagnose, group_totals, league_table, losing_months, monthly_trend


@pytest.fixture(scope="module")
def con(tmp_path_factory):
    path = write_csv(str(tmp_path_factory.mktemp("d") / "pnl.csv"))
    return connect(path)


def test_generator_is_deterministic_and_complete():
    a, b = generate(1), generate(1)
    assert a == b
    assert len(a) == 7 * 24
    assert all(r["revenue"] > 0 for r in a)


def test_league_table_matches_manual_sum(con):
    rows = league_table(con)
    b5 = next(r for r in rows if r["branch"] == "Branch 5")
    manual = con.execute("SELECT SUM(revenue), SUM(labour_cost) FROM monthly_pnl WHERE branch='Branch 5'").fetchone()
    assert b5["revenue"] == pytest.approx(manual[0])
    assert b5["labour_pct"] == pytest.approx(manual[1] / manual[0])


def test_rows_sorted_by_profit_and_margin_consistent(con):
    rows = league_table(con)
    assert [r["profit"] for r in rows] == sorted((r["profit"] for r in rows), reverse=True)
    for r in rows:
        assert r["margin"] == pytest.approx(r["profit"] / r["revenue"])
        assert r["prime_cost_pct"] == pytest.approx(r["food_pct"] + r["labour_pct"])


def test_year_filter(con):
    all_rev = sum(r["revenue"] for r in league_table(con))
    y24 = sum(r["revenue"] for r in league_table(con, "2024"))
    y25 = sum(r["revenue"] for r in league_table(con, "2025"))
    assert y24 + y25 == pytest.approx(all_rev)
    assert y25 > y24


def test_group_totals_weighted(con):
    rows = league_table(con)
    g = group_totals(rows)
    assert g["margin"] == pytest.approx(g["profit"] / g["revenue"])
    assert min(r["food_pct"] for r in rows) <= g["food_pct"] <= max(r["food_pct"] for r in rows)


def test_diagnosis_finds_the_planted_problems(con):
    rows = league_table(con)
    d = {x["branch"]: x for x in diagnose(rows)}
    assert d["Branch 5"]["driver"] == "labour"
    assert d["Branch 3"]["driver"] == "food cost"
    assert d["Branch 5"]["worth"] > 0
    assert "Branch 4" not in d  # best branch is never flagged


def test_trend_and_losing_months(con):
    t = monthly_trend(con)
    assert len(t) == 24 and t[0]["month"] == "2024-01"
    assert all(m["profit"] < 0 for m in losing_months(con))


def test_schema_enforces_unique_branch_month(con):
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO monthly_pnl VALUES ('2024-01','Branch 1',1,1,1,1,1,1)")
