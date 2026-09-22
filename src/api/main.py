"""FastAPI REST server for Nifty 100 Analytics."""
import sqlite3,time
from pathlib import Path
import pandas as pd
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from src.common import DB_PATH,REPORT_DIR,ROOT

START=time.time(); app=FastAPI(title='Nifty 100 Analytics API',version='1.0.0'); app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])

def clean_records(rows):
    """Replace non-JSON numeric values with None."""
    if not rows:return []
    d=pd.DataFrame(rows).replace([float('inf'),float('-inf')],None).astype(object); d=d.where(pd.notna(d),None); return d.to_dict('records')

def q(sql,params=()):
    """Execute a read-only SQLite query."""
    con=sqlite3.connect(DB_PATH); con.row_factory=sqlite3.Row; rows=[dict(x) for x in con.execute(sql,params).fetchall()]; con.close(); return clean_records(rows)

def latest(table,ticker):
    """Return the latest year-keyed row."""
    rows=q(f'SELECT * FROM {table} WHERE company_id=? ORDER BY year DESC',(ticker,)); return rows[-1] if rows else None

@app.get('/api/v1/health')
def health():
    """Return API health and database row counts."""
    tables=['companies','profitandloss','balancesheet','cashflow','analysis','documents','prosandcons','sectors','stock_prices','financial_ratios']; return {'status':'ok','db_row_counts':{t:q(f'SELECT COUNT(*) n FROM {t}')[0]['n'] for t in tables},'uptime_seconds':time.time()-START,'version':'1.0.0'}

@app.get('/api/v1/companies')
def companies(sector:str|None=None,market_cap_category:str|None=None,search:str|None=None):
    """List all companies with latest annual ROE/ROCE."""
    rows=q('SELECT c.*,s.broad_sector,s.sub_sector,s.market_cap_category FROM companies c LEFT JOIN sectors s USING(company_id)'); d=pd.DataFrame(q('SELECT company_id,year,return_on_equity_pct,return_on_capital_employed_pct FROM financial_ratios')); d['yn']=pd.to_numeric(d.year.str[:4],errors='coerce'); d=d[d.year!='2024-12'].sort_values(['yn','year']).groupby('company_id').tail(1); rows=pd.DataFrame(rows).merge(d.drop(columns='yn'),on='company_id',how='left').to_dict('records')
    if sector: rows=[x for x in rows if x.get('broad_sector')==sector]
    if market_cap_category: rows=[x for x in rows if x.get('market_cap_category')==market_cap_category]
    if search: rows=[x for x in rows if search.lower() in (str(x.get('company_name',''))+' '+str(x.get('company_id',''))).lower()]
    return clean_records(rows)

@app.get('/api/v1/companies/{ticker}')
def company(ticker:str):
    """Return a full company profile with latest KPIs."""
    rows=q('SELECT c.*,s.broad_sector,s.sub_sector,s.market_cap_category FROM companies c LEFT JOIN sectors s USING(company_id) WHERE c.company_id=?',(ticker.upper(),));
    if not rows: raise HTTPException(404,'Ticker not found')
    rows[0]['latest_kpis']=latest('financial_ratios',ticker.upper()); return clean_records(rows)[0]

def history(table,ticker,from_year,to_year):
    """Return bounded history for a company."""
    sql=f'SELECT * FROM {table} WHERE company_id=?'; params=[ticker.upper()]
    if from_year: sql+=' AND year>=?'; params.append(from_year)
    if to_year: sql+=' AND year<=?'; params.append(to_year)
    sql+=' ORDER BY year'; return q(sql,tuple(params))

@app.get('/api/v1/companies/{ticker}/pl')
def pl(ticker:str,from_year:str|None=None,to_year:str|None=None):
    """Return P&L history."""; return history('profitandloss',ticker,from_year,to_year)
@app.get('/api/v1/companies/{ticker}/bs')
def bs(ticker:str,from_year:str|None=None,to_year:str|None=None):
    """Return balance-sheet history."""; return history('balancesheet',ticker,from_year,to_year)
@app.get('/api/v1/companies/{ticker}/cashflow')
def cashflow(ticker:str,from_year:str|None=None,to_year:str|None=None):
    """Return cash-flow history."""; return history('cashflow',ticker,from_year,to_year)
