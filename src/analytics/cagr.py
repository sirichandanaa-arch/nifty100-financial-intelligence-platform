"""CAGR calculations with explicit edge-case flags."""

def cagr(start,end,years):
    """Return (CAGR percentage, edge-case flag)."""
    if years<=0 or start is None or end is None: return (None,'INSUFFICIENT')
    if start==0: return (None,'ZERO_BASE')
    if start>0 and end>0: return (((end/start)**(1/years)-1)*100,None)
    if start>0 and end<0: return (None,'DECLINE_TO_LOSS')
    if start<0 and end>0: return (None,'TURNAROUND')
    if start<0 and end<0: return (None,'BOTH_NEGATIVE')
    return (None,'INSUFFICIENT')

def cagr_with_flag(start,end,years,available=True):
    """Return (value, flag) for the six documented CAGR edge cases."""
    if not available: return None,'INSUFFICIENT'
    if start is None or end is None: return None,'INSUFFICIENT'
    if start==0: return None,'ZERO_BASE'
    if start>0 and end>0: return cagr(start,end,years)
    if start>0 and end<0: return None,'DECLINE_TO_LOSS'
    if start<0 and end>0: return None,'TURNAROUND'
    return None,'BOTH_NEGATIVE'
