"""Download the supplied ValidStep source files into source/."""
from pathlib import Path
import urllib.request
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'source'
URLS={
'financial_ratios.xlsx':'https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501620089-fb3ae469-financial_ratios.xlsx',
'market_cap.xlsx':'https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501620397-69ae3e7f-market_cap.xlsx',
'peer_groups.xlsx':'https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501620796-5060f580-peer_groups.xlsx',
'sectors.xlsx':'https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501621129-8684701e-sectors.xlsx',
'stock_prices.xlsx':'https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501621395-a51977cd-stock_prices.xlsx',
'Nifty100_Project_Document_FINAL.pdf':'https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501606810-ee37de07-Nifty100_Project_Document_FINAL.pdf',
'analysis.xlsx':'https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501604303-57986a9b-analysis.xlsx',
'prosandcons.xlsx':'https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501607452-d6bbe55b-prosandcons.xlsx',
'profitandloss.xlsx':'https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501607124-aad40f4f-profitandloss.xlsx',
'balancesheet.xlsx':'https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501604829-ac8c0874-balancesheet.xlsx',
'cashflow.xlsx':'https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501605758-8e951681-cashflow.xlsx',
'companies.xlsx':'https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501606103-7177b6c2-companies.xlsx',
'documents.xlsx':'https://assets.validstep.com/workspace/shared-datasets/e32cc66a-109c-41fc-8446-1ea55d626543/1788501606362-ba899c04-documents.xlsx'}
for name,url in URLS.items():
    path=OUT/name
    if path.exists() and path.stat().st_size>0: continue
    print('Downloading',name)
    urllib.request.urlretrieve(url,path)
print('Source download complete.')
