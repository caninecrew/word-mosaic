#!/usr/bin/env python3
"""
Word Mosaic - A single-player word strategy game
Main entry point for the game
"""

import sys
import os

# Ensure necessary databases exist before starting
from database import create_database
from merriam_webster_api import merriam_webster

def initialize_databases():
    """Initialize required databases for the game"""
    if not os.path.exists("dictionary.db"):
        print("Setting up dictionary database for first run...")
        create_database()
    
    # Check for Merriam-Webster API key and notify user if missing
    if not merriam_webster.api_key:
        print("Note: Merriam-Webster API key not found. Set the MERRIAM_WEBSTER_API_KEY environment variable")
        print("      for enhanced word validation. Using local dictionary as fallback.")

# Start the game
from gui import WordMosaicApp
from PyQt5.QtWidgets import QApplication

def main():
    """Main entry point for Word Mosaic game"""
    initialize_databases()
    app = QApplication(sys.argv)
    window = WordMosaicApp()
    
    # Clear definitions after each turn
    window.clear_definitions()
    
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()