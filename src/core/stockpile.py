"""
Stockpile management module for the RSB Combinator.
Handles stockpile operations and tracking.
"""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

@dataclass
class StockpileItem:
    """Represents a single item in the stockpile."""
    quantity: int
    length: float

class StockpileManager:
    """Manages stockpile operations and state."""
    
    def __init__(self):
        self.items: List[StockpileItem] = []
        
    @property
    def has_items(self) -> bool:
        """Check if stockpile has any items."""
        return len(self.items) > 0
        
    def add_items(self, lengths: List[float], quantities: List[int]) -> None:
        """
        Add items to stockpile.
        
        Args:
            lengths: List of lengths to add
            quantities: List of quantities for each length
        """
        for qty, length in zip(quantities, lengths):
            if qty > 0:
                self.items.append(StockpileItem(qty, length))
                
    def get_current_item(self) -> Tuple[int, float]:
        """
        Get the current stockpile item to process.
        
        Returns:
            Tuple of (quantity, length) for current item
        """
        if not self.has_items:
            raise ValueError("No items in stockpile")
        return self.items[-1].quantity, self.items[-1].length
    
    def update_quantity(self, used_quantity: int) -> None:
        """
        Update quantity after using some items.
        
        Args:
            used_quantity: Number of items used
        """
        if not self.has_items:
            return
            
        current = self.items[-1]
        if used_quantity >= current.quantity:
            self.items.pop()
        else:
            current.quantity -= used_quantity
            
    def get_all_items(self) -> List[Tuple[int, float]]:
        """
        Get all items in stockpile.
        
        Returns:
            List of (quantity, length) tuples
        """
        return [(item.quantity, item.length) for item in self.items]
    
    def clear(self) -> None:
        """Clear all items from stockpile."""
        self.items.clear()
        
    def total_length(self) -> float:
        """
        Calculate total length of all items.
        
        Returns:
            Total length of all items
        """
        return sum(item.quantity * item.length for item in self.items)
    
    def total_quantity(self) -> int:
        """
        Calculate total quantity of all items.
        
        Returns:
            Total quantity of all items
        """
        return sum(item.quantity for item in self.items) 