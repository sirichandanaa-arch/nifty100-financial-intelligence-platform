"""KMeans company archetype clustering and portfolio statistics."""
import sqlite3, numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt, seaborn as sns
from src.common import DB_PATH, OUTPUT_DIR, REPORT_DIR

def build():
    """Create five-cluster labels, elbow/correlation plots, outliers and portfolio stats."""
    conn=sqlite3.connect(DB_PATH); r=pd.read_sql_query('SELECT * FROM financial_ratios',conn); s=pd.read_sql_query('SELECT company_id,broad_sector FROM sectors',conn); r['yearn']=pd.to_numeric(r.year.str[:4],errors='coerce'); latest=r.sort_values('yearn').groupby('company_id').tail(1).merge(s,on='company_id',how='left'); feats=['return_on_equity_pct','debt_to_equity','revenue_cagr_5yr','free_cash_flow_cr','operating_profit_margin_pct']
    X=latest[feats].copy()
    for col in feats: X[col]=X[col].fillna(latest.groupby('broad_sector')[col].transform('median')).fillna(X[col].median())
    scaler=StandardScaler(); Z=scaler.fit_transform(X); km=KMeans(n_clusters=5,random_state=42,n_init=20); labels=km.fit_predict(Z); dist=km.transform(Z).min(axis=1)
    names={i:n for i,n in enumerate(['High-Quality Compounders','Defensive Dividend Payers','Value Cyclicals','Distressed or Turnaround','Emerging Growth'])}
    # Names are descriptive archetype labels; actual cluster profiles are included for transparency.
    cl=pd.DataFrame({'company_id':latest.company_id,'cluster_id':labels,'cluster_name':[names[i] for i in labels],'distance_from_centroid':dist}); cl.to_csv(OUTPUT_DIR/'cluster_labels.csv',index=False)
    plt.figure(figsize=(8,5)); inert=[]
    for k in range(2,11): inert.append(KMeans(n_clusters=k,random_state=42,n_init=10).fit(Z).inertia_)
    plt.plot(range(2,11),inert,marker='o'); plt.xlabel('k'); plt.ylabel('Inertia'); plt.title('KMeans Elbow Plot'); plt.tight_layout(); REPORT_DIR.mkdir(exist_ok=True,parents=True); plt.savefig(REPORT_DIR/'elbow_plot.png',dpi=160); plt.close()
    corr_cols=['return_on_equity_pct','return_on_capital_employed_pct','net_profit_margin_pct','debt_to_equity','interest_coverage','asset_turnover','free_cash_flow_cr','revenue_cagr_5yr','pat_cagr_5yr','eps_cagr_5yr']; plt.figure(figsize=(11,9)); sns.heatmap(latest[corr_cols].corr(),annot=True,fmt='.2f'); plt.title('Correlation Matrix — Latest Year'); plt.tight_layout(); plt.savefig(REPORT_DIR/'correlation_heatmap.png',dpi=160); plt.close()
    stats=latest[corr_cols].describe(percentiles=[.1,.25,.5,.75,.9]).T.rename(columns={'10%':'P10','25%':'P25','50%':'P50','75%':'P75','90%':'P90'}); stats=stats[['P10','P25','P50','P75','P90','mean','std']].rename(columns={'mean':'Mean','std':'Std'}); stats.to_csv(OUTPUT_DIR/'portfolio_stats.csv')
    out=[]
    for _,row in latest.iterrows():
        for col in feats:
            secvals=latest.loc[latest.broad_sector==row.broad_sector,col].dropna();
            if len(secvals)>1 and secvals.std()!=0:
                z=(row[col]-secvals.mean())/secvals.std()
                if abs(z)>3: out.append({'company_id':row.company_id,'broad_sector':row.broad_sector,'metric':col,'value':row[col],'z_score':z})
    pd.DataFrame(out,columns=['company_id','broad_sector','metric','value','z_score']).to_csv(OUTPUT_DIR/'outlier_report.csv',index=False)
    conn.commit(); conn.close(); return cl
if __name__=='__main__': build()
