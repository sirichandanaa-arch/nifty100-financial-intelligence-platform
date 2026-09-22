import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st
from src.common import DB_PATH

def read(sql,params=()):
    """Read SQL into a DataFrame."""
    conn=sqlite3.connect(DB_PATH); 
    try:return pd.read_sql_query(sql,conn,params=params)
    finally:conn.close()
@st.cache_data(ttl=600)
def get_companies(): return read('SELECT * FROM companies')
@st.cache_data(ttl=600)
def get_ratios(ticker,year=None): return read('SELECT * FROM financial_ratios WHERE company_id=?'+(' AND year=?' if year else '')+' ORDER BY year',[ticker]+([year] if year else []))
@st.cache_data(ttl=600)
def get_pl(ticker): return read('SELECT * FROM profitandloss WHERE company_id=? ORDER BY year',[ticker])
@st.cache_data(ttl=600)
def get_bs(ticker): return read('SELECT * FROM balancesheet WHERE company_id=? ORDER BY year',[ticker])
@st.cache_data(ttl=600)
def get_cf(ticker): return read('SELECT * FROM cashflow WHERE company_id=? ORDER BY year',[ticker])
@st.cache_data(ttl=600)
def get_sectors(): return read('SELECT * FROM sectors')
@st.cache_data(ttl=600)
def get_peers(group_name): return read('SELECT * FROM peer_percentiles WHERE peer_group_name=?',[group_name])
@st.cache_data(ttl=600)
def get_valuation(ticker):
    p=Path('output/valuation_summary.xlsx'); return pd.read_excel(p).query('company_id==@ticker') if p.exists() else pd.DataFrame()
