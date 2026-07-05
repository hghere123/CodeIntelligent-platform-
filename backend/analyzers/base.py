"""Base analyzer interfaces and shared helpers."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Optional

from models.graph import CodeMetrics, Entity, EntityType, FileAnalysis


class BaseAnalyzer(ABC):
    """Language analyzer plugin contract."""

    language: str
    extensions: List[str]

    @abstractmethod
    def analyze(self, file_path: str, content: str) -> FileAnalysis:
        """Analyze one file and return extracted entities."""

    @abstractmethod
    def extract_entities(self, tree: Any) -> List[Entity]:
        """Extract entities from a parsed syntax tree."""

    def parse_tree_sitter(self, content: str, language_name: str) -> Optional[Any]:
        """Parse source using tree-sitter-languages when available.

        Args:
            content: Source text.
            language_name: Tree-sitter language key.

        Returns:
            Parsed tree or None when parsing is unavailable.
        """

        try:
            from tree_sitter_languages import get_parser

            parser = get_parser(language_name)
            return parser.parse(content.encode("utf-8", errors="ignore"))
        except Exception:
            return None

    def base_metrics(self, content: str) -> CodeMetrics:
        """Calculate language-agnostic source metrics."""

        lines = [line for line in content.splitlines() if line.strip()]
        complexity_tokens = re.findall(
            r"\b(if|for|while|case|catch|except|elif|&&|\|\||\?|match|when)\b", content
        )
        return CodeMetrics(loc=len(lines), cyclomatic_complexity=1 + len(complexity_tokens))


class RegexAnalyzer(BaseAnalyzer):
    """Pragmatic analyzer using tree-sitter availability plus robust regex fallback."""

    class_patterns: List[str] = []
    function_patterns: List[str] = []
    interface_patterns: List[str] = []
    import_patterns: List[str] = []
    call_pattern: str = r"\b([A-Za-z_][\w]*)\s*\("

    def analyze(self, file_path: str, content: str) -> FileAnalysis:
        """Analyze source text using configured patterns."""

        tree = self.parse_tree_sitter(content, self.language)
        entities = self.extract_entities(tree)
        if not entities:
            entities = list(self._regex_entities(file_path, content))

        imports = self._matches(self.import_patterns, content)
        calls = sorted(set(re.findall(self.call_pattern, content)))
        metrics = self.base_metrics(content)
        metrics.functions = len([entity for entity in entities if entity.type in {EntityType.FUNCTION, EntityType.METHOD}])
        metrics.classes = len([entity for entity in entities if entity.type == EntityType.CLASS])
        metrics.source_files = 1
        return FileAnalysis(
            file_path=file_path,
            language=self.language,
            entities=entities,
            imports=imports,
            calls=calls,
            metrics=metrics,
        )

    def extract_entities(self, tree: Any) -> List[Entity]:
        """Return entities from AST. Regex fallback is used by analyze."""

        return []

    def _regex_entities(self, file_path: str, content: str) -> Iterable[Entity]:
        for entity_type, patterns in (
            (EntityType.CLASS, self.class_patterns),
            (EntityType.INTERFACE, self.interface_patterns),
            (EntityType.FUNCTION, self.function_patterns),
        ):
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    name = match.group("name")
                    line = content[: match.start()].count("\n") + 1
                    yield Entity(
                        id=f"{file_path}:{entity_type.value}:{name}:{line}",
                        type=entity_type,
                        name=name,
                        file_path=file_path,
                        line=line,
                    )

    def _matches(self, patterns: List[str], content: str) -> List[str]:
        values: List[str] = []
        for pattern in patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                values.append(match.group("name") if "name" in match.groupdict() else match.group(1))
        return sorted(set(values))

