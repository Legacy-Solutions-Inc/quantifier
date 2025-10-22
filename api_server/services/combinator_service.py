"""
Service for handling RSB combinator operations
Integrates the existing combinator logic with the web API
"""

import sys
import os
import asyncio
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# Add the parent directory to the path to import the core modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.combinator import Combinator, CombinatorConfig, CombinationResult
from src.core.combinator_manager import CombinatorManager
from src.core.stockpile import StockpileManager
from api_server.models.schemas import (
    CalculationRequest, CalculationResult, CombinationResult as SchemaCombinationResult,
    RebarItem, StockpileItem
)

class CombinatorService:
    """Service for handling RSB combinator operations"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_calculation(self, request: CalculationRequest) -> Dict[float, CalculationResult]:
        """
        Process a calculation request using the combinator engine
        
        Args:
            request: Calculation request with rebar data and parameters
            
        Returns:
            Dictionary mapping diameter to calculation results
        """
        try:
            # Group rebar data by diameter
            diameter_groups = self._group_by_diameter(request.rebar_data)
            
            results = {}
            
            # Process each diameter group
            for diameter, rebar_items in diameter_groups.items():
                # Create combinator configuration
                config = self._create_combinator_config(
                    diameter, 
                    rebar_items, 
                    request.target_lengths,
                    request.tolerance,
                    request.tolerance_step
                )
                
                # Create and run combinator
                combinator = Combinator(config)
                
                # Add stockpile constraints if specified
                if request.use_stockpile and request.stockpile_data:
                    self._apply_stockpile_constraints(combinator, request.stockpile_data, diameter)
                
                # Run optimization
                combinator.iterate_combinations()
                combinator.calculate_waste()
                
                # Convert results to API format
                results[diameter] = self._convert_combinator_results(combinator)
            
            return results
            
        except Exception as e:
            raise Exception(f"Calculation processing failed: {str(e)}")
    
    def _group_by_diameter(self, rebar_data: List[RebarItem]) -> Dict[float, List[RebarItem]]:
        """Group rebar items by diameter"""
        groups = {}
        for item in rebar_data:
            diameter = item.diameter
            if diameter not in groups:
                groups[diameter] = []
            groups[diameter].append(item)
        return groups
    
    def _create_combinator_config(
        self, 
        diameter: float, 
        rebar_items: List[RebarItem], 
        target_lengths: List[float],
        tolerance: float,
        tolerance_step: float
    ) -> CombinatorConfig:
        """Create combinator configuration from rebar items"""
        
        # Extract data
        lengths = [item.length for item in rebar_items]
        pieces = [item.pieces for item in rebar_items]
        
        # Extract tagging information
        tag_ids = [item.tag_id for item in rebar_items if item.tag_id]
        floor_ids = [item.floor_id for item in rebar_items if item.floor_id]
        zone_ids = [item.zone_id for item in rebar_items if item.zone_id]
        location_ids = [item.location_id for item in rebar_items if item.location_id]
        member_type_ids = [item.member_type_id for item in rebar_items if item.member_type_id]
        rebar_type_ids = [item.rebar_type_id for item in rebar_items if item.rebar_type_id]
        specific_tag_ids = [item.specific_tag_id for item in rebar_items if item.specific_tag_id]
        
        return CombinatorConfig(
            diameter=diameter,
            lengths=lengths,
            pcs=pieces,
            targets=target_lengths,
            tolerance=tolerance,
            tolerance_step=tolerance_step,
            tagID=tag_ids if tag_ids else None,
            floorID=floor_ids if floor_ids else None,
            zoneID=zone_ids if zone_ids else None,
            locationID=location_ids if location_ids else None,
            member_typeID=member_type_ids if member_type_ids else None,
            rebar_typeID=rebar_type_ids if rebar_type_ids else None,
            specific_tagID=specific_tag_ids if specific_tag_ids else None
        )
    
    def _apply_stockpile_constraints(
        self, 
        combinator: Combinator, 
        stockpile_data: List[StockpileItem], 
        diameter: float
    ):
        """Apply stockpile constraints to combinator"""
        # Filter stockpile data for current diameter
        diameter_stockpile = [item for item in stockpile_data if item.diameter == diameter]
        
        if diameter_stockpile:
            # Create stockpile manager
            stockpile_manager = StockpileManager()
            
            # Add stockpile items
            lengths = [item.length for item in diameter_stockpile]
            quantities = [item.quantity for item in diameter_stockpile]
            stockpile_manager.add_items(lengths, quantities)
            
            # Update combinator stockpile
            combinator.stockpile = stockpile_manager
    
    def _convert_combinator_results(self, combinator: Combinator) -> CalculationResult:
        """Convert combinator results to API format"""
        
        # Convert combination results
        schema_results = []
        for result in combinator.results:
            schema_result = SchemaCombinationResult(
                quantity=result.quantity,
                combination=result.combination,
                lengths=result.lengths,
                combined_length=result.combined_length,
                target=result.target,
                waste=result.waste,
                remaining_pieces=result.remaining_pcs
            )
            schema_results.append(schema_result)
        
        # Calculate statistics
        total_utilized_weight = sum(
            result.quantity * result.combined_length * combinator.length_to_weight 
            for result in combinator.results
        )
        total_commercial_weight = sum(
            result.quantity * result.target * combinator.length_to_weight 
            for result in combinator.results
        )
        total_waste_weight = total_commercial_weight - total_utilized_weight
        waste_percentage = combinator.get_total_waste_percentage()
        
        return CalculationResult(
            diameter=combinator.config.diameter,
            results=schema_results,
            total_waste_percentage=waste_percentage,
            total_utilized_weight=round(total_utilized_weight, 2),
            total_commercial_weight=round(total_commercial_weight, 2),
            total_waste_weight=round(total_waste_weight, 2)
        )
    
    async def validate_input_data(self, request: CalculationRequest) -> Dict[str, Any]:
        """
        Validate input data for calculation
        
        Args:
            request: Calculation request to validate
            
        Returns:
            Validation results with errors and warnings
        """
        errors = []
        warnings = []
        
        # Validate target lengths
        if not request.target_lengths or len(request.target_lengths) == 0:
            errors.append("At least one target length is required")
        
        if any(length <= 0 for length in request.target_lengths):
            errors.append("All target lengths must be positive")
        
        # Validate rebar data
        if not request.rebar_data or len(request.rebar_data) == 0:
            errors.append("At least one rebar item is required")
        
        for i, item in enumerate(request.rebar_data):
            if item.length <= 0:
                errors.append(f"Rebar item {i+1}: Length must be positive")
            if item.pieces < 0:
                errors.append(f"Rebar item {i+1}: Pieces cannot be negative")
            if item.diameter <= 0:
                errors.append(f"Rebar item {i+1}: Diameter must be positive")
        
        # Check for achievable combinations
        if not errors:
            try:
                # Quick feasibility check
                max_length = max(item.length for item in request.rebar_data)
                min_target = min(request.target_lengths)
                
                if max_length < min_target:
                    warnings.append("No single rebar length can achieve the minimum target length")
                
            except Exception as e:
                warnings.append(f"Could not perform feasibility check: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    async def get_optimization_suggestions(self, request: CalculationRequest) -> Dict[str, Any]:
        """
        Get suggestions for optimizing the calculation
        
        Args:
            request: Calculation request to analyze
            
        Returns:
            Optimization suggestions
        """
        suggestions = []
        
        # Analyze rebar lengths
        lengths = [item.length for item in request.rebar_data]
        unique_lengths = set(lengths)
        
        if len(unique_lengths) < len(lengths):
            suggestions.append("Consider consolidating duplicate rebar lengths")
        
        # Check for special RSB lengths
        special_lengths = [0.75, 1.25, 2.25, 3.75, 5.25]
        has_special_lengths = any(length in special_lengths for length in unique_lengths)
        
        if not has_special_lengths:
            suggestions.append("Consider using standard RSB lengths (0.75, 1.25, 2.25, 3.75, 5.25) for better optimization")
        
        # Analyze target lengths
        target_lengths = request.target_lengths
        if len(target_lengths) > 5:
            suggestions.append("Consider reducing the number of target lengths for better optimization")
        
        # Check tolerance settings
        if request.tolerance == 0:
            suggestions.append("Consider setting a small tolerance (> 0) for better combination finding")
        
        return {
            "suggestions": suggestions,
            "estimated_complexity": self._estimate_complexity(request)
        }
    
    def _estimate_complexity(self, request: CalculationRequest) -> str:
        """Estimate calculation complexity"""
        total_combinations = 1
        for item in request.rebar_data:
            total_combinations *= (item.pieces + 1)
        
        if total_combinations < 1000:
            return "Low"
        elif total_combinations < 10000:
            return "Medium"
        else:
            return "High"
