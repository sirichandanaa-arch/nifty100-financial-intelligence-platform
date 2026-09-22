"""Cash-flow intelligence output."""
import sqlite3, pandas as pd, numpy as np
from src.common import DB_PATH, OUTPUT_DIR

def build():
    """Generate cashflow_intelligence.xlsx and distress_alerts.csv."""
    conn=sqlite3.connect(DB_PATH); r=pd.read_sql_query('SELECT * FROM financial_ratios',conn); s=pd.read_sql_query('SELECT company_id,broad_sector FROM sectors',conn); b=pd.read_sql_query('SELECT * FROM balancesheet',conn); cf=pd.read_sql_query('SELECT * FROM cashflow',conn); pl=pd.read_sql_query('SELECT company_id,year,net_profit FROM profitandloss',conn); conn.close(); r['yn']=pd.to_numeric(r.year.str[:4],errors='coerce'); latest=r.sort_values('yn').groupby('company_id').tail(1).merge(s,on='company_id',how='left'); b['yn']=pd.to_numeric(b.year.str[:4],errors='coerce'); bl=b.sort_values('yn').groupby('company_id').tail(1)[['company_id','borrowings']].rename(columns={'borrowings':'latest_borrowings'}); cf['yn']=pd.to_numeric(cf.year.str[:4],errors='coerce'); cfl=cf.sort_values('yn').groupby('company_id').tail(1); pl['yn']=pd.to_numeric(pl.year.str[:4],errors='coerce'); pll=pl.sort_values('yn').groupby('company_id').tail(1); out=latest.merge(bl,on='company_id',how='left').merge(cfl[['company_id','operating_activity','financing_activity']],on='company_id',how='left').merge(pll[['company_id','net_profit']],on='company_id',how='left'); out=out.rename(columns={'operating_activity':'latest_cfo','financing_activity':'latest_cff','net_profit':'latest_net_profit'}); out['fcf_cagr_5yr']=np.nan; out['distress_flag']=(out.latest_cfo<0)&(out.latest_cff>0); out['deleveraging_flag']=False
    # YoY borrowings decline
    for cid in out.company_id:
        x=b[b.company_id==cid].sort_values('yn'); z=cfl[cfl.company_id==cid]; out.loc[out.company_id==cid,'deleveraging_flag']=bool(len(x)>=2 and len(z)>0 and x.borrowings.iloc[-1]<x.borrowings.iloc[-2] and z.financing_activity.iloc[-1]<0)
    cols=['company_id','broad_sector','cfo_quality_score','cfo_quality_label','capex_intensity_pct','capex_label','fcf_cagr_5yr','fcf_conversion_pct','distress_flag','deleveraging_flag','capital_allocation_label']; out[cols].rename(columns={'broad_sector':'sector'}).to_excel(OUTPUT_DIR/'cashflow_intelligence.xlsx',index=False); out[out.distress_flag][['company_id','broad_sector','latest_cfo','latest_cff','latest_net_profit']].rename(columns={'broad_sector':'sector'}).to_csv(OUTPUT_DIR/'distress_alerts.csv',index=False); return out
if __name__=='__main__': build()


def cfo_quality(values):
    """Return average CFO/PAT ratio and its label."""
    vals=[float(x) for x in values if x is not None]
    if not vals: return (None,None)
    v=sum(vals)/len(vals); return (v, 'High Quality' if v>1 else ('Moderate' if v>=0.5 else 'Accrual Risk'))

def capex_intensity(investing_activity, sales):
    """Return CapEx intensity percentage and label."""
    if sales==0: return (None,None)
    v=abs(float(investing_activity))/float(sales)*100; return (v,'Asset Light' if v<3 else ('Moderate' if v<=8 else 'Capital Intensive'))

def allocation_pattern(cfo,cfi,cff):
    """Classify a CFO/CFI/CFF sign pattern."""
    s=(('+' if cfo>0 else '-' if cfo<0 else '0'),('+' if cfi>0 else '-' if cfi<0 else '0'),('+' if cff>0 else '-' if cff<0 else '0'))
    return {('+','-','-'):'Reinvestor',('+','-','+'):'Mixed',('+','+','-'):'Liquidating Assets',('-','+','+'):'Distress Signal',('-','-','+'):'Growth Funded by Debt',('+','+','+'):'Cash Accumulator',('-','-','-'):'Pre-Revenue'}.get(s,'Mixed')

def fcf(operating_activity, investing_activity):
    """Return free cash flow as CFO plus CFI."""
    return operating_activity+investing_activity
