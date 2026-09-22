from pathlib import Path
import os, re, math
import pandas as pd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DB_PATH = Path(os.getenv("DB_PATH", ROOT / "data" / "nifty100.db"))
SOURCE_DIR = Path(os.getenv("SOURCE_DIR", ROOT / "source"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", ROOT / "output"))
REPORT_DIR = Path(os.getenv("REPORT_DIR", ROOT / "reports"))
DOCS_DIR = ROOT / "docs"
for p in [DB_PATH.parent, OUTPUT_DIR, REPORT_DIR, DOCS_DIR]: p.mkdir(parents=True, exist_ok=True)

SOURCE_FILES = ["companies.xlsx","profitandloss.xlsx","balancesheet.xlsx","cashflow.xlsx","documents.xlsx","analysis.xlsx","prosandcons.xlsx","sectors.xlsx","stock_prices.xlsx","financial_ratios.xlsx","market_cap.xlsx","peer_groups.xlsx"]

def norm_ticker(v):
    """Normalize a ticker/company identifier."""
    if pd.isna(v): return ""
    return str(v).strip().upper()

def norm_year(v):
    """Normalize financial period labels to YYYY-MM; TTM is mapped to 2024-12."""
    if pd.isna(v): return None
    s=str(v).strip()
    if not s or s.lower()=='nan': return None
    if s.upper()=='TTM': return '2024-12'
    m=re.search(r'(20\d{2})\s*[-/]\s*(\d{1,2})$',s)
    if m: return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}"
    m=re.search(r'([A-Za-z]{3,9})[- ](20\d{2})$',s)
    if m:
        mon=pd.to_datetime(m.group(1),format='%b',errors='coerce')
        if pd.isna(mon): mon=pd.to_datetime(m.group(1),format='%B',errors='coerce')
        return f"{int(m.group(2)):04d}-{int(mon.month):02d}" if pd.notna(mon) else s
    m=re.search(r'(20\d{2})$',s)
    if m: return f"{int(m.group(1)):04d}-12"
    try:
        dt=pd.to_datetime(v,errors='coerce')
        if pd.notna(dt): return f"{dt.year:04d}-{dt.month:02d}"
    except Exception: pass
    return s

def safe_num(x):
    """Convert a value to float or None."""
    try:
        y=pd.to_numeric(x,errors='coerce'); return None if pd.isna(y) else float(y)
    except Exception: return None

def read_excel_clean(path, preferred_header=1):
    """Read an Excel sheet while detecting whether a title row precedes the header."""
    raw=pd.read_excel(path,header=None)
    # Find first row containing company_id, or a distinctive id/header row.
    header_idx=None
    for i,row in raw.iterrows():
        vals=[str(x).strip().lower() for x in row.tolist() if not pd.isna(x)]
        if 'company_id' in vals:
            header_idx=i; break
    if header_idx is None: header_idx=preferred_header
    df=pd.read_excel(path,header=header_idx)
    df=df.loc[:,~df.columns.astype(str).str.startswith('Unnamed')]
    df.columns=[str(c).strip().lower().replace(' ','_') for c in df.columns]
    return df

def dedupe_company_year(df, table, audit_rows=None):
    """Resolve duplicate company-year records deterministically, preferring the first source row."""
    if not {'company_id','year'}.issubset(df.columns): return df
    df=df.copy(); df['company_id']=df['company_id'].map(norm_ticker); df['year']=df['year'].map(norm_year)
    before=len(df)
    dup=df.duplicated(['company_id','year'],keep=False)
    conflicts=df.loc[dup].groupby(['company_id','year']).size()
    # Exact duplicates and duplicate source blocks are safely collapsed to first occurrence.
    df=df.drop_duplicates(['company_id','year'],keep='first').reset_index(drop=True)
    if audit_rows is not None:
        audit_rows.append({'table':table,'source_rows':before,'loaded_rows':len(df),'rejected_rows':before-len(df),'severity':'WARNING' if before!=len(df) else ''})
    return df
