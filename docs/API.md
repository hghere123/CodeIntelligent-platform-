# API Reference

Base URL: `http://localhost:8000/api`

## `GET /health`

Returns service status.

```json
{ "status": "ok" }
```

## `POST /upload`

Uploads a ZIP repository and starts analysis.

Request: multipart form field `file`.

Response:

```json
{
  "analysis_id": "uuid",
  "summary": {
    "analysis_id": "uuid",
    "repository_name": "repo",
    "files_count": 12,
    "languages": { "python": 4 },
    "frameworks": ["FastAPI"],
    "metrics": { "loc": 300 }
  }
}
```

Errors:

- `400`: invalid file type, corrupt ZIP, unsafe path, unsupported member.
- `413`: upload exceeds 500MB.
- `500`: unexpected server error.

## `GET /analysis/{analysis_id}`

Returns the full `AnalysisResult` document.

## `GET /analysis/{analysis_id}/graph`

Returns:

```json
{
  "nodes": [{ "id": "file:app.py", "type": "file", "name": "app.py", "file_path": "app.py", "metadata": {} }],
  "edges": [{ "source": "file:app.py", "target": "package:fastapi", "type": "imports", "metadata": {} }]
}
```

## `GET /analysis/{analysis_id}/tree`

Returns repository tree nodes with `name`, `path`, `type`, and `children`.

## `GET /analysis/{analysis_id}/metrics`

Returns LOC, source file count, cyclomatic complexity, functions, classes, dead code, circular dependencies, and language counts.

## `GET /analysis/{analysis_id}/search?q={query}`

Case-insensitive substring search across entity name, type, file path, and metadata.

## `POST /compare`

Request:

```json
{
  "left_analysis_id": "uuid-a",
  "right_analysis_id": "uuid-b"
}
```

Response includes added, removed, shared node names and metric deltas.

## `GET /export/{analysis_id}/mermaid`

Returns `text/plain` Mermaid graph syntax.

## Rate Limiting

No built-in rate limiting is enabled. Deployments should add reverse proxy or gateway limits for public environments.

