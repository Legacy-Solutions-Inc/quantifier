"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class CalculationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Base schemas
class BaseResponse(BaseModel):
    success: bool = True
    message: str = "Operation completed successfully"
    timestamp: datetime = Field(default_factory=datetime.now)

class ErrorResponse(BaseResponse):
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# Authentication schemas
class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class LoginRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")

class RegisterRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")
    name: Optional[str] = Field(None, description="User full name")

# Project schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    status: ProjectStatus = ProjectStatus.DRAFT

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[ProjectStatus] = None

class ProjectResponse(ProjectBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Rebar data schemas
class RebarItem(BaseModel):
    length: float = Field(..., gt=0, description="Rebar length in meters")
    pieces: int = Field(..., ge=0, description="Number of pieces available")
    diameter: float = Field(..., gt=0, description="Rebar diameter in mm")
    
    # Optional tagging fields
    tag_id: Optional[str] = None
    floor_id: Optional[str] = None
    zone_id: Optional[str] = None
    location_id: Optional[str] = None
    member_type_id: Optional[str] = None
    rebar_type_id: Optional[str] = None
    specific_tag_id: Optional[str] = None

class StockpileItem(BaseModel):
    length: float = Field(..., gt=0, description="Stockpile length in meters")
    quantity: int = Field(..., ge=0, description="Available quantity")
    diameter: float = Field(..., gt=0, description="Rebar diameter in mm")

# Calculation schemas
class CalculationRequest(BaseModel):
    project_id: str = Field(..., description="Project ID")
    target_lengths: List[float] = Field(..., min_items=1, description="Target lengths for cutting")
    rebar_data: List[RebarItem] = Field(..., min_items=1, description="Available rebar data")
    stockpile_data: Optional[List[StockpileItem]] = Field(None, description="Optional stockpile constraints")
    tolerance: float = Field(0.0, ge=0, le=1.0, description="Tolerance for length matching")
    tolerance_step: float = Field(0.1, ge=0.01, le=0.5, description="Tolerance increment step")
    use_stockpile: bool = Field(False, description="Whether to use stockpile constraints")

class CombinationResult(BaseModel):
    quantity: int = Field(..., description="Number of commercial pieces")
    combination: List[int] = Field(..., description="Combination of lengths used")
    lengths: List[float] = Field(..., description="Lengths used in combination")
    combined_length: float = Field(..., description="Total combined length")
    target: float = Field(..., description="Target length")
    waste: float = Field(..., description="Waste in kg")
    remaining_pieces: List[int] = Field(..., description="Remaining pieces after combination")

class CalculationResult(BaseModel):
    diameter: float = Field(..., description="Rebar diameter")
    results: List[CombinationResult] = Field(..., description="Combination results")
    total_waste_percentage: float = Field(..., description="Total waste percentage")
    total_utilized_weight: float = Field(..., description="Total utilized weight in kg")
    total_commercial_weight: float = Field(..., description="Total commercial weight in kg")
    total_waste_weight: float = Field(..., description="Total waste weight in kg")

class CalculationResponse(BaseModel):
    id: str
    project_id: str
    status: CalculationStatus
    results: Optional[Dict[float, CalculationResult]] = None  # diameter -> result
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# File upload schemas
class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_size: int
    content_type: str
    uploaded_at: datetime
    project_id: Optional[str] = None

class FileValidationResponse(BaseModel):
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    data_preview: Optional[Dict[str, Any]] = None
    detected_columns: List[str] = []
    required_columns: List[str] = ["Lengths", "Pcs", "Diameter"]

# Export schemas
class ExportRequest(BaseModel):
    calculation_id: str
    format: str = Field("excel", description="Export format (excel, csv, json)")
    include_summary: bool = Field(True, description="Include summary statistics")
    include_details: bool = Field(True, description="Include detailed results")

class ExportResponse(BaseModel):
    file_url: str
    filename: str
    file_size: int
    expires_at: datetime

# Statistics schemas
class ProjectStatistics(BaseModel):
    total_projects: int
    active_projects: int
    total_calculations: int
    total_waste_saved: float  # in kg
    average_waste_percentage: float

class DiameterStatistics(BaseModel):
    diameter: float
    total_weight: float
    waste_weight: float
    waste_percentage: float
    commercial_pieces: int

class GlobalStatistics(BaseModel):
    total_weight: float
    total_waste: float
    waste_percentage: float
    commercial_pieces: int
    diameter_breakdown: List[DiameterStatistics]

# Pagination
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool
