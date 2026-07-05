from pathlib import Path
import zipfile
import tempfile
import shutil
from utils.extractor import SecureZipExtractor
from utils.file_detection import IGNORED_DIRS, IGNORED_EXTENSIONS, ALLOWED_EXTENSIONS

print('IGNORED_DIRS', IGNORED_DIRS)
print('IGNORED_EXTENSIONS', IGNORED_EXTENSIONS)
print('ALLOWED_EXTENSIONS contains .pyc', '.pyc' in ALLOWED_EXTENSIONS)

with tempfile.TemporaryDirectory() as tmp:
    archive = Path(tmp) / 'repo.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('repo/app.py', 'print("hello")\n')
        z.writestr('repo/__pycache__/main.cpython-313.pyc', b'\x03\xf3\r\n')
        z.writestr('repo/README.md', '# Test\n')
    try:
        extracted = SecureZipExtractor(max_size_mb=1).extract(archive)
        print('EXTRACT SUCCESS', extracted)
        print('PYCC EXISTS', (Path(extracted) / 'repo' / '__pycache__' / 'main.cpython-313.pyc').exists())
        print('FILES', [p.as_posix() for p in Path(extracted).rglob('*') if p.is_file()])
    except Exception as e:
        print('EXTRACT FAILED', type(e).__name__, str(e))
