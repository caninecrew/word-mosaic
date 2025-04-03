from word_validator import WordValidator
from scoring import Scoring

from scoring import Scoring

class Board:
    def __init__(self, rows, cols, special_tiles):
        self.rows = rows
        self.cols = cols
        self.board = [['' for _ in range(cols)] for _ in range(rows)]  # Initialize as a 2D list
        self.special_tiles = special_tiles  # Pass special tiles to the board
        self.special_tiles_occupied = {pos: False for pos in special_tiles}  # Track special tile occupancy
        self.scoring = Scoring(special_tiles)  # Initialize Scoring with special tiles

    def calculate_turn_score(self, words):
        """
        Calculate the total score for all words formed during a turn.

        Args:
            words (list): A list of tuples, where each tuple contains:
                          - word (str): The word formed.
                          - positions (list): A list of (row, col) tuples representing the positions of the letters in the word.

        Returns:
            int: The total score for the turn.
        """
        return self.scoring.calculate_turn_score(words)

    def validate_word_positions(self, word, positions):
        """
        Validate that the word's positions align with the board's rules.

        Args:
            word (str): The word to validate.
            positions (list): A list of (row, col) tuples representing the positions of the letters in the word.

        Returns:
            bool: True if the word is valid, False otherwise.
        """
        return self.scoring.validate_word_positions(word, positions)
    
    def define_special_tiles(self):
            """
            Define special tiles and their multipliers based on Scrabble's layout.
            """
            self.special_tiles = {
                # Triple Word (TW)
                (0, 0): 'TW', (0, 7): 'TW', (0, 14): 'TW',
                (7, 0): 'TW', (7, 14): 'TW',
                (14, 0): 'TW', (14, 7): 'TW', (14, 14): 'TW',

                # Double Word (DW)
                (1, 1): 'DW', (2, 2): 'DW', (3, 3): 'DW', (4, 4): 'DW',
                (10, 10): 'DW', (11, 11): 'DW', (12, 12): 'DW', (13, 13): 'DW',
                (1, 13): 'DW', (2, 12): 'DW', (3, 11): 'DW', (4, 10): 'DW',
                (10, 4): 'DW', (11, 3): 'DW', (12, 2): 'DW', (13, 1): 'DW',

                # Triple Letter (TL)
                (1, 5): 'TL', (1, 9): 'TL', (5, 1): 'TL', (5, 5): 'TL',
                (5, 9): 'TL', (5, 13): 'TL', (9, 1): 'TL', (9, 5): 'TL',
                (9, 9): 'TL', (9, 13): 'TL', (13, 5): 'TL', (13, 9): 'TL',

                # Double Letter (DL)
                (0, 3): 'DL', (0, 11): 'DL', (2, 6): 'DL', (2, 8): 'DL',
                (3, 0): 'DL', (3, 7): 'DL', (3, 14): 'DL', (6, 2): 'DL',
                (6, 6): 'DL', (6, 8): 'DL', (6, 12): 'DL', (7, 3): 'DL',
                (7, 11): 'DL', (8, 2): 'DL', (8, 6): 'DL', (8, 8): 'DL',
                (8, 12): 'DL', (11, 0): 'DL', (11, 7): 'DL', (11, 14): 'DL',
                (12, 6): 'DL', (12, 8): 'DL', (14, 3): 'DL', (14, 11): 'DL',
            }

            # Initialize all special tiles as unoccupied
            self.special_tiles_occupied = {pos: False for pos in self.special_tiles}

    def __str__(self):
        """
        Generate a string representation of the board.
        
        Returns:
            str: A formatted string showing the current board state
        """
        # Generate a string representation of the board for display
        board_str = '' # Initialize an empty string
        for i in range(self.rows): # Loop through each row
            for j in range(self.cols): # Loop through each column
                board_str += self.board[i * self.cols + j] + ' ' # Add the letter or space to the string
            board_str += '\n' # Add a newline after each row
        return board_str # Return the complete board string
    
    def place_letter(self, letter, row, col):
        print(f"Placing letter '{letter}' at ({row}, {col})")
        print(f"Board dimensions: {self.rows}x{self.cols}")
        print(f"Before placement: {self.board[row]}")  # Print the row before placement
        """
        Place a letter on the board at the specified position.

        Args:
            letter (str): The letter to place
            row (int): Row position
            col (int): Column position

        Raises:
            ValueError: If the position is already occupied or invalid
            TypeError: If letter is not a string
            ValueError: If letter is not a single alphabetic character
        """
        # Input validation
        if not isinstance(letter, str):
            raise TypeError("Letter must be a string")
        if len(letter) != 1:
            raise ValueError("Letter must be a single character")
        if not letter.isalpha() and letter != '0':  # Allow blank tiles ('0')
            raise ValueError("Only alphabetic characters or blank tiles ('0') are allowed")

        # Position validation
        if not self.is_valid_position(row, col):
            raise ValueError(f"Position ({row}, {col}) is outside the board boundaries")
        if self.is_occupied(row, col):
            raise ValueError(f"Position ({row}, {col}) is already occupied")

        # Place the letter
        self.board[row][col] = letter.upper() if letter != '0' else ''  # Convert to uppercase, blank tiles are empty

        # Update special tile status
        if (row, col) in self.special_tiles:
            self.special_tiles_occupied[(row, col)] = True
        
        self.board[row][col] = letter.upper() if letter != '0' else ''

        print(f"After placement: {self.board[row]}")  # Print the row after placement

    def is_occupied(self, row, col):
        """
        Check if the specified position is occupied by a letter.

        Args:
            row (int): Row position
            col (int): Column position

        Returns:
            bool: True if position contains a letter, False otherwise
        """
        if not self.is_valid_position(row, col):
            raise ValueError(f"Position ({row}, {col}) is outside the board boundaries")
        return self.board[row][col] != ''  # Check if the position is occupied
    
    def get_letter(self, row, col):
        """
        Retrieve the letter at the specified position.
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            str: The letter at the position, or None if position is invalid
            
        Raises:
            ValueError: If position is outside board boundaries
        """
        if not self.is_valid_position(row, col):
            raise ValueError(f"Position ({row}, {col}) is outside the board boundaries")
        return self.board[row * self.cols + col]
    
    def clear_position(self, row, col):
        """
        Remove the letter from the specified position.
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Raises:
            ValueError: If position is outside board boundaries
        """
        if not self.is_valid_position(row, col):
            raise ValueError(f"Position ({row}, {col}) is outside the board boundaries")
        
        self.board[row * self.cols + col] = ' '
        if (row, col) in self.special_tiles:
            self.special_tiles_occupied[(row, col)] = False

    def reset_board(self):
        """Clear all letters from the board but keep special tiles."""
        print(f"Before reset: {self.special_tiles_occupied}")
        self.board = [' ' for _ in range(self.rows * self.cols)]  # Reset the board to empty spaces
        print(f"After reset: {self.special_tiles_occupied}")

    def is_center_covered(self):
        """
        Check if the center position has a letter.
        
        Returns:
            bool: True if center position is occupied, False otherwise
        """
        return self.is_occupied(self.center[0], self.center[1]) # Check if the center is occupied
    
    def is_valid_position(self, row, col):
        """
        Check if the given coordinates are within board boundaries.
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            bool: True if position is within boundaries, False otherwise
        """
        return 0 <= row < self.rows and 0 <= col < self.cols # Check if the position is valid
    
    def has_adjacent_letter(self, row, col):
        """
        Check if a position has at least one adjacent letter.
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            bool: True if position has an adjacent letter, False otherwise
        """
        # Check if a position connects to existing letters
        if not self.is_valid_position(row, col):
            return False # Ensure the position is valid
        # Check adjacent positions for letters
        adjacent_positions = [
            (row-1, col), (row+1, col), (row, col-1), (row, col+1) # Up, Down, Left, Right
        ]
        for r, c in adjacent_positions: # Loop through adjacent positions
            if self.is_valid_position(r, c) and self.is_occupied(r, c): # Check if occupied
                return True # Return True if any adjacent position has a letter
        return False # Return False if no adjacent letters are found
    
    def get_horizontal_word(self, row, col):
        """
        Retrieve a complete word reading horizontally from the given position.
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            str: The complete horizontal word containing this position
        """
        # Retrieve a word reading from left to right
        if not self.is_valid_position(row, col): # Ensure the position is valid
            return "" # Return empty string if invalid
        if not self.is_occupied(row, col): # Check if the position is occupied
            return "" # Return empty string if not occupied
        
        start_col = col # Start column for the word
        while start_col > 0 and self.is_occupied(row, start_col - 1): # Move left to find the start of the word
            start_col -= 1 # Check if the position is occupied
            
        end_col = col # End column for the word
        while end_col < self.cols - 1 and self.is_occupied(row, end_col + 1):
            end_col += 1 # Move right to find the end of the word
            
        # Build the word character by character (slice won't work properly with 1D array)
        word = ""
        for c in range(start_col, end_col + 1):
            word += self.board[row * self.cols + c]
        return word

    def get_vertical_word(self, row, col):
        """
        Retrieve a complete word reading vertically from the given position.
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            str: The complete vertical word containing this position
        """
        # Retrieve a word reading from top to bottom
        if not self.is_valid_position(row, col) or not self.is_occupied(row, col):
            return ""
            
        # Find start and end positions
        start_row = row # Start row for the word
        while start_row > 0 and self.is_occupied(start_row - 1, col): # Move up to find the start of the word
            start_row -= 1 # Check if the position is occupied
            
        end_row = row # End row for the word
        while end_row < self.rows - 1 and self.is_occupied(end_row + 1, col): # Move down to find the end of the word
            end_row += 1 # Check if the position is occupied
            
        # Build the word letter by letter
        word = "" # Initialize an empty string for the word
        for r in range(start_row, end_row + 1): # Loop through the rows
            word += self.board[r * self.cols + col] # Add each letter to the word
        return word # Return the complete word
    
    def get_word_at_position(self, row, col, direction):
        """
        Extract a complete word given a position and direction.
        
        Args:
            row (int): Row position
            col (int): Column position
            direction (str): Either 'horizontal' or 'vertical'
            
        Returns:
            str: The complete word in the specified direction
            
        Raises:
            ValueError: If an invalid direction is provided
        """
        # Extract a complete word given a position and direction
        if direction == 'horizontal': 
            return self.get_horizontal_word(row, col)
        elif direction == 'vertical':
            return self.get_vertical_word(row, col)
        else:
            raise ValueError("Invalid direction")
        
    def get_all_words(self):
        """
        Retrieve all words formed during the current turn.

        Returns:
            list: A list of tuples, where each tuple contains:
                - word (str): The word formed.
                - positions (list): A list of (row, col) tuples representing the positions of the letters in the word.
        """
        words = []

        # Horizontal words
        for row in range(self.rows):
            current_word = ""
            positions = []
            for col in range(self.cols):
                letter = self.board[row][col]
                if letter:
                    current_word += letter
                    positions.append((row, col))
                else:
                    if len(current_word) > 1:
                        words.append((current_word, positions))
                    current_word = ""
                    positions = []
            if len(current_word) > 1:
                words.append((current_word, positions))

        # Vertical words
        for col in range(self.cols):
            current_word = ""
            positions = []
            for row in range(self.rows):
                letter = self.board[row][col]
                if letter:
                    current_word += letter
                    positions.append((row, col))
                else:
                    if len(current_word) > 1:
                        words.append((current_word, positions))
                    current_word = ""
                    positions = []
            if len(current_word) > 1:
                words.append((current_word, positions))

        return words
    
    def get_words_formed(self, row, col, letter):
        """
        Find all words that would be formed by placing a new letter.
        
        This method temporarily places the letter, identifies words, then removes it.
        
        Args:
            row (int): Row position
            col (int): Column position
            letter (str): The letter to place
            
        Returns:
            list: A list of unique words that would be formed
        """
        # Find all words formed by placing a new letter(s)
        words = []
        if self.is_valid_position(row, col) and not self.is_occupied(row, col): # Check if the position is valid and not occupied
            self.place_letter(letter, row, col) # Place the letter
            words.append(self.get_horizontal_word(row, col)) # Add horizontal word
            words.append(self.get_vertical_word(row, col)) # Add vertical word
            self.clear_position(row, col) # Clear the position after checking
        return list(set(words)) # Return unique words formed
    
    def get_occupied_positions(self):
        """
        List all positions on the board that contain letters.
        
        Returns:
            list: A list of (row, col) tuples representing occupied positions
        """
        # List all occupied positions on the board
        occupied_positions = []
        for row in range(self.rows): # Loop through each row
            for col in range(self.cols): # Loop through each column
                if self.is_occupied(row, col): # Check if the position is occupied
                    occupied_positions.append((row, col)) # Add occupied position to the list
        return occupied_positions # Return the list of occupied positions
    
    def calculate_coverage(self):
        """
        Calculate the percentage of the board that is filled with letters.
        
        Returns:
            float: Percentage of board coverage (0-100)
        """
        # Calculate the percentage of the board that is filled
        total_positions = self.rows * self.cols # Total number of positions on the board
        occupied_positions = len(self.get_occupied_positions()) # Count occupied positions
        return (occupied_positions / total_positions) * 100
    
    def find_valid_placements(self, letter):
        """
        Identify all legal positions for placing a new letter.
        
        Args:
            letter (str): The letter to place
            
        Returns:
            list: A list of (row, col) tuples representing valid placement positions
        """
        # Identify legal positions for placing new letters
        valid_positions = []
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.is_occupied(row, col) and self.has_adjacent_letter(row, col):
                    valid_positions.append((row, col))
        return valid_positions
    
    def get_special_tiles(self):
        """
        Retrieve all unoccupied special tiles and their multipliers.
        
        Returns:
            dict: A dictionary mapping (row, col) positions to multiplier types
        """
        # Retrieve special tiles and their multipliers
        return {pos: self.special_tiles[pos] for pos in self.special_tiles if not self.special_tiles_occupied[pos]} # Return unoccupied special tiles
    
    def get_special_tile_multiplier(self, row, col):
        """
        Get the multiplier type for a special tile at the specified position.
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            str: Multiplier type (e.g., 'DL', 'TL'), or None if not a special tile
        """
        # Get the multiplier for a special tile at the specified position
        return self.special_tiles.get((row, col), None)
    
    def get_state(self):
        """
        Return the current state of the board.
        
        Returns:
            dict: A dictionary containing the board state information including
                  the board, special tiles, center position, and current coverage
        """
        # Return the current state of the board
        return {
            'board': self.board,
            'special_tiles': self.special_tiles_occupied,
            'center': self.center,
            'coverage': self.calculate_coverage()
        }
    
    def is_valid_placement(self, letter, row, col, first_play=False):
        """
        Check if placing a letter follows all game rules.
        
        Args:
            letter (str): The letter to place
            row (int): Row position
            col (int): Column position
            first_play (bool): Whether this is the first play of the game
            
        Returns:
            bool: True if placement is valid according to game rules
            
        Raises:
            TypeError: If letter is not a string
            ValueError: If letter is not a single alphabetic character
        """
        # Validate letter
        if not isinstance(letter, str):
            raise TypeError("Letter must be a string")
        if len(letter) != 1 or not letter.isalpha():
            raise ValueError("Letter must be a single alphabetic character")
        
        # Check position and game rules
        if not self.is_valid_position(row, col):
            return False
        if self.is_occupied(row, col):
            return False
            
        # First play must cross center
        if first_play and (row != self.center[0] or col != self.center[1]):
            return False
            
        # After first play, must connect to existing mosaic
        if not first_play and not self.has_adjacent_letter(row, col):
            return False
            
        return True
    
    def is_valid_word_placement(self, word, row, col, direction):
        """
        Check if an entire word can be validly placed on the board.
        
        Args:
            word (str): The word to place
            row (int): Starting row position
            col (int): Starting column position
            direction (str): Either 'horizontal' or 'vertical'
            
        Returns:
            bool: True if the word can be validly placed
        """
        if direction not in ['horizontal', 'vertical']:
            return False
            
        # Check if word fits on board
        if direction == 'horizontal' and col + len(word) > self.cols:
            return False
        if direction == 'vertical' and row + len(word) > self.rows:
            return False
            
        # Check if placement conflicts with existing letters
        for i, letter in enumerate(word):
            r, c = (row, col + i) if direction == 'horizontal' else (row + i, col)
            if self.is_occupied(r, c) and self.get_letter(r, c) != letter:
                return False
                
        return True
    
    def place_word(self, word, row, col, direction):
        """
        Place an entire word on the board.
        
        Args:
            word (str): The word to place
            row (int): Starting row position
            col (int): Starting column position
            direction (str): Either 'horizontal' or 'vertical'
            
        Returns:
            bool: True if the word was successfully placed
            
        Raises:
            ValueError: If the word or direction is invalid
            ValueError: If the word doesn't fit on the board
            ValueError: If the word conflicts with existing letters
        """
        # Input validation
        if not isinstance(word, str) or not word:
            raise ValueError("Word must be a non-empty string")
        if not word.isalpha():
            raise ValueError("Word must contain only alphabetic characters")
        if direction not in ['horizontal', 'vertical']:
            raise ValueError("Direction must be 'horizontal' or 'vertical'")
        
        # Check if word fits on board
        if direction == 'horizontal' and col + len(word) > self.cols:
            raise ValueError(f"Word '{word}' doesn't fit horizontally at position ({row}, {col})")
        if direction == 'vertical' and row + len(word) > self.rows:
            raise ValueError(f"Word '{word}' doesn't fit vertically at position ({row}, {col})")
        
        # Check for conflicts with existing letters
        conflicts = []
        for i, letter in enumerate(word):
            r, c = (row, col + i) if direction == 'horizontal' else (row + i, col)
            if self.is_occupied(r, c) and self.get_letter(r, c) != letter:
                conflicts.append((r, c, self.get_letter(r, c), letter))
        
        if conflicts:
            conflict_details = [f"({r},{c}): '{existing}' vs '{new}'" for r, c, existing, new in conflicts]
            raise ValueError(f"Word placement conflicts with existing letters: {', '.join(conflict_details)}")
        
        # Place the word
        for i, letter in enumerate(word.upper()):  # Convert to uppercase
            r, c = (row, col + i) if direction == 'horizontal' else (row + i, col)
            if not self.is_occupied(r, c):
                self.board[r * self.cols + c] = letter
                if (r, c) in self.special_tiles:
                    self.special_tiles_occupied[(r, c)] = True
                    
        return True

    def get_board_2d(self):
        """
        Return the board as a 2D array for easier display in the UI.
        
        Returns:
            list: A 2D list representation of the board where board_2d[row][col]
                  gives the letter at that position
        """
        board_2d = [] # Initialize an empty 2D array
        for r in range(self.rows): # Loop through each row
            row = [] # Initialize an empty row
            for c in range(self.cols): # Loop through each column
                row.append(self.board[r * self.cols + c]) # Add each letter to the row
            board_2d.append(row) # Add the row to the 2D array
        return board_2d # Return the complete 2D board
    
    def validate_word(self, word):
        """
        Check if a word is valid using the WordValidator.

        Args:
            word (str): The word to validate

        Returns:
            bool: True if the word is valid, False otherwise
        """
        return self.word_validator.validate_word(word)
    
    def calculate_word_score(self, word, row, col, direction):
        """
        Calculate score for a word based on letter values and multipliers.
        
        Args:
            word (str): The word to score
            row (int): Starting row position
            col (int): Column position
            direction (str): Either 'horizontal' or 'vertical'
            
        Returns:
            int: The calculated score for the word
        """
        score = 0
        word_multiplier = 1
        
        # Define letter values (A=1, B=3, etc.)
        letter_values = {
            'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4,
            'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3,
            'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8,
            'Y': 4, 'Z': 10
        }
        
        # Calculate score based on letter position and special tiles
        for i, letter in enumerate(word.upper()):
            r, c = (row, col + i) if direction == 'horizontal' else (row + i, col)
            letter_multiplier = 1
            
            # Apply special tile multipliers
            tile_type = self.get_special_tile_multiplier(r, c)
            if tile_type == 'DL':
                letter_multiplier = 2
            elif tile_type == 'TL':
                letter_multiplier = 3
            elif tile_type == 'DW':
                word_multiplier *= 2
            elif tile_type == 'TW':
                word_multiplier *= 3
                
            score += letter_values.get(letter, 0) * letter_multiplier
        
        # Apply word multiplier and length bonus
        final_score = score * word_multiplier
        
        # Word length bonus (5+ letters)
        if len(word) >= 5:
            final_score += (len(word) - 4) * 2
            
        return final_score
    
    def has_valid_moves(self, available_letters):
        """
        Check if there are any valid moves available with the given letters.
        
        Args:
            available_letters (list): List of available letters
            
        Returns:
            bool: True if valid moves exist, False otherwise
        """
        for letter in set(available_letters):  # Use set to avoid checking duplicates
            if self.find_valid_placements(letter):
                return True
        return False
    
    def get_words_formed(self):
        """
        Retrieve all words formed during the current turn.
        
        Returns:
            list: A list of words formed on the board
        """
        words = []
        # Logic to extract words formed horizontally and vertically
        for row in range(self.rows):
            current_word = ""
            for col in range(self.cols):
                letter = self.get_letter(row, col)
                if letter:
                    current_word += letter
                else:
                    if len(current_word) > 1:
                        words.append(current_word)
                    current_word = ""
            if len(current_word) > 1:
                words.append(current_word)
        
        for col in range(self.cols):
            current_word = ""
            for row in range(self.rows):
                letter = self.get_letter(row, col)
                if letter:
                    current_word += letter
                else:
                    if len(current_word) > 1:
                        words.append(current_word)
                    current_word = ""
            if len(current_word) > 1:
                words.append(current_word)
        
        return words
        
    def find_potential_words(self, available_letters, dictionary):
        """
        Find potential words that could be placed on the board.
        
        Args:
            available_letters (list): List of available letters
            dictionary (list): List of valid words
            
        Returns:
            list: Tuples of (word, row, col, direction, score)
        """
        potential_words = []
        
        # This would be a more complex implementation using available letters
        # and checking against valid positions
        
        return potential_words
    
    def to_json(self):
        """Convert the board to a JSON-serializable dictionary."""
        return {
            "rows": self.rows,
            "cols": self.cols,
            "board": self.board,
            "special_tiles_occupied": self.special_tiles_occupied
        }

    @classmethod
    def from_json(cls, data):
        """Create a board from a JSON dictionary."""
        board = cls(data["rows"], data["cols"])
        board.board = data["board"]
        board.special_tiles_occupied = data["special_tiles_occupied"]
        return board

if __name__ == "__main__":
    # Create a test board
    print("Creating a new 15x15 game board...")
    game = Board(15, 15)
    
    # Test 1: Basic letter placement
    print("\n--- Test 1: Basic Letter Placement ---")
    game.place_letter('A', 7, 7)  # Center
    game.place_letter('P', 7, 8)
    game.place_letter('P', 7, 9)
    game.place_letter('L', 7, 10)
    game.place_letter('E', 7, 11)
    print(game)
    print(f"Word at center (horizontal): {game.get_horizontal_word(7, 7)}")
    
    # Test 2: Word placement - Make a compatible crossword 
    print("\n--- Test 2: Word Placement ---")
    # Place a word that shares 'A' with DRAMA
    game.place_word("DRAMA", 3, 7, "vertical")
    print(game)
    print("Words on board:", game.get_all_words())
    
    # Test 3: Error handling
    print("\n--- Test 3: Error Handling ---")
    try:
        game.place_letter('X', 7, 7)  # Already occupied
        print("Test failed: Should have raised an error")
    except ValueError as e:
        print(f"Success! Caught error: {e}")
        
    try:
        game.place_letter('1', 0, 0)  # Non-alphabetic
        print("Test failed: Should have raised an error")
    except ValueError as e:
        print(f"Success! Caught error: {e}")
    
    # Test 4: Special tiles
    print("\n--- Test 4: Special Tiles ---")
    test_board_special = Board(15, 15)  # Use a separate board for this test
    print(f"Special tiles before: {test_board_special.get_special_tiles()}")
    test_board_special.place_letter('Z', 0, 0)  # Place on DL tile
    print(f"Special tiles after: {test_board_special.get_special_tiles()}")
    print(f"Multiplier at (0,0): {test_board_special.get_special_tile_multiplier(0, 0)}")
    print(f"Is special tile occupied: {test_board_special.special_tiles_occupied[(0, 0)]}")
    
    # Test 5: Board coverage
    print("\n--- Test 5: Board Coverage ---")
    print(f"Board coverage: {game.calculate_coverage():.2f}%")
    print(f"Occupied positions: {game.get_occupied_positions()}")
    
    # Test 6: Word identification
    print("\n--- Test 6: Word Identification ---")
    horizontal = game.get_horizontal_word(7, 7)
    vertical = game.get_vertical_word(7, 7)
    print(f"Horizontal word at (7,7): {horizontal}")
    print(f"Vertical word at (7,7): {vertical}")
    
    # Test 7: Finding valid placements
    print("\n--- Test 7: Finding Valid Placements ---")
    valid_placements = game.find_valid_placements('X')
    print(f"Number of valid placements: {len(valid_placements)}")
    print(f"Sample valid positions: {valid_placements[:5] if valid_placements else 'None'}")
    
    # Test 8: Serialization
    print("\n--- Test 8: Serialization ---")
    board_state = game.to_json()
    print(f"Board serialized to: {type(board_state)}")
    
    # Test 9: Create a new board from serialized data
    print("\n--- Test 9: Deserialization ---")
    new_game = Board.from_json(board_state)
    print("Recreated board:")
    print(new_game)
    print(f"Words on recreated board:")
    for word in new_game.get_all_words():
        print(f"  - {word}")
    
    # Test 10: Clear and reset
    print("\n--- Test 10: Clear and Reset ---")
    new_board = Board(15, 15)  # Create a fresh board for this test
    new_board.place_letter('X', 7, 7)  # Place a letter
    print("Before reset:")
    print(new_board)
    new_board.reset_board()
    print("After reset:")
    print(new_board)
    print(f"Board coverage after reset: {new_board.calculate_coverage():.2f}%")
    
    # Test 11: Complex word placement scenario
    print("\n--- Test 11: Complex Word Scenario ---")
    test_board = Board(15, 15)
    test_board.place_word("HELLO", 5, 5, "horizontal")  # Use place_word instead of individual letters
    test_board.place_word("YELLOW", 3, 7, "vertical")   # Will share the 'L' with HELLO
    print(test_board)
    print(f"Words on board: {test_board.get_all_words()}")
    
    # Test 12: 2D representation
    print("\n--- Test 12: 2D Representation ---")
    board_2d = test_board.get_board_2d()  # Use test_board from Test 11
    print("First 5 rows of 2D board:")
    for row in board_2d[:5]:
        print(''.join([f"[{c if c != ' ' else ' '}]" for c in row[:5]]))
    
    # Test 13: Word validation
    print("\n--- Test 13: Word Validation ---")
    valid_words = ["APPLE", "A", "TEST", "PROGRAMMING", "PYTHON"]
    for word in valid_words:
        print(f"Is '{word}' valid? {game.validate_word(word)}")
    
    print("\nAll tests completed!")