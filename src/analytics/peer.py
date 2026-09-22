"""Peer-group percentile engine and radar charts."""
import sqlite3, numpy as np, pandas as pd
import matplotlib.pyplot as plt
from src.common import DB_PATH,OUTPUT_DIR,REPORT_DIR

def build():
    """Populate peer_percentiles, peer comparison workbook and 92 radar charts."""
    conn=sqlite3.connect(DB_PATH); p=pd.read_sql_query('SELECT * FROM peer_groups',conn); r=pd.read_sql_query('SELECT * FROM financial_ratios',conn); conn.close(); r['yearn']=pd.to_numeric(r.year.str[:4],errors='coerce'); latest=r[r.year!='2024-12'].sort_values(['yearn','year']).groupby('company_id').tail(1); latest=latest.merge(p[['peer_group_name','company_id','is_benchmark']],on='company_id',how='left')
    metrics={'ROE':'return_on_equity_pct','ROCE':'return_on_capital_employed_pct','NPM':'net_profit_margin_pct','D/E':'debt_to_equity','FCF':'free_cash_flow_cr','PAT CAGR 5yr':'pat_cagr_5yr','Revenue CAGR 5yr':'revenue_cagr_5yr','EPS CAGR 5yr':'eps_cagr_5yr','Interest Coverage':'interest_coverage','Asset Turnover':'asset_turnover'}; rows=[]
    for grp,g in latest.dropna(subset=['peer_group_name']).groupby('peer_group_name'):
        for metric,col in metrics.items():
            v=pd.to_numeric(g[col],errors='coerce'); rank=v.rank(pct=True,method='average');
            if metric=='D/E': rank=1-rank
            for cid,val,pr in zip(g.company_id,v,rank): rows.append((cid,grp,metric,None if pd.isna(val) else float(val),None if pd.isna(pr) else float(pr*100),g.loc[g.company_id==cid,'year'].iloc[0]))
    out=pd.DataFrame(rows,columns=['company_id','peer_group_name','metric','value','percentile_rank','year']); conn=sqlite3.connect(DB_PATH); conn.execute('DELETE FROM peer_percentiles'); out.to_sql('peer_percentiles',conn,if_exists='append',index=False); conn.commit(); conn.close()
    with pd.ExcelWriter(OUTPUT_DIR/'peer_comparison.xlsx',engine='openpyxl') as w:
        for grp,g in p.groupby('peer_group_name'):
            ids=g.company_id.tolist(); base=latest[latest.company_id.isin(ids)].copy(); pct=out[out.peer_group_name==grp].pivot_table(index='company_id',columns='metric',values='percentile_rank'); base=base.merge(pct,left_on='company_id',right_index=True,how='left'); base.to_excel(w,sheet_name=str(grp)[:31],index=False)
    rdir=REPORT_DIR/'radar_charts'; rdir.mkdir(parents=True,exist_ok=True)
    axes=['ROE','ROCE','NPM','D/E','FCF','PAT CAGR 5yr','Revenue CAGR 5yr','EPS CAGR 5yr']; cols=[metrics[x] for x in axes]
    for _,x in latest.iterrows():
        vals=[]
        for col in cols:
            series=pd.to_numeric(latest[col],errors='coerce'); val=x[col]; lo=series.quantile(.1); hi=series.quantile(.9); z=50 if pd.isna(val) or hi==lo else float((min(max(val,lo),hi)-lo)/(hi-lo)*100); vals.append(z)
        ang=np.linspace(0,2*np.pi,len(axes),endpoint=False).tolist(); vals2=vals+[vals[0]]; ang2=ang+[ang[0]]; fig=plt.figure(figsize=(6,6)); ax=fig.add_subplot(111,polar=True); ax.plot(ang2,vals2,marker='o'); ax.fill(ang2,vals2,alpha=.15); ax.set_xticks(ang); ax.set_xticklabels(axes,fontsize=8); ax.set_ylim(0,100); ax.set_title(f"{x.company_id} — Peer Radar"); fig.tight_layout(); fig.savefig(rdir/f'{x.company_id}_radar.png',dpi=140); plt.close(fig)
    return out
if __name__=='__main__': build()
