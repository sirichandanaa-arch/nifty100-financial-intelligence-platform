"""Valuation summary from the supplied simulated market-cap workbook."""
import sqlite3, numpy as np, pandas as pd
from src.common import *

def build():
    """Create valuation_summary.xlsx/csv and database table."""
    conn=sqlite3.connect(DB_PATH); m=read_excel_clean(SOURCE_DIR/'market_cap.xlsx',0); m['company_id']=m.company_id.map(norm_ticker); m['year']=pd.to_numeric(m.year,errors='coerce').astype('Int64'); s=pd.read_sql_query('SELECT company_id,broad_sector FROM sectors',conn); c=pd.read_sql_query('SELECT company_id,company_name FROM companies',conn); latest_pl=pd.read_sql_query('SELECT company_id,year,operating_profit,net_profit FROM profitandloss',conn); latest_pl['yearn']=pd.to_numeric(latest_pl.year.str[:4],errors='coerce'); latest_pl=latest_pl.sort_values('yearn').groupby('company_id').tail(1); r=pd.read_sql_query('SELECT company_id,year,free_cash_flow_cr FROM financial_ratios',conn); r['yearn']=pd.to_numeric(r.year.str[:4],errors='coerce'); r=r.sort_values('yearn').groupby('company_id').tail(1)
    m=m.merge(s,on='company_id',how='left').merge(c,on='company_id',how='left').merge(r[['company_id','free_cash_flow_cr']],on='company_id',how='left'); m['pe']=m.pe_ratio; m['pb']=m.pb_ratio; m['ev_ebitda']=m.ev_ebitda; m['fcf_yield_pct']=m.free_cash_flow_cr/m.market_cap_crore*100
    med=m.groupby(['broad_sector','year'])['pe'].transform('median'); m['five_year_median_pe']=m.groupby('broad_sector')['pe'].transform(lambda x:x.rolling(5,min_periods=1).median()); m['pe_vs_sector_median_pct']=np.where(med.notna() & (med!=0),(m.pe/med-1)*100,np.nan); m['flag']=np.select([m.pe>med*1.5,m.pe<med*.7],['Caution','Discount'],'Fair')
    out=m[['company_id','company_name','broad_sector','year','pe','pb','ev_ebitda','fcf_yield_pct','five_year_median_pe','pe_vs_sector_median_pct','flag','market_cap_crore']].rename(columns={'broad_sector':'sector'}); latest_out=out.sort_values('year').groupby('company_id').tail(1).reset_index(drop=True); latest_out.to_excel(OUTPUT_DIR/'valuation_summary.xlsx',index=False); latest_out[latest_out.flag.isin(['Caution','Discount'])].to_csv(OUTPUT_DIR/'valuation_flags.csv',index=False)
    conn.execute('DELETE FROM valuation_summary'); out.to_sql('valuation_summary',conn,if_exists='append',index=False); conn.commit(); conn.close(); return out
if __name__=='__main__': build()
