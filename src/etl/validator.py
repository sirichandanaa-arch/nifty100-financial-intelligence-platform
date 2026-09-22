"""Data-quality validation for the Nifty 100 source foundation."""
import sqlite3, pandas as pd, numpy as np
from src.common import DB_PATH, OUTPUT_DIR

def validate(conn=None):
    """Run DQ-01 through DQ-16 and write validation_failures.csv."""
    own=conn is None
    conn=conn or sqlite3.connect(DB_PATH); issues=[]
    def add(rule,table,field,issue,severity='WARNING',company_id=''):
        issues.append({'rule_id':rule,'table':table,'company_id':company_id,'field':field,'issue':issue,'severity':severity})
    # DQ-01 PK uniqueness and DQ-02 company-year uniqueness
    for t in ['companies','profitandloss','balancesheet','cashflow','financial_ratios']:
        pk='company_id' if t=='companies' else 'company_id,year'
        q=f"SELECT {pk},COUNT(*) n FROM {t} GROUP BY {pk} HAVING n>1"
        for row in conn.execute(q): add('DQ-01' if t=='companies' else 'DQ-02',t,pk,'Duplicate primary key','CRITICAL',str(row[0]))
    # DQ-03 FK
    if list(conn.execute('PRAGMA foreign_key_check')): add('DQ-03','database','','Foreign-key integrity failure','CRITICAL')
    pl=pd.read_sql_query('SELECT * FROM profitandloss',conn); bs=pd.read_sql_query('SELECT * FROM balancesheet',conn)
    # DQ-04 balance
    for _,r in bs.iterrows():
        a,b=r.total_assets,r.total_liabilities
        if pd.notna(a) and a and pd.notna(b) and abs(a-b)/abs(a)>0.01: add('DQ-04','balancesheet','total_assets','Assets/liabilities differ by >1%','WARNING',r.company_id)
    # DQ-05 OPM
    for _,r in pl.dropna(subset=['sales','operating_profit','opm_percentage']).iterrows():
        calc=r.operating_profit/r.sales*100 if r.sales else None
        if calc is not None and abs(calc-r.opm_percentage)>1: add('DQ-05','profitandloss','opm_percentage','OPM cross-check differs by >1 percentage point','WARNING',r.company_id)
    # DQ-06 sales positive
    for _,r in pl[pl.sales<=0].iterrows(): add('DQ-06','profitandloss','sales','Sales is not positive','WARNING',r.company_id)
    # DQ-07 net cash, DQ-08 tax, DQ-09 dividend, DQ-10 URL, DQ-11 EPS sign, DQ-12 BSE balance, DQ-13 coverage, DQ-14 company coverage, DQ-15 stock prices, DQ-16 source coverage
    bs2=bs.copy();
    for _,r in bs2.iterrows():
        if pd.notna(r.borrowings) and pd.notna(r.investments) and r.borrowings-r.investments < -1e12: add('DQ-07','balancesheet','borrowings','Extreme negative net debt','WARNING',r.company_id)
    for _,r in pl[pl.tax_percentage.notna()].iterrows():
        if r.tax_percentage < -100 or r.tax_percentage>200: add('DQ-08','profitandloss','tax_percentage','Tax rate outside plausible range','WARNING',r.company_id)
    for _,r in pl[pl.dividend_payout.notna()].iterrows():
        if r.dividend_payout<0 or r.dividend_payout>200: add('DQ-09','profitandloss','dividend_payout','Dividend payout outside 0-200%','WARNING',r.company_id)
    docs=pd.read_sql_query('SELECT * FROM documents',conn)
    for _,r in docs.iterrows():
        if pd.notna(r.annual_report) and not str(r.annual_report).startswith(('http://','https://')): add('DQ-10','documents','annual_report','Report URL is not HTTP(S)','WARNING',r.company_id)
    for _,r in pl.iterrows():
        if pd.notna(r.eps) and pd.notna(r.net_profit) and r.net_profit<0 and r.eps>0: add('DQ-11','profitandloss','eps','EPS sign inconsistent with net loss','WARNING',r.company_id)
    for _,r in bs.iterrows():
        if pd.notna(r.total_assets) and pd.notna(r.total_liabilities) and r.total_assets==0 and r.total_liabilities!=0: add('DQ-12','balancesheet','total_assets','Zero assets with nonzero liabilities','WARNING',r.company_id)
    for _,r in pl.iterrows():
        if pd.notna(r.interest) and r.interest<0: add('DQ-13','profitandloss','interest','Negative interest expense','WARNING',r.company_id)
    for t in ['profitandloss','balancesheet','cashflow']:
        counts=pd.read_sql_query(f'SELECT company_id,COUNT(*) n FROM {t} GROUP BY company_id',conn)
        for _,r in counts.iterrows():
            if r.n<5: add('DQ-14',t,'year','Company has fewer than 5 records','WARNING',r.company_id)
    sp=pd.read_sql_query('SELECT * FROM stock_prices',conn)
    if sp.empty: add('DQ-15','stock_prices','','No stock price records','CRITICAL')
    if len(pd.read_sql_query('SELECT * FROM companies',conn))!=92: add('DQ-16','companies','company_id','Expected 92 companies','CRITICAL')
    out=pd.DataFrame(issues,columns=['rule_id','table','company_id','field','issue','severity']).drop(columns=['table']); out.to_csv(OUTPUT_DIR/'validation_failures.csv',index=False)
    if own: conn.close()
    return out

if __name__=='__main__': print(validate().to_string(index=False))
