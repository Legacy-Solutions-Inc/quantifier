"""
Manager class for handling multiple combinators with different diameters.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from .combinator import Combinator, CombinatorConfig

class CombinatorManager:
    """Manages multiple combinators for different bar diameters."""
    
    # Special lengths for RSB with no wastage
    SPECIAL_LENGTHS = [0.75, 1.25, 2.25, 3.75, 5.25]
    
    def __init__(self):
        # initializes an empty dictionary that is tied to the diameter: Dict[diameter, CombinatorInstance]
        self.combinators: Dict[float, Combinator] = {}
        self.current_diameter: Optional[float] = None
        
    def round_off(self, df: pd.DataFrame, decimal_places: int = 2, tolerance: float = 0.02) -> pd.DataFrame:
        """
        Round lengths considering special RSB lengths and tolerance.
        
        Args:
            df: DataFrame containing the lengths to round
            decimal_places: Number of decimal places to round to
            tolerance: Maximum difference to round down instead of up
            
        Returns:
            DataFrame with both original and rounded lengths
        """
        def smart_round(x: float) -> float:
            # First check if we're close to any special length
            for special in self.SPECIAL_LENGTHS:
                if abs(x - special) <= tolerance:
                    return special
                    
            # If not near a special length, apply normal rounding with tolerance
            rounded_down = np.floor(x * (10 ** decimal_places)) / (10 ** decimal_places)
            rounded_up = np.ceil(x * (10 ** decimal_places)) / (10 ** decimal_places)
            # Check difference to next rounded value
            diff_to_next = rounded_up - x
            
            # If difference to next value is within tolerance, round down
            # Otherwise round up to ensure sufficient length
            if diff_to_next <= tolerance:
                return rounded_down
            return rounded_up
            
        # Create a copy to avoid modifying original
        df = df.copy()
        # Store original lengths and create rounded lengths column
        df['Original_Lengths'] = df['Lengths'].copy()
        df['Rounded_Lengths'] = df['Lengths'].apply(smart_round)
        
        return df
        
    def load_data(self, df: pd.DataFrame, apply_rounding: bool = False, 
                  decimal_places: int = 2, tolerance: float = 0.02) -> None:
        """
        Load data from DataFrame and create combinators for each diameter.
        Groups identical lengths and sums their quantities for each diameter.
        
        Args:
            df: DataFrame containing Lengths, Pcs, and Diameter columns
            apply_rounding: Whether to apply length rounding before processing
            decimal_places: Number of decimal places to round to if apply_rounding is True
            tolerance: Tolerance for rounding if apply_rounding is True
        """
        if apply_rounding:
            df = self.round_off(df, decimal_places, tolerance)
            # Use Rounded_Lengths for grouping but keep Original_Lengths for calculations
            grouping_col = 'Rounded_Lengths'
        else:
            df['Original_Lengths'] = df['Lengths'].copy()
            grouping_col = 'Lengths'
            
        # Group data by diameter
        grouped = df.groupby('Diameter')
        
        # Create combinators for each diameter
        for diameter, group_df in grouped:
            # Group identical lengths and sum their pieces
            aggregated_df = (group_df.groupby(grouping_col)['Pcs']
                           .sum()
                           .reset_index())
            
            # Use the original lengths for the combinator
            if apply_rounding:
                original_lengths = []
                for rounded_len in aggregated_df[grouping_col]:
                    # Find the original lengths that correspond to this rounded length
                    orig_lens = group_df[group_df[grouping_col] == rounded_len]['Original_Lengths'].unique()
                    # Use the maximum original length to ensure sufficient material
                    original_lengths.append(max(orig_lens))
            else:
                original_lengths = aggregated_df[grouping_col].tolist()
            
            config = CombinatorConfig(
                diameter=diameter,
                lengths=original_lengths,
                pcs=aggregated_df['Pcs'].tolist(),
                targets=group_df['Target'].unique().tolist() if 'Target' in group_df else None,
            )
            self.combinators[diameter] = Combinator(config)
            
        # Set current diameter to first one
        if self.combinators:
            self.current_diameter = min(self.combinators.keys())
            
    def get_diameters(self) -> List[float]:
        """Get list of available diameters."""
        return sorted(self.combinators.keys())
        
    def set_current_diameter(self, diameter: float) -> None:
        """Set the current active diameter."""
        if diameter in self.combinators:
            self.current_diameter = diameter
            
    def get_current_combinator(self) -> Optional[Combinator]:
        """Get the currently active combinator."""
        if self.current_diameter is not None:
            return self.combinators.get(self.current_diameter)
        return None
        
    def run_all(self) -> None:
        """Run combination process for all combinators."""
        for combinator in self.combinators.values():
            combinator.iterate_combinations()
            combinator.calculate_waste()
            
    def get_total_stats(self) -> dict:
        """
        Calculate total statistics across all combinators.
        
        Returns:
            Dictionary containing total statistics
        """
        total_weight = 0
        total_waste = 0
        total_utilized = 0
        commercial_pieces = 0
        
        for combinator in self.combinators.values():
            # Calculate weights for this diameter
            for result in combinator.results:
                utilized_weight = (result.quantity * result.combined_length * 
                                 combinator.length_to_weight)
                total_weight_this = result.quantity * result.target * combinator.length_to_weight
                
                total_utilized += utilized_weight
                total_weight += total_weight_this
                total_waste += result.waste
                commercial_pieces += result.quantity
                
        # Calculate total waste percentage
        waste_percentage = ((total_weight - total_utilized) / total_weight * 100 
                          if total_weight > 0 else 0)
        
        return {
            'total_weight': round(total_weight, 2),
            'total_waste': round(total_waste, 2),
            'waste_percentage': round(waste_percentage, 2),
            'commercial_pieces': commercial_pieces
        }
        
    def reset(self) -> None:
        """Reset all combinators."""
        for combinator in self.combinators.values():
            combinator.reset()
        
    def create_summary_dataframe(self) -> pd.DataFrame:
        """
        Create a summary DataFrame with results from all diameters.
        
        Returns:
            DataFrame containing summary information
        """
        data = []
        
        for diameter, combinator in sorted(self.combinators.items()):
            total_weight = 0
            total_utilized = 0
            total_pieces = 0
            
            for result in combinator.results:
                utilized = result.quantity * result.combined_length * combinator.length_to_weight
                total = result.quantity * result.target * combinator.length_to_weight
                total_utilized += utilized
                total_weight += total
                total_pieces += result.quantity
                
            waste_pct = ((total_weight - total_utilized) / total_weight * 100 
                        if total_weight > 0 else 0)
                        
            data.append({
                'Diameter': diameter,
                'Total Weight (kg)': round(total_weight, 2),
                'Waste (kg)': round(total_weight - total_utilized, 2),
                'Waste %': round(waste_pct, 2),
                'Commercial Pieces': total_pieces
            })
            
        # Add total row
        stats = self.get_total_stats()
        data.append({
            'Diameter': 'TOTAL',
            'Total Weight (kg)': stats['total_weight'],
            'Waste (kg)': stats['total_waste'],
            'Waste %': stats['waste_percentage'],
            'Commercial Pieces': stats['commercial_pieces']
        })
        
        return pd.DataFrame(data)