from src.analytics.cagr import cagr_with_flag
from src.analytics.ratios import pattern_label

def test_cagr_positive(): assert round(cagr_with_flag(100,121,2)[0],1)==10.0
def test_cagr_turnaround(): assert cagr_with_flag(-10,20,5)[1]=='TURNAROUND'
def test_cagr_decline_loss(): assert cagr_with_flag(10,-2,5)[1]=='DECLINE_TO_LOSS'
def test_cagr_both_negative(): assert cagr_with_flag(-10,-2,5)[1]=='BOTH_NEGATIVE'
def test_cagr_zero(): assert cagr_with_flag(0,10,5)[1]=='ZERO_BASE'
def test_cagr_insufficient(): assert cagr_with_flag(1,2,5,False)[1]=='INSUFFICIENT'
def test_reinvestor(): assert pattern_label(10,-5,-2)=='Reinvestor'
def test_cash_accumulator(): assert pattern_label(10,2,3)=='Cash Accumulator'
def test_distress(): assert pattern_label(-1,2,3)=='Distress Signal'
def test_debt_growth(): assert pattern_label(-1,-2,3)=='Growth Funded by Debt'
