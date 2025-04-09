#!/usr/bin/env python3
"""
Word Mosaic - A single-player word strategy game
Main entry point for the game
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from board import Board
from letter_bank import LetterBank
from scoring import Scoring
from word_validator import WordValidator

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

# Define special tiles
special_tiles = {
    (0, 0): 'TW', (0, 7): 'TW', (0, 14): 'TW',
    (7, 0): 'TW', (7, 14): 'TW',
    (14, 0): 'TW', (14, 7): 'TW', (14, 14): 'TW',
    (1, 1): 'DW', (2, 2): 'DW', (3, 3): 'DW', (4, 4): 'DW',
    (10, 10): 'DW', (11, 11): 'DW', (12, 12): 'DW', (13, 13): 'DW',
    (1, 13): 'DW', (2, 12): 'DW', (3, 11): 'DW', (4, 10): 'DW',
    (10, 4): 'DW', (11, 3): 'DW', (12, 2): 'DW', (13, 1): 'DW',
    (1, 5): 'TL', (1, 9): 'TL', (5, 1): 'TL', (5, 5): 'TL',
    (5, 9): 'TL', (5, 13): 'TL', (9, 1): 'TL', (9, 5): 'TL',
    (9, 9): 'TL', (9, 13): 'TL', (13, 5): 'TL', (13, 9): 'TL',
    (0, 3): 'DL', (0, 11): 'DL', (2, 6): 'DL', (2, 8): 'DL',
    (3, 0): 'DL', (3, 7): 'DL', (3, 14): 'DL', (6, 2): 'DL',
    (6, 6): 'DL', (6, 8): 'DL', (6, 12): 'DL', (7, 3): 'DL',
    (7, 11): 'DL', (8, 2): 'DL', (8, 6): 'DL', (8, 8): 'DL',
    (8, 12): 'DL', (11, 0): 'DL', (11, 7): 'DL', (11, 14): 'DL',
    (12, 6): 'DL', (12, 8): 'DL', (14, 3): 'DL', (14, 11): 'DL',
}

class Game:
    """Game logic for Word Mosaic"""
    def __init__(self):
        self.board = Board(15, 15, special_tiles)
        self.letter_bank = LetterBank()
        self.scoring = Scoring(special_tiles, LetterBank.LETTER_VALUES)
        self.word_validator = WordValidator()
        self.score = 0
        self.played_words = []
        
    def new_game(self):
        """Reset the game to a new state"""
        self.board.reset_board()
        self.letter_bank = LetterBank()  # Get a fresh set of letters
        self.score = 0
        self.played_words = []
        
    def play_word(self, word):
        """
        Play a word on the board if valid
        
        Args:
            word (str): Word to play
            
        Returns:
            dict: Result containing validity and score info
        """
        word = word.upper()
        
        # First, check if word is valid
        if not self.word_validator.validate_word(word):
            return {'valid': False, 'reason': 'Not a valid dictionary word'}
            
        # Check if we have the necessary letters
        if not self.letter_bank.has_letters(word):
            return {'valid': False, 'reason': 'Insufficient letters available'}
            
        # TODO: Add logic for board placement
        # For now, just add to played words
        self.played_words.append(word)
        
        # Calculate score (placeholder)
        word_score = sum(LetterBank.LETTER_VALUES.get(letter.lower(), 0) for letter in word)
        
        # Use letters from the letter bank
        self.letter_bank.use_letters(word)
        
        # Update total score
        self.score += word_score
        
        return {'valid': True, 'score': word_score}
        
    def get_word_definition(self, word):
        """Get a definition for a word if available"""
        # This would require dictionary API integration
        return f"Definition for '{word}' (placeholder)"

def main():
    """
    Main entry point for the Word Mosaic game
    """
    # Initialize the game
    game = Game()
    
    # Initialize the GUI
    app = QApplication(sys.argv)
    window = WordMosaicApp(game)
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()