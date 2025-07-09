"""
Drag and drop component for file imports.
"""

import customtkinter as ctk
from typing import Any, Callable
import pandas as pd
import os
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog

class DragDropFrame(ctk.CTkFrame):
    """Frame that accepts drag and drop file inputs."""
    
    def __init__(self, parent: Any, app: Any, on_file_drop: Callable[[str], None]):
        super().__init__(parent)
        self.app = app
        self.on_file_drop = on_file_drop
        
        # Configure frame appearance
        self.configure(
            fg_color=("gray85", "gray25"),
            corner_radius=10,
            border_width=2,
            border_color=("gray75", "gray35")
        )
        
        # Create layout
        self.create_widgets()
        
        # Bind drag and drop events
        self.bind_drop_events()
        
    def create_widgets(self) -> None:
        """Create the frame's widgets."""
        # Main label
        self.label = ctk.CTkLabel(
            self,
            text="Drag & Drop Excel File\nor\nClick to Browse",
            font=("Arial", 14),
            text_color=("gray45", "gray65")
        )
        self.label.pack(pady=20, padx=20)
        
        # Accepted formats label
        self.format_label = ctk.CTkLabel(
            self,
            text="Accepted formats: .xlsx, .xls, .csv",
            font=("Arial", 10),
            text_color=("gray45", "gray65")
        )
        self.format_label.pack(pady=(0, 10))
        
        # Bind click event for manual file selection
        self.bind("<Button-1>", self.browse_file)
        self.label.bind("<Button-1>", self.browse_file)
        
    def bind_drop_events(self) -> None:
        """Bind drag and drop events."""
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.handle_drop)
        
        # Visual feedback for drag over
        self.dnd_bind("<<DragEnter>>", lambda e: self.configure(border_color=("blue", "lightblue")))
        self.dnd_bind("<<DragLeave>>", lambda e: self.configure(border_color=("gray75", "gray35")))
        
    def handle_drop(self, event: Any) -> None:
        """Handle file drop event."""
        file_path = event.data
        
        # Clean up the file path (Windows specific handling)
        file_path = file_path.strip('{}')
        
        if self.is_valid_file(file_path):
            self.process_file(file_path)
        else:
            self.app.show_error("Invalid file format. Please use Excel (.xlsx, .xls) or CSV files.")
            
    def browse_file(self, event: Any) -> None:
        """Open file browser for manual file selection."""
        file_types = (
            ("Excel files", "*.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        )
        
        file_path = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=file_types
        )
        
        if file_path and self.is_valid_file(file_path):
            self.process_file(file_path)
            
    def is_valid_file(self, file_path: str) -> bool:
        """
        Check if the file is a valid format.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if valid format, False otherwise
        """
        valid_extensions = ('.xlsx', '.xls', '.csv')
        return os.path.splitext(file_path)[1].lower() in valid_extensions
        
    def process_file(self, file_path: str) -> None:
        """
        Process the imported file.
        
        Args:
            file_path: Path to the file to process
        """
        try:
            # Read the file based on its extension
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
                
            # Validate the DataFrame structure
            required_columns = {'Lengths', 'Pcs', 'Diameter', 
                                    'TagID', 'FloorID', 'ZoneID', 
                                    'LocationID', 'MemberTypeID', 
                                    'RebarTypeID', 'SpecificTagID'}
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"File must contain {required_columns} columns")
            
            print(df)
            # Debug: Save the DataFrame to a log file
            df.to_csv("import_debug_log.csv", index=False)

            # Pass the data to the callback
            self.on_file_drop(df)
            
            # Update visual feedback
            self.label.configure(text="File imported successfully!")
            self.configure(border_color=("green", "lightgreen"))
            
            # Reset visual feedback after 2 seconds
            self.after(2000, self.reset_appearance)
            
        except Exception as e:
            self.app.show_error(f"Error processing file: {str(e)}")
            self.configure(border_color=("red", "darkred"))
            
    def reset_appearance(self) -> None:
        """Reset the frame's appearance to default."""
        self.label.configure(text="Drag & Drop Excel File\nor\nClick to Browse")
        self.configure(border_color=("gray75", "gray35")) 