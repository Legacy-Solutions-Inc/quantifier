"""
Main entry point for the RSB Combinator application.
"""

import os
import customtkinter as ctk
from src.ui.app import App
from src.ui.theme_manager import ThemeManager

def main():
    """Initialize and run the application."""
    # Set theme
    theme_path = os.path.join("data", "settings", "dark_cyan.json")
    if os.path.exists(theme_path):
        ctk.set_default_color_theme(theme_path)
    else:
        print(f"Warning: Theme file not found at {theme_path}")
        
    # Set appearance mode
    ctk.set_appearance_mode("dark")
    
    # Create and run application
    theme_manager = ThemeManager()
    theme_manager.set_theme("dark_cyan")
    app = App()
    app.run()

if __name__ == "__main__":
    main()
