"""
Scoring module for the RSB Combinator.
Contains classes and functions for calculating and managing scores for combinations.
"""

import numpy as np

class ScoringSystem:
    """Handles scoring calculations for combinations."""
    
    def __init__(self, pcs_weight=2, waste_weight=2, length_weight=2):
        self.pcs_weight = pcs_weight
        self.waste_weight = waste_weight
        self.length_weight = length_weight
        
        self.lengths_score = np.array([])
        self.solo_waste_score = np.array([])
    
    def calculate_solo_waste_score(self, length, targets):
        """
        Calculate waste score for a single length.
        
        Args:
            length (float): Length to score
            targets (np.ndarray): Target lengths
            
        Returns:
            float: Normalized waste score
        """
        waste = np.min(targets - (np.floor(targets / length) * length))
        max_waste = np.max(targets)
        score = waste / max_waste
        return score * self.waste_weight
    
    def calculate_solo_waste_scores(self, lengths, targets):
        """Calculate waste scores for all lengths."""
        self.solo_waste_score = np.array([
            self.calculate_solo_waste_score(length, targets) 
            for length in lengths
        ])
        return self.solo_waste_score
    
    def calculate_length_score(self, length, lengths):
        """
        Calculate normalized length score.
        
        Args:
            length (float): Length to score
            lengths (np.ndarray): All available lengths
            
        Returns:
            float: Normalized length score
        """
        max_length = np.max(lengths)
        score = length / max_length * self.length_weight
        return score
    
    def calculate_length_scores(self, lengths):
        """Calculate length scores for all lengths."""
        self.lengths_score = np.array([
            self.calculate_length_score(length, lengths)
            for length in lengths
        ])
        return self.lengths_score
    
    def calculate_pcs_scores(self, pcs):
        """
        Calculate normalized piece scores.
        
        Args:
            pcs (np.ndarray): Piece counts
            
        Returns:
            np.ndarray: Array of normalized piece scores
        """
        total_pcs = np.sum(pcs)
        return (pcs / total_pcs) * self.pcs_weight if total_pcs > 0 else np.zeros_like(pcs)
    
    def score_combination(self, combination, lengths, pcs):
        """
        Score a specific combination.
        
        Args:
            combination (np.ndarray): Combination to score
            lengths (np.ndarray): Available lengths
            pcs (np.ndarray): Available pieces
            
        Returns:
            float: Total score for the combination
        """
        # Normalize waste scores
        total_waste_score = np.sum(self.solo_waste_score)
        waste_percentages = (self.solo_waste_score / total_waste_score 
                           if total_waste_score > 0 else np.zeros_like(self.solo_waste_score))
        
        # Normalize length scores
        total_length_score = np.sum(self.lengths_score)
        length_percentages = (self.lengths_score / total_length_score 
                            if total_length_score > 0 else np.zeros_like(self.lengths_score))
        
        # Calculate final weights
        weights = (self.calculate_pcs_scores(pcs) + 
                  waste_percentages + 
                  0.5 * length_percentages) * combination
                  
        return np.sum(weights) 