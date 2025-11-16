"""Main API routes."""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.models.schemas import (
    ExportRequest,
    ReportFormat,
    ScanRequest,
    ScanResponse,
    ScanResult,
    ScanStatus,
)
from app.scanner.scanner import CodeScanner
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()
scanner = CodeScanner()


@router.post("/scan", response_model=ScanResponse)
async def create_scan(
    request: ScanRequest,
    db: AsyncSession = Depends(get_db),
) -> ScanResponse:
    """
    Create a new scan job.

    Args:
        request: Scan request parameters
        db: Database session

    Returns:
        Scan response with scan ID
    """
    scan_id = str(uuid.uuid4())
    logger.info("Creating scan", scan_id=scan_id, request=request.model_dump())

    # Start scan asynchronously (in production, use background tasks)
    # For now, we'll run it synchronously
    try:
        result = await scanner.scan(
            repository_url=str(request.repository_url) if request.repository_url else None,
            repository_path=request.repository_path,
            branch=request.branch,
            file_paths=request.file_paths,
            include_patterns=request.include_patterns,
            exclude_patterns=request.exclude_patterns,
        )

        return ScanResponse(
            scan_id=result.scan_id,
            status=result.status,
            repository_url=result.repository_url,
            repository_path=result.repository_path,
            started_at=result.started_at,
            completed_at=result.completed_at,
            total_files=result.total_files,
            scanned_files=result.scanned_files,
            total_issues=len(result.issues),
            issues_by_severity={
                "critical": sum(1 for i in result.issues if i.severity.value == "critical"),
                "high": sum(1 for i in result.issues if i.severity.value == "high"),
                "medium": sum(1 for i in result.issues if i.severity.value == "medium"),
                "low": sum(1 for i in result.issues if i.severity.value == "low"),
                "info": sum(1 for i in result.issues if i.severity.value == "info"),
            },
            error=result.summary.get("error") if isinstance(result.summary, dict) else None,
        )
    except Exception as e:
        logger.error("Scan failed", scan_id=scan_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/scan/upload", response_model=ScanResponse)
async def scan_upload(
    file: UploadFile = FastAPIFile(...),
    db: AsyncSession = Depends(get_db),
) -> ScanResponse:
    """
    Scan uploaded zip file.

    Args:
        file: Uploaded zip file
        db: Database session

    Returns:
        Scan response
    """
    # TODO: Implement zip file extraction and scanning
    raise HTTPException(status_code=501, detail="Upload scanning not yet implemented")


@router.get("/scan/{scan_id}", response_model=ScanResult)
async def get_scan_result(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
) -> ScanResult:
    """
    Get scan result by ID.

    Args:
        scan_id: Scan identifier
        db: Database session

    Returns:
        Complete scan result
    """
    # TODO: Retrieve from database
    raise HTTPException(status_code=501, detail="Database retrieval not yet implemented")


@router.get("/scans", response_model=List[ScanResponse])
async def list_scans(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
) -> List[ScanResponse]:
    """
    List all scans.

    Args:
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session

    Returns:
        List of scan responses
    """
    # TODO: Retrieve from database
    return []


@router.post("/scan/{scan_id}/export")
async def export_scan(
    scan_id: str,
    request: ExportRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Export scan report in various formats.

    Args:
        scan_id: Scan identifier
        request: Export request with format
        db: Database session

    Returns:
        Export result (file URL or content)
    """
    # TODO: Implement export functionality
    raise HTTPException(status_code=501, detail="Export not yet implemented")


@router.delete("/scan/{scan_id}")
async def delete_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Delete a scan and its data.

    Args:
        scan_id: Scan identifier
        db: Database session

    Returns:
        Deletion confirmation
    """
    # TODO: Implement deletion
    from app.rag.vector_store import VectorStore
    vector_store = VectorStore()
    vector_store.delete_scan_data(scan_id)
    return {"message": "Scan deleted", "scan_id": scan_id}

