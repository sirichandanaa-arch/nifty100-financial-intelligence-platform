import sqlite3,pandas as pd
from src.common import DB_PATH,OUTPUT_DIR

def build():
    """Generate peer comparison workbook."""
    conn=sqlite3.connect(DB_PATH); p=pd.read_sql_query('SELECT * FROM peer_groups',conn); r=pd.read_sql_query('SELECT * FROM financial_ratios',conn); pp=pd.read_sql_query('SELECT * FROM peer_percentiles',conn); conn.close();
    with pd.ExcelWriter(OUTPUT_DIR/'peer_comparison.xlsx',engine='openpyxl') as w:
        for g in p.peer_group_name.unique():
            ids=p[p.peer_group_name==g].company_id.tolist(); base=r[r.company_id.isin(ids)].copy(); base['yn']=pd.to_numeric(base.year.str[:4],errors='coerce'); base=base.sort_values('yn').groupby('company_id').tail(1); pct=pp[pp.peer_group_name==g].pivot_table(index='company_id',columns='metric',values='percentile_rank'); base=base.merge(pct,left_on='company_id',right_index=True,how='left'); base.to_excel(w,sheet_name=str(g)[:31],index=False)
