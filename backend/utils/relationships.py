"""Relationship inference, metrics aggregation, and exports."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Set

from models.graph import CodeMetrics, Edge, Entity, EntityType, FileAnalysis, KnowledgeGraph, Node, RelationshipType


def build_graph(files: List[FileAnalysis], detected: Dict[str, List[str]]) -> KnowledgeGraph:
    """Build a knowledge graph from file analyses and detected technologies."""

    nodes: Dict[str, Node] = {}
    edges: List[Edge] = []
    entity_by_name: Dict[str, Entity] = {}

    for file_analysis in files:
        file_id = f"file:{file_analysis.file_path}"
        nodes[file_id] = Node(
            id=file_id,
            type=EntityType.FILE,
            name=file_analysis.file_path.split("/")[-1],
            file_path=file_analysis.file_path,
            metadata={"language": file_analysis.language},
        )
        for entity in file_analysis.entities:
            nodes[entity.id] = Node(
                id=entity.id,
                type=entity.type,
                name=entity.name,
                file_path=entity.file_path,
                metadata=entity.metadata | {"line": entity.line},
            )
            entity_by_name.setdefault(entity.name, entity)
            edges.append(Edge(source=file_id, target=entity.id, type=RelationshipType.CONTAINS))
        for imported in file_analysis.imports:
            import_id = f"package:{imported}"
            nodes.setdefault(import_id, Node(id=import_id, type=EntityType.PACKAGE, name=imported))
            edges.append(Edge(source=file_id, target=import_id, type=RelationshipType.IMPORTS))

    for file_analysis in files:
        source_entities = [entity for entity in file_analysis.entities if entity.type in {EntityType.FUNCTION, EntityType.METHOD}]
        for call in file_analysis.calls:
            target = entity_by_name.get(call)
            if not target:
                continue
            for source in source_entities:
                if source.id != target.id:
                    edges.append(Edge(source=source.id, target=target.id, type=RelationshipType.CALLS))

    for category, values in detected.items():
        node_type = _category_node_type(category)
        for value in values:
            node_id = f"{category}:{value}"
            nodes[node_id] = Node(id=node_id, type=node_type, name=value, metadata={"category": category})
            for file_analysis in files:
                if value.lower() in " ".join(file_analysis.imports + file_analysis.calls).lower():
                    edges.append(Edge(source=f"file:{file_analysis.file_path}", target=node_id, type=RelationshipType.USES))

    return KnowledgeGraph(nodes=list(nodes.values()), edges=_dedupe_edges(edges))


def aggregate_metrics(files: List[FileAnalysis], graph: KnowledgeGraph) -> CodeMetrics:
    """Aggregate repository metrics."""

    metrics = CodeMetrics()
    for file_analysis in files:
        metrics.loc += file_analysis.metrics.loc
        metrics.source_files += 1 if file_analysis.language != "config" else 0
        metrics.cyclomatic_complexity += file_analysis.metrics.cyclomatic_complexity
        metrics.functions += file_analysis.metrics.functions
        metrics.classes += file_analysis.metrics.classes
        metrics.languages[file_analysis.language] = metrics.languages.get(file_analysis.language, 0) + 1
    metrics.dead_code = detect_dead_code(graph)
    metrics.circular_dependencies = detect_circular_dependencies(graph)
    return metrics


def detect_dead_code(graph: KnowledgeGraph) -> List[str]:
    """Detect unreferenced functions and classes using graph reachability."""

    referenced = {edge.target for edge in graph.edges if edge.type in {RelationshipType.CALLS, RelationshipType.USES}}
    return sorted(
        node.name
        for node in graph.nodes
        if node.type in {EntityType.FUNCTION, EntityType.METHOD, EntityType.CLASS}
        and not node.name.startswith("_")
        and node.id not in referenced
    )


def detect_circular_dependencies(graph: KnowledgeGraph) -> List[List[str]]:
    """Detect circular import/dependency relationships."""

    adjacency: Dict[str, Set[str]] = defaultdict(set)
    id_to_name = {node.id: node.name for node in graph.nodes}
    for edge in graph.edges:
        if edge.type in {RelationshipType.IMPORTS, RelationshipType.DEPENDS_ON}:
            adjacency[edge.source].add(edge.target)

    cycles: Set[tuple[str, ...]] = set()

    def visit(node: str, path: List[str]) -> None:
        if node in path:
            cycle = path[path.index(node) :] + [node]
            cycles.add(tuple(id_to_name.get(item, item) for item in cycle))
            return
        if len(path) > 20:
            return
        for target in adjacency.get(node, set()):
            visit(target, path + [node])

    for start in adjacency:
        visit(start, [])
    return [list(cycle) for cycle in sorted(cycles)]


def export_mermaid(graph: KnowledgeGraph) -> str:
    """Export a compact Mermaid graph."""

    lines = ["graph TD"]
    for node in graph.nodes[:200]:
        safe_id = _safe_mermaid_id(node.id)
        lines.append(f'  {safe_id}["{node.name} ({node.type.value})"]')
    node_ids = {node.id for node in graph.nodes[:200]}
    for edge in graph.edges[:400]:
        if edge.source in node_ids and edge.target in node_ids:
            lines.append(f"  {_safe_mermaid_id(edge.source)} -->|{edge.type.value}| {_safe_mermaid_id(edge.target)}")
    return "\n".join(lines)


def _safe_mermaid_id(value: str) -> str:
    return "n_" + "".join(char if char.isalnum() else "_" for char in value)[:80]


def _category_node_type(category: str) -> EntityType:
    return {
        "frameworks": EntityType.FRAMEWORK,
        "databases": EntityType.DATABASE,
        "cloud": EntityType.CLOUD,
        "containers": EntityType.CONTAINER,
        "ai_ml": EntityType.AI_COMPONENT,
        "apis": EntityType.API,
        "queues": EntityType.QUEUE,
    }.get(category, EntityType.CONFIG)


def _dedupe_edges(edges: Iterable[Edge]) -> List[Edge]:
    seen = set()
    deduped: List[Edge] = []
    for edge in edges:
        key = (edge.source, edge.target, edge.type.value)
        if key not in seen:
            seen.add(key)
            deduped.append(edge)
    return deduped

