"""
Database models and table definitions for Supabase
"""

from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

class Project(Base):
    """Project model for organizing calculations"""
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="draft")  # draft, active, completed, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    calculations = relationship("Calculation", back_populates="project", cascade="all, delete-orphan")
    files = relationship("ProjectFile", back_populates="project", cascade="all, delete-orphan")

class ProjectFile(Base):
    """File attachments for projects"""
    __tablename__ = "project_files"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # Supabase storage path
    file_size = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="files")

class Calculation(Base):
    """Calculation model for storing optimization results"""
    __tablename__ = "calculations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    input_data = Column(JSON, nullable=False)  # Store input parameters
    results = Column(JSON, nullable=True)  # Store calculation results
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="calculations")

class RebarData(Base):
    """Rebar data model for storing input data"""
    __tablename__ = "rebar_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    calculation_id = Column(String, ForeignKey("calculations.id"), nullable=False)
    length = Column(Float, nullable=False)
    pieces = Column(Integer, nullable=False)
    diameter = Column(Float, nullable=False)
    
    # Optional tagging fields
    tag_id = Column(String, nullable=True)
    floor_id = Column(String, nullable=True)
    zone_id = Column(String, nullable=True)
    location_id = Column(String, nullable=True)
    member_type_id = Column(String, nullable=True)
    rebar_type_id = Column(String, nullable=True)
    specific_tag_id = Column(String, nullable=True)
    
    # Relationships
    calculation = relationship("Calculation")

class StockpileData(Base):
    """Stockpile data model for inventory constraints"""
    __tablename__ = "stockpile_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    calculation_id = Column(String, ForeignKey("calculations.id"), nullable=False)
    length = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    diameter = Column(Float, nullable=False)
    
    # Relationships
    calculation = relationship("Calculation")

class CalculationResult(Base):
    """Detailed calculation results"""
    __tablename__ = "calculation_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    calculation_id = Column(String, ForeignKey("calculations.id"), nullable=False)
    diameter = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    combination = Column(JSON, nullable=False)  # Array of combination values
    lengths = Column(JSON, nullable=False)  # Array of lengths used
    combined_length = Column(Float, nullable=False)
    target = Column(Float, nullable=False)
    waste = Column(Float, nullable=False)
    remaining_pieces = Column(JSON, nullable=False)  # Array of remaining pieces
    
    # Relationships
    calculation = relationship("Calculation")

class ExportHistory(Base):
    """Track export history for files"""
    __tablename__ = "export_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    calculation_id = Column(String, ForeignKey("calculations.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    file_path = Column(String, nullable=False)  # Supabase storage path
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    format = Column(String, nullable=False)  # excel, csv, json
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    calculation = relationship("Calculation")
    user = relationship("User")
