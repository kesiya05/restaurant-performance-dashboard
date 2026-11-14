"""Builds the dashboard page, the memo, an Excel file and a chart from the league table."""
import html
from pathlib import Path

from openpyxl import Workbook

from .metrics import diagnose, group_totals, league_table, losing_months, monthly_trend

e = html.escape


def money(x: float) -> str:
    return f"{x:,.0f}"


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def memo(rows, years: str = "2024-2025") -> str:
    g = group_totals(rows)
    d = diagnose(rows)
    lines = [f"# Branch performance memo ({years}, synthetic data)", "",
             f"Group revenue {money(g['revenue'])}, profit {money(g['profit'])} ({pct(g['margin'])} margin). "
             f"Food cost is {pct(g['food_pct'])} of revenue and labour {pct(g['labour_pct'])}.", ""]
    losing = [r for r in rows if r["profit"] < 0]
    if losing:
        for r in losing:
            lines.append(f"- **{r['branch']} loses money**: {money(r['profit'])} over the period "
                         f"(margin {pct(r['margin'])}).")
        lines.append("")
    for x in d:
        lines.append(f"- {x['branch']}: margin {pct(x['margin'])}, the gap is mostly **{x['driver']}**, "
                     f"{x['gap_pts'] * 100:.1f} points above the group. Closing it is worth about "
                     f"{money(x['worth'])} over the period.")
    lines += ["", "## Suggested next step", "",
              "Start with the branch at the top of the list above. Compare its rota to the best-run branch "
              "of similar size before cutting hours, and check whether the gap is staffing level or wage mix."]
    return "\n".join(lines) + "\n"


def bar_svg(rows) -> str:
    W, H, L, T, B = 640, 240, 40, 16, 34
    vals = [r["margin"] for r in rows]
    lo, hi = min(0, min(vals)), max(vals)
    span = hi - lo or 1
    zero = T + (H - T - B) * (hi / span)
    bw = (W - L - 8) / len(rows)
    out = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-label="Profit margin by branch">',
           f'<line x1="{L}" x2="{W - 8}" y1="{zero:.1f}" y2="{zero:.1f}" stroke="#999"/>']
    for i, r in enumerate(rows):
        h = abs(r["margin"]) / span * (H - T - B)
        y = zero - h if r["margin"] >= 0 else zero
        col = "#1f4e4a" if r["margin"] >= 0 else "#a33c2a"
        x = L + i * bw + bw * 0.15
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw * 0.7:.1f}" height="{max(h, 1):.1f}" fill="{col}"/>')
        out.append(f'<text x="{x + bw * 0.35:.1f}" y="{H - 16}" font-size="11" text-anchor="middle">{e(r["branch"][-1])}</text>')
        out.append(f'<text x="{x + bw * 0.35:.1f}" y="{y - 4 if r["margin"] >= 0 else y + h + 12:.1f}" font-size="10" text-anchor="middle">{r["margin"] * 100:.1f}%</text>')
    out.append("</svg>")
    return "".join(out)


def dashboard_html(rows, trend, losing) -> str:
    g = group_totals(rows)
    body = "".join(
        f"<tr><td>{e(r['branch'])}</td><td class=r>{money(r['revenue'])}</td><td class=r>{pct(r['food_pct'])}</td>"
        f"<td class=r>{pct(r['labour_pct'])}</td><td class=r>{pct(r['prime_cost_pct'])}</td>"
        f"<td class=r>{money(r['profit'])}</td><td class=r>{pct(r['margin'])}</td></tr>" for r in rows)
    return f"""<!DOCTYPE html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Restaurant performance dashboard</title>
<style>body{{font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:0 auto;padding:1rem}}
table{{border-collapse:collapse;width:100%;font-size:.9rem}}td,th{{border-bottom:1px solid #ddd;padding:.35rem;text-align:left}}.r{{text-align:right}}
.k{{display:flex;gap:1.5rem;flex-wrap:wrap}}.k div b{{display:block;font-size:1.4rem}}</style></head><body>
<h1>Restaurant performance dashboard</h1><p>Synthetic data, 7 branches, 24 months.</p>
<div class=k><div><b>{money(g['revenue'])}</b>revenue</div><div><b>{pct(g['margin'])}</b>group margin</div>
<div><b>{pct(g['food_pct'])}</b>food cost</div><div><b>{pct(g['labour_pct'])}</b>labour</div>
<div><b>{len(losing)}</b>loss-making branch-months</div></div>
<h2>Profit margin by branch</h2>{bar_svg(rows)}
<h2>League table</h2><table><tr><th>Branch<th class=r>Revenue<th class=r>Food<th class=r>Labour<th class=r>Prime cost<th class=r>Profit<th class=r>Margin</tr>{body}</table>
</body></html>"""


def excel(rows, path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Branch summary"
    ws.append(["Branch", "Revenue", "Food %", "Labour %", "Prime cost %", "Profit", "Margin"])
    for r in rows:
        ws.append([r["branch"], round(r["revenue"], 2), r["food_pct"], r["labour_pct"], r["prime_cost_pct"],
                   round(r["profit"], 2), r["margin"]])
    for col in "CDEG":
        for cell in ws[col][1:]:
            cell.number_format = "0.0%"
    ws.column_dimensions["A"].width = 14
    wb.save(path)


def chart_png(rows, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.bar([r["branch"] for r in rows], [r["margin"] * 100 for r in rows],
           color=["#1f4e4a" if r["margin"] >= 0 else "#a33c2a" for r in rows])
    ax.axhline(0, color="#666", lw=0.8)
    ax.set_ylabel("Profit margin %")
    ax.set_title("Profit margin by branch (synthetic data)")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def build_all(con, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    rows = league_table(con)
    trend, losing = monthly_trend(con), losing_months(con)
    (out / "dashboard.html").write_text(dashboard_html(rows, trend, losing), encoding="utf-8")
    (out / "memo.md").write_text(memo(rows), encoding="utf-8")
    excel(rows, out / "branch_summary.xlsx")
    chart_png(rows, out / "branch_margin.png")
    return {"rows": rows, "diagnosis": diagnose(rows), "group": group_totals(rows)}
