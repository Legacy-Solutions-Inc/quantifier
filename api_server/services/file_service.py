"""
Service for managing file operations and validation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import io
import json

class FileService:
    """Service for managing file operations"""
    
    def __init__(self, db):
        self.db = db
    
    async def store_file_metadata(self, file_data: Dict[str, Any]) -> str:
        """
        Store file metadata in database
        
        Args:
            file_data: File metadata to store
            
        Returns:
            File ID
        """
        try:
            # Insert file metadata into database
            response = self.db.table("project_files").insert(file_data).execute()
            
            if response.data:
                return response.data[0]["id"]
            else:
                raise Exception("Failed to store file metadata")
                
        except Exception as e:
            raise Exception(f"Database error storing file metadata: {str(e)}")
    
    async def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get file metadata by ID
        
        Args:
            file_id: File ID
            
        Returns:
            File metadata or None if not found
        """
        try:
            response = self.db.table("project_files").select("*").eq("id", file_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            raise Exception(f"Database error getting file metadata: {str(e)}")
    
    async def list_files(
        self, 
        user_id: str,
        project_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List files for a user
        
        Args:
            user_id: User ID
            project_id: Filter by project ID
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of files
        """
        try:
            # Build query
            if project_id:
                # Get files for specific project
                query = self.db.table("project_files").select("*").eq("project_id", project_id)
            else:
                # Get files for user's projects
                project_ids = self.db.table("projects").select("id").eq("user_id", user_id)
                query = self.db.table("project_files").select("*").in_("project_id", project_ids)
            
            query = query.range(offset, offset + limit - 1).order("uploaded_at", desc=True)
            
            response = query.execute()
            return response.data
            
        except Exception as e:
            raise Exception(f"Database error listing files: {str(e)}")
    
    async def get_file_count(
        self, 
        user_id: str,
        project_id: Optional[str] = None
    ) -> int:
        """
        Get total count of files for a user
        
        Args:
            user_id: User ID
            project_id: Filter by project ID
            
        Returns:
            Total count
        """
        try:
            if project_id:
                # Count files for specific project
                query = self.db.table("project_files").select("id", count="exact").eq("project_id", project_id)
            else:
                # Count files for user's projects
                project_ids = self.db.table("projects").select("id").eq("user_id", user_id)
                query = self.db.table("project_files").select("id", count="exact").in_("project_id", project_ids)
            
            response = query.execute()
            return response.count if hasattr(response, 'count') else 0
            
        except Exception as e:
            raise Exception(f"Database error getting file count: {str(e)}")
    
    async def delete_file_metadata(self, file_id: str) -> bool:
        """
        Delete file metadata
        
        Args:
            file_id: File ID
            
        Returns:
            True if successful
        """
        try:
            response = self.db.table("project_files").delete().eq("id", file_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise Exception(f"Database error deleting file metadata: {str(e)}")
    
    async def validate_file_structure(self, content: bytes, filename: str) -> Dict[str, Any]:
        """
        Validate file structure and content
        
        Args:
            content: File content as bytes
            filename: Original filename
            
        Returns:
            Validation results
        """
        try:
            errors = []
            warnings = []
            data_preview = None
            detected_columns = []
            
            # Required columns for RSB data
            required_columns = ["Lengths", "Pcs", "Diameter"]
            optional_columns = [
                "TagID", "FloorID", "ZoneID", "LocationID", 
                "MemberTypeID", "RebarTypeID", "SpecificTagID"
            ]
            
            # Read file based on extension
            if filename.lower().endswith('.csv'):
                try:
                    df = pd.read_csv(io.BytesIO(content))
                except Exception as e:
                    errors.append(f"Failed to read CSV file: {str(e)}")
                    return {
                        "valid": False,
                        "errors": errors,
                        "warnings": warnings,
                        "data_preview": None,
                        "detected_columns": [],
                        "required_columns": required_columns
                    }
            else:
                try:
                    df = pd.read_excel(io.BytesIO(content))
                except Exception as e:
                    errors.append(f"Failed to read Excel file: {str(e)}")
                    return {
                        "valid": False,
                        "errors": errors,
                        "warnings": warnings,
                        "data_preview": None,
                        "detected_columns": [],
                        "required_columns": required_columns
                    }
            
            # Get detected columns
            detected_columns = df.columns.tolist()
            
            # Check for required columns
            missing_columns = [col for col in required_columns if col not in detected_columns]
            if missing_columns:
                errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Check for data types and values
            if "Lengths" in df.columns:
                if not pd.api.types.is_numeric_dtype(df["Lengths"]):
                    errors.append("Lengths column must contain numeric values")
                elif (df["Lengths"] <= 0).any():
                    errors.append("All lengths must be positive")
            
            if "Pcs" in df.columns:
                if not pd.api.types.is_numeric_dtype(df["Pcs"]):
                    errors.append("Pcs column must contain numeric values")
                elif (df["Pcs"] < 0).any():
                    errors.append("All piece counts must be non-negative")
            
            if "Diameter" in df.columns:
                if not pd.api.types.is_numeric_dtype(df["Diameter"]):
                    errors.append("Diameter column must contain numeric values")
                elif (df["Diameter"] <= 0).any():
                    errors.append("All diameters must be positive")
            
            # Check for empty data
            if df.empty:
                errors.append("File contains no data")
            elif len(df) == 0:
                errors.append("File contains no rows")
            
            # Check for duplicate rows
            if df.duplicated().any():
                warnings.append("File contains duplicate rows")
            
            # Check for missing values
            missing_values = df.isnull().sum()
            if missing_values.any():
                missing_cols = missing_values[missing_values > 0].index.tolist()
                warnings.append(f"Missing values found in columns: {', '.join(missing_cols)}")
            
            # Create data preview
            if not errors and not df.empty:
                data_preview = {
                    "total_rows": len(df),
                    "columns": detected_columns,
                    "sample_data": df.head(5).to_dict('records'),
                    "data_types": df.dtypes.to_dict(),
                    "missing_values": missing_values.to_dict()
                }
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "data_preview": data_preview,
                "detected_columns": detected_columns,
                "required_columns": required_columns
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"File validation failed: {str(e)}"],
                "warnings": [],
                "data_preview": None,
                "detected_columns": [],
                "required_columns": required_columns
            }
    
    async def parse_file_data(self, content: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse file data into structured format
        
        Args:
            content: File content as bytes
            filename: Original filename
            
        Returns:
            Parsed data structure
        """
        try:
            # Read file based on extension
            if filename.lower().endswith('.csv'):
                df = pd.read_csv(io.BytesIO(content))
            else:
                df = pd.read_excel(io.BytesIO(content))
            
            # Convert to structured format
            rebar_data = []
            stockpile_data = []
            
            for _, row in df.iterrows():
                # Create rebar item
                rebar_item = {
                    "length": float(row["Lengths"]),
                    "pieces": int(row["Pcs"]),
                    "diameter": float(row["Diameter"]),
                    "tag_id": row.get("TagID"),
                    "floor_id": row.get("FloorID"),
                    "zone_id": row.get("ZoneID"),
                    "location_id": row.get("LocationID"),
                    "member_type_id": row.get("MemberTypeID"),
                    "rebar_type_id": row.get("RebarTypeID"),
                    "specific_tag_id": row.get("SpecificTagID")
                }
                
                # Remove None values
                rebar_item = {k: v for k, v in rebar_item.items() if v is not None}
                
                rebar_data.append(rebar_item)
            
            return {
                "rebar_data": rebar_data,
                "stockpile_data": stockpile_data,  # Will be populated if stockpile sheet exists
                "metadata": {
                    "total_rows": len(df),
                    "columns": df.columns.tolist(),
                    "filename": filename
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse file data: {str(e)}")
    
    async def get_file_statistics(self, file_id: str) -> Dict[str, Any]:
        """
        Get statistics for a file
        
        Args:
            file_id: File ID
            
        Returns:
            File statistics
        """
        try:
            # Get file metadata
            file_metadata = await self.get_file_metadata(file_id)
            
            if not file_metadata:
                raise Exception("File not found")
            
            # Get file from storage
            file_content = self.db.storage.from_("files").download(file_metadata["file_path"])
            
            if not file_content:
                raise Exception("File not found in storage")
            
            # Parse file data
            parsed_data = await self.parse_file_data(file_content, file_metadata["filename"])
            
            # Calculate statistics
            rebar_data = parsed_data["rebar_data"]
            
            if not rebar_data:
                return {
                    "total_items": 0,
                    "total_pieces": 0,
                    "total_length": 0.0,
                    "diameter_breakdown": {},
                    "length_breakdown": {}
                }
            
            # Basic statistics
            total_items = len(rebar_data)
            total_pieces = sum(item["pieces"] for item in rebar_data)
            total_length = sum(item["length"] * item["pieces"] for item in rebar_data)
            
            # Diameter breakdown
            diameter_breakdown = {}
            for item in rebar_data:
                diameter = item["diameter"]
                if diameter not in diameter_breakdown:
                    diameter_breakdown[diameter] = {
                        "count": 0,
                        "total_pieces": 0,
                        "total_length": 0.0
                    }
                diameter_breakdown[diameter]["count"] += 1
                diameter_breakdown[diameter]["total_pieces"] += item["pieces"]
                diameter_breakdown[diameter]["total_length"] += item["length"] * item["pieces"]
            
            # Length breakdown
            length_breakdown = {}
            for item in rebar_data:
                length = item["length"]
                if length not in length_breakdown:
                    length_breakdown[length] = {
                        "count": 0,
                        "total_pieces": 0,
                        "diameters": set()
                    }
                length_breakdown[length]["count"] += 1
                length_breakdown[length]["total_pieces"] += item["pieces"]
                length_breakdown[length]["diameters"].add(item["diameter"])
            
            # Convert sets to lists for JSON serialization
            for length_data in length_breakdown.values():
                length_data["diameters"] = list(length_data["diameters"])
            
            return {
                "total_items": total_items,
                "total_pieces": total_pieces,
                "total_length": round(total_length, 2),
                "diameter_breakdown": diameter_breakdown,
                "length_breakdown": length_breakdown
            }
            
        except Exception as e:
            raise Exception(f"Failed to get file statistics: {str(e)}")
