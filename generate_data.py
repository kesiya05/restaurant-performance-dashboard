"""Create SYNTHETIC monthly P&L data for 7 restaurant branches (24 months).

    python generate_data.py          # writes data/monthly_pnl.csv

Not real data. The branches are built with different profiles on purpose: Branch 5 has a
labour problem and Branch 3 has a food cost problem, so there is something to find.
"""
import csv
import os
import random

BRANCHES = {
    # name: (base monthly revenue, food %, labour %, rent, utilities, other %)
    "Branch 1": (92_000, 0.32, 0.32, 8_200, 3_300, 0.150),
    "Branch 2": (84_000, 0.32, 0.33, 7_600, 3_100, 0.150),
    "Branch 3": (78_000, 0.39, 0.32, 7_300, 3_000, 0.150),
    "Branch 4": (101_000, 0.31, 0.31, 8_600, 3_600, 0.140),
    "Branch 5": (66_000, 0.32, 0.45, 6_800, 2_800, 0.150),
    "Branch 6": (73_000, 0.33, 0.33, 6_900, 2_900, 0.150),
    "Branch 7": (88_000, 0.32, 0.32, 7_800, 3_200, 0.150),
}
SEASON = {1: 0.92, 2: 0.9, 3: 0.97, 4: 1.0, 5: 1.05, 6: 1.08, 7: 1.1, 8: 1.07, 9: 1.0, 10: 1.0, 11: 1.03, 12: 1.18}
FIELDS = ["month", "branch", "revenue", "food_cost", "labour_cost", "rent", "utilities", "other_costs"]


def generate(seed: int = 42):
    rnd = random.Random(seed)
    rows = []
    for year in (2024, 2025):
        for month in range(1, 13):
            growth = 1.0 + 0.04 * (year - 2024) + 0.002 * month
            for branch, (base, food, labour, rent, util, other) in BRANCHES.items():
                revenue = base * SEASON[month] * growth * rnd.uniform(0.96, 1.04)
                rows.append({
                    "month": f"{year}-{month:02d}",
                    "branch": branch,
                    "revenue": round(revenue, 2),
                    "food_cost": round(revenue * food * rnd.uniform(0.97, 1.03), 2),
                    "labour_cost": round(revenue * labour * rnd.uniform(0.97, 1.03), 2),
                    "rent": rent,
                    "utilities": round(util * rnd.uniform(0.9, 1.1), 2),
                    "other_costs": round(revenue * other * rnd.uniform(0.9, 1.1), 2),
                })
    return rows


def write_csv(path="data/monthly_pnl.csv", seed: int = 42):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(generate(seed))
    return path


if __name__ == "__main__":
    print("wrote", write_csv())
