#!/usr/bin/env python3
"""Create a static-site ZIP with index.html AT ZIP ROOT (no backend/secret files)."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'ShareBite_Amplify_UPLOAD.zip'
PAGE_NAMES={p+'.html' for p in ('connection-check','index','browse','food-details','dashboard','add-food','my-listings','messages','profile','login','register','confirm-account','forgot-password','reset-password','how-it-works','privacy','faq')}
files=[p for p in ROOT.iterdir() if p.is_file() and p.name in PAGE_NAMES]
files += [p for group in ('assets','css') for p in (ROOT/group).rglob('*') if p.is_file()]
files += [ROOT/'js'/'config.js',ROOT/'js'/'sharebite.bundle.js']
assert "mode: 'live'" in (ROOT/'js'/'config.js').read_text() or '"mode": "live"' in (ROOT/'js'/'config.js').read_text(), 'Refusing to package DEMO mode for Amplify. Run tools/set_mode.py live.'
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(ROOT).as_posix())
with ZipFile(OUT) as z: assert z.namelist().count('index.html')==1
print('Amplify static-site ZIP:',OUT,'(',len(files),'files; index.html at root)')
