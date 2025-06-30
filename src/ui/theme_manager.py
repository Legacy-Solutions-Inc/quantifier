"""
Theme manager for the RSB Combinator UI.
Handles loading and accessing theme properties.
"""

import json
import os
from typing import Any, Dict, List

class ThemeManager:
    """Manages UI theme properties."""
    
    _instance = None
    _theme: Dict[str, Any] = {}
    _current_theme: str = "default"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._load_theme()
        return cls._instance
    
    def _load_theme(self) -> None:
        """Load theme from JSON file."""
        theme_path = os.path.join(os.path.dirname(__file__), "theme.json")
        try:
            with open(theme_path, 'r') as f:
                self._theme = json.load(f)
        except Exception as e:
            print(f"Error loading theme: {e}")
            # Fallback to default theme
            self._theme = {
                "themes": {
                    "default": {
                        "colors": {
                            "primary": {"main": "#2B2B2B", "hover": "#404040", "text": "white"},
                            "background": {"main": "#F5F5F5", "input": "white", "dropdown": "white"},
                            "validation": {"success": "#4CAF50", "error": "#F44336"},
                            "text": {"primary": "#2B2B2B", "secondary": "#666666"}
                        }
                    }
                },
                "fonts": {
                    "regular": {"family": "Arial", "size": 12, "weight": "normal"},
                    "bold": {"family": "Arial", "size": 12, "weight": "bold"}
                }
            }
    
    def get_available_themes(self) -> List[str]:
        """Get list of available themes."""
        return list(self._theme["themes"].keys())
    
    def set_theme(self, theme_name: str) -> None:
        """Set the current theme."""
        if theme_name in self._theme["themes"]:
            self._current_theme = theme_name
        else:
            print(f"Theme '{theme_name}' not found, using default theme")
            self._current_theme = "default"
    
    def get_color(self, category: str, variant: str) -> str:
        """Get a color value from the current theme."""
        return self._theme["themes"][self._current_theme]["colors"][category][variant]
    
    def get_font(self, style: str) -> tuple:
        """Get a font configuration from the theme."""
        font = self._theme["fonts"][style]
        return (font["family"], font["size"], font["weight"])
    
    def get_component_style(self, component: str) -> Dict[str, Any]:
        """Get component styling properties."""
        return self._theme["components"][component]
    
    def get_theme(self) -> Dict[str, Any]:
        """Get the entire theme configuration."""
        return self._theme 