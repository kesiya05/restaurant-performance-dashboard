"""KPIs per branch, calculated in SQL."""

PROFIT = "revenue - food_cost - labour_cost - rent - utilities - other_costs"

LEAGUE = f"""
SELECT branch,
       SUM(revenue) AS revenue,
       SUM(food_cost) * 1.0 / SUM(revenue) AS food_pct,
       SUM(labour_cost) * 1.0 / SUM(revenue) AS labour_pct,
       (SUM(food_cost) + SUM(labour_cost)) * 1.0 / SUM(revenue) AS prime_cost_pct,
       SUM({PROFIT}) AS profit,
       SUM({PROFIT}) * 1.0 / SUM(revenue) AS margin
FROM monthly_pnl {{where}}
GROUP BY branch
ORDER BY profit DESC
"""


def league_table(con, year: str | None = None) -> list[dict]:
    where, args = ("WHERE month LIKE ?", (f"{year}-%",)) if year else ("", ())
    return [dict(r) for r in con.execute(LEAGUE.format(where=where), args)]


def group_totals(rows: list[dict]) -> dict:
    revenue = sum(r["revenue"] for r in rows)
    profit = sum(r["profit"] for r in rows)
    food = sum(r["food_pct"] * r["revenue"] for r in rows) / revenue
    labour = sum(r["labour_pct"] * r["revenue"] for r in rows) / revenue
    return {"revenue": revenue, "profit": profit, "margin": profit / revenue, "food_pct": food, "labour_pct": labour}


def monthly_trend(con) -> list[dict]:
    q = f"SELECT month, SUM(revenue) AS revenue, SUM({PROFIT}) AS profit FROM monthly_pnl GROUP BY month ORDER BY month"
    return [dict(r) for r in con.execute(q)]


def losing_months(con) -> list[dict]:
    q = f"SELECT month, branch, {PROFIT} AS profit FROM monthly_pnl WHERE {PROFIT} < 0 ORDER BY profit"
    return [dict(r) for r in con.execute(q)]


def diagnose(rows: list[dict]) -> list[dict]:
    """For every branch below the group margin, say which cost line explains the gap and what closing it is worth."""
    g = group_totals(rows)
    out = []
    for r in rows:
        if r["margin"] >= g["margin"]:
            continue
        gaps = {"food cost": r["food_pct"] - g["food_pct"], "labour": r["labour_pct"] - g["labour_pct"]}
        driver = max(gaps, key=gaps.get)
        gap = gaps[driver]
        if gap < 0.01:
            continue
        out.append({"branch": r["branch"], "margin": r["margin"], "profit": r["profit"], "driver": driver,
                    "gap_pts": gap, "worth": max(gap, 0) * r["revenue"]})
    return sorted(out, key=lambda d: d["margin"])
