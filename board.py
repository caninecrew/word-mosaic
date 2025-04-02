class Board:
    def __init__(self, rows, cols):
        self.rows = rows # Store the number of rows
        self.cols = cols # Store the number of columns
        self.board = [' ' for _ in range(rows * cols)] # Initialize the board with empty spaces
        self.center = (rows // 2, cols // 2) # Calculate the center position
        self.special_tiles = { # Define special tiles with their multipliers
            (0, 0): 'DL', (0, 7): 'DL', (0, 14): 'DL',
            (7, 0): 'DL', (7, 7): 'TL', (7, 14): 'DL',
            (14, 0): 'DL', (14, 7): 'DL', (14, 14): 'DL'
        }
        self.special_tiles_occupied = {pos: False for pos in self.special_tiles} # Track if special tiles are occupied

    def __str__(self):
        # Generate a string representation of the board for display
        board_str = '' # Initialize an empty string
        for i in range(self.rows): # Loop through each row
            for j in range(self.cols): # Loop through each column
                board_str += self.board[i * self.cols + j] + ' ' # Add the letter or space to the string
            board_str += '\n' # Add a newline after each row
        return board_str # Return the complete board string
    
    def place_letter(self, letter, row, col):
        # Place a letter on the board at the specified position
        if self.is_occupied(row, col): # Check if the position is occupied
            raise ValueError("Position already occupied")
        if not self.is_valid_position(row, col):
            raise ValueError("Invalid position")
        self.board[row * self.cols + col] = letter # Place the letter
        if (row, col) in self.special_tiles: # Check if it's a special tile
            self.special_tiles_occupied[(row, col)] = True # Mark the special tile as occupied

    def is_occupied(self, row, col):
        # Check if the specified position is occupied
        return self.board[row * self.cols + col] != ' '
    
    def get_letter(self, row, col):
        # Retrieve the letter at the specified position
        return self.board[row * self.cols + col] if self.is_valid_position(row, col) else None
        
"""
Is occupied: Check if a position already has a letter
Get letter: Retrieve the letter at a given position
Clear position: Remove a letter from a position
Reset board: Clear all letters from the board
game = Board(15, 15) # Create a new game board
print(game) # Print the initial empty board
Game Rule Enforcement
Is center covered: Check if the center position has a letter
Is valid position: Ensure coordinates are within bounds
Has adjacent letter: Check if a position connects to existing letters
Get word at position: Extract a complete word given a position and direction
Word Formation
Get horizontal word: Retrieve a word reading from left to right
Get vertical word: Retrieve a word reading from top to bottom
Get all words: Find all words formed by a new placement
Board Analysis
Get occupied positions: List all positions with letters
Calculate coverage: Determine percentage of board filled
Find valid placements: Identify legal positions for new letters
Display Support
To string: Generate string representation of board
Get state: Return the current state for the GUI to display"
"""