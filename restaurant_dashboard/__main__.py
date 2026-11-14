from pathlib import Path

from generate_data import write_csv

from .db import ROOT, connect
from .report import build_all

csv_path = ROOT / "data" / "monthly_pnl.csv"
if not csv_path.exists():
    write_csv(str(csv_path))
result = build_all(connect(csv_path), ROOT / "outputs")
print(f"Built {Path('outputs').resolve()} (dashboard.html, memo.md, branch_summary.xlsx, branch_margin.png)")
for d in result["diagnosis"][:3]:
    print(f"- {d['branch']}: margin {d['margin']:.1%}, main driver {d['driver']} (+{d['gap_pts'] * 100:.1f} pts)")
