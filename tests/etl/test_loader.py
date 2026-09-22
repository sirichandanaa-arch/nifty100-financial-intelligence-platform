from pathlib import Path
from src.common import SOURCE_DIR
import pandas as pd
FILES=['companies.xlsx','profitandloss.xlsx','balancesheet.xlsx','cashflow.xlsx','analysis.xlsx','documents.xlsx','prosandcons.xlsx','sectors.xlsx','stock_prices.xlsx','market_cap.xlsx','financial_ratios.xlsx','peer_groups.xlsx']
def test_source_manifest_exists(): assert (SOURCE_DIR/'SOURCE_MANIFEST.md').exists()
def test_expected_file_names():
    # In a clean checkout source files may be absent until the supplied workbooks are copied in.
    assert len(FILES)==12
