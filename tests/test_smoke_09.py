from src.common import norm_ticker,norm_year
def test_ticker_9(): assert norm_ticker(" abc ")=="ABC"
def test_year_9(): assert norm_year("Mar 2024")=="2024-03"
