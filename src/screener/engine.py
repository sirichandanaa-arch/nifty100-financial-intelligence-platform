"""Configurable screener with six documented presets."""
import sqlite3, yaml, numpy as np, pandas as pd
from src.common import DB_PATH, OUTPUT_DIR, ROOT, read_excel_clean, norm_ticker

def load_data():
    """Load latest financial ratios and valuation metadata."""
    conn=sqlite3.connect(DB_PATH)
    r=pd.read_sql_query('SELECT * FROM financial_ratios',conn); c=pd.read_sql_query('SELECT company_id,company_name FROM companies',conn); s=pd.read_sql_query('SELECT * FROM sectors',conn); v=pd.read_sql_query('SELECT * FROM valuation_summary',conn); conn.close()
    r['yearn']=pd.to_numeric(r.year.str[:4],errors='coerce'); r=r[r.year!='2024-12']; r=r.sort_values(['yearn','year']).groupby('company_id').tail(1)
    v=v.sort_values('year').groupby('company_id').tail(1) if not v.empty else v
    m=read_excel_clean(ROOT/'source'/'market_cap.xlsx',0); m['company_id']=m.company_id.map(norm_ticker); m=m.sort_values('year').groupby('company_id').tail(1)
    return r.merge(c,on='company_id',how='left').merge(s,on='company_id',how='left').merge(v[['company_id','pe','pb','market_cap_crore','fcf_yield_pct']],on='company_id',how='left').merge(m[['company_id','dividend_yield_pct']],on='company_id',how='left')

def apply_filters(df,filters):
    """Apply threshold filters, exempting Financials from D/E screening."""
    x=df.copy()
    conn=sqlite3.connect(DB_PATH); pl=pd.read_sql_query('SELECT company_id,year,net_profit,sales FROM profitandloss',conn); conn.close(); pl['yn']=pd.to_numeric(pl.year.str[:4],errors='coerce'); pl=pl.sort_values('yn').groupby('company_id').tail(1); x=x.merge(pl[['company_id','net_profit','sales']],on='company_id',how='left')
    mapping={'roe_min':'return_on_equity_pct','fcf_min':'free_cash_flow_cr','revenue_cagr_5yr_min':'revenue_cagr_5yr','pat_cagr_5yr_min':'pat_cagr_5yr','opm_min':'operating_profit_margin_pct','eps_cagr_min':'eps_cagr_5yr','asset_turnover_min':'asset_turnover','sales_min':'sales','net_profit_min':'net_profit'}
    for k,col in mapping.items():
        v=filters.get(k)
        if v is not None: x=x[pd.to_numeric(x[col],errors='coerce').fillna(-np.inf)>=float(v)]
    if filters.get('de_max') is not None: x=x[x.broad_sector.eq('Financials') | (pd.to_numeric(x.debt_to_equity,errors='coerce')<=float(filters['de_max']))]
    if filters.get('icr_min') is not None: x=x[x.icr_label.eq('Debt Free') | (pd.to_numeric(x.interest_coverage,errors='coerce')>=float(filters['icr_min']))]
    if filters.get('pe_max') is not None: x=x[pd.to_numeric(x.pe,errors='coerce')<=float(filters['pe_max'])]
    if filters.get('pb_max') is not None: x=x[pd.to_numeric(x.pb,errors='coerce')<=float(filters['pb_max'])]
    if filters.get('dividend_yield_min') is not None: x=x[pd.to_numeric(x.dividend_yield_pct,errors='coerce').fillna(-np.inf)>=float(filters['dividend_yield_min'])]
    if filters.get('market_cap_min') is not None: x=x[pd.to_numeric(x.market_cap_crore,errors='coerce').fillna(-np.inf)>=float(filters['market_cap_min'])]
    return x.sort_values('composite_quality_score',ascending=False)

def run_presets():
    """Generate six preset sheets."""
    df=load_data(); cfg=yaml.safe_load((ROOT/'config/screener_config.yaml').read_text())['presets']; out=OUTPUT_DIR/'screener_output.xlsx'
    with pd.ExcelWriter(out,engine='openpyxl') as w:
        for name,f in cfg.items(): apply_filters(df,f).to_excel(w,sheet_name=name[:31],index=False)
    return out
if __name__=='__main__': run_presets()
