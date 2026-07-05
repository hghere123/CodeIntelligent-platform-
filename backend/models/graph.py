"""Graph and analysis data models."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Supported knowledge graph entity types."""

    FILE = "file"
    CLASS = "class"
    INTERFACE = "interface"
    FUNCTION = "function"
    METHOD = "method"
    MODULE = "module"
    PACKAGE = "package"
    DEPENDENCY = "dependency"
    FRAMEWORK = "framework"
    DATABASE = "database"
    CLOUD = "cloud"
    CONTAINER = "container"
    AI_COMPONENT = "ai_component"
    API = "api"
    QUEUE = "queue"
    CONFIG = "config"


class RelationshipType(str, Enum):
    """Supported relationships between graph entities."""

    CONTAINS = "contains"
    IMPORTS = "imports"
    EXTENDS = "extends"
    IMPLEMENTS = "implements"
    CALLS = "calls"
    USES = "uses"
    DEPENDS_ON = "depends_on"
    DECLARES = "declares"
    CONFIGURES = "configures"
    EXPOSES = "exposes"


class Node(BaseModel):
    """A graph node."""

    id: str
    type: EntityType
    name: str
    file_path: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Edge(BaseModel):
    """A directed graph relationship."""

    source: str
    target: str
    type: RelationshipType
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraph(BaseModel):
    """A graph of code entities and relationships."""

    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)


class CodeMetrics(BaseModel):
    """Code metrics for a file or repository."""

    loc: int = 0
    source_files: int = 0
    cyclomatic_complexity: int = 0
    functions: int = 0
    classes: int = 0
    dead_code: List[str] = Field(default_factory=list)
    circular_dependencies: List[List[str]] = Field(default_factory=list)
    languages: Dict[str, int] = Field(default_factory=dict)


class Entity(BaseModel):
    """Entity extracted from a file."""

    id: str
    type: EntityType
    name: str
    file_path: str
    line: int = 1
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FileAnalysis(BaseModel):
    """Analysis result for one source or config file."""

    file_path: str
    language: str
    entities: List[Entity] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    calls: List[str] = Field(default_factory=list)
    metrics: CodeMetrics = Field(default_factory=CodeMetrics)
    errors: List[str] = Field(default_factory=list)


class RepositoryTreeNode(BaseModel):
    """Tree node for repository explorer data."""

    name: str
    path: str
    type: str
    children: List["RepositoryTreeNode"] = Field(default_factory=list)


class AnalysisSummary(BaseModel):
    """Compact analysis summary shown on dashboards."""

    analysis_id: str
    repository_name: str
    files_count: int
    languages: Dict[str, int]
    frameworks: List[str]
    metrics: CodeMetrics


class AnalysisResult(BaseModel):
    """Complete repository analysis result."""

    analysis_id: str
    repository_name: str
    graph: KnowledgeGraph
    tree: RepositoryTreeNode
    files: List[FileAnalysis]
    metrics: CodeMetrics
    detected: Dict[str, List[str]] = Field(default_factory=dict)
    summary: Optional[AnalysisSummary] = None


class CompareRequest(BaseModel):
    """Request body for comparing two stored analyses."""

    left_analysis_id: str
    right_analysis_id: str


class CompareResult(BaseModel):
    """Comparison result between two repositories."""

    left_analysis_id: str
    right_analysis_id: str
    added_nodes: List[str]
    removed_nodes: List[str]
    shared_nodes: List[str]
    metric_delta: Dict[str, int]


RepositoryTreeNode.model_rebuild()

