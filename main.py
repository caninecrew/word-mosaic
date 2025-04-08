#!/usr/bin/env python3
"""
Word Mosaic - A single-player word strategy game
Main entry point for the game
"""

import sys
import os

# Ensure dictionary database exists before starting
from database import create_database
if not os.path.exists("dictionary.db"):
    print("Setting up dictionary database for first run...")
    create_database()

# Start the game
from gui import WordMosaicApp
from PyQt5.QtWidgets import QApplication

def main():
    """Main entry point for Word Mosaic game"""
    app = QApplication(sys.argv)
    window = WordMosaicApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()