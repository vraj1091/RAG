# Enhanced Documents Router - FIXED for DeepSeek Integration
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Request, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import os
import validators
import logging
from datetime import datetime
import json
import re
import pandas as pd
import numpy as np

from app.db.database import get_db
from app.utils.dependencies import get_current_user
from app.models.models import User, Document
from app.services.rag_service import get_rag_service  # FIXED: Import factory function
from app.services.tally_services import tally_service
from app.core.config import settings
from pydantic import BaseModel
from app.services.financial_analytics_service import FinancialAnalyticsService


class URLRequest(BaseModel):
    url: str


class MultipleSourcesRequest(BaseModel):
    sources: List[dict]


logger = logging.getLogger(__name__)
router = APIRouter()

# REMOVED global instantiation - will create per request
# rag_service = RAGService()  # REMOVED THIS LINE
financial_service = FinancialAnalyticsService()


# ============================================================================
# HELPER FUNCTION: Get RAG Service (called in each endpoint)
# ============================================================================

def get_rag(db: Session, user_id: int):
    """Helper to get RAG service - call this at start of each endpoint"""
    return get_rag_service(db, user_id)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def convert_google_drive_url(url: str) -> str:
    """Convert Google Drive share URL to direct download URL for gdown."""
    patterns = [
        r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
        r'drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
        r'drive\.google\.com/uc\?id=([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/uc?id={file_id}"
    
    return url


async def generate_excel_insights(file_path: str, file_extension: str):
    """Generate financial insights from Excel/CSV files"""
    try:
        if file_extension == '.csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path, sheet_name=0)
        
        df.columns = df.columns.str.strip()
        
        for col in df.columns:
            if 'date' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass
        
        insights = {
            "summary": {
                "total_rows": int(len(df)),
                "total_columns": int(len(df.columns)),
                "columns": list(df.columns)
            },
            "insights": [],
            "charts": {}
        }
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        category_cols = [col for col in df.columns if any(x in col.lower() for x in ['region', 'category', 'type', 'product', 'item', 'rep', 'name'])]
        amount_cols = [col for col in df.columns if any(x in col.lower() for x in ['total', 'amount', 'revenue', 'sales', 'value', 'price'])]
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        if len(category_cols) > 0 and len(amount_cols) > 0:
            cat_col = category_cols[0]
            amt_col = amount_cols[0]
            grouped = df.groupby(cat_col)[amt_col].sum().sort_values(ascending=False)
            
            insights["charts"]["revenue_by_category"] = {
                "type": "bar",
                "title": f"Revenue by {cat_col}",
                "data": {
                    "labels": [str(x) for x in grouped.index[:10]],
                    "datasets": [{
                        "label": "Revenue",
                        "data": [float(x) for x in grouped.values[:10]],
                        "backgroundColor": "rgba(75, 192, 192, 0.6)",
                        "borderColor": "rgba(75, 192, 192, 1)",
                        "borderWidth": 1
                    }]
                }
            }
        
        if len(date_cols) > 0 and len(amount_cols) > 0:
            date_col = date_cols[0]
            amt_col = amount_cols[0]
            df['YearMonth'] = df[date_col].dt.to_period('M').astype(str)
            monthly = df.groupby('YearMonth')[amt_col].sum().sort_index()
            
            insights["charts"]["monthly_trend"] = {
                "type": "line",
                "title": "Monthly Trend",
                "data": {
                    "labels": list(monthly.index),
                    "datasets": [{
                        "label": "Amount",
                        "data": [float(x) for x in monthly.values],
                        "borderColor": "rgb(75, 192, 192)",
                        "tension": 0.4
                    }]
                }
            }
        
        if len(amount_cols) > 0:
            amt_col = amount_cols[0]
            insights["summary"]["total_amount"] = float(df[amt_col].sum())
            insights["summary"]["average_amount"] = float(df[amt_col].mean())
        
        insights["insights"].append(f"📊 Analyzed {len(df):,} rows with {len(df.columns)} columns")
        
        return insights
        
    except Exception as e:
        logger.error(f"❌ Insight generation failed: {e}")
        return None


# ============================================================================
# GET ENDPOINTS
# ============================================================================

@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get enhanced document processing statistics."""
    # CREATE RAG SERVICE FOR THIS REQUEST
    rag_service = get_rag(db, current_user.id)
    
    logger.info(f"📊 Getting stats for user {current_user.id}")
    
    try:
        stats = rag_service.get_document_stats()
        
        local_docs = db.query(Document).filter(
            Document.user_id == current_user.id, 
            Document.file_type.notin_(["pdf_url", "web_url", "enhanced_web_url", "google_drive_file", "google_drive_folder"])
        ).count()
        
        external_docs = db.query(Document).filter(
            Document.user_id == current_user.id, 
            Document.file_type.in_(["pdf_url", "web_url", "enhanced_web_url"])
        ).count()
        
        google_drive_docs = db.query(Document).filter(
            Document.user_id == current_user.id, 
            Document.file_type.in_(["google_drive_file", "google_drive_folder"])
        ).count()
        
        content = {
            **stats, 
            "local_documents": local_docs, 
            "external_sources": external_docs,
            "google_drive_sources": google_drive_docs
        }
        
        return JSONResponse(status_code=status.HTTP_200_OK, content=content)
        
    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}", exc_info=True)
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "total_documents": 0,
            "total_chunks": 0
        })


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
        logger.error(f"Failed to retrieve documents: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}",
        )


@router.get("/{document_id}", status_code=status.HTTP_200_OK)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document by ID."""
    document = db.query(Document).filter(
        Document.id == document_id, 
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    return document


# ============================================================================
# UPLOAD ENDPOINT
# ============================================================================

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enhanced upload with auto-detect Tally/Excel files"""
    # CREATE RAG SERVICE FOR THIS REQUEST
    rag_service = get_rag(db, current_user.id)
    
    allowed_extensions = {".pdf", ".docx", ".txt", ".xlsx", ".xls", ".csv", ".png", ".jpg", ".jpeg", ".xml"}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not supported"
        )
    
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
            file_type=file_extension.replace(".", ""),
            file_size=len(content),
            processing_status="processing",
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        is_tally = tally_service.is_tally_file(file.filename)
        extracted_text = None
        financial_insights = None
        
        if is_tally:
            logger.info(f"🏦 Processing Tally file: {file.filename}")
            result = await tally_service.process_tally_file_advanced(
                file_path, file.filename, file_extension.replace(".", "")
            )
            if result['success']:
                extracted_text = result['extracted_text']
                financial_insights = result['financial_analysis']
        
        elif file_extension in ['.xlsx', '.xls', '.csv']:
            logger.info(f"📊 Processing Excel file: {file.filename}")
            extracted_text = rag_service._extract_text_from_excel_enhanced(file_path)
            financial_insights = await generate_excel_insights(file_path, file_extension)
        
        else:
            extracted_text = rag_service._extract_text_from_pdf(file_path) if file_extension == '.pdf' else \
                           rag_service._extract_text_from_docx(file_path) if file_extension in ['.docx', '.doc'] else \
                           rag_service._extract_text_from_image_ocr(file_path) if file_extension in ['.png', '.jpg', '.jpeg'] else \
                           open(file_path, 'r', encoding='utf-8').read()
        
        if not extracted_text:
            document.processing_status = "failed"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to extract text"
            )
        
        document.content = extracted_text
        chunks = rag_service._create_and_store_chunks(extracted_text, document.id)
        
        document.processing_status = "completed"
        db.commit()
        
        response_data = {
            "message": "Document uploaded successfully",
            "document_id": document.id,
            "filename": file.filename,
            "chunks_created": len(chunks)
        }
        
        if financial_insights:
            response_data["financial_insights"] = financial_insights
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}", exc_info=True)
        if 'document' in locals():
            document.processing_status = "failed"
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )
# ============================================================================
# GOOGLE DRIVE ENDPOINTS
# ============================================================================

@router.post("/process-pdf-url", status_code=status.HTTP_200_OK)
async def process_pdf_url(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process PDF document from external URL or Google Drive."""
    # CREATE RAG SERVICE FOR THIS REQUEST
    rag_service = get_rag(db, current_user.id)
    
    pdf_url = None
    
    try:
        body_bytes = await request.body()
        
        if not body_bytes or len(body_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request body is empty"
            )
        
        from urllib.parse import parse_qs
        form_data = parse_qs(body_bytes.decode())
        pdf_url = form_data.get("url", [None])[0] or form_data.get("pdf_url", [None])[0]
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error parsing request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request format: {str(e)}"
        )
    
    if not pdf_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'url' or 'pdf_url' field is required"
        )
    
    if not validators.url(pdf_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format"
        )

    try:
        if "drive.google.com" in pdf_url:
            converted_url = convert_google_drive_url(pdf_url)
            result = rag_service._process_google_drive_file(converted_url, {})
            
            if "error" in result:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=result["error"]
                )

            return JSONResponse(content={
                "message": "Google Drive PDF processed successfully",
                "document_id": result.get("doc_id"),
                "url": pdf_url,
                "chunks_created": result.get("chunks", 0)
            })
        
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Only Google Drive links supported"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PDF processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF processing failed: {str(e)}"
        )


