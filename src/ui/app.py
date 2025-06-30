"""
Main application module for the RSB Combinator.
Handles the main window and component integration.
"""

import customtkinter as ctk
import os
from typing import Optional
import pandas as pd
from tkinterdnd2 import TkinterDnD

from ..core.combinator import Combinator, CombinatorConfig
from ..core.combinator_manager import CombinatorManager
from .components.main_window import MainWindow
from .components.sidebar import Sidebar
from .components.title_window import TitleWindow

class App(TkinterDnD.Tk):
    """Main application class."""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Engr. Rei's RSB Combinator v1.0")
        self.setup_window()
        
        # Initialize combinator manager
        self.combinator_manager = CombinatorManager()
        
        # Create UI components
        self.create_components()
        
    def setup_window(self) -> None:
        """Configure the main window."""
        # Set window icon
        icon_path = os.path.join("data", "assets", "logo.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
            
        # Set window size and properties
        self.geometry("1024x768")
        self.resizable(True, True)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)  # Sidebar
        self.grid_columnconfigure(1, weight=5)  # Main content
        self.grid_rowconfigure(0, weight=1)
        
    def create_components(self) -> None:
        """Create and arrange UI components."""
        # Create sidebar container
        self.sidebar_frame = ctk.CTkFrame(self, width=1000)
        self.sidebar_frame.grid(
            row=0,
            column=0,
            sticky="nwe",
            padx=10,
            pady=10
        )
        
        # Configure sidebar frame
        self.sidebar_frame.grid_rowconfigure(2, weight=1)
        self.sidebar_frame.grid_columnconfigure(0, weight=1)
        
        # Add sidebar title
        self.title_bar = ctk.CTkLabel(
            self.sidebar_frame,
            width=20,
            text="Controls:",
            font=("Arial", 18)
        )
        self.title_bar.grid(
            row=0,
            column=0,
            sticky="new",
            padx=10,
            pady=10
        )
        
        # Create sidebar
        self.sidebar = Sidebar(self.sidebar_frame, self)
        self.sidebar.grid(
            row=1,
            column=0,
            sticky="new",
            padx=10,
            pady=10
        )
        
        # Create right side container
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(
            row=0,
            column=1,
            sticky="nswe",
            padx=10,
            pady=10
        )
        
        # Configure right frame
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=4)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # Create title window
        self.title_window = TitleWindow(self.right_frame, self)
        self.title_window.grid(
            row=0,
            column=0,
            sticky="nswe",
            padx=10,
            pady=10
        )
        
        # Create main window
        self.main_window = MainWindow(self.right_frame, self)
        self.main_window.grid(
            row=1,
            column=0,
            sticky="nswe",
            padx=10,
            pady=10
        )
        
    def create_output_dataframe(self, cleaned: bool = False) -> pd.DataFrame:
        """
        Create a DataFrame from current results.
        
        Args:
            cleaned: Whether to clean and format the output
            
        Returns:
            DataFrame containing the results
        """
        # Get current combinator
        combinator = self.combinator_manager.get_current_combinator()
        if not combinator:
            return pd.DataFrame()
            
        # Extract data
        data = {
            'Quantity': [],
            'Combined Length': [],
            'Target Length': [],
            'Waste': []
        }
        
        # Add length columns if cleaned
        if cleaned:
            for length in combinator.original_lengths:
                data[f'{length}'] = []
                
        # Populate data
        for result in combinator.results:
            data['Quantity'].append(result.quantity)
            data['Combined Length'].append(result.combined_length)
            data['Target Length'].append(result.target)
            data['Waste'].append(result.waste)
            
            if cleaned:
                # Create mapping of lengths to factors
                length_factors = dict(zip(result.lengths, result.combination))
                for length in combinator.original_lengths:
                    data[f'{length}'].append(length_factors.get(length, 0))
                    
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Set index to start at 1
        df.index = df.index + 1
        
        return df
        
    def run(self) -> None:
        """Start the application."""
        self.mainloop()
        
    def show_error(self, message: str) -> None:
        """
        Display an error message.
        
        Args:
            message: Error message to display
        """
        self.title_window.show_error(message)
        
    def show_success(self, message: str) -> None:
        """
        Display a success message.
        
        Args:
            message: Success message to display
        """
        # Clear any existing error messages
        self.title_window.clear_details()
        
        # Show success message in title window
        self.title_window.show_success(message)
        
    def clear_results(self) -> None:
        """Clear all results and reset display."""
        self.combinator_manager.reset()
        self.main_window.clear_table()
        self.title_window.clear_details() 