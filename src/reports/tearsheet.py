"""Two-page company tearsheet PDF generator."""
import sqlite3, pandas as pd, matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from src.common import DB_PATH, REPORT_DIR

def make_tearsheet(ticker,outfile):
    """Generate a two-page PDF tearsheet for one ticker."""
    conn=sqlite3.connect(DB_PATH); c=pd.read_sql_query('SELECT * FROM companies WHERE company_id=?',conn,params=(ticker,)); r=pd.read_sql_query('SELECT * FROM financial_ratios WHERE company_id=? ORDER BY year',conn,params=(ticker,)); p=pd.read_sql_query('SELECT * FROM profitandloss WHERE company_id=? ORDER BY year',conn,params=(ticker,)); b=pd.read_sql_query('SELECT * FROM balancesheet WHERE company_id=? ORDER BY year',conn,params=(ticker,)); cf=pd.read_sql_query('SELECT * FROM cashflow WHERE company_id=? ORDER BY year',conn,params=(ticker,)); pc=pd.read_sql_query('SELECT * FROM prosandcons_generated WHERE company_id=?',conn,params=(ticker,)); conn.close();
    name=c.iloc[0].company_name if not c.empty else ticker; styles=getSampleStyleSheet(); doc=SimpleDocTemplate(str(outfile),pagesize=A4,rightMargin=28,leftMargin=28,topMargin=28,bottomMargin=28); story=[Paragraph(f'<b>{name}</b> — {ticker}',styles['Title']),Spacer(1,10)]
    if not r.empty:
        q=r.iloc[-1]; data=[["ROE","ROCE","NPM"],[f"{q.return_on_equity_pct:.1f}%" if pd.notna(q.return_on_equity_pct) else 'N/A',f"{q.return_on_capital_employed_pct:.1f}%" if pd.notna(q.return_on_capital_employed_pct) else 'N/A',f"{q.net_profit_margin_pct:.1f}%" if pd.notna(q.net_profit_margin_pct) else 'N/A'],["D/E","5Y Rev CAGR","FCF"],[f"{q.debt_to_equity:.2f}" if pd.notna(q.debt_to_equity) else 'N/A',f"{q.revenue_cagr_5yr:.1f}%" if pd.notna(q.revenue_cagr_5yr) else 'N/A',f"{q.free_cash_flow_cr:.0f} Cr" if pd.notna(q.free_cash_flow_cr) else 'N/A']]; t=Table(data,colWidths=[170]*3); t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.4,colors.grey),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#d9e2f3')),('BACKGROUND',(0,2),(-1,2),colors.HexColor('#d9e2f3')),('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE')])); story += [t,Spacer(1,12)]
    if not p.empty:
        fig,ax=plt.subplots(figsize=(7.2,3.2)); ax.bar(p.year.astype(str),p.sales,label='Revenue'); ax.plot(p.year.astype(str),p.net_profit,marker='o',label='Net Profit'); ax.tick_params(axis='x',rotation=60,labelsize=6); ax.legend(); fig.tight_layout(); img=str(outfile).replace('.pdf','_trend.png'); fig.savefig(img,dpi=220); plt.close(fig); story += [Image(img,width=520,height=230)]
    story += [PageBreak(),Paragraph('<b>Balance Sheet & Cash Flow</b>',styles['Heading2']),Spacer(1,8)]
    if not b.empty: story.append(Table([["Year","Equity","Borrowings","Assets"]]+[[str(x.year),f'{x.equity_capital:.0f}',f'{x.borrowings:.0f}',f'{x.total_assets:.0f}'] for _,x in b.tail(10).iterrows()],colWidths=[100,100,100,100],repeatRows=1,style=TableStyle([('GRID',(0,0),(-1,-1),.3,colors.grey),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#d9e2f3'))]))); story.append(Spacer(1,10))
    if not cf.empty: x=cf.iloc[-1]; story.append(Paragraph(f"Latest cash flow — CFO: {x.operating_activity:.0f} Cr; CFI: {x.investing_activity:.0f} Cr; CFF: {x.financing_activity:.0f} Cr; Net: {x.net_cash_flow:.0f} Cr",styles['BodyText']))
    story += [Spacer(1,10),Paragraph('<b>Pros</b>',styles['Heading2'])]
    pros=pc[pc.type=='pro'].text.tolist() if not pc.empty else ['No generated positive signal available.']; story += [Paragraph('• '+x,styles['BodyText']) for x in pros[:6]]+[Paragraph('<b>Cons</b>',styles['Heading2'])]
    cons=pc[pc.type=='con'].text.tolist() if not pc.empty else ['No generated caution signal available.']; story += [Paragraph('• '+x,styles['BodyText']) for x in cons[:6]]
    doc.build(story)

def build_all():
    """Generate company tearsheets for all companies."""
    out=REPORT_DIR/'tearsheets'; out.mkdir(parents=True,exist_ok=True); conn=sqlite3.connect(DB_PATH); ids=pd.read_sql_query('SELECT company_id FROM companies',conn).company_id.tolist(); conn.close()
    for cid in ids: make_tearsheet(cid,out/f'{cid}_tearsheet.pdf')
    return len(ids)
