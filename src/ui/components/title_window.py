"""
Title window component for the RSB Combinator.
Displays application title, logo, and summary information.
"""

import customtkinter as ctk
from PIL import Image
from typing import Any, Optional
import os
from src.ui.theme_manager import ThemeManager

class TitleWindow(ctk.CTkFrame):
    """Title window displaying application header and summary."""
    
    def __init__(self, parent: Any, app: Any):
        theme = ThemeManager()
        super().__init__(parent, fg_color=theme.get_color("background", "main"))
        self.app = app
        
        # Configure grid for main frame
        self.grid_rowconfigure(1, weight=1)  # Give weight to scrollable area
        self.grid_columnconfigure(0, weight=1)
        
        # Create header frame for logo and title
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10,0))
        self.header_frame.grid_columnconfigure(1, weight=1)  # Give weight to middle column
        
        # Create scrollable frame for details
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            height=200  # Fixed height for scroll area
        )
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize components
        self.logo_label: Optional[ctk.CTkLabel] = None
        self.title_label: Optional[ctk.CTkLabel] = None
        self.details_label: Optional[ctk.CTkLabel] = None
        
        # Show initial components
        self.show_logo()
        
    def show_logo(self) -> None:
        """Display the application logo and title."""
        try:
            # Load and display logo
            logo_path = os.path.join("data", "assets", "logo.png")
            logo_image = Image.open(logo_path)
            self.logo = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(80, 80)
            )
            
            self.logo_label = ctk.CTkLabel(
                self.header_frame,
                image=self.logo,
                text=""
            )
            self.logo_label.grid(
                row=0,
                column=2,
                padx=20,
                pady=10,
                sticky="e"
            )
            
        except Exception as e:
            print(f"Error loading logo: {e}")
            
        # Display title
        theme = ThemeManager()
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Engr. Rei's RSB Combinator v1.0",
            font=theme.get_font("bold"),
            text_color=theme.get_color("text", "primary")
        )
        self.title_label.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=20,
            pady=10,
            sticky="w"
        )
        
    def show_waste_percentage(self, waste_percentage: float) -> None:
        """
        Display waste percentage and other details.
        
        Args:
            waste_percentage: Current waste percentage to display
        """
        # Get current combinator
        combinator = self.app.combinator_manager.get_current_combinator()
        if not combinator:
            return
              # Clear previous details if any
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Format numbers to clean up float displays
        def format_number(x: float) -> str:
            """Format a number to remove unnecessary decimal places."""
            if x.is_integer():
                return str(int(x))
            return f"{x:.2f}".rstrip('0').rstrip('.')
            
        def format_list(lst: list) -> str:
            """Format a list of numbers."""
            return [format_number(x) for x in lst]
            
        # Create table-like format for lengths and pieces
        lengths = format_list(combinator.original_lengths.tolist())
        pieces = format_list(combinator.original_pcs.tolist())
        
        # Format the table header and rows
        table_rows = []
        table_rows.append("Length (m) | Pieces")
        table_rows.append("-" * 20)  # Separator line
        for length, pcs in zip(lengths, pieces):
            table_rows.append(f"{length:>8} | {pcs:>6}")
              # Calculate weights
        total_length = sum(l * p for l, p in zip(combinator.original_lengths, combinator.original_pcs))
        commercial_weight = total_length * (combinator.config.diameter ** 2) / 162
        utilized_weight = commercial_weight * (1 - (waste_percentage / 100))
        
        # Format details text with better alignment
        details = [
            "Input Details:",
            f"Diameter: {format_number(combinator.config.diameter)}",
            "\nCut Lengths and Pieces:",
            "\n".join(table_rows),
            f"\nTargets: {format_list(combinator.targets.tolist())}",
            f"\nWeight Details:",
            f"Total Utilized Weight: {format_number(utilized_weight)} kg",
            f"Total Commercial Weight: {format_number(commercial_weight)} kg",
            f"Waste Percentage: {waste_percentage:.2f}%"
        ]
          # Create and display details label with monospace font for better alignment
        theme = ThemeManager()
        self.details_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="\n".join(details),
            font=("Consolas", 12),  # Use monospace font for better alignment
            text_color=theme.get_color("text", "primary"),
            anchor="w",
            justify="left",
            wraplength=400  # Prevent horizontal scrolling
        )
        self.details_label.grid(
            row=0,
            column=0,
            padx=(20, 10),
            pady=10,
            sticky="nw"
        )
        
    def show_error(self, message: str) -> None:
        """
        Display an error message.
        
        Args:
            message: Error message to display
        """
        if self.details_label:
            self.details_label.destroy()
            
        theme = ThemeManager()
        self.details_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=f"Error: {message}",
            font=theme.get_font("regular"),
            text_color=theme.get_color("validation", "error"),
            anchor="w",
            justify="left"
        )
        self.details_label.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=20,
            pady=20,
            sticky="w"
        )
        
    def show_success(self, message: str) -> None:
        """
        Display a success message.
        
        Args:
            message: Success message to display
        """
        if self.details_label:
            self.details_label.destroy()
            
        theme = ThemeManager()
        self.details_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=f"✓ {message}",
            font=theme.get_font("regular"),
            text_color=theme.get_color("validation", "success"),
            anchor="w",
            justify="left"
        )
        self.details_label.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=20,
            pady=20,
            sticky="w"
        )
        
        # Clear success message after 3 seconds
        self.after(3000, self.clear_details)
        
    def clear_details(self) -> None:
        """Clear all details from the display."""
        if self.details_label:
            self.details_label.destroy()
            self.details_label = None