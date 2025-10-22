"""
Project management router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from api_server.models.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, BaseResponse,
    PaginationParams, PaginatedResponse, ProjectStatistics
)
from api_server.database.connection import get_db
from api_server.auth.supabase_auth import verify_token
from api_server.services.project_service import ProjectService

router = APIRouter()

# Dependency for authentication
async def get_current_user(token: str = Depends()):
    """Get current authenticated user"""
    user = await verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return user

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Create a new project
    
    Creates a new project for organizing RSB calculations.
    """
    try:
        project_service = ProjectService(db)
        
        # Create project
        project_data = {
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "user_id": current_user["id"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        project_id = await project_service.create_project(project_data)
        
        # Get created project
        created_project = await project_service.get_project(project_id)
        
        return ProjectResponse(**created_project)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get project by ID
    
    Retrieves a specific project and its details.
    """
    try:
        project_service = ProjectService(db)
        
        # Get project
        project = await project_service.get_project(project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check if user owns the project
        if project["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return ProjectResponse(**project)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project: {str(e)}"
        )

@router.get("/", response_model=PaginatedResponse)
async def list_projects(
    status: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    List user's projects
    
    Retrieves a paginated list of projects for the current user.
    """
    try:
        project_service = ProjectService(db)
        
        # Get projects
        projects = await project_service.list_projects(
            user_id=current_user["id"],
            status=status,
            limit=pagination.limit,
            offset=(pagination.page - 1) * pagination.limit
        )
        
        # Get total count
        total = await project_service.get_project_count(
            user_id=current_user["id"],
            status=status
        )
        
        return PaginatedResponse(
            items=projects,
            total=total,
            page=pagination.page,
            limit=pagination.limit,
            pages=(total + pagination.limit - 1) // pagination.limit,
            has_next=pagination.page * pagination.limit < total,
            has_prev=pagination.page > 1
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    updates: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Update project
    
    Updates project information.
    """
    try:
        project_service = ProjectService(db)
        
        # Check if project exists and user owns it
        project = await project_service.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update project
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        success = await project_service.update_project(project_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update project"
            )
        
        # Get updated project
        updated_project = await project_service.get_project(project_id)
        
        return ProjectResponse(**updated_project)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )

@router.delete("/{project_id}", response_model=BaseResponse)
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete project
    
    Deletes a project and all associated data.
    """
    try:
        project_service = ProjectService(db)
        
        # Check if project exists and user owns it
        project = await project_service.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Delete project
        success = await project_service.delete_project(project_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete project"
            )
        
        return BaseResponse(message="Project deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )

@router.get("/{project_id}/statistics", response_model=ProjectStatistics)
async def get_project_statistics(
    project_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get project statistics
    
    Retrieves statistics for a specific project.
    """
    try:
        project_service = ProjectService(db)
        
        # Check if project exists and user owns it
        project = await project_service.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Get statistics
        stats = await project_service.get_project_statistics(project_id)
        
        return ProjectStatistics(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project statistics: {str(e)}"
        )

@router.get("/statistics/global", response_model=ProjectStatistics)
async def get_global_statistics(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get global statistics for user
    
    Retrieves overall statistics for all user's projects.
    """
    try:
        project_service = ProjectService(db)
        
        # Get global statistics
        stats = await project_service.get_global_statistics(current_user["id"])
        
        return ProjectStatistics(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get global statistics: {str(e)}"
        )
