# Portable project root: set NORP_ROOT to override when invoked outside the repository.
from pathlib import Path as _Path
import os as _os
PROJECT_ROOT = _Path(_os.environ.get('NORP_ROOT', _Path(__file__).resolve().parents[1]))

import re,html
from pathlib import Path
s=html.unescape(Path(str(PROJECT_ROOT / 'hfcb_investor_relations.html')).read_text(errors='ignore'))
for m in re.finditer(r'[^"\\]{0,180}\.pdf',s,re.I):
 seg=s[max(0,m.start()-180):min(len(s),m.end()+80)].replace('\\n',' ').replace('\\"','"')
 if any(k in seg.lower() for k in ['annual','financial','result','q1','q2','q3','q4','h1','h2','interim']):print(seg)