@app.get('/api/v1/companies/{ticker}/ratios')
def ratios(ticker:str,year:str|None=None):
    """Return computed KPIs."""; return q('SELECT * FROM financial_ratios WHERE company_id=? '+('AND year=? ' if year else '')+'ORDER BY year',(ticker.upper(),year) if year else (ticker.upper(),))
@app.get('/api/v1/companies/{ticker}/tearsheet')
def tearsheet(ticker:str):
    """Return a generated tearsheet PDF."""; p=REPORT_DIR/'tearsheets'/f'{ticker.upper()}_tearsheet.pdf';
    if not p.exists(): raise HTTPException(404,'Tearsheet unavailable')
    return FileResponse(p,media_type='application/pdf',filename=p.name)
@app.get('/api/v1/screener')
def screener(min_roe:float|None=None,max_de:float|None=None,min_fcf:float|None=None,sector:str|None=None,min_rev_cagr_5yr:float|None=None,min_pat_cagr_5yr:float|None=None,max_pe:float|None=None):
    """Run the configurable screener."""
    from src.screener.engine import load_data,apply_filters
    f={'roe_min':min_roe,'de_max':max_de,'fcf_min':min_fcf,'revenue_cagr_5yr_min':min_rev_cagr_5yr,'pat_cagr_5yr_min':min_pat_cagr_5yr,'pe_max':max_pe}; d=load_data();
    if sector:d=d[d.broad_sector==sector]
    return clean_records(apply_filters(d,f).to_dict('records'))
@app.get('/api/v1/sectors')
def sectors():
    """Return sector counts and latest median KPIs."""
    r=pd.DataFrame(q('SELECT * FROM financial_ratios')); s=pd.DataFrame(q('SELECT * FROM sectors')); v=pd.DataFrame(q('SELECT * FROM valuation_summary')); r['yn']=pd.to_numeric(r.year.str[:4],errors='coerce'); d=r[r.year!='2024-12'].sort_values(['yn','year']).groupby('company_id').tail(1).merge(s,on='company_id'); v=v.sort_values('year').groupby('company_id').tail(1); d=d.merge(v[['company_id','pe']],on='company_id',how='left'); return clean_records(d.groupby('broad_sector').agg(company_count=('company_id','count'),median_roe=('return_on_equity_pct','median'),median_pe=('pe','median'),median_de=('debt_to_equity','median')).reset_index().to_dict('records'))
@app.get('/api/v1/sectors/{sector}/companies')
def sector_companies(sector:str):
    """Return companies in a sector."""; rows=companies(sector=sector); 
    if not rows: raise HTTPException(404,'Unknown sector')
    return rows
@app.get('/api/v1/peers/{group_name}')
def peers(group_name:str):
    """Return peer percentile rows."""; rows=q('SELECT * FROM peer_percentiles WHERE peer_group_name=?',(group_name,));
    if not rows: raise HTTPException(404,'Unknown peer group')
    return rows
@app.get('/api/v1/companies/{ticker}/peers/compare')
def peer_compare(ticker:str):
    """Return peer comparison data for a company."""; return q('SELECT * FROM peer_percentiles WHERE company_id=?',(ticker.upper(),))
@app.get('/api/v1/market-cap/{ticker}')
def market_cap(ticker:str):
    """Return historical valuation multiples."""; return q('SELECT * FROM valuation_summary WHERE company_id=? ORDER BY year',(ticker.upper(),))
@app.get('/api/v1/portfolio/stats')
def portfolio_stats():
    """Return portfolio KPI statistics."""; return clean_records(pd.read_csv(ROOT/'output'/'portfolio_stats.csv').to_dict('records'))
@app.get('/api/v1/companies/{ticker}/documents')
def documents(ticker:str):
    """Return annual report links with validity flags."""; rows=q('SELECT * FROM documents WHERE company_id=? ORDER BY year DESC',(ticker.upper(),)); import requests
    for x in rows:
        try:x['is_url_valid']=requests.head(x['annual_report'],timeout=5,allow_redirects=True).status_code<400
        except Exception:x['is_url_valid']=False
    return clean_records(rows)
