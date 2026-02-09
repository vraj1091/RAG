from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import os
import validators
import logging

from app.db.database import get_db
from app.api.endpoints.auth import get_current_user
from app.models.models import User, Document
from app.services.rag_service import RAGService
from app.services.tally_services import tally_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# ❌ REMOVED: rag_service = RAGService()

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user_documents(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a list of user documents with pagination."""
    try:
        documents = (
            db.query(Document)
            .filter(Document.user_id == current_user.id)
            .order_by(Document.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return documents
    except Exception as e:
        logger.error(f"Failed to retrieve documents for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}",
        )

@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload and process a document."""
    
    # ✅ Create RAGService instance with proper parameters
    rag_service = RAGService(db, current_user.id)
    
    file_extension = file.filename.split(".")[-1].strip().lower()
    logger.info(f"Uploading file: {file.filename} with extension: {file_extension}")
    logger.info(f"Allowed file types: {settings.allowed_file_types_list}")

    if file_extension not in settings.allowed_file_types_list:
        error_detail = f"Unsupported file type: '{file_extension}'. Allowed types: {settings.allowed_file_types}"
        logger.error(error_detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > settings.max_file_size_bytes:
        error_detail = f"File size ({file_size} bytes) exceeds {settings.max_file_size_mb}MB limit."
        logger.error(error_detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)

    try:
        file_path = os.path.join(settings.upload_path, f"{current_user.id}_{file.filename}")
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        document = Document(
            user_id=current_user.id,
            filename=f"{current_user.id}_{file.filename}",
            original_filename=file.filename,
            file_path=file_path,
            file_type=file_extension,
            file_size=file_size,
            processing_status="pending",
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        success = await rag_service.process_document(document, db)

        if success:
            document_data = {
                "id": document.id,
                "original_filename": document.original_filename,
                "file_path": document.file_path,
                "file_size": document.file_size,
                "file_type": document.file_type,
                "processing_status": "completed",
                "document_type": getattr(document, "document_type", None),
                "user_id": document.user_id,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat() if document.updated_at else None,
            }
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"message": "Document processed successfully", "document": document_data},
            )
        else:
            error_detail = (
                "Document processing failed after upload. "
                "Check backend configuration or document validity. See backend logs for details."
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_detail)

    except Exception as e:
        logger.error(f"File upload critical failure for {file.filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"A critical error occurred during file upload: {str(e)}",
        )

@router.post("/process-pdf-url", status_code=status.HTTP_200_OK)
async def process_pdf_url(
    pdf_url: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process PDF document from external URL."""
    
    # ✅ Create instance
    rag_service = RAGService(db, current_user.id)
    
    if not validators.url(pdf_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL format")
    try:
        success = await rag_service.process_external_source("pdf_url", pdf_url, current_user.id, db)
        if success:
            return JSONResponse(content={"message": "PDF URL processed successfully."})
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process PDF from URL.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/process-web-url", status_code=status.HTTP_200_OK)
async def process_web_url(
    web_url: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Scrape and process content from web URL."""
    
    # ✅ Create instance
    rag_service = RAGService(db, current_user.id)
    
    if not validators.url(web_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL format")
    try:
        success = await rag_service.process_external_source("web_url", web_url, current_user.id, db)
        if success:
            return JSONResponse(content={"message": "Web URL processed successfully."})
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process web URL.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/process-multiple-sources", status_code=status.HTTP_200_OK)
async def process_multiple_sources(
    sources: List[dict],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process multiple sources in batch, max 10."""
    
    # ✅ Create instance
    rag_service = RAGService(db, current_user.id)
    
    if len(sources) > 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum 10 sources allowed per batch.")

    results = []
    for source in sources:
        url = source.get("url")
        source_type = source.get("type", "web_url")
        if not validators.url(url):
            results.append({"url": url, "status": "failed", "error": "Invalid URL"})
            continue
        try:
            success = await rag_service.process_external_source(source_type, url, current_user.id, db)
            results.append({"url": url, "status": "completed" if success else "failed"})
        except Exception as e:
            results.append({"url": url, "status": "failed", "error": str(e)})
    return JSONResponse(content={"results": results})

@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get enhanced document processing statistics."""
    
    # ✅ Create instance
    rag_service = RAGService(db, current_user.id)
    
    stats = rag_service.get_collection_stats(current_user.id)
    local_docs, external_docs, status_counts = 0, 0, {}
    try:
        local_docs = (
            db.query(Document)
            .filter(Document.user_id == current_user.id, Document.file_type.notin_(["pdf_url", "web_url"]))
            .count()
        )
        external_docs = (
            db.query(Document)
            .filter(Document.user_id == current_user.id, Document.file_type.in_(["pdf_url", "web_url"]))
            .count()
        )
        status_results = (
            db.query(Document.processing_status, func.count(Document.id))
            .filter(Document.user_id == current_user.id)
            .group_by(Document.processing_status)
            .all()
        )
        status_counts = {status: count for status, count in status_results}
    except Exception as e:
        logger.warning(f"Cannot retrieve document stats: {e}")
    content = {**stats, "local_documents": local_docs, "external_sources": external_docs, "processing_status": status_counts}
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)

@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete a document and its associated vectors."""
    
    # ✅ Create instance
    rag_service = RAGService(db, current_user.id)
    
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    try:
        rag_service.delete_document_from_vector_store(document.id, current_user.id)
        if not validators.url(document.file_path) and os.path.exists(document.file_path):
            os.remove(document.file_path)
        db.delete(document)
        db.commit()
        return JSONResponse(content={"message": "Document deleted successfully."})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete document: {e}")

@router.post("/preview-source", status_code=status.HTTP_200_OK)
async def preview_source(
    source_url: str = Form(...), 
    source_type: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Preview content from an external source."""
    
    # ✅ Create instance
    rag_service = RAGService(db, current_user.id)
    
    if not validators.url(source_url):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL format.")
    try:
        if source_type == "web_url":
            text = await rag_service._extract_web_content(source_url)
            return JSONResponse(
                content={
                    "preview": text[:500] + "..." if text else "",
                    "word_count": len(text.split()) if text else 0,
                    "supported": bool(text),
                }
            )
        elif source_type == "pdf_url":
            return JSONResponse(
                content={
                    "preview": "PDF content will be downloaded and processed.",
                    "supported": True,
                }
            )
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported source type for preview.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate preview: {e}")
