import pytest
from src.analytics.cagr import cagr
from src.analytics.cashflow_kpis import capex_intensity,cfo_quality,allocation_pattern
@pytest.mark.parametrize('n',range(30))
def test_repeated_formula_smoke(n):
    assert cagr(100,100+n,1)[0]==pytest.approx(float(n))
