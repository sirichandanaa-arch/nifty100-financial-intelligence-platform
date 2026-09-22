"""Compute the financial ratio engine from P&L, balance sheet and cash flow data."""
import sqlite3, math
import pandas as pd, numpy as np
from src.common import DB_PATH, OUTPUT_DIR
from src.analytics.cagr import cagr_with_flag

def _latest(df): return df.sort_values('year').groupby('company_id').tail(1)
def _calc_window(series, idx, years):
    if idx-years<0: return (None,'INSUFFICIENT')
    return cagr_with_flag(series.iloc[idx-years],series.iloc[idx],years,True)

def build():
    """Populate financial_ratios and capital_allocation.csv."""
    conn=sqlite3.connect(DB_PATH); pl=pd.read_sql_query('SELECT * FROM profitandloss',conn); bs=pd.read_sql_query('SELECT * FROM balancesheet',conn); cf=pd.read_sql_query('SELECT * FROM cashflow',conn); sec=pd.read_sql_query('SELECT * FROM sectors',conn); comp=pd.read_sql_query('SELECT * FROM companies',conn)
    for d in [pl,bs,cf]: d['year_num']=pd.to_numeric(d.year.str[:4],errors='coerce')
    # exact company-year join; missing BS/CF remains NaN
    x=pl.merge(bs,on=['company_id','year'],how='left',suffixes=('','_bs')).merge(cf,on=['company_id','year'],how='left',suffixes=('','_cf')).merge(sec[['company_id','broad_sector']],on='company_id',how='left')
    rows=[]
    for cid,g in x.groupby('company_id'):
        g=g.sort_values(['year_num','year']).drop_duplicates('year',keep='first').reset_index(drop=True)
        # cashflow duplicates were already collapsed by loader
        for i,r in g.iterrows():
            sales=r.sales; op=r.operating_profit; pat=r.net_profit; equity=(r.equity_capital if pd.notna(r.equity_capital) else 0)+(r.reserves if pd.notna(r.reserves) else 0); assets=r.total_assets; debt=r.borrowings; interest=r.interest; other_income=r.other_income
            roe=pat/equity*100 if pd.notna(pat) and equity>0 else None
            roce=(op+other_income)/(equity+(debt if pd.notna(debt) else 0))*100 if pd.notna(op) and equity+(debt if pd.notna(debt) else 0)>0 else None
            de=(debt/equity) if pd.notna(debt) and equity>0 else (0 if pd.notna(debt) and debt==0 else None)
            icr=(op+other_income)/interest if pd.notna(interest) and interest!=0 else None
            fcf=(r.operating_activity if pd.notna(r.operating_activity) else 0)+(r.investing_activity if pd.notna(r.investing_activity) else 0)
            cfo=r.operating_activity
            capex=abs(r.investing_activity) if pd.notna(r.investing_activity) else None
            capint=capex/sales*100 if capex is not None and pd.notna(sales) and sales!=0 else None
            # CFO/PAT 5y average for available observations
            hist=g.iloc[max(0,i-4):i+1]
            ratios=[a/b for a,b in zip(hist.operating_activity,hist.net_profit) if pd.notna(a) and pd.notna(b) and b!=0]
            cfoq=sum(ratios)/len(ratios) if ratios else None
            cfoql='High Quality' if cfoq is not None and cfoq>1 else ('Moderate' if cfoq is not None and cfoq>=0.5 else ('Accrual Risk' if cfoq is not None else None))
            caplabel='Asset Light' if capint is not None and capint<3 else ('Moderate' if capint is not None and capint<=8 else ('Capital Intensive' if capint is not None else None))
            fcfconv=fcf/op*100 if pd.notna(op) and op!=0 else None
            pattern=pattern_label(r.operating_activity,r.investing_activity,r.financing_activity,cfoq)
            vals={}
            for base,col in [('revenue','sales'),('pat','net_profit'),('eps','eps')]:
                s=g[col]
                for n in [3,5,10]:
                    val,flag=_calc_window(s,i,n); vals[f'{base}_cagr_{n}yr']=val; vals[f'{base}_cagr_{n}yr_flag']=flag
            rows.append(dict(company_id=cid,year=r.year,net_profit_margin_pct=(pat/sales*100 if pd.notna(pat) and pd.notna(sales) and sales!=0 else None),operating_profit_margin_pct=(op/sales*100 if pd.notna(op) and pd.notna(sales) and sales!=0 else None),return_on_equity_pct=roe,return_on_capital_employed_pct=roce,debt_to_equity=de,interest_coverage=icr,icr_label='Debt Free' if icr is None else None,asset_turnover=(sales/assets if pd.notna(sales) and pd.notna(assets) and assets!=0 else None),free_cash_flow_cr=fcf,capex_cr=capex,earnings_per_share=r.eps,book_value_per_share=((equity/r.equity_capital) if pd.notna(r.equity_capital) and r.equity_capital!=0 else None),dividend_payout_ratio_pct=r.dividend_payout,total_debt_cr=debt,cash_from_operations_cr=cfo,cfo_quality_score=cfoq,cfo_quality_label=cfoql,capex_intensity_pct=capint,capex_label=caplabel,fcf_conversion_pct=fcfconv,capital_allocation_label=pattern,high_leverage_flag=int(pd.notna(de) and de>5 and r.broad_sector!='Financials'),icr_warning_flag=int(pd.notna(icr) and icr<1.5),**vals))
    out=pd.DataFrame(rows)
    # quality score based on latest cross-sectional P10/P90 normalization
    latest=out.sort_values('year').groupby('company_id').tail(1).copy()
    def norm(s,higher=True):
        a=pd.to_numeric(s,errors='coerce'); lo=a.quantile(.1); hi=a.quantile(.9); z=((a.clip(lo,hi)-lo)/(hi-lo)*100 if hi!=lo else pd.Series(50,index=a.index)); return z if higher else 100-z
    for col in ['return_on_equity_pct','return_on_capital_employed_pct','net_profit_margin_pct','free_cash_flow_cr','cfo_quality_score','revenue_cagr_5yr','pat_cagr_5yr','debt_to_equity','interest_coverage']:
        if col not in latest: latest[col]=np.nan
    score=(norm(latest.return_on_equity_pct)*.15+norm(latest.return_on_capital_employed_pct)*.10+norm(latest.net_profit_margin_pct)*.10+norm(latest.free_cash_flow_cr)*.15+norm(latest.cfo_quality_score)*.10+latest.free_cash_flow_cr.notna().astype(float)*5+norm(latest.revenue_cagr_5yr)*.10+norm(latest.pat_cagr_5yr)*.10+norm(latest.debt_to_equity,False)*.10+norm(latest.interest_coverage)*.05).clip(0,100)
    scoremap=dict(zip(latest.company_id,score))
    out['composite_quality_score']=out.company_id.map(scoremap)
    # overwrite table
    conn.execute('DELETE FROM financial_ratios'); out.to_sql('financial_ratios',conn,if_exists='append',index=False)
    ca=out[['company_id','year','capital_allocation_label']].copy(); ca['cfo_sign']=np.sign(cfo.set_index(['company_id','year']).reindex(pd.MultiIndex.from_frame(ca[['company_id','year']])) if False else 0)
    # regenerate signs directly from CF
    cft=cf[['company_id','year','operating_activity','investing_activity','financing_activity']].drop_duplicates(['company_id','year'])
    ca=ca.drop(columns=['cfo_sign']).merge(cft,on=['company_id','year'],how='left'); ca['cfo_sign']=ca.operating_activity.apply(sign); ca['cfi_sign']=ca.investing_activity.apply(sign); ca['cff_sign']=ca.financing_activity.apply(sign); ca=ca[['company_id','year','cfo_sign','cfi_sign','cff_sign','capital_allocation_label']].rename(columns={'capital_allocation_label':'pattern_label'}); ca.to_csv(OUTPUT_DIR/'capital_allocation.csv',index=False)
    conn.commit(); conn.close(); return out

def sign(x):
    """Return +, -, or 0 for a cash-flow value."""
    if pd.isna(x) or x==0:return '0'
    return '+' if x>0 else '-'

def pattern_label(cfo,cfi,cff,cfoq=None):
    """Classify CFO/CFI/CFF sign pattern using the documented labels."""
    s=(sign(cfo),sign(cfi),sign(cff))
    if s==('+','-','-'): return 'Shareholder Returns' if cfoq is not None and cfoq>1 else 'Reinvestor'
    return {('+','+','-'):'Liquidating Assets',('-','+','+'):'Distress Signal',('-','-','+'):'Growth Funded by Debt',('+','+','+'):'Cash Accumulator',('-','-','-'):'Pre-Revenue',('+','-','+'):'Mixed'}.get(s,'Mixed')

if __name__=='__main__': print(build().shape)
