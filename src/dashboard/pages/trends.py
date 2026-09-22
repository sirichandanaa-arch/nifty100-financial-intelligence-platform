import sqlite3, pandas as pd, streamlit as st
from src.common import DB_PATH
def render():
    """Render the Trend Analysis screen."""
    st.header("Trend Analysis")
    try:
        con=sqlite3.connect(DB_PATH)
        if "trends"=="home":
            r=pd.read_sql_query("SELECT * FROM financial_ratios",con); st.metric("Total Companies",r.company_id.nunique()); st.dataframe(r.sort_values("composite_quality_score",ascending=False).head(5),use_container_width=True)
        elif "trends"=="profile":
            t=st.text_input("Ticker", "TCS").upper(); r=pd.read_sql_query("SELECT * FROM financial_ratios WHERE company_id=? ORDER BY year",con,params=(t,)); st.dataframe(r.tail(10),use_container_width=True)
        elif "trends"=="screener":
            from src.screener.engine import load_data,apply_filters; d=load_data(); st.dataframe(apply_filters(d,{}),use_container_width=True); st.download_button("Download CSV",apply_filters(d,{}).to_csv(index=False),"screener.csv","text/csv")
        elif "trends"=="peers": st.dataframe(pd.read_sql_query("SELECT * FROM peer_percentiles",con).head(100),use_container_width=True)
        elif "trends"=="trends": st.dataframe(pd.read_sql_query("SELECT * FROM financial_ratios ORDER BY year",con).head(100),use_container_width=True)
        elif "trends"=="sectors": st.dataframe(pd.read_sql_query("SELECT * FROM sectors",con),use_container_width=True)
        elif "trends"=="capital": st.dataframe(pd.read_csv("output/capital_allocation.csv"),use_container_width=True)
        else: st.dataframe(pd.read_sql_query("SELECT * FROM documents LIMIT 200",con),use_container_width=True)
        con.close()
    except Exception as e: st.error(f"Data unavailable: {e}")
