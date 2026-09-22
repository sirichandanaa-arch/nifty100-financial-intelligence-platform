from src.analytics.cashflow_kpis import build as cashflow
from src.reports.peer_report import build as peer
from src.reports.docs import build as docs

def main():
    """Generate remaining final output artifacts."""
    cashflow(); peer(); docs()
if __name__=='__main__': main()
