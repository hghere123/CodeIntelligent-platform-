import zipfile
from pathlib import Path

z = zipfile.ZipFile('scrapy-master.zip')
ext_names = set()
for info in z.infolist():
    name = info.filename
    if name.endswith('/'):
        continue
    p = Path(name)
    if p.suffix == '':
        next_names.add(p.name)
print('\n'.join(sorted(next_names)))
