# Nifty 100 Financial Intelligence Platform

A reproducible data/analytics platform built from the supplied Nifty 100 source workbooks. It covers ETL, data quality, financial ratios, CAGR edge cases, screener presets, peer percentiles, valuation, cash-flow intelligence, NLP pros/cons, clustering, PDF reporting, Streamlit and FastAPI.

## Windows quick start

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.pipeline
python -m pytest tests --html=reports/pytest_report.html --self-contained-html -q
python -m src.acceptance
python -m src.finalize
```

If GNU Make is installed, the Makefile targets are also available. The Python commands are the canonical cross-platform commands.

## Source data

Place these 12 Excel files in `source/`: companies.xlsx, profitandloss.xlsx, balancesheet.xlsx, cashflow.xlsx, documents.xlsx, analysis.xlsx, prosandcons.xlsx, sectors.xlsx, stock_prices.xlsx, financial_ratios.xlsx, market_cap.xlsx, peer_groups.xlsx. `Nifty100_Project_Document_FINAL.pdf` is included as project documentation.

## Main outputs

- `data/nifty100.db`
- `output/load_audit.csv`, `validation_failures.csv`, `capital_allocation.csv`
- `output/screener_output.xlsx`, `peer_comparison.xlsx`, `valuation_summary.xlsx`
- `output/cashflow_intelligence.xlsx`, `pros_cons_generated.csv`, `analysis_parsed.csv`
- `output/cluster_labels.csv`, `outlier_report.csv`, `portfolio_stats.csv`
- `reports/tearsheets/` (92 PDFs), `reports/sector/`, `reports/portfolio/`
- `reports/pytest_report.html`, `docs/openapi.json`, `docs/analyst_guide.pdf`, `docs/acceptance_checklist.pdf`

## Notes

- Monetary values are INR Crore.
- Company identifiers are normalized to uppercase.
- Duplicate company-year source rows are resolved deterministically and logged in `load_audit.csv` rather than inserted into primary-key tables.
- Financials are exempt from the D/E screener warning/filter behavior where specified.
- Negative CAGR bases produce explicit edge-case flags.
- The supplied market-cap and stock-price datasets are labelled simulated in the dashboard/report documentation.
