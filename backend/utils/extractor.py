"""Secure ZIP extraction utilities."""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable

from config import get_settings
from utils.exceptions import UploadValidationError
from utils.file_detection import ALLOWED_EXTENSIONS, CONFIG_NAMES, IGNORED_DIRS, IGNORED_EXTENSIONS


class SecureZipExtractor:
    """Validate and extract ZIP repositories safely."""

    def __init__(self, max_size_mb: int | None = None) -> None:
        """Create an extractor."""

        settings = get_settings()
        self.max_size_bytes = (max_size_mb or settings.max_zip_size_mb) * 1024 * 1024

    def extract(self, archive_path: Path) -> Path:
        """Extract an archive into an isolated temporary directory.

        Args:
            archive_path: Path to an uploaded ZIP file.

        Returns:
            Temporary directory containing extracted files.

        Raises:
            UploadValidationError: When archive safety checks fail.
        """

        if archive_path.stat().st_size > self.max_size_bytes:
            raise UploadValidationError("ZIP file exceeds maximum size")
        if not zipfile.is_zipfile(archive_path):
            raise UploadValidationError("Uploaded file is not a valid ZIP archive")

        target_dir = Path(tempfile.mkdtemp(prefix="cip_repo_")).resolve()
        try:
            with zipfile.ZipFile(archive_path) as archive:
                bad_member = archive.testzip()
                if bad_member:
                    raise UploadValidationError(f"Corrupt ZIP member: {bad_member}")
                allowed_members = self._validate_members(archive.infolist(), target_dir)
                archive.extractall(target_dir, members=allowed_members)
        except Exception:
            shutil.rmtree(target_dir, ignore_errors=True)
            raise
        return target_dir

    def cleanup(self, path: Path) -> None:
        """Delete a temporary extraction directory."""

        shutil.rmtree(path, ignore_errors=True)

    def _validate_members(self, members: Iterable[zipfile.ZipInfo], target_dir: Path) -> list[zipfile.ZipInfo]:
        total_size = 0
        allowed = []
        for member in members:
            member_path = (target_dir / member.filename).resolve()
            if not str(member_path).startswith(str(target_dir)):
                raise UploadValidationError("ZIP contains unsafe path traversal")
            total_size += member.file_size
            if total_size > self.max_size_bytes:
                raise UploadValidationError("Uncompressed repository exceeds maximum size")
            if member.filename.endswith("/"):
                allowed.append(member)
                continue
            path = Path(member.filename)
            suffix = path.suffix.lower()
            name = path.name.lower()
            if any(part in IGNORED_DIRS for part in path.parts):
                continue
            if suffix in IGNORED_EXTENSIONS:
                continue
            if suffix and suffix not in ALLOWED_EXTENSIONS:
                continue
            if not suffix and name not in CONFIG_NAMES and name not in {"readme", "license"}:
                continue
            allowed.append(member)
        return allowed
