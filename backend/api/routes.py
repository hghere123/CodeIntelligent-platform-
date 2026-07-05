"""API routes for repository analysis."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse

from config import Settings, get_settings
from models.graph import CompareRequest
from utils.exceptions import NotFoundError, UploadValidationError
from utils.pipeline import AnalysisPipeline
from utils.storage import AnalysisStore

router = APIRouter()


def get_pipeline(settings: Settings = Depends(get_settings)) -> AnalysisPipeline:
    """Create an analysis pipeline for a request."""

    return AnalysisPipeline(AnalysisStore(settings.database_path))


@router.get("/health")
async def health() -> dict[str, str]:
    """Return service health."""

    return {"status": "ok"}


@router.post("/upload")
async def upload_repository(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    pipeline: AnalysisPipeline = Depends(get_pipeline),
) -> dict[str, object]:
    """Upload a ZIP repository and run analysis."""

    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only ZIP uploads are supported")
    content = await file.read()
    if len(content) > settings.max_zip_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="ZIP file exceeds maximum size")
    try:
        result = await pipeline.analyze_zip(file.filename, content)
    except UploadValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"analysis_id": result.analysis_id, "summary": result.summary}


@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str, pipeline: AnalysisPipeline = Depends(get_pipeline)):
    """Return full analysis result."""

    try:
        return pipeline.store.get(analysis_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/analysis/{analysis_id}/graph")
async def get_graph(analysis_id: str, pipeline: AnalysisPipeline = Depends(get_pipeline)):
    """Return knowledge graph."""

    return pipeline.store.get(analysis_id).graph


@router.get("/analysis/{analysis_id}/tree")
async def get_tree(analysis_id: str, pipeline: AnalysisPipeline = Depends(get_pipeline)):
    """Return repository tree."""

    return pipeline.store.get(analysis_id).tree


@router.get("/analysis/{analysis_id}/metrics")
async def get_metrics(analysis_id: str, pipeline: AnalysisPipeline = Depends(get_pipeline)):
    """Return repository metrics."""

    return pipeline.store.get(analysis_id).metrics


@router.get("/analysis/{analysis_id}/search")
async def search(analysis_id: str, q: str = Query(..., min_length=1), pipeline: AnalysisPipeline = Depends(get_pipeline)):
    """Search across graph entities."""

    return {"results": pipeline.search(analysis_id, q)}


@router.post("/compare")
async def compare(request: CompareRequest, pipeline: AnalysisPipeline = Depends(get_pipeline)):
    """Compare two analysis results."""

    return pipeline.compare(request.left_analysis_id, request.right_analysis_id)


@router.get("/export/{analysis_id}/mermaid", response_class=PlainTextResponse)
async def export_mermaid(analysis_id: str, pipeline: AnalysisPipeline = Depends(get_pipeline)) -> str:
    """Export the graph as Mermaid syntax."""

    return pipeline.mermaid(analysis_id)

