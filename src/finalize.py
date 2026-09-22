"""Archive the final project outputs."""
import shutil
from src.common import ROOT,DB_PATH,OUTPUT_DIR,REPORT_DIR,DOCS_DIR
from src.acceptance import run

def main():
    """Run acceptance audit and archive the final submission artifacts."""
    results=run(); archive=OUTPUT_DIR/'final_deliverables'
    if archive.exists(): shutil.rmtree(archive)
    archive.mkdir(parents=True)
    # Keep a flat, submission-friendly archive without recursively copying the archive into itself.
    for src in [DB_PATH, OUTPUT_DIR/'load_audit.csv',OUTPUT_DIR/'validation_failures.csv',OUTPUT_DIR/'capital_allocation.csv',OUTPUT_DIR/'screener_output.xlsx',OUTPUT_DIR/'screener_output.csv',OUTPUT_DIR/'peer_comparison.xlsx',OUTPUT_DIR/'valuation_summary.xlsx',OUTPUT_DIR/'valuation_flags.csv',OUTPUT_DIR/'cashflow_intelligence.xlsx',OUTPUT_DIR/'pros_cons_generated.csv',OUTPUT_DIR/'analysis_parsed.csv',OUTPUT_DIR/'cluster_labels.csv',OUTPUT_DIR/'distress_alerts.csv',OUTPUT_DIR/'outlier_report.csv',OUTPUT_DIR/'portfolio_stats.csv',REPORT_DIR/'pytest_report.html',REPORT_DIR/'elbow_plot.png',REPORT_DIR/'correlation_heatmap.png',DOCS_DIR/'openapi.json',DOCS_DIR/'analyst_guide.pdf',DOCS_DIR/'acceptance_checklist.pdf']:
        if src.exists():
            dest=archive/src.name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dest)
    for dirname in ['tearsheets','sector','portfolio','radar_charts']:
        src=REPORT_DIR/dirname
        if src.exists(): shutil.copytree(src,archive/dirname)
    return archive
if __name__=='__main__': print(main())
