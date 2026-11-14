-- Branch league table: the query behind the dashboard.
SELECT branch,
       SUM(revenue)                                                   AS revenue,
       SUM(food_cost) * 1.0 / SUM(revenue)                            AS food_pct,
       SUM(labour_cost) * 1.0 / SUM(revenue)                          AS labour_pct,
       (SUM(food_cost) + SUM(labour_cost)) * 1.0 / SUM(revenue)       AS prime_cost_pct,
       SUM(revenue - food_cost - labour_cost - rent - utilities - other_costs) AS profit
FROM monthly_pnl
GROUP BY branch
ORDER BY profit DESC;

-- Monthly trend for the whole group.
SELECT month,
       SUM(revenue) AS revenue,
       SUM(revenue - food_cost - labour_cost - rent - utilities - other_costs) AS profit
FROM monthly_pnl
GROUP BY month
ORDER BY month;

-- Months where a branch lost money.
SELECT month, branch,
       revenue - food_cost - labour_cost - rent - utilities - other_costs AS profit
FROM monthly_pnl
WHERE revenue - food_cost - labour_cost - rent - utilities - other_costs < 0
ORDER BY profit;
