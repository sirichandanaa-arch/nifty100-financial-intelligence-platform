"""Parse structured CAGR statements from analysis.xlsx."""
import re, pandas as pd
from src.common import SOURCE_DIR, OUTPUT_DIR, read_excel_clean, norm_ticker

def build():
    """Generate analysis_parsed.csv and parse_failures.csv."""
    df=read_excel_clean(SOURCE_DIR/'analysis.xlsx'); rows=[]; failures=[]
    for _,r in df.iterrows():
        for metric in ['compounded_sales_growth','compounded_profit_growth','stock_price_cagr','roe']:
            text=str(r.get(metric,'')); m=re.search(r'(\d+)\s*Years?:?\s*([\d.]+)%',text)
            if m: rows.append([norm_ticker(r.company_id),metric,int(m.group(1)),float(m.group(2))])
            elif text not in ('nan',''): failures.append([norm_ticker(r.company_id),metric,text])
    pd.DataFrame(rows,columns=['company_id','metric_type','period_years','value_pct']).to_csv(OUTPUT_DIR/'analysis_parsed.csv',index=False); pd.DataFrame(failures,columns=['company_id','metric_type','raw_text']).to_csv(OUTPUT_DIR/'parse_failures.csv',index=False); return rows
if __name__=='__main__': build()
