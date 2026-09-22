-- ============================================================
-- Nifty 100 Financial Intelligence Platform
-- Exploratory SQL Queries
-- ============================================================

-- 1. Total number of companies
SELECT COUNT(*) AS total_companies
FROM companies;


-- 2. Companies by sector
SELECT
    broad_sector,
    COUNT(*) AS company_count
FROM sectors
GROUP BY broad_sector
ORDER BY company_count DESC;


-- 3. Financial ratio records by company
SELECT
    company_id,
    COUNT(*) AS ratio_records
FROM financial_ratios
GROUP BY company_id
ORDER BY ratio_records DESC;


-- 4. Latest financial ratios
SELECT
    company_id,
    year,
    net_profit_margin_pct,
    operating_profit_margin_pct,
    return_on_equity_pct,
    return_on_capital_employed_pct,
    debt_to_equity,
    interest_coverage
FROM financial_ratios
ORDER BY year DESC
LIMIT 20;


-- 5. Companies with highest ROE
SELECT
    company_id,
    year,
    return_on_equity_pct
FROM financial_ratios
WHERE return_on_equity_pct IS NOT NULL
ORDER BY return_on_equity_pct DESC
LIMIT 10;


-- 6. Companies with lowest debt-to-equity
SELECT
    company_id,
    year,
    debt_to_equity
FROM financial_ratios
WHERE debt_to_equity IS NOT NULL
ORDER BY debt_to_equity ASC
LIMIT 10;


-- 7. Companies with highest interest coverage
SELECT
    company_id,
    year,
    interest_coverage
FROM financial_ratios
WHERE interest_coverage IS NOT NULL
ORDER BY interest_coverage DESC
LIMIT 10;


-- 8. Stock-price record count by company
SELECT
    company_id,
    COUNT(*) AS price_records
FROM stock_prices
GROUP BY company_id
ORDER BY price_records DESC;


-- 9. Valuation summary
SELECT *
FROM valuation_summary
LIMIT 20;


-- 10. Peer groups
SELECT
    peer_group_name,
    COUNT(*) AS company_count,
    SUM(is_benchmark) AS benchmark_count
FROM peer_groups
GROUP BY peer_group_name
ORDER BY company_count DESC;


-- 11. Peer percentile records
SELECT *
FROM peer_percentiles
LIMIT 20;


-- 12. Profit and loss records
SELECT *
FROM profitandloss
LIMIT 20;


-- 13. Balance-sheet records
SELECT *
FROM balancesheet
LIMIT 20;


-- 14. Cash-flow records
SELECT *
FROM cashflow
LIMIT 20;


-- 15. Companies with generated pros and cons
SELECT
    company_id,
    COUNT(*) AS records
FROM prosandcons_generated
GROUP BY company_id
ORDER BY records DESC;


-- 16. Analysis records
SELECT *
FROM analysis
LIMIT 20;


-- 17. Sector-level financial ratio summary
SELECT
    s.broad_sector,
    AVG(fr.net_profit_margin_pct) AS avg_net_profit_margin,
    AVG(fr.return_on_equity_pct) AS avg_roe,
    AVG(fr.return_on_capital_employed_pct) AS avg_roce
FROM sectors s
JOIN financial_ratios fr
    ON UPPER(TRIM(s.company_id)) = UPPER(TRIM(fr.company_id))
GROUP BY s.broad_sector
ORDER BY avg_roe DESC;


-- 18. Companies with positive ROE and low debt
SELECT
    company_id,
    year,
    return_on_equity_pct,
    debt_to_equity
FROM financial_ratios
WHERE return_on_equity_pct > 15
  AND debt_to_equity < 1
ORDER BY return_on_equity_pct DESC;


-- 19. Latest ratio record for each company
SELECT
    fr.company_id,
    fr.year,
    fr.net_profit_margin_pct,
    fr.return_on_equity_pct,
    fr.debt_to_equity
FROM financial_ratios fr
WHERE fr.year = (
    SELECT MAX(fr2.year)
    FROM financial_ratios fr2
    WHERE fr2.company_id = fr.company_id
)
ORDER BY fr.company_id;


-- 20. Financial-ratio data coverage
SELECT
    COUNT(DISTINCT company_id) AS companies,
    COUNT(*) AS total_ratio_records,
    MIN(year) AS earliest_year,
    MAX(year) AS latest_year
FROM financial_ratios;