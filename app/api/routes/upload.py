"""Document upload API routes."""

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status

from app.api.deps import get_upload_service
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.document import DocumentListResponse, DocumentResponse
from app.services.upload_service import UploadService

router = APIRouter(tags=["documents"])


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document for ingestion",
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    upload_service: UploadService = Depends(get_upload_service),
) -> DocumentResponse:
    """Upload a PDF, DOCX, or TXT file. Ingestion runs in the background."""
    return await upload_service.upload_file(
        user=current_user,
        file=file,
        background_tasks=background_tasks,
    )


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    summary="List uploaded documents",
)
async def list_documents(
    current_user: User = Depends(get_current_user),
    upload_service: UploadService = Depends(get_upload_service),
) -> DocumentListResponse:
    """Return all documents belonging to the authenticated user."""
    documents = await upload_service.list_documents(current_user)
    return DocumentListResponse(documents=documents, total=len(documents))


@router.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
    summary="Get document by ID",
)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    upload_service: UploadService = Depends(get_upload_service),
) -> DocumentResponse:
    """Return metadata for a single document."""
    return await upload_service.get_document(user=current_user, document_id=document_id)


@router.delete(
    "/document/{document_id}",
    status_code=204,
    summary="Delete a document",
)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    upload_service: UploadService = Depends(get_upload_service),
) -> None:
    """Delete document metadata, chunks, vectors, and stored file."""
    await upload_service.delete_document(user=current_user, document_id=document_id)
