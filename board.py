from word_validator import WordValidator
from scoring import Scoring

from scoring import Scoring

from letter_bank import LetterBank

class Board:
    """
    Represents the game board for Word Mosaic
    """
    def __init__(self, rows=15, cols=15, special_tiles=None):
        """
        Initialize the game board
        
        Args:
            rows (int): Number of rows
            cols (int): Number of columns
            special_tiles (dict): Dictionary of special tiles {(row, col): multiplier}
        """
        self.rows = rows
        self.cols = cols
        self.board = [['0' for _ in range(cols)] for _ in range(rows)]
        
        # Default Scrabble-like special tiles if none provided
        self.special_tiles = special_tiles or self._default_special_tiles()
        
    def _default_special_tiles(self):
        """
        Create default special tile configuration
        
        Returns:
            dict: {(row, col): multiplier}
        """
        special = {}
        
        # Triple word scores
        for r, c in [(0, 0), (0, 7), (0, 14), (7, 0), (7, 14), (14, 0), (14, 7), (14, 14)]:
            if r < self.rows and c < self.cols:
                special[(r, c)] = "TW"  # Triple word
                
        # Double word scores
        for r, c in [(1, 1), (2, 2), (3, 3), (4, 4), (10, 10), (11, 11), (12, 12), (13, 13),
                     (1, 13), (2, 12), (3, 11), (4, 10), (10, 4), (11, 3), (12, 2), (13, 1)]:
            if r < self.rows and c < self.cols:
                special[(r, c)] = "DW"  # Double word
                
        # Triple letter scores
        for r, c in [(1, 5), (1, 9), (5, 1), (5, 5), (5, 9), (5, 13), (9, 1), (9, 5), (9, 9), (9, 13), (13, 5), (13, 9)]:
            if r < self.rows and c < self.cols:
                special[(r, c)] = "TL"  # Triple letter
                
        # Double letter scores
        for r, c in [(0, 3), (0, 11), (2, 6), (2, 8), (3, 0), (3, 7), (3, 14), (6, 2), (6, 6), (6, 8), (6, 12),
                     (7, 3), (7, 11), (8, 2), (8, 6), (8, 8), (8, 12), (11, 0), (11, 7), (11, 14), (12, 6), (12, 8), (14, 3), (14, 11)]:
            if r < self.rows and c < self.cols:
                special[(r, c)] = "DL"  # Double letter
                
        return special
        
    def place_letter(self, letter, row, col):
        """
        Place a letter on the board
        
        Args:
            letter (str): The letter to place
            row (int): Row position
            col (int): Column position
            
        Raises:
            ValueError: If the position is invalid or already occupied
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise ValueError(f"Position ({row}, {col}) is outside the board")
            
        if self.board[row][col] != '0':
            raise ValueError(f"Position ({row}, {col}) is already occupied")
            
        self.board[row][col] = letter
        
    def clear_position(self, row, col):
        """
        Clear a position on the board
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Raises:
            ValueError: If the position is invalid
        """
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise ValueError(f"Position ({row}, {col}) is outside the board")
            
        self.board[row][col] = '0'
        
    def get_letter(self, row, col):
        """
        Get the letter at a position
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            str: The letter at the position, or '0' if empty
        """
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.board[row][col]
        return None
        
    def is_position_empty(self, row, col):
        """
        Check if a position is empty
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            bool: True if empty, False otherwise
        """
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.board[row][col] == '0'
        return False
        
    def get_special_tile_multiplier(self, row, col):
        """
        Get the multiplier for a special tile
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            str: The multiplier type, or None if not a special tile
        """
        return self.special_tiles.get((row, col))
        
    def reset(self):
        """Reset the board to initial state"""
        self.board = [['0' for _ in range(self.cols)] for _ in range(self.rows)]
        
    def get_all_words(self):
        """
        Get all words formed on the board
        
        Returns:
            list: List of tuples (word, positions) where positions is a list of (row, col)
        """
        words = []
        
        # Check horizontal words
        for row in range(self.rows):
            word = ""
            positions = []
            for col in range(self.cols):
                letter = self.get_letter(row, col)
                if letter != '0':
                    word += letter
                    positions.append((row, col))
                else:
                    if len(word) > 1:  # Only consider words of 2 or more letters
                        words.append((word, positions[:]))
                    word = ""
                    positions = []
            
            # Check if there's a word at the end of the row
            if len(word) > 1:
                words.append((word, positions))
        
        # Check vertical words
        for col in range(self.cols):
            word = ""
            positions = []
            for row in range(self.rows):
                letter = self.get_letter(row, col)
                if letter != '0':
                    word += letter
                    positions.append((row, col))
                else:
                    if len(word) > 1:  # Only consider words of 2 or more letters
                        words.append((word, positions[:]))
                    word = ""
                    positions = []
            
            # Check if there's a word at the end of the column
            if len(word) > 1:
                words.append((word, positions))
                
        return words
        
    def is_connected(self, row, col):
        """
        Check if a position is adjacent to an existing letter
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            bool: True if connected, False otherwise
        """
        # Check all adjacent positions
        for r, c in [(row-1, col), (row+1, col), (row, col-1), (row, col+1)]:
            if 0 <= r < self.rows and 0 <= c < self.cols:
                if self.board[r][c] != '0':
                    return True
        return False

    def is_center(self, row, col):
        """
        Check if a position is at the center of the board
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            bool: True if at center, False otherwise
        """
        center_row = self.rows // 2
        center_col = self.cols // 2
        return row == center_row and col == center_col