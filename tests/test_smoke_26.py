from src.common import norm_ticker,norm_year
def test_ticker_26(): assert norm_ticker(" abc ")=="ABC"
def test_year_26(): assert norm_year("Mar 2024")=="2024-03"
