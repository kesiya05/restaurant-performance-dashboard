# Power BI version

I haven't included a `.pbix` file, because Power BI Desktop is a Windows app and it doesn't run in the
environment I built this in. This folder gives you everything needed to build it in about 30 minutes.

1. In Power BI Desktop choose **Get data > Text/CSV** and load `data/monthly_pnl.csv`.
2. Create these measures (Modeling > New measure):

```
Revenue = SUM(monthly_pnl[revenue])
Food % = DIVIDE(SUM(monthly_pnl[food_cost]), [Revenue])
Labour % = DIVIDE(SUM(monthly_pnl[labour_cost]), [Revenue])
Profit = [Revenue] - SUM(monthly_pnl[food_cost]) - SUM(monthly_pnl[labour_cost])
         - SUM(monthly_pnl[rent]) - SUM(monthly_pnl[utilities]) - SUM(monthly_pnl[other_costs])
Margin = DIVIDE([Profit], [Revenue])
```

3. Page 1: cards for Revenue, Margin, Food %, Labour %. A clustered bar of Margin by branch, with conditional
   colour (red below zero). A line chart of Profit by month. A slicer on branch and year.
4. Check your numbers against `outputs/branch_summary.xlsx`. They should match to the cent.
