"""
Service for managing calculation operations and database interactions
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

class CalculationService:
    """Service for managing calculation operations"""
    
    def __init__(self, db):
        self.db = db
    
    async def create_calculation(self, calculation_data: Dict[str, Any]) -> str:
        """
        Create a new calculation record
        
        Args:
            calculation_data: Calculation data to store
            
        Returns:
            Calculation ID
        """
        try:
            # Insert calculation into database
            response = self.db.table("calculations").insert(calculation_data).execute()
            
            if response.data:
                return response.data[0]["id"]
            else:
                raise Exception("Failed to create calculation record")
                
        except Exception as e:
            raise Exception(f"Database error creating calculation: {str(e)}")
    
    async def get_calculation(self, calculation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get calculation by ID
        
        Args:
            calculation_id: Calculation ID
            
        Returns:
            Calculation data or None if not found
        """
        try:
            response = self.db.table("calculations").select("*").eq("id", calculation_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            raise Exception(f"Database error getting calculation: {str(e)}")
    
    async def update_calculation(
        self, 
        calculation_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update calculation record
        
        Args:
            calculation_id: Calculation ID
            updates: Fields to update
            
        Returns:
            True if successful
        """
        try:
            updates["updated_at"] = datetime.utcnow()
            
            response = self.db.table("calculations").update(updates).eq("id", calculation_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise Exception(f"Database error updating calculation: {str(e)}")
    
    async def delete_calculation(self, calculation_id: str) -> bool:
        """
        Delete calculation and related data
        
        Args:
            calculation_id: Calculation ID
            
        Returns:
            True if successful
        """
        try:
            # Delete calculation results first
            self.db.table("calculation_results").delete().eq("calculation_id", calculation_id).execute()
            
            # Delete rebar data
            self.db.table("rebar_data").delete().eq("calculation_id", calculation_id).execute()
            
            # Delete stockpile data
            self.db.table("stockpile_data").delete().eq("calculation_id", calculation_id).execute()
            
            # Delete calculation
            response = self.db.table("calculations").delete().eq("id", calculation_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise Exception(f"Database error deleting calculation: {str(e)}")
    
    async def list_calculations(
        self, 
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List calculations with optional filtering
        
        Args:
            project_id: Filter by project ID
            status: Filter by status
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of calculations
        """
        try:
            query = self.db.table("calculations").select("*")
            
            if project_id:
                query = query.eq("project_id", project_id)
            if status:
                query = query.eq("status", status)
            
            query = query.range(offset, offset + limit - 1).order("created_at", desc=True)
            
            response = query.execute()
            return response.data
            
        except Exception as e:
            raise Exception(f"Database error listing calculations: {str(e)}")
    
    async def get_calculation_count(
        self, 
        project_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """
        Get total count of calculations
        
        Args:
            project_id: Filter by project ID
            status: Filter by status
            
        Returns:
            Total count
        """
        try:
            query = self.db.table("calculations").select("id", count="exact")
            
            if project_id:
                query = query.eq("project_id", project_id)
            if status:
                query = query.eq("status", status)
            
            response = query.execute()
            return response.count if hasattr(response, 'count') else 0
            
        except Exception as e:
            raise Exception(f"Database error getting calculation count: {str(e)}")
    
    async def store_calculation_results(
        self, 
        calculation_id: str, 
        results: Dict[str, Any]
    ) -> bool:
        """
        Store calculation results
        
        Args:
            calculation_id: Calculation ID
            results: Results to store
            
        Returns:
            True if successful
        """
        try:
            # Update calculation with results
            await self.update_calculation(calculation_id, {
                "results": results,
                "status": "completed",
                "completed_at": datetime.utcnow()
            })
            
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
                    
                    self.db.table("calculation_results").insert(result_data).execute()
            
            return True
            
        except Exception as e:
            raise Exception(f"Database error storing results: {str(e)}")
    
    async def get_calculation_results(self, calculation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed calculation results
        
        Args:
            calculation_id: Calculation ID
            
        Returns:
            Detailed results or None if not found
        """
        try:
            # Get calculation
            calculation = await self.get_calculation(calculation_id)
            if not calculation:
                return None
            
            # Get detailed results
            response = self.db.table("calculation_results").select("*").eq("calculation_id", calculation_id).execute()
            
            # Group results by diameter
            results_by_diameter = {}
            for result in response.data:
                diameter = result["diameter"]
                if diameter not in results_by_diameter:
                    results_by_diameter[diameter] = []
                
                results_by_diameter[diameter].append({
                    "quantity": result["quantity"],
                    "combination": result["combination"],
                    "lengths": result["lengths"],
                    "combined_length": result["combined_length"],
                    "target": result["target"],
                    "waste": result["waste"],
                    "remaining_pieces": result["remaining_pieces"]
                })
            
            return results_by_diameter
            
        except Exception as e:
            raise Exception(f"Database error getting results: {str(e)}")
    
    async def reset_calculation(self, calculation_id: str) -> bool:
        """
        Reset calculation to pending status and clear results
        
        Args:
            calculation_id: Calculation ID
            
        Returns:
            True if successful
        """
        try:
            # Clear results
            self.db.table("calculation_results").delete().eq("calculation_id", calculation_id).execute()
            
            # Reset calculation
            await self.update_calculation(calculation_id, {
                "status": "pending",
                "results": None,
                "error_message": None,
                "completed_at": None
            })
            
            return True
            
        except Exception as e:
            raise Exception(f"Database error resetting calculation: {str(e)}")
    
    async def get_calculation_statistics(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get calculation statistics
        
        Args:
            project_id: Filter by project ID
            
        Returns:
            Statistics dictionary
        """
        try:
            # Get basic counts
            total_calculations = await self.get_calculation_count(project_id)
            completed_calculations = await self.get_calculation_count(project_id, "completed")
            failed_calculations = await self.get_calculation_count(project_id, "failed")
            
            # Get calculations with results for waste analysis
            query = self.db.table("calculations").select("results").eq("status", "completed")
            if project_id:
                query = query.eq("project_id", project_id)
            
            response = query.execute()
            
            total_waste_saved = 0.0
            total_weight = 0.0
            calculation_count = 0
            
            for calc in response.data:
                if calc.get("results"):
                    for diameter, result in calc["results"].items():
                        total_waste_saved += result.get("total_waste_weight", 0)
                        total_weight += result.get("total_commercial_weight", 0)
                        calculation_count += 1
            
            average_waste_percentage = 0.0
            if total_weight > 0:
                average_waste_percentage = (total_waste_saved / total_weight) * 100
            
            return {
                "total_calculations": total_calculations,
                "completed_calculations": completed_calculations,
                "failed_calculations": failed_calculations,
                "total_waste_saved": round(total_waste_saved, 2),
                "average_waste_percentage": round(average_waste_percentage, 2),
                "total_weight_processed": round(total_weight, 2)
            }
            
        except Exception as e:
            raise Exception(f"Database error getting statistics: {str(e)}")
