"""Tree-sitter AST traversal helpers."""

from __future__ import annotations

from typing import Any, Generator


def walk_tree(node: Any) -> Generator[Any, None, None]:
    """Yield a tree-sitter node and all descendants.

    Args:
        node: Root tree-sitter node.

    Yields:
        Descendant nodes in depth-first order.
    """

    yield node
    for child in getattr(node, "children", []):
        yield from walk_tree(child)


def node_text(node: Any, source: bytes) -> str:
    """Return decoded source text for a tree-sitter node."""

    return source[node.start_byte : node.end_byte].decode("utf-8", errors="ignore")

