#!/usr/bin/env python3
"""Change ONLY mode for offline demo / AWS-live testing; never edit cloud IDs."""
from pathlib import Path
import sys,re
p=Path(__file__).resolve().parents[1]/'js'/'config.js'
mode=sys.argv[1] if len(sys.argv)==2 else ''
if mode not in ('live','demo'):
    raise SystemExit('Usage: python tools/set_mode.py live|demo')
s=p.read_text()
s,n=re.subn(r"mode:\s*['\"](?:live|demo)['\"]", "mode: '"+mode+"'", s,count=1)
if n!=1:raise SystemExit('No recognizable mode setting; file unchanged.')
p.write_text(s)
print('Mode:',mode,'\nIMPORTANT: use live before publishing or sharing the website.')
