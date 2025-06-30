"""
Main window component for the RSB Combinator.
Handles the display of combination results and data tables.
"""

import customtkinter as ctk
from typing import List, Any, Optional
import pandas as pd
import tkinter as tk

from src.ui.theme_manager import ThemeManager

class MainWindow(ctk.CTkScrollableFrame):
    """Main content area displaying combination results."""
    
    def __init__(self, parent: Any, app: Any):
        super().__init__(parent)
        self.app = app
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create table frame
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Store current table state
        self.current_headers: List[str] = []
        self.current_data: List[List[Any]] = []
        
        # Create context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy Table", command=self._copy_table)
        
        # Bind right-click event
        self.table_frame.bind("<Button-3>", self._show_context_menu)
        
    def _show_context_menu(self, event: Any) -> None:
        """Show the context menu on right-click."""
        self.context_menu.post(event.x_root, event.y_root)
        
    def _copy_table(self) -> None:
        """Copy the current table to clipboard in Excel-friendly format."""
        if not self.current_headers or not self.current_data:
            return
            
        # Format headers
        formatted_headers = []
        for header in self.current_headers:
            if "Cut length" in header:
                length_value = header.split("Cut length ")[1]
                formatted_headers.append(f"Cut Length {length_value}")
            elif "Pcs (combination)" in header:
                combo_num = header.split("Pcs (combination) ")[1]
                formatted_headers.append(f"Pcs {combo_num}")
            else:
                formatted_headers.append(header)
                
        # Format data
        formatted_data = []
        for row in self.current_data:
            formatted_row = []
            for value in row:
                if isinstance(value, (int, float)):
                    if value.is_integer():
                        formatted_row.append(str(int(value)))
                    else:
                        formatted_row.append(f"{value:.2f}".rstrip('0').rstrip('.'))
                else:
                    formatted_row.append(str(value))
            formatted_data.append(formatted_row)
            
        # Create tab-separated string
        table_text = "\t".join(formatted_headers) + "\n"
        for row in formatted_data:
            table_text += "\t".join(row) + "\n"
            
        # Copy to clipboard
        self.clipboard_clear()
        self.clipboard_append(table_text)
        
        # Show success message
        self.app.show_success("Table copied to clipboard!")
        
    def clear_table(self) -> None:
        """Clear all widgets from the table frame."""
        for widget in self.table_frame.winfo_children():
            widget.destroy()
            
    def create_header(self, header: str, column: int) -> None:
        """Create a header cell in the table."""
        label = ctk.CTkLabel(
            self.table_frame, 
            text=header, 
            font=("Arial", 14, "bold")
        )
        label.grid(row=0, column=column, padx=5, pady=5, sticky="new")
        
    def create_cell(self, value: Any, row: int, column: int) -> None:
        """Create a data cell in the table."""
        label = ctk.CTkLabel(
            self.table_frame, 
            text=str(value), 
            font=("Arial", 12)
        )
        label.grid(row=row, column=column, padx=5, pady=5)
        
    def display_table(self, headers: List[str], data: List[List[Any]]) -> None:
        """Display data in a table format."""
        # Clear existing table
        self.clear_table()
        
        # Store current data for copy functionality
        self.current_headers = headers
        self.current_data = data
        
        # Configure column weights
        for i in range(len(headers)):
            self.table_frame.grid_columnconfigure(i, weight=1)
        
        # Create headers
        for col, header in enumerate(headers):
            # Format header text for better readability
            if "Cut length" in header:
                length_value = header.split("Cut length")[1].strip()
                header_text = f"Cut Length {length_value}"
            elif "Pcs (combination)" in header:
                pcs_value = header.split("Pcs (combination)")[1].strip()
                header_text = f"Pcs {pcs_value}"
            else:
                header_text = header
                
            self.create_header(header_text, col)
            
        # Create data rows
        for row, row_data in enumerate(data, 1):
            for col, value in enumerate(row_data):
                self.create_cell(value, row, col)
                
        # Add copy instruction note
        theme = ThemeManager()
        copy_note = ctk.CTkLabel(
            self.table_frame,
            text="💡 Right-click on the table to copy data",
            font=theme.get_font("regular"),
            text_color=theme.get_color("text", "secondary")
        )
        copy_note.grid(row=len(data) + 1, column=0, columnspan=len(headers), pady=(10, 0), sticky="e")
        
    def display_dataframe(self, df: pd.DataFrame) -> None:
        """
        Display a pandas DataFrame as a table.
        
        Args:
            df: DataFrame to display
        """
        # Format column names for better display
        formatted_headers = []
        for col in df.columns:
            if "Cut length" in col:
                # Extract the length value from the column name
                length_value = col.split("Cut length ")[1]
                formatted_headers.append(f"Cut Length {length_value}")
            elif "Pcs (combination)" in col:
                # Extract the combination number from the column name
                combo_num = col.split("Pcs (combination) ")[1]
                formatted_headers.append(f"Pcs {combo_num}")
            else:
                formatted_headers.append(col)
                
        self.display_table(
            data=df.values.tolist(),
            headers=formatted_headers
        )
        
    def update_cell(self, row: int, column: int, value: Any) -> None:
        """
        Update a specific cell in the table.
        
        Args:
            row: Row index (0-based)
            column: Column index (0-based)
            value: New value for the cell
        """
        if row < len(self.current_data) and column < len(self.current_headers):
            self.current_data[row][column] = value
            self.create_cell(value, row + 1, column)  # +1 for header row
            
    def get_selected_rows(self) -> List[int]:
        """
        Get indices of currently selected rows.
        
        Returns:
            List of selected row indices
        """
        # TODO: Implement row selection functionality
        return []
        
    def refresh(self) -> None:
        """Refresh the current table display."""
        self.display_table(self.current_headers, self.current_data)