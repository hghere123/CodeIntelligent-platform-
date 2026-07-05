"""SQLite persistence for analysis results."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import List

from models.graph import AnalysisResult
from utils.exceptions import NotFoundError


class AnalysisStore:
    """Persist and load analysis results as JSON documents."""

    def __init__(self, database_path: Path) -> None:
        """Initialize storage."""

        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def save(self, result: AnalysisResult) -> None:
        """Save an analysis result."""

        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO analyses (id, repository_name, payload)
                VALUES (?, ?, ?)
                """,
                (result.analysis_id, result.repository_name, result.model_dump_json()),
            )
            connection.commit()

    def get(self, analysis_id: str) -> AnalysisResult:
        """Load an analysis result."""

        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute("SELECT payload FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        if not row:
            raise NotFoundError(f"Analysis not found: {analysis_id}")
        return AnalysisResult.model_validate(json.loads(row[0]))

    def list_ids(self) -> List[str]:
        """Return stored analysis identifiers."""

        with sqlite3.connect(self.database_path) as connection:
            rows = connection.execute("SELECT id FROM analyses ORDER BY created_at DESC").fetchall()
        return [row[0] for row in rows]

    def _init_db(self) -> None:
        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    repository_name TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.commit()

