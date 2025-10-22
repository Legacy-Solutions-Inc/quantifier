"""
Service for managing project operations and database interactions
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

class ProjectService:
    """Service for managing project operations"""
    
    def __init__(self, db):
        self.db = db
    
    async def create_project(self, project_data: Dict[str, Any]) -> str:
        """
        Create a new project
        
        Args:
            project_data: Project data to store
            
        Returns:
            Project ID
        """
        try:
            # Generate project ID
            project_id = str(uuid.uuid4())
            project_data["id"] = project_id
            
            # Insert project into database
            response = self.db.table("projects").insert(project_data).execute()
            
            if response.data:
                return project_id
            else:
                raise Exception("Failed to create project record")
                
        except Exception as e:
            raise Exception(f"Database error creating project: {str(e)}")
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project by ID
        
        Args:
            project_id: Project ID
            
        Returns:
            Project data or None if not found
        """
        try:
            response = self.db.table("projects").select("*").eq("id", project_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            raise Exception(f"Database error getting project: {str(e)}")
    
    async def update_project(
        self, 
        project_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update project record
        
        Args:
            project_id: Project ID
            updates: Fields to update
            
        Returns:
            True if successful
        """
        try:
            updates["updated_at"] = datetime.utcnow()
            
            response = self.db.table("projects").update(updates).eq("id", project_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise Exception(f"Database error updating project: {str(e)}")
    
    async def delete_project(self, project_id: str) -> bool:
        """
        Delete project and related data
        
        Args:
            project_id: Project ID
            
        Returns:
            True if successful
        """
        try:
            # Delete related calculations first
            self.db.table("calculations").delete().eq("project_id", project_id).execute()
            
            # Delete project files
            self.db.table("project_files").delete().eq("project_id", project_id).execute()
            
            # Delete project
            response = self.db.table("projects").delete().eq("id", project_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise Exception(f"Database error deleting project: {str(e)}")
    
    async def list_projects(
        self, 
        user_id: str,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List projects for a user
        
        Args:
            user_id: User ID
            status: Filter by status
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of projects
        """
        try:
            query = self.db.table("projects").select("*").eq("user_id", user_id)
            
            if status:
                query = query.eq("status", status)
            
            query = query.range(offset, offset + limit - 1).order("created_at", desc=True)
            
            response = query.execute()
            return response.data
            
        except Exception as e:
            raise Exception(f"Database error listing projects: {str(e)}")
    
    async def get_project_count(
        self, 
        user_id: str,
        status: Optional[str] = None
    ) -> int:
        """
        Get total count of projects for a user
        
        Args:
            user_id: User ID
            status: Filter by status
            
        Returns:
            Total count
        """
        try:
            query = self.db.table("projects").select("id", count="exact").eq("user_id", user_id)
            
            if status:
                query = query.eq("status", status)
            
            response = query.execute()
            return response.count if hasattr(response, 'count') else 0
            
        except Exception as e:
            raise Exception(f"Database error getting project count: {str(e)}")
    
    async def get_project_statistics(self, project_id: str) -> Dict[str, Any]:
        """
        Get statistics for a specific project
        
        Args:
            project_id: Project ID
            
        Returns:
            Project statistics
        """
        try:
            # Get project info
            project = await self.get_project(project_id)
            if not project:
                raise Exception("Project not found")
            
            # Get calculation counts
            calc_query = self.db.table("calculations").select("status", count="exact").eq("project_id", project_id)
            calc_response = calc_query.execute()
            
            total_calculations = calc_response.count if hasattr(calc_response, 'count') else 0
            
            # Get completed calculations
            completed_query = self.db.table("calculations").select("id", count="exact").eq("project_id", project_id).eq("status", "completed")
            completed_response = completed_query.execute()
            completed_calculations = completed_response.count if hasattr(completed_response, 'count') else 0
            
            # Get waste statistics from completed calculations
            waste_query = self.db.table("calculations").select("results").eq("project_id", project_id).eq("status", "completed")
            waste_response = waste_query.execute()
            
            total_waste_saved = 0.0
            total_weight = 0.0
            calculation_count = 0
            
            for calc in waste_response.data:
                if calc.get("results"):
                    for diameter, result in calc["results"].items():
                        total_waste_saved += result.get("total_waste_weight", 0)
                        total_weight += result.get("total_commercial_weight", 0)
                        calculation_count += 1
            
            average_waste_percentage = 0.0
            if total_weight > 0:
                average_waste_percentage = (total_waste_saved / total_weight) * 100
            
            return {
                "total_projects": 1,  # This is for a single project
                "active_projects": 1 if project["status"] == "active" else 0,
                "total_calculations": total_calculations,
                "total_waste_saved": round(total_waste_saved, 2),
                "average_waste_percentage": round(average_waste_percentage, 2)
            }
            
        except Exception as e:
            raise Exception(f"Database error getting project statistics: {str(e)}")
    
    async def get_global_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get global statistics for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Global statistics
        """
        try:
            # Get project counts
            total_projects = await self.get_project_count(user_id)
            active_projects = await self.get_project_count(user_id, "active")
            
            # Get calculation counts
            calc_query = self.db.table("calculations").select("status", count="exact").eq("project_id", 
                self.db.table("projects").select("id").eq("user_id", user_id))
            calc_response = calc_query.execute()
            
            total_calculations = calc_response.count if hasattr(calc_response, 'count') else 0
            
            # Get waste statistics from all completed calculations
            waste_query = self.db.table("calculations").select("results").eq("status", "completed").in_("project_id", 
                self.db.table("projects").select("id").eq("user_id", user_id))
            waste_response = waste_query.execute()
            
            total_waste_saved = 0.0
            total_weight = 0.0
            calculation_count = 0
            
            for calc in waste_response.data:
                if calc.get("results"):
                    for diameter, result in calc["results"].items():
                        total_waste_saved += result.get("total_waste_weight", 0)
                        total_weight += result.get("total_commercial_weight", 0)
                        calculation_count += 1
            
            average_waste_percentage = 0.0
            if total_weight > 0:
                average_waste_percentage = (total_waste_saved / total_weight) * 100
            
            return {
                "total_projects": total_projects,
                "active_projects": active_projects,
                "total_calculations": total_calculations,
                "total_waste_saved": round(total_waste_saved, 2),
                "average_waste_percentage": round(average_waste_percentage, 2)
            }
            
        except Exception as e:
            raise Exception(f"Database error getting global statistics: {str(e)}")
    
    async def archive_project(self, project_id: str) -> bool:
        """
        Archive a project
        
        Args:
            project_id: Project ID
            
        Returns:
            True if successful
        """
        try:
            return await self.update_project(project_id, {"status": "archived"})
            
        except Exception as e:
            raise Exception(f"Database error archiving project: {str(e)}")
    
    async def restore_project(self, project_id: str) -> bool:
        """
        Restore an archived project
        
        Args:
            project_id: Project ID
            
        Returns:
            True if successful
        """
        try:
            return await self.update_project(project_id, {"status": "active"})
            
        except Exception as e:
            raise Exception(f"Database error restoring project: {str(e)}")
