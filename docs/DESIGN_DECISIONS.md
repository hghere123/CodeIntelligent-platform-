# Design Decisions

## FastAPI Over Flask Or Django

FastAPI provides first-class type hints, Pydantic validation, OpenAPI generation, async endpoints, and a small operational footprint. Django would add unnecessary ORM and admin surface for this ZIP-first analysis workflow, while Flask would require more manual validation and API scaffolding.

## Tree-sitter Over Regex Parsing

Tree-sitter provides incremental, error-tolerant AST parsing across many languages. The implementation includes regex and Python AST fallbacks so the platform remains useful when a grammar is unavailable or malformed source is uploaded.

## Cytoscape.js Over D3.js

Cytoscape.js is purpose-built for interactive graph exploration with layouts, zooming, panning, selection, and graph styling. D3.js is more flexible but would require more custom graph interaction code.

## Plugin Analyzer Architecture

Each analyzer declares `language`, `extensions`, and `analyze`. The pipeline dispatches by extension, making it straightforward to add new language support without changing API or storage code.

## Performance Optimizations

- Binary and ignored directories are skipped.
- File content is read with tolerant UTF-8 decoding.
- Technology detection uses a compact dependency and content haystack.
- SQLite stores whole analysis documents to avoid join-heavy graph reconstruction.

## Security Decisions

- Upload size is capped at 500MB.
- ZIP integrity is checked with `testzip`.
- Paths are resolved before extraction to block traversal.
- Extraction happens in a temporary directory and is removed after analysis.
- Supported extensions are whitelisted.

## Trade-offs

- Relationship inference is intentionally conservative and name-based.
- Dead code detection is heuristic and may flag public API entrypoints.
- Config parsing covers common structures, not every build tool variant.
- SQLite persistence favors simplicity over distributed concurrency.

