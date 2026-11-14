from pathlib import Path

from generate_data import write_csv
from restaurant_dashboard.db import connect
from restaurant_dashboard.report import build_all, memo


def test_build_all_writes_every_output(tmp_path):
    con = connect(write_csv(str(tmp_path / "pnl.csv")))
    result = build_all(con, tmp_path / "out")
    for name in ("dashboard.html", "memo.md", "branch_summary.xlsx", "branch_margin.png"):
        assert (Path(tmp_path) / "out" / name).stat().st_size > 500, name
    page = (tmp_path / "out" / "dashboard.html").read_text()
    assert "Branch 5" in page and "<svg" in page
    assert result["diagnosis"][0]["branch"] == "Branch 5"


def test_memo_names_the_loss_maker(tmp_path):
    con = connect(write_csv(str(tmp_path / "pnl.csv")))
    result = build_all(con, tmp_path / "out")
    text = memo(result["rows"])
    assert "Branch 5 loses money" in text and "labour" in text
