"""Repository analysis pipeline."""

from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

from analyzers import analyzer_for_extension
from models.graph import AnalysisResult, AnalysisSummary, CompareResult, FileAnalysis, RepositoryTreeNode
from utils.detector import ConfigurationAnalyzer
from utils.extractor import SecureZipExtractor
from utils.file_detection import detect_language, is_config_file, iter_repository_files, read_text, repository_tree
from utils.relationships import aggregate_metrics, build_graph, export_mermaid
from utils.storage import AnalysisStore


class AnalysisPipeline:
    """Coordinates upload validation, extraction, analysis, and storage."""

    def __init__(self, store: AnalysisStore) -> None:
        """Create a pipeline."""

        self.store = store
        self.extractor = SecureZipExtractor()
        self.config_analyzer = ConfigurationAnalyzer()

    async def analyze_zip(self, upload_name: str, content: bytes) -> AnalysisResult:
        """Analyze an uploaded ZIP archive."""

        temp_fd, temp_name = tempfile.mkstemp(prefix="cip_upload_", suffix=".zip")
        temp_zip = Path(temp_name)
        os.close(temp_fd)
        temp_zip.write_bytes(content)
        extracted_dir: Path | None = None
        try:
            extracted_dir = self.extractor.extract(temp_zip)
            result = self.analyze_directory(extracted_dir, Path(upload_name).stem)
            self.store.save(result)
            return result
        finally:
            temp_zip.unlink(missing_ok=True)
            if extracted_dir:
                self.extractor.cleanup(extracted_dir)

    def analyze_directory(self, root: Path, repository_name: str) -> AnalysisResult:
        """Analyze an extracted repository directory."""

        logger.info("Starting analysis for {}", repository_name)
        files: List[FileAnalysis] = []
        dependencies: List[str] = []
        content_blobs: List[str] = []

        actual_root = self._normalize_root(root)
        for path in iter_repository_files(actual_root):
            relative_path = path.relative_to(actual_root).as_posix()
            content = read_text(path)
            content_blobs.append(content[:50_000])
            analyzer = analyzer_for_extension(path.suffix.lower())
            if analyzer:
                files.append(analyzer.analyze(relative_path, content))
            elif is_config_file(path):
                facts = self._safe_config(path, content)
                dependencies.extend(facts.get("dependencies", []))
                files.append(
                    FileAnalysis(
                        file_path=relative_path,
                        language="config",
                        metrics={"loc": len(content.splitlines())},
                    )
                )

        detected = self.config_analyzer.detect(dependencies, content_blobs)
        graph = build_graph(files, detected)
        metrics = aggregate_metrics(files, graph)
        tree = RepositoryTreeNode.model_validate(repository_tree(actual_root))
        analysis_id = str(uuid.uuid4())
        summary = AnalysisSummary(
            analysis_id=analysis_id,
            repository_name=repository_name,
            files_count=len(files),
            languages=metrics.languages,
            frameworks=detected.get("frameworks", []),
            metrics=metrics,
        )
        return AnalysisResult(
            analysis_id=analysis_id,
            repository_name=repository_name,
            graph=graph,
            tree=tree,
            files=files,
            metrics=metrics,
            detected=detected,
            summary=summary,
        )

    def compare(self, left_analysis_id: str, right_analysis_id: str) -> CompareResult:
        """Compare two stored analyses."""

        left = self.store.get(left_analysis_id)
        right = self.store.get(right_analysis_id)
        left_nodes = {node.name for node in left.graph.nodes}
        right_nodes = {node.name for node in right.graph.nodes}
        return CompareResult(
            left_analysis_id=left_analysis_id,
            right_analysis_id=right_analysis_id,
            added_nodes=sorted(right_nodes - left_nodes),
            removed_nodes=sorted(left_nodes - right_nodes),
            shared_nodes=sorted(left_nodes & right_nodes),
            metric_delta={
                "loc": right.metrics.loc - left.metrics.loc,
                "functions": right.metrics.functions - left.metrics.functions,
                "classes": right.metrics.classes - left.metrics.classes,
            },
        )

    def mermaid(self, analysis_id: str) -> str:
        """Export a stored analysis as Mermaid."""

        return export_mermaid(self.store.get(analysis_id).graph)

    def search(self, analysis_id: str, query: str) -> List[Dict[str, Any]]:
        """Search graph entities using case-insensitive substring matching."""

        result = self.store.get(analysis_id)
        needle = query.lower()
        matches = []
        for node in result.graph.nodes:
            haystack = f"{node.name} {node.type.value} {node.file_path} {node.metadata}".lower()
            if needle in haystack:
                matches.append(node.model_dump())
        return matches

    def _safe_config(self, path: Path, content: str) -> Dict[str, Any]:
        try:
            return self.config_analyzer.analyze_file(path, content)
        except Exception as exc:
            logger.warning("Failed to parse config {}: {}", path, exc)
            return {"dependencies": []}

    def _normalize_root(self, root: Path) -> Path:
        children = [child for child in root.iterdir() if child.name not in {"__MACOSX"}]
        if len(children) == 1 and children[0].is_dir():
            return children[0]
        return root
