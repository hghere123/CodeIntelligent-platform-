"""Relationship inference tests."""

from models.graph import Entity, EntityType, FileAnalysis, RelationshipType
from utils.relationships import aggregate_metrics, build_graph


def test_graph_contains_imports_calls_and_dead_code() -> None:
    """Graph builder infers import and call relationships."""

    files = [
        FileAnalysis(
            file_path="a.py",
            language="python",
            entities=[
                Entity(id="a.py:function:main:1", type=EntityType.FUNCTION, name="main", file_path="a.py"),
                Entity(id="a.py:function:helper:2", type=EntityType.FUNCTION, name="helper", file_path="a.py"),
            ],
            imports=["fastapi"],
            calls=["helper"],
        )
    ]
    graph = build_graph(files, {"frameworks": ["FastAPI"]})
    assert any(edge.type == RelationshipType.IMPORTS for edge in graph.edges)
    assert any(edge.type == RelationshipType.CALLS for edge in graph.edges)
    metrics = aggregate_metrics(files, graph)
    assert "main" in metrics.dead_code

