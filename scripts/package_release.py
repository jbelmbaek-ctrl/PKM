"""Package only reviewed distributable files; never browser data or backups."""
from pathlib import Path
import csv,hashlib,zipfile
root=Path(__file__).resolve().parent.parent
out=root/'downloads'
source=out/'Cardmarket-SV7.csv'
with source.open(encoding='utf-8-sig',newline='') as f:
 rows=list(csv.DictReader(f,delimiter=';'))
 assert len(rows)==135
 assert set(rows[0])=={'setkode','kortnummer','version','cardmarket_url'}
 assert all(r['setkode']=='SV7' and r['kortnummer'].isdigit() and r['version'].lower() in ['normal','holo'] and r['cardmarket_url'].startswith('https://www.cardmarket.com/en/Pokemon/Products/Singles/') for r in rows)
files={'PKM-UI-V2.2.html':root/'dist/PKM-UI-V2.2.html','Cardmarket-SV7.csv':source,'LAES-MIG.txt':out/'LAES-MIG.txt'}
with zipfile.ZipFile(out/'PKM-v2.2.0.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for name,path in files.items():
  info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,path.read_bytes())
(out/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in [root/'dist/PKM-UI-V2.2.html',source,out/'LAES-MIG.txt',out/'PKM-v2.2.0.zip']))
print('Validated 135 public Cardmarket links; built downloadable ZIP and SHA-256 manifest')
