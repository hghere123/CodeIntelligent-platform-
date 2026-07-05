"""Secure ZIP extractor tests."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from utils.exceptions import UploadValidationError
from utils.extractor import SecureZipExtractor


def test_extractor_rejects_path_traversal(tmp_path: Path) -> None:
    """Extractor blocks ZIP path traversal."""

    archive = tmp_path / "bad.zip"
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.writestr("../evil.py", "print('bad')")
    with pytest.raises(UploadValidationError):
        SecureZipExtractor(max_size_mb=1).extract(archive)


def test_extractor_accepts_safe_source(tmp_path: Path) -> None:
    """Extractor accepts normal source archives."""

    archive = tmp_path / "repo.zip"
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.writestr("repo/app.py", "def main():\n    return 1\n")
    extractor = SecureZipExtractor(max_size_mb=1)
    extracted = extractor.extract(archive)
    try:
        assert (extracted / "repo" / "app.py").exists()
    finally:
        extractor.cleanup(extracted)


def test_extractor_ignores_unknown_files(tmp_path: Path) -> None:
    """Extractor ignores files that are not explicitly allowed."""

    archive = tmp_path / "repo.zip"
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.writestr("repo/app.py", "def main():\n    return 1\n")
        zip_file.writestr("repo/unknown.bin", b"\x00\x01\x02")
        zip_file.writestr("repo/extra.foo", "not allowed")
    extractor = SecureZipExtractor(max_size_mb=1)
    extracted = extractor.extract(archive)
    try:
        assert (extracted / "repo" / "app.py").exists()
        assert not (extracted / "repo" / "unknown.bin").exists()
        assert not (extracted / "repo" / "extra.foo").exists()
    finally:
        extractor.cleanup(extracted)

