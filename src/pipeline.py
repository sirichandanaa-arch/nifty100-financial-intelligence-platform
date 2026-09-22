"""End-to-end reproducible pipeline."""
from src.etl.loader import load
from src.etl.validator import validate
from src.analytics.ratios import build as ratios
from src.analytics.valuation import build as valuation
from src.screener.engine import run_presets
from src.analytics.peer import build as peer
from src.analytics.clustering import build as cluster
from src.nlp.parser import build as parser
from src.nlp.pros_cons_generator import build as proscons
from src.analytics.cashflow_kpis import build as cashflow
from src.reports.generate_all import run as reports
from src.api.export_openapi import main as openapi
from src.reports.docs import build as docs

def main():
    """Execute all data, analytics, reporting and API generation steps."""
    load(); validate(); ratios(); valuation(); run_presets(); peer(); cluster(); parser(); proscons(); cashflow(); reports(); openapi(); docs()
if __name__=='__main__': main()
