"""
Calculation router for RSB optimization endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import asyncio
import uuid
from datetime import datetime

from api_server.models.schemas import (
    CalculationRequest, CalculationResponse, CalculationResult,
    BaseResponse, ErrorResponse, PaginationParams, PaginatedResponse
)
from api_server.database.connection import get_db
from api_server.auth.supabase_auth import verify_token
from api_server.services.calculation_service import CalculationService
from api_server.services.combinator_service import CombinatorService

router = APIRouter()

# Dependency for authentication
async def get_current_user(token: str = Depends()):
    """Get current authenticated user"""
    user = await verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return user

@router.post("/", response_model=CalculationResponse)
async def create_calculation(
    request: CalculationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Create a new RSB optimization calculation
    
    This endpoint accepts rebar data and target lengths, then runs the optimization
    algorithm to find the best combinations that minimize waste.
    """
    try:
        # Initialize services
        calculation_service = CalculationService(db)
        combinator_service = CombinatorService()
        
        # Create calculation record
        calculation_id = str(uuid.uuid4())
        calculation_data = {
            "id": calculation_id,
            "project_id": request.project_id,
            "status": "pending",
            "input_data": request.dict(),
            "created_at": datetime.utcnow()
        }
        
        # Store calculation in database
        await calculation_service.create_calculation(calculation_data)
        
        # Start background calculation
        background_tasks.add_task(
            run_calculation_background,
            calculation_id,
            request,
            db
        )
        
        return CalculationResponse(
            id=calculation_id,
            project_id=request.project_id,
            status="pending",
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create calculation: {str(e)}"
        )

async def run_calculation_background(
    calculation_id: str,
    request: CalculationRequest,
    db
):
    """Background task to run the calculation"""
    try:
        # Update status to processing
        await update_calculation_status(calculation_id, "processing", db)
        
        # Initialize combinator service
        combinator_service = CombinatorService()
        
        # Process calculation
        results = await combinator_service.process_calculation(request)
        
        # Store results
        await store_calculation_results(calculation_id, results, db)
        
        # Update status to completed
        await update_calculation_status(calculation_id, "completed", db)
        
    except Exception as e:
        # Update status to failed
        await update_calculation_status(
            calculation_id, 
            "failed", 
            db, 
            error_message=str(e)
        )

async def update_calculation_status(
    calculation_id: str, 
    status: str, 
    db, 
    error_message: str = None
):
    """Update calculation status in database"""
    try:
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if status == "completed":
            update_data["completed_at"] = datetime.utcnow()
        elif status == "failed" and error_message:
            update_data["error_message"] = error_message
            
        # Update in database
        db.table("calculations").update(update_data).eq("id", calculation_id).execute()
        
    except Exception as e:
        print(f"Failed to update calculation status: {e}")

async def store_calculation_results(calculation_id: str, results: Dict, db):
    """Store calculation results in database"""
    try:
        # Store main results
        db.table("calculations").update({
            "results": results,
            "updated_at": datetime.utcnow()
        }).eq("id", calculation_id).execute()
        
        # Store detailed results for each diameter
        for diameter, result in results.items():
            for combination in result.get("results", []):
                result_data = {
                    "id": str(uuid.uuid4()),
                    "calculation_id": calculation_id,
                    "diameter": diameter,
                    "quantity": combination["quantity"],
                    "combination": combination["combination"],
                    "lengths": combination["lengths"],
                    "combined_length": combination["combined_length"],
                    "target": combination["target"],
                    "waste": combination["waste"],
                    "remaining_pieces": combination["remaining_pieces"]
                }
                
                db.table("calculation_results").insert(result_data).execute()
                
    except Exception as e:
        print(f"Failed to store calculation results: {e}")

@router.get("/{calculation_id}", response_model=CalculationResponse)
async def get_calculation(
    calculation_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get calculation details and results"""
    try:
        calculation_service = CalculationService(db)
        calculation = await calculation_service.get_calculation(calculation_id)
        
        if not calculation:
            raise HTTPException(status_code=404, detail="Calculation not found")
        
        return CalculationResponse(**calculation)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get calculation: {str(e)}"
        )

@router.get("/", response_model=PaginatedResponse)
async def list_calculations(
    project_id: str = None,
    status: str = None,
    pagination: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """List calculations with optional filtering"""
    try:
        calculation_service = CalculationService(db)
        
        # Build query
        query = db.table("calculations").select("*")
        
        if project_id:
            query = query.eq("project_id", project_id)
        if status:
            query = query.eq("status", status)
            
        # Add pagination
        offset = (pagination.page - 1) * pagination.limit
        query = query.range(offset, offset + pagination.limit - 1)
        
        # Execute query
        response = query.execute()
        calculations = response.data
        
        # Get total count
        count_response = db.table("calculations").select("id", count="exact").execute()
        total = count_response.count if hasattr(count_response, 'count') else len(calculations)
        
        return PaginatedResponse(
            items=calculations,
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
            detail=f"Failed to list calculations: {str(e)}"
        )

@router.delete("/{calculation_id}", response_model=BaseResponse)
async def delete_calculation(
    calculation_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete a calculation and its results"""
    try:
        calculation_service = CalculationService(db)
        
        # Check if calculation exists
        calculation = await calculation_service.get_calculation(calculation_id)
        if not calculation:
            raise HTTPException(status_code=404, detail="Calculation not found")
        
        # Delete calculation and related data
        await calculation_service.delete_calculation(calculation_id)
        
        return BaseResponse(message="Calculation deleted successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete calculation: {str(e)}"
        )

@router.post("/{calculation_id}/rerun", response_model=BaseResponse)
async def rerun_calculation(
    calculation_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Rerun a calculation with the same parameters"""
    try:
        calculation_service = CalculationService(db)
        
        # Get original calculation
        calculation = await calculation_service.get_calculation(calculation_id)
        if not calculation:
            raise HTTPException(status_code=404, detail="Calculation not found")
        
        # Reset status and clear results
        await calculation_service.reset_calculation(calculation_id)
        
        # Start background rerun
        background_tasks.add_task(
            run_calculation_background,
            calculation_id,
            calculation["input_data"],
            db
        )
        
        return BaseResponse(message="Calculation rerun initiated")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to rerun calculation: {str(e)}"
        )