@router.post("/process-google-drive-file", status_code=status.HTTP_200_OK)
async def process_google_drive_file(
    drive_url: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process a single Google Drive file"""
    # CREATE RAG SERVICE FOR THIS REQUEST
    rag_service = get_rag(db, current_user.id)
    
    if not validators.url(drive_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format"
        )

    try:
        converted_url = convert_google_drive_url(drive_url)
        result = rag_service._process_google_drive_source(converted_url)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=result["error"]
            )

        return JSONResponse(content={
            "message": "Google Drive file processed successfully",
            "document_id": result.get("doc_id"),
            "chunks_created": result.get("chunks", 0)
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Google Drive processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process Google Drive file: {str(e)}"
        )


@router.post("/process-google-drive-folder", status_code=status.HTTP_200_OK)
async def process_google_drive_folder(
    folder_url: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process all supported files in a Google Drive folder"""
    # CREATE RAG SERVICE FOR THIS REQUEST
    rag_service = get_rag(db, current_user.id)
    
    if not validators.url(folder_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid URL format"
        )

    try:
        result = rag_service._process_google_drive_source(folder_url)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=result["error"]
            )

        return JSONResponse(content={
            "message": "Google Drive folder processed successfully",
            "total_files": result.get("total_files", 0),
            "processed": result.get("processed", 0),
            "failed": result.get("failed", 0),
            "total_chunks": result.get("total_chunks", 0)
        })

    except Exception as e:
        logger.error(f"❌ Google Drive folder processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )


# ============================================================================
# WEB SCRAPING ENDPOINTS
# ============================================================================

@router.post("/process-web-url-enhanced", status_code=status.HTTP_200_OK)
async def process_web_url_enhanced(
    web_url: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enhanced web scraping with intelligent content extraction"""
    # CREATE RAG SERVICE FOR THIS REQUEST
    rag_service = get_rag(db, current_user.id)
    
    if not validators.url(web_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid URL format"
        )

    try:
        result = rag_service._process_url_enhanced(web_url)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=result["error"]
            )

        return JSONResponse(content={
            "message": "Enhanced web scraping completed successfully",
            "document_id": result.get("doc_id"),
            "text_length": result.get("text_length", 0),
            "chunks_created": result.get("chunks", 0)
        })

    except Exception as e:
        logger.error(f"❌ Enhanced web scraping failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )


@router.post("/process-web-url", status_code=status.HTTP_200_OK)
async def process_web_url(
    request: URLRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Scrape and process content from web URL."""
    # CREATE RAG SERVICE FOR THIS REQUEST
    rag_service = get_rag(db, current_user.id)
    
    if not validators.url(request.url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid URL format"
        )

    try:
        result = rag_service._process_url_enhanced(request.url)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=result["error"]
            )
        
        return JSONResponse(content={
            "message": "Web URL processed successfully",
            "url": request.url,
            "chunks_created": result.get("chunks", 0)
        })
        
    except Exception as e:
        logger.error(f"❌ Web URL processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )


@router.post("/process-multiple-sources", status_code=status.HTTP_200_OK)
async def process_multiple_sources(
    request: MultipleSourcesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process multiple sources in batch, max 10."""
    # CREATE RAG SERVICE FOR THIS REQUEST
    rag_service = get_rag(db, current_user.id)
    
    if len(request.sources) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Maximum 10 sources allowed per batch"
        )

    results = []
    for source in request.sources:
        url = source.get("url")
        source_type = source.get("type", "web_url")

        if not url or not validators.url(url):
            results.append({
                "url": url, 
                "status": "failed", 
                "error": "Invalid URL"
            })
            continue

        try:
            if source_type == "google_drive_file":
                converted_url = convert_google_drive_url(url)
                result = rag_service._process_google_drive_source(converted_url)
            else:
                result = rag_service._process_url_enhanced(url)

            results.append({
                "url": url, 
                "status": "completed" if "doc_id" in result else "failed",
                "error": result.get("error")
            })

        except Exception as e:
            logger.error(f"❌ Error processing {url}: {e}")
            results.append({
                "url": url, 
                "status": "failed", 
                "error": str(e)
            })

    return JSONResponse(content={"results": results})


# ============================================================================
# DELETE ENDPOINT
# ============================================================================

@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(
    document_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Delete a document and its associated vectors."""
    # CREATE RAG SERVICE FOR THIS REQUEST
    rag_service = get_rag(db, current_user.id)
    
    document = db.query(Document).filter(
        Document.id == document_id, 
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Document not found"
        )

    try:
        # Delete from vector store
        success = rag_service.delete_document(document_id)

        # Delete file if local
        if not validators.url(document.file_path) and os.path.exists(document.file_path):
            os.remove(document.file_path)

        # Delete from database
        db.delete(document)
        db.commit()

        return JSONResponse(content={"message": "Document deleted successfully"})

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Delete failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to delete document: {e}"
        )
