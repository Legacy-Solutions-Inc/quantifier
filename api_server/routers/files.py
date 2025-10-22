"""
File management router for handling file uploads and downloads
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import uuid
from datetime import datetime, timedelta
import pandas as pd
import json

from api_server.models.schemas import (
    FileUploadResponse, FileValidationResponse, ExportRequest, ExportResponse,
    BaseResponse, PaginationParams, PaginatedResponse
)
from api_server.database.connection import get_db
from api_server.auth.supabase_auth import verify_token
from api_server.services.file_service import FileService
from api_server.services.export_service import ExportService

router = APIRouter()

# Dependency for authentication
async def get_current_user(token: str = Depends()):
    """Get current authenticated user"""
    user = await verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return user

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    project_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Upload a file for processing
    
    Accepts Excel (.xlsx, .xls) or CSV files for RSB data processing.
    """
    try:
        file_service = FileService(db)
        
        # Validate file type
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=400,
                detail="Only Excel (.xlsx, .xls) and CSV files are supported"
            )
        
        # Generate file ID
        file_id = str(uuid.uuid4())
        
        # Upload file to Supabase storage
        file_path = f"uploads/{current_user['id']}/{file_id}_{file.filename}"
        
        # Read file content
        content = await file.read()
        
        # Upload to Supabase storage
        storage_response = db.storage.from_("files").upload(file_path, content)
        
        if not storage_response:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to storage"
            )
        
        # Store file metadata
        file_data = {
            "id": file_id,
            "filename": file.filename,
            "file_path": file_path,
            "file_size": len(content),
            "content_type": file.content_type or "application/octet-stream",
            "uploaded_at": datetime.utcnow(),
            "project_id": project_id
        }
        
        await file_service.store_file_metadata(file_data)
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_size=len(content),
            content_type=file.content_type or "application/octet-stream",
            uploaded_at=datetime.utcnow(),
            project_id=project_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}"
        )

@router.post("/validate", response_model=FileValidationResponse)
async def validate_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Validate file structure and content
    
    Validates uploaded file for correct format and required columns.
    """
    try:
        file_service = FileService(db)
        
        # Read file content
        content = await file.read()
        
        # Validate file structure
        validation_result = await file_service.validate_file_structure(content, file.filename)
        
        return FileValidationResponse(**validation_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File validation failed: {str(e)}"
        )

@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Download a file
    
    Downloads a file from storage.
    """
    try:
        file_service = FileService(db)
        
        # Get file metadata
        file_metadata = await file_service.get_file_metadata(file_id)
        
        if not file_metadata:
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Check if user has access to the file
        if file_metadata.get("project_id"):
            # Check project ownership
            project_query = db.table("projects").select("user_id").eq("id", file_metadata["project_id"])
            project_response = project_query.execute()
            
            if not project_response.data or project_response.data[0]["user_id"] != current_user["id"]:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied"
                )
        
        # Get file from storage
        file_path = file_metadata["file_path"]
        file_content = db.storage.from_("files").download(file_path)
        
        if not file_content:
            raise HTTPException(
                status_code=404,
                detail="File not found in storage"
            )
        
        # Return file response
        return FileResponse(
            path=file_path,
            filename=file_metadata["filename"],
            media_type=file_metadata["content_type"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"File download failed: {str(e)}"
        )

@router.get("/", response_model=PaginatedResponse)
async def list_files(
    project_id: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    List user's files
    
    Retrieves a paginated list of files for the current user.
    """
    try:
        file_service = FileService(db)
        
        # Get files
        files = await file_service.list_files(
            user_id=current_user["id"],
            project_id=project_id,
            limit=pagination.limit,
            offset=(pagination.page - 1) * pagination.limit
        )
        
        # Get total count
        total = await file_service.get_file_count(
            user_id=current_user["id"],
            project_id=project_id
        )
        
        return PaginatedResponse(
            items=files,
            total=total,
            page=pagination.page,
            limit=pagination.limit,
            pages=(total + pagination.limit - 1) // pagination.limit,
            has_next=pagination.page * pagination.limit < total,
            has_prev=pagination.page > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list files: {str(e)}"
        )

@router.delete("/{file_id}", response_model=BaseResponse)
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete a file
    
    Deletes a file and its metadata.
    """
    try:
        file_service = FileService(db)
        
        # Get file metadata
        file_metadata = await file_service.get_file_metadata(file_id)
        
        if not file_metadata:
            raise HTTPException(
                status_code=404,
                detail="File not found"
            )
        
        # Check if user has access to the file
        if file_metadata.get("project_id"):
            # Check project ownership
            project_query = db.table("projects").select("user_id").eq("id", file_metadata["project_id"])
            project_response = project_query.execute()
            
            if not project_response.data or project_response.data[0]["user_id"] != current_user["id"]:
                raise HTTPException(
                    status_code=403,
                    detail="Access denied"
                )
        
        # Delete file from storage
        file_path = file_metadata["file_path"]
        db.storage.from_("files").remove([file_path])
        
        # Delete file metadata
        await file_service.delete_file_metadata(file_id)
        
        return BaseResponse(message="File deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )

@router.post("/export", response_model=ExportResponse)
async def export_calculation_results(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Export calculation results
    
    Exports calculation results in the specified format.
    """
    try:
        export_service = ExportService(db)
        
        # Start background export task
        export_id = str(uuid.uuid4())
        
        background_tasks.add_task(
            export_service.export_calculation_results,
            export_id,
            request.calculation_id,
            request.format,
            request.include_summary,
            request.include_details,
            current_user["id"]
        )
        
        # Return export response with temporary URL
        return ExportResponse(
            file_url=f"/api/files/export/{export_id}",
            filename=f"rsb_results_{request.calculation_id}.{request.format}",
            file_size=0,  # Will be updated when export completes
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )

@router.get("/export/{export_id}")
async def download_export(
    export_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Download exported file
    
    Downloads a previously exported file.
    """
    try:
        export_service = ExportService(db)
        
        # Get export file
        export_file = await export_service.get_export_file(export_id, current_user["id"])
        
        if not export_file:
            raise HTTPException(
                status_code=404,
                detail="Export file not found"
            )
        
        # Check if file has expired
        if export_file["expires_at"] < datetime.utcnow():
            raise HTTPException(
                status_code=410,
                detail="Export file has expired"
            )
        
        # Get file from storage
        file_content = db.storage.from_("exports").download(export_file["file_path"])
        
        if not file_content:
            raise HTTPException(
                status_code=404,
                detail="Export file not found in storage"
            )
        
        # Return file response
        return FileResponse(
            path=export_file["file_path"],
            filename=export_file["filename"],
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export download failed: {str(e)}"
        )
