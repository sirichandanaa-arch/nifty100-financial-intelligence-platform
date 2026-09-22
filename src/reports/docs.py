"""Generate analyst guide and acceptance checklist PDFs."""
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from src.common import DOCS_DIR, OUTPUT_DIR
import pandas as pd

def build():
    """Generate the analyst guide and populated acceptance checklist PDFs."""
    styles=getSampleStyleSheet(); DOCS_DIR.mkdir(exist_ok=True)
    sections=['Project Overview','Installation','ETL Data Load','Financial Ratios','Screener','Peer Comparison','Valuation','Cash Flow Intelligence','NLP Pros and Cons','Clustering','Streamlit Dashboard','FastAPI Server','PDF Reports','Testing','Acceptance Gates','Troubleshooting','Data Definitions','Simulated Data Notice','Reproducibility','Final Submission']
    doc=SimpleDocTemplate(str(DOCS_DIR/'analyst_guide.pdf'),pagesize=A4); story=[]
    for s in sections:
        story += [Paragraph(s,styles['Title']),Spacer(1,8),Paragraph('Use the project commands and generated outputs for this module. All monetary values are INR Crore. The supplied market-cap and stock-price datasets are treated as SIMULATED as required by the project specification. Review generated CSV/XLSX/PDF artifacts after running the pipeline.',styles['BodyText']),Spacer(1,20),PageBreak()]
    doc.build(story)
    rows=[]; p=OUTPUT_DIR/'acceptance_results.csv'
    if p.exists(): rows=pd.read_csv(p).to_dict('records')
    ac=SimpleDocTemplate(str(DOCS_DIR/'acceptance_checklist.pdf'),pagesize=A4); st=[Paragraph('Nifty 100 Analytics — Acceptance Checklist',styles['Title']),Spacer(1,12)]
    for x in rows:
        st.append(Paragraph(f"{x['gate']}: <b>{x['status']}</b> — {x['detail']}",styles['BodyText'])); st.append(Spacer(1,7))
    st += [Spacer(1,20),Paragraph('Team Lead Sign-off: ____________________    Date: ____________________',styles['BodyText'])]; ac.build(st)
