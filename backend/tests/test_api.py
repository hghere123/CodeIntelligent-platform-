"""API integration tests."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from config import get_settings
from main import app


def test_upload_and_fetch_analysis(tmp_path: Path, monkeypatch) -> None:
    """Upload endpoint stores an analysis retrievable by API."""

    settings = get_settings()
    monkeypatch.setattr(settings, "database_path", tmp_path / "analysis.db")
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.writestr("repo/app.py", "from fastapi import FastAPI\napp = FastAPI()\ndef health():\n    return 'ok'\n")
        zip_file.writestr("repo/package.json", '{"dependencies":{"react":"latest"}}')
    archive.seek(0)

    client = TestClient(app)
    response = client.post("/api/upload", files={"file": ("repo.zip", archive.getvalue(), "application/zip")})
    assert response.status_code == 200
    analysis_id = response.json()["analysis_id"]
    graph_response = client.get(f"/api/analysis/{analysis_id}/graph")
    assert graph_response.status_code == 200
    assert graph_response.json()["nodes"]

