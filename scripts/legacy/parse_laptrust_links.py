# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import csv,re
records=[
 {'title':'LAPTRUST IMARA I-REIT 2024 Annual Report','url':'https://laptrustimaraireit.co.ke/wp-content/uploads/2025/03/LAPTRUST-IMARA-I-REIT-2024-Annual-report.pdf','source_page':'https://laptrustimaraireit.co.ke/integrated-annual-reports/'},
 {'title':'LAPTRUST IMARA I-REIT 2023 Annual Report','url':'https://laptrustimaraireit.co.ke/wp-content/uploads/2024/05/LAPTRUST-IMARA-I-REIT-2023-Annual-Report-compressed.pdf','source_page':'https://laptrustimaraireit.co.ke/integrated-annual-reports/'},
 {'title':'2025 Semi-Annual Report — LAPTRUST IMARA I-REIT','url':'https://laptrustimaraireit.co.ke/wp-content/uploads/2025/07/Semi-Annual-Report-2025-LAPTRUST-IMARA-I-REIT.pdf','source_page':'https://laptrustimaraireit.co.ke/semi-annual-reports/'},
 {'title':'2024 Semi-Annual Report — LAPTRUST IMARA I-REIT','url':'https://laptrustimaraireit.co.ke/wp-content/uploads/2024/07/2024-LAPTRUST-Imara-I-REIT-Semi-Annual-Report.pdf','source_page':'https://laptrustimaraireit.co.ke/semi-annual-reports/'},
 {'title':'2023 Semi-Annual Report — LAPTRUST IMARA I-REIT','url':'https://laptrustimaraireit.co.ke/wp-content/uploads/2023/07/2023-Semi-Annual-Report-LAPTRUST-Imara-I-REIT-Final.pdf','source_page':'https://laptrustimaraireit.co.ke/semi-annual-reports/'},
 {'title':'LAPTRUST IMARA I-REIT H1 2023 Financial Statements','url':'https://laptrustimaraireit.co.ke/wp-content/uploads/2023/08/LAPTRUST-IMARA-I-REIT-H1-2023.pdf','source_page':'https://laptrustimaraireit.co.ke/semi-annual-reports/'},
]
for r in records:r.update(filename=r['url'].rsplit('/',1)[-1])
with open(str(PROJECT_ROOT / 'laptrust_report_links.csv'),'w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['title','url','filename','source_page']);w.writeheader();w.writerows(records)
print('records',len(records))
for r in records:print(r)
