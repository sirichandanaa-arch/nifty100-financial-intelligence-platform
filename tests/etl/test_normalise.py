import pytest
from src.etl.normaliser import normalize_ticker,normalize_year
@pytest.mark.parametrize('x,e',[(' TCS ','TCS'),('tcs','TCS'),('INFY','INFY'),(' hdfcbank ','HDFCBANK'),('RELIANCE','RELIANCE'),('itc','ITC'),('  ABB  ','ABB'),('aPi','API'),('',''),(None,'')])
def test_ticker(x,e): assert normalize_ticker(x)==e
@pytest.mark.parametrize('x',[('Mar-23'),('2023-03'),('2023/03'),('Mar 2023'),('2024'),('2020-21'),('FY2023'),('Apr-24'),('Dec-22'),('Jan-21')])
def test_year(x): assert normalize_year(x) is not None
