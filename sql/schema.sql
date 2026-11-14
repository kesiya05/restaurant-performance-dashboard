CREATE TABLE IF NOT EXISTS monthly_pnl (
    month        TEXT NOT NULL,      -- YYYY-MM
    branch       TEXT NOT NULL,
    revenue      REAL NOT NULL,
    food_cost    REAL NOT NULL,
    labour_cost  REAL NOT NULL,
    rent         REAL NOT NULL,
    utilities    REAL NOT NULL,
    other_costs  REAL NOT NULL,
    PRIMARY KEY (month, branch)
);
CREATE INDEX IF NOT EXISTS idx_pnl_branch ON monthly_pnl(branch);
