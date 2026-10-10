"""Fail on common credential patterns or tracked private storage, without printing values."""
from pathlib import Path
import re,subprocess
root=Path(__file__).resolve().parent.parent
paths=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0')
patterns=[re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(r'AKIA[A-Z0-9]{16}')]
failures=[]
for name in filter(None,paths):
 p=root/name
 if name.split('/')[0] in {'data','private','backups','uploads','exports'} or p.suffix in {'.pkm','.pem','.key','.sqlite','.db'} or p.name=='.env' or re.match(r'PKM-(?:lager|dubletter|mangler|samling|backup)-',p.name):failures.append(name+': private file tracked')
 if not p.is_file():continue
 try:text=p.read_text()
 except UnicodeError:continue
 if any(pattern.search(text) for pattern in patterns):failures.append(name+': possible credential')
if failures:raise SystemExit('\n'.join(failures))
print('PASS: tracked-file credential and private-storage checks')
