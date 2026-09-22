import pytest
from src.analytics.cagr import cagr
from src.analytics.cashflow_kpis import cfo_quality,capex_intensity,allocation_pattern,fcf
@pytest.mark.parametrize('start,end,years,flag',[ (100,121,2,None),(100,110,1,None),(10,20,2,None),(0,10,5,'ZERO_BASE'),(-10,10,5,'TURNAROUND'),(10,-10,5,'DECLINE_TO_LOSS'),(-10,-5,5,'BOTH_NEGATIVE') ])
def test_cagr_cases(start,end,years,flag): assert cagr(start,end,years)[1]==flag
@pytest.mark.parametrize('x,y',[ (100,110),(200,250),(50,75),(1000,1200),(10,15),(1,2),(5,5),(80,90),(30,45),(400,600) ])
def test_cagr_positive(x,y): assert cagr(x,y,1)[0]==pytest.approx((y/x-1)*100)
@pytest.mark.parametrize('vals,expected',[([1.2,1.1], 'High Quality'),([.6,.7],'Moderate'),([.1,.3],'Accrual Risk')])
def test_cfo_quality(vals,expected): assert cfo_quality(vals)[1]==expected
@pytest.mark.parametrize('inv,sales,lab',[(10,1000,'Asset Light'),(50,1000,'Moderate'),(100,1000,'Capital Intensive')])
def test_capex(inv,sales,lab): assert capex_intensity(inv,sales)[1]==lab
@pytest.mark.parametrize('a,b,c,lab',[(1,-1,-1,'Reinvestor'),(1,-1,1,'Mixed'),(1,1,-1,'Liquidating Assets'),(-1,1,1,'Distress Signal'),(-1,-1,1,'Growth Funded by Debt'),(1,1,1,'Cash Accumulator'),(-1,-1,-1,'Pre-Revenue')])
def test_allocation(a,b,c,lab): assert allocation_pattern(a,b,c)==lab
@pytest.mark.parametrize('a,b,e',[(10,-3,7),(0,0,0),(100,-50,50),(-1,-2,-3),(20,-10,10)])
def test_fcf(a,b,e): assert fcf(a,b)==e
