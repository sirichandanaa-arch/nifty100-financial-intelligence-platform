"""Rule-based pros and cons generation with transparent confidence scores."""
import sqlite3, pandas as pd, numpy as np
from src.common import DB_PATH, OUTPUT_DIR

def build():
    """Generate at least one rule-based pro and con per company where signals permit."""
    conn=sqlite3.connect(DB_PATH); r=pd.read_sql_query('SELECT * FROM financial_ratios',conn); s=pd.read_sql_query('SELECT company_id,broad_sector FROM sectors',conn); r['yearn']=pd.to_numeric(r.year.str[:4],errors='coerce'); latest=r.sort_values('yearn').groupby('company_id').tail(1).merge(s,on='company_id',how='left'); rows=[]
    for cid,g in r.groupby('company_id'):
        g=g.sort_values('yearn'); x=latest[latest.company_id==cid].iloc[0]; nonfin=x.broad_sector!='Financials'
        pros=[]; cons=[]
        if x.return_on_equity_pct>20: pros.append(('P01','Consistently high return on equity above 20% demonstrates strong capital efficiency',min(99,60+x.return_on_equity_pct)))
        if (g.free_cash_flow_cr>0).tail(5).sum()>=5: pros.append(('P02','Strong free cash flow generation over 5 years signals healthy cash fundamentals',90))
        if x.debt_to_equity==0: pros.append(('P03','Debt-free balance sheet provides financial flexibility and eliminates interest burden',95))
        if x.revenue_cagr_5yr>15: pros.append(('P04','Revenue growing at above 15% CAGR over 5 years reflects strong business momentum',90))
        if x.operating_profit_margin_pct>25: pros.append(('P05','Operating profit margin above 25% indicates strong pricing power and cost discipline',88))
        if x.pat_cagr_5yr>20: pros.append(('P06','Net profit compounding at above 20% over 5 years indicates strong earnings compounding',90))
        if pd.isna(x.interest_coverage) or x.interest_coverage>10: pros.append(('P07','Very high interest coverage or debt-free status indicates limited debt-servicing pressure',92))
        if x.dividend_payout_ratio_pct is not None and x.dividend_payout_ratio_pct>0 and x.free_cash_flow_cr>0: pros.append(('P08','Dividend distribution is backed by positive free cash flow',80))
        if x.eps_cagr_5yr>15: pros.append(('P09','Earnings per share growing above 15% CAGR indicates strong earnings compounding',88))
        if len(pros)==0: pros.append(('P12','Operating and financial metrics provide a measurable basis for continued monitoring',65))
        if nonfin and x.debt_to_equity>2: cons.append(('C01',f'Debt-to-equity ratio of {x.debt_to_equity:.2f} is elevated for a non-financial company and warrants monitoring',90))
        if (g.free_cash_flow_cr<0).tail(3).sum()>=3: cons.append(('C02','Free cash flow has been negative for 3 consecutive years, weakening cash-generation quality',92))
        if len(g)>=3 and g.operating_profit_margin_pct.tail(3).is_monotonic_decreasing: cons.append(('C03','Operating margins have declined across the latest three observations',82))
        if x.net_profit_margin_pct<0: cons.append(('C04','The latest period shows a net loss relative to sales',95))
        if pd.notna(x.interest_coverage) and x.interest_coverage<1.5: cons.append(('C06','Interest coverage below 1.5x indicates elevated debt-servicing pressure',92))
        if x.dividend_payout_ratio_pct>100: cons.append(('C07','Dividend payout above 100% indicates distributions exceed reported net profit',90))
        if x.return_on_capital_employed_pct<10: cons.append(('C10','Return on capital employed below 10% indicates relatively modest capital returns',82))
        if x.revenue_cagr_5yr<5: cons.append(('C12','Revenue growth below 5% CAGR over 5 years indicates limited top-line momentum',80))
        if not cons: cons.append(('C12','Some key financial indicators remain below the strongest peer-growth signals and warrant monitoring',65))
        for typ,arr in [('pro',pros),('con',cons)]:
            for rid,text,conf in arr: rows.append([cid,typ,rid,text,round(float(conf),1)])
    out=pd.DataFrame(rows,columns=['company_id','type','rule_id','text','confidence_pct']); out=out[out.confidence_pct>60]; out.to_csv(OUTPUT_DIR/'pros_cons_generated.csv',index=False); conn.execute('CREATE TABLE IF NOT EXISTS prosandcons_generated (company_id TEXT,type TEXT,rule_id TEXT,text TEXT,confidence_pct REAL)'); conn.execute('DELETE FROM prosandcons_generated'); out.to_sql('prosandcons_generated',conn,if_exists='append',index=False); conn.commit(); conn.close(); return out
if __name__=='__main__': build()
