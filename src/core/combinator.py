"""
Core combinator module for the RSB Combinator.
Contains the main combination generation and optimization logic.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

from .scoring import ScoringSystem
from .stockpile import StockpileManager

@dataclass
class CombinatorConfig:
    """Configuration for the Combinator."""
    tolerance: float = 0.0
    tolerance_step: float = 0.1
    targets: List[float] = None
    lengths: List[float] = None
    pcs: List[int] = None
    diameter: float = 0.0

    def __post_init__(self):
        """Set default values for None fields."""
        if self.targets is None:
            self.targets = [12, 10.5, 9, 7.5]
        if self.lengths is None:
            self.lengths = []
        if self.pcs is None:
            self.pcs = []

class CombinationResult:
    """Stores results of a combination calculation."""
    def __init__(self, quantity: int, combination: List[int], 
                 lengths: List[float], combined_length: float,
                 target: float, remaining_pcs: List[int]):
        self.quantity = quantity
        self.combination = combination
        self.lengths = lengths
        self.combined_length = combined_length
        self.target = target
        self.remaining_pcs = remaining_pcs
        self.waste = 0.0

class Combinator:
    """Main combinator class with optimized algorithms."""
    
    def __init__(self, config: CombinatorConfig):
        self.config = config
        self.scoring = ScoringSystem()
        self.stockpile = StockpileManager()
        
        # Convert lists to numpy arrays for better performance
        self.targets = np.array(config.targets)
        self.lengths = np.array(config.lengths)
        self.pcs = np.array(config.pcs)
        
        # Store original values
        self.original_targets = self.targets.copy()
        self.original_lengths = self.lengths.copy()
        self.original_pcs = self.pcs.copy()
        
        # Results storage
        self.results: List[CombinationResult] = []
        self.combinations: List[np.ndarray] = []
        self.scores: List[float] = []
        
        # Calculate weight conversion factor
        self.length_to_weight = 0.0
        if config.diameter > 0:
            self.set_diameter(config.diameter)
            
    def set_diameter(self, diameter: float) -> None:
        """Set bar diameter and calculate weight conversion factor."""
        self.config.diameter = diameter
        self.length_to_weight = (math.pi / 4) * 7850 * ((diameter / 1000) ** 2)
        
    def generate_combinations(self, target: float, lengths: np.ndarray, 
                            max_pieces: np.ndarray) -> List[List[int]]:
        """
        Generate valid combinations for target length.
        Uses dynamic programming for efficiency.
        """
        if len(lengths) == 0:
            return []
            
        if len(lengths) == 1:
            length = lengths[0]
            min_pieces = math.ceil((target - self.config.tolerance) / length)
            max_pieces_allowed = min(math.floor(target / length), max_pieces[0])
            
            return [[pieces] for pieces in range(min_pieces, max_pieces_allowed + 1)]
            
        results = []
        length = lengths[-1]
        max_pieces_current = min(math.floor(target / length), max_pieces[-1])
        
        for pieces in range(max_pieces_current + 1):
            remaining_target = target - pieces * length
            if remaining_target < -self.config.tolerance:
                break
                
            sub_combinations = self.generate_combinations(
                remaining_target, 
                lengths[:-1],
                max_pieces[:-1]
            )
            
            for sub_comb in sub_combinations:
                results.append(sub_comb + [pieces])
                
        return results
        
    def find_best_combination(self, target: float) -> Optional[np.ndarray]:
        """Find the best scoring combination for a target length."""
        combinations = self.generate_combinations(target, self.lengths, self.pcs)
        if not combinations:
            return None
            
        # Convert to numpy array for faster operations
        combinations_array = np.array(combinations)
        
        # Calculate scores for all combinations
        scores = np.array([
            self.scoring.score_combination(comb, self.lengths, self.pcs)
            for comb in combinations_array
        ])
        
        # Find best combination
        best_idx = np.argmax(scores)
        self.combinations = combinations_array
        self.scores = scores
        
        return combinations_array[best_idx]
        
    def get_largest_multiple(self, combination: np.ndarray) -> int:
        """Calculate largest possible multiple for a combination."""
        non_zero_mask = combination > 0
        if not np.any(non_zero_mask):
            return 0
            
        multiples = self.pcs[non_zero_mask] // combination[non_zero_mask]
        multiple = np.min(multiples)
        
        if self.stockpile.has_items:
            target_pcs, _ = self.stockpile.get_current_item()
            multiple = min(multiple, target_pcs)
            
        return multiple
        
    def process_combination(self, combination: np.ndarray, 
                          target: float) -> CombinationResult:
        """Process a combination and update state."""
        quantity = self.get_largest_multiple(combination)
        
        # Update remaining pieces
        remaining_pcs = self.pcs - (quantity * combination)
        
        # Calculate combined length
        combined_length = np.sum(self.lengths * combination)
        
        result = CombinationResult(
            quantity=quantity,
            combination=combination.tolist(),
            lengths=self.lengths.tolist(),
            combined_length=combined_length,
            target=target,
            remaining_pcs=remaining_pcs.tolist()
        )
        
        # Update state
        self.pcs = remaining_pcs
        self.results.append(result)
        
        # Update stockpile if needed
        if self.stockpile.has_items:
            self.stockpile.update_quantity(quantity)
            
        return result
        
    def iterate_combinations(self) -> None:
        """Main iteration loop for finding combinations."""
        self.results = []
        self.scoring.calculate_length_scores(self.lengths)
        
        # Keep track of current target index
        current_target_idx = 0
        
        while np.any(self.pcs > 0):
            # Get current target length
            target = self.targets[current_target_idx]
            if self.stockpile.has_items:
                _, target = self.stockpile.get_current_item()
                
            self.scoring.calculate_solo_waste_scores(self.lengths, self.targets)
            combination = self.find_best_combination(target)
            
            if combination is None:
                # Try next target length
                current_target_idx = (current_target_idx + 1) % len(self.targets)
                
                # If we've tried all targets, increase tolerance
                if current_target_idx == 0:
                    self.config.tolerance += self.config.tolerance_step
                continue
                
            self.process_combination(combination, target)
            
            # Reset target index after successful combination
            current_target_idx = 0
            
    def calculate_waste(self) -> None:
        """Calculate waste for all results."""
        for result in self.results:
            utilized_weight = (result.quantity * result.combined_length * 
                             self.length_to_weight)
            total_weight = result.quantity * result.target * self.length_to_weight
            result.waste = round(total_weight - utilized_weight, 2)
            
    def get_total_waste_percentage(self) -> float:
        """Calculate total waste percentage."""
        total_utilized = sum(result.quantity * result.combined_length 
                           for result in self.results)
        total_target = sum(result.quantity * result.target 
                          for result in self.results)
        
        if total_target == 0:
            return 0.0
            
        return ((total_target - total_utilized) / total_target) * 100
        
    def reset(self) -> None:
        """Reset combinator to initial state."""
        self.targets = self.original_targets.copy()
        self.lengths = self.original_lengths.copy()
        self.pcs = self.original_pcs.copy()
        self.config.tolerance = 0
        self.results = []
        self.combinations = []
        self.scores = []
        self.stockpile.clear() 