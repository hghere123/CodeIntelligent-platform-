import zipfile
from pathlib import Path

archive = Path('test_repo.zip')
with zipfile.ZipFile(archive, 'w') as z:
    z.writestr('repo/app.py', 'from fastapi import FastAPI\napp = FastAPI()\n\n@app.get("/hello")\ndef hello():\n    return {"hello": "world"}\n')
    z.writestr('repo/requirements.txt', 'fastapi\nuvicorn\n')
    z.writestr('repo/README.md', '# Test Repo\nThis is a test repository for upload.\n')
    z.writestr('repo/__pycache__/main.cpython-313.pyc', b'\x03\xf3\r\n')
    z.writestr('repo/node_modules/lib/index.js', 'console.log("hi")\n')
print('CREATED', archive.resolve())
