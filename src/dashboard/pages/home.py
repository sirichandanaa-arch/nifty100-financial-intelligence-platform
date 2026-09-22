import sqlite3, pandas as pd, streamlit as st
from src.common import DB_PATH
def render():
    """Render the Home screen."""
    st.header("Home")
    try:
        con=sqlite3.connect(DB_PATH)
        if "home"=="home":
            r=pd.read_sql_query("SELECT * FROM financial_ratios",con); st.metric("Total Companies",r.company_id.nunique()); st.dataframe(r.sort_values("composite_quality_score",ascending=False).head(5),use_container_width=True)
        elif "home"=="profile":
            t=st.text_input("Ticker", "TCS").upper(); r=pd.read_sql_query("SELECT * FROM financial_ratios WHERE company_id=? ORDER BY year",con,params=(t,)); st.dataframe(r.tail(10),use_container_width=True)
        elif "home"=="screener":
            from src.screener.engine import load_data,apply_filters; d=load_data(); st.dataframe(apply_filters(d,{}),use_container_width=True); st.download_button("Download CSV",apply_filters(d,{}).to_csv(index=False),"screener.csv","text/csv")
        elif "home"=="peers": st.dataframe(pd.read_sql_query("SELECT * FROM peer_percentiles",con).head(100),use_container_width=True)
        elif "home"=="trends": st.dataframe(pd.read_sql_query("SELECT * FROM financial_ratios ORDER BY year",con).head(100),use_container_width=True)
        elif "home"=="sectors": st.dataframe(pd.read_sql_query("SELECT * FROM sectors",con),use_container_width=True)
        elif "home"=="capital": st.dataframe(pd.read_csv("output/capital_allocation.csv"),use_container_width=True)
        else: st.dataframe(pd.read_sql_query("SELECT * FROM documents LIMIT 200",con),use_container_width=True)
        con.close()
    except Exception as e: st.error(f"Data unavailable: {e}")
