"""Automated final acceptance-gate audit."""
import sqlite3, subprocess, time, pandas as pd
from pathlib import Path
from src.common import ROOT,DB_PATH,OUTPUT_DIR,REPORT_DIR,DOCS_DIR

def run():
    """Evaluate the 20 documented acceptance gates and save acceptance_results.csv."""
    checks=[]; con=sqlite3.connect(DB_PATH)
    def add(g,ok,d): checks.append({'gate':g,'status':'PASS' if ok else 'FAIL','detail':d})
    add('AC-01',con.execute('SELECT COUNT(*) FROM companies').fetchone()[0]==92,'companies count = 92')
    for t in ['profitandloss','balancesheet','cashflow']:
        n=con.execute(f'SELECT COUNT(*) FROM (SELECT company_id,COUNT(*) n FROM {t} GROUP BY company_id HAVING n>=10)').fetchone()[0]; add('AC-02-'+t,n>=83,f'{n}/92 companies have >=10 records')
    add('AC-03',not list(con.execute('PRAGMA foreign_key_check')),'foreign key check = 0 rows')
    add('AC-04',con.execute('SELECT COUNT(*) FROM financial_ratios').fetchone()[0]>=1100,'financial_ratios >= 1100 rows')
    # AC-05: deterministic formula spot check against raw P&L values for three companies.
    pl=pd.read_sql_query('SELECT * FROM profitandloss',con); bs=pd.read_sql_query('SELECT * FROM balancesheet',con); pl['yn']=pd.to_numeric(pl.year.str[:4],errors='coerce'); samples=[x for x in ['TCS','RELIANCE','INFY'] if x in set(pl.company_id)]; good=0
    for cid in samples:
        g=pl[pl.company_id==cid].sort_values('yn').drop_duplicates('year');
        if len(g)>=6:
            a,b=g.iloc[-6].sales,g.iloc[-1].sales; calc=((b/a)**(1/5)-1)*100 if a>0 and b>0 else None
            db=pd.read_sql_query('SELECT revenue_cagr_5yr FROM financial_ratios WHERE company_id=? ORDER BY year',con,params=(cid,))
            val=db.iloc[-1,0] if not db.empty else None
            if calc is not None and pd.notna(val) and abs(calc-val)<0.1: good+=1
    add('AC-05',good==len(samples) and len(samples)>=3,f'{good}/{len(samples)} manual-equivalent CAGR spot checks within 0.1%')
    # AC-06 source ROE comparison for five companies.
    x=pd.read_sql_query("SELECT r.company_id,r.year,r.return_on_equity_pct,c.roe_percentage FROM financial_ratios r JOIN companies c USING(company_id) WHERE r.year NOT LIKE '2024-12' AND r.year=(SELECT MAX(r2.year) FROM financial_ratios r2 WHERE r2.company_id=r.company_id AND r2.year NOT LIKE '2024-12')",con); x=x.dropna(); add('AC-06',len(x)>=5 and int(((x.return_on_equity_pct-x.roe_percentage).abs()<=5).sum())>=5,'at least 5 latest annual ROE comparisons within 5%')
    from src.screener.engine import load_data,apply_filters
    d=load_data(); q=apply_filters(d,{'roe_min':15,'de_max':1,'fcf_min':0,'revenue_cagr_5yr_min':10}); add('AC-07',10<=len(q)<=50,f'Quality Compounder strict result count = {len(q)}')
    # AC-08 data/query performance proxy for five profiles.
    from src.api.main import company
    times=[]
    for cid in ['TCS','HDFCBANK','RELIANCE','SUNPHARMA','TATASTEEL']:
        if cid in set(d.company_id):
            t=time.perf_counter(); company(cid); times.append(time.perf_counter()-t)
    add('AC-08',bool(times) and max(times)<3,f'profile query max = {max(times):.3f}s' if times else 'no samples')
    # AC-09 CSV validity.
    import csv
    csvp=OUTPUT_DIR/'screener_output.csv'; q.to_csv(csvp,index=False); valid=csvp.exists() and bool(list(csv.reader(csvp.open(encoding='utf-8')))); add('AC-09',valid,'screener CSV generated and parseable')
    # AC-10 structural PDF sample check.
    from pypdf import PdfReader
    pdfs=list((REPORT_DIR/'tearsheets').glob('*.pdf')); sample=pdfs[:5]; goodpdf=all(len(PdfReader(str(p)).pages)==2 for p in sample); add('AC-10',len(sample)==5 and goodpdf,'5 sample tearsheets contain exactly 2 pages')
    from fastapi.testclient import TestClient
    from src.api.main import app
    client=TestClient(app); hr=client.get('/api/v1/health'); add('AC-11',hr.status_code==200 and hr.json().get('status')=='ok','health endpoint HTTP 200')
    tr=client.get('/api/v1/companies/TCS/ratios'); add('AC-12',tr.status_code==200 and len(tr.json())>=10,f'TCS ratios records = {len(tr.json()) if tr.status_code==200 else 0}')
    ar=client.get('/api/v1/screener',params={'min_roe':15,'max_de':1,'min_fcf':0,'min_rev_cagr_5yr':10}); add('AC-13',ar.status_code==200 and len(ar.json())==len(q),f'API screener count {len(ar.json()) if ar.status_code==200 else 0} matches strict workbook query {len(q)}')
    add('AC-14',con.execute('SELECT COUNT(DISTINCT peer_group_name) FROM peer_percentiles').fetchone()[0]==11,'11 peer groups')
    cl=pd.read_csv(OUTPUT_DIR/'cluster_labels.csv'); add('AC-15',len(cl)==92 and cl.company_id.nunique()==92,'92 companies have cluster IDs')
    pc=pd.read_csv(OUTPUT_DIR/'pros_cons_generated.csv'); counts=pc.groupby(['company_id','type']).size().unstack(fill_value=0); add('AC-16',len(counts)==92 and (counts.get('pro',pd.Series(0,index=counts.index))>=1).all() and (counts.get('con',pd.Series(0,index=counts.index))>=1).all(),'every company has >=1 pro and >=1 con')
    sizes=[p.stat().st_size for p in pdfs]; add('AC-17',len(pdfs)==92 and min(sizes)>=30000 if sizes else False,f'{len(pdfs)} tearsheets; minimum size {min(sizes) if sizes else 0} bytes')
    # pytest report is generated by the final runner; existing report is checked here.
    add('AC-18',(REPORT_DIR/'pytest_report.html').exists(),'pytest HTML report exists')
    vf=OUTPUT_DIR/'validation_failures.csv'; add('AC-19',vf.exists() and set(['company_id','field','issue','severity']).issubset(pd.read_csv(vf).columns),'validation failure schema present')
    guide=DOCS_DIR/'analyst_guide.pdf'; pages=len(PdfReader(str(guide)).pages) if guide.exists() else 0; add('AC-20',pages>=10,f'analyst guide pages = {pages}')
    con.close(); out=pd.DataFrame(checks); out.to_csv(OUTPUT_DIR/'acceptance_results.csv',index=False); return out
if __name__=='__main__': print(run().to_string(index=False))
