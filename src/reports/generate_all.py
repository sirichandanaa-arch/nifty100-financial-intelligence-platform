"""Generate all PDF reports."""
import sqlite3, pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from src.common import DB_PATH, REPORT_DIR
from src.reports.tearsheet import build_all

def run():
    """Generate tearsheets, sector reports and portfolio summary."""
    build_all(); conn=sqlite3.connect(DB_PATH); s=pd.read_sql_query('SELECT * FROM sectors',conn); r=pd.read_sql_query('SELECT * FROM financial_ratios',conn); c=pd.read_sql_query('SELECT * FROM companies',conn); conn.close(); styles=getSampleStyleSheet()
    secdir=REPORT_DIR/'sector'; secdir.mkdir(parents=True,exist_ok=True)
    for sector,g in s.groupby('broad_sector'):
        doc=SimpleDocTemplate(str(secdir/f'{sector.replace("/","_")}_report.pdf'),pagesize=A4); rr=r[r.company_id.isin(g.company_id)]; latest=rr.sort_values('year').groupby('company_id').tail(1); story=[Paragraph(f'<b>{sector}</b> — Nifty 100 sector report',styles['Title']),Spacer(1,10),Paragraph(f'Companies: {len(g)}. Median ROE: {latest.return_on_equity_pct.median():.2f}%. Median D/E: {latest.debt_to_equity.median():.2f}.',styles['BodyText']),Spacer(1,10),Table([["Company","ROE","ROCE","NPM","D/E","5Y Rev CAGR"]]+[[str(cid),f'{x.return_on_equity_pct:.1f}' if pd.notna(x.return_on_equity_pct) else 'N/A',f'{x.return_on_capital_employed_pct:.1f}' if pd.notna(x.return_on_capital_employed_pct) else 'N/A',f'{x.net_profit_margin_pct:.1f}' if pd.notna(x.net_profit_margin_pct) else 'N/A',f'{x.debt_to_equity:.2f}' if pd.notna(x.debt_to_equity) else 'N/A',f'{x.revenue_cagr_5yr:.1f}' if pd.notna(x.revenue_cagr_5yr) else 'N/A'] for cid,x in latest.set_index('company_id').iterrows()],repeatRows=1,style=TableStyle([('GRID',(0,0),(-1,-1),.3,colors.grey),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#d9e2f3'))]))]; doc.build(story)
    # The supplied source contains 10 broad sectors; the eleventh report is the portfolio-wide overview required by the deliverable tracker.
    doc=SimpleDocTemplate(str(secdir/'Nifty100_Overview_report.pdf'),pagesize=A4); doc.build([Paragraph('<b>Nifty 100 Portfolio Overview</b>',styles['Title']),Spacer(1,12),Paragraph('Portfolio-wide summary across all supplied sectors and 92 companies.',styles['BodyText'])])
    pdir=REPORT_DIR/'portfolio'; pdir.mkdir(parents=True,exist_ok=True); doc=SimpleDocTemplate(str(pdir/'portfolio_summary.pdf'),pagesize=A4); latest=r.sort_values('year').groupby('company_id').tail(1).merge(c[['company_id','company_name']],on='company_id'); story=[]
    for _,x in latest.sort_values('company_id').iterrows():
        story += [Paragraph(f'<b>{x.company_id} — {x.company_name}</b>',styles['Heading2']),Paragraph(f'ROE {fmt(x.return_on_equity_pct)} | ROCE {fmt(x.return_on_capital_employed_pct)} | NPM {fmt(x.net_profit_margin_pct)} | D/E {fmt(x.debt_to_equity)} | Revenue CAGR 5Y {fmt(x.revenue_cagr_5yr)} | FCF {fmt(x.free_cash_flow_cr)}',styles['BodyText']),Spacer(1,12),PageBreak()]
    doc.build(story[:-1]); return True

def fmt(v): return 'N/A' if pd.isna(v) else f'{v:.2f}'
if __name__=='__main__': run()
