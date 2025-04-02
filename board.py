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
    
    def clear_position(self, row, col):
        # Remove the letter from the specified position
        if self.is_valid_position(row, col):
            self.board[row * self.cols + col] = ' '# Clear the position
        if (row, col) in self.special_tiles: # Check if it's a special tile
            self.special_tiles_occupied[(row, col)] = False # Mark the special tile as unoccupied

    def reset_board(self):
        # Clear all letters from the board
        self.board = [' ' for _ in range(self.rows * self.cols)] # Reset the board to empty spaces
        self.special_tiles_occupied = {pos: False for pos in self.special_tiles} # Reset special tiles

    def is_center_covered(self):
        # Check if the center position has a letter
        return self.is_occupied(self.center[0], self.center[1]) # Check if the center is occupied
    
    def is_valid_position(self, row, col):
        # Ensure coordinates are within bounds
        return 0 <= row < self.rows and 0 <= col < self.cols # Check if the position is valid
    
    def has_adjacent_letter(self, row, col):
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
        return ''.join(self.board[row * self.cols + start_col:end_col + 1]) # Extract the word from the board
    
    def get_vertical_word(self, row, col):
        # Retrieve a word reading from top to bottom
        if not self.is_valid_position(row, col):
            return ""
        if not self.is_occupied(row, col): # Check if the position is occupied
            return ""
        start_row = row # Start row for the word
        while start_row > 0 and self.is_occupied(start_row - 1, col): # Move up to find the start of the word
            start_row -= 1 # Check if the position is occupied
        end_row = row # End row for the word
        while end_row < self.rows - 1 and self.is_occupied(end_row + 1, col): # Move down to find the end of the word
            end_row += 1 # Move down to find the end of the word
        return ''.join(self.board[start_row * self.cols + col:end_row * self.cols + col + 1]) # Extract the word from the board
    
    def get_word_at_position(self, row, col, direction):
        # Extract a complete word given a position and direction
        if direction == 'horizontal': 
            return self.get_horizontal_word(row, col)
        elif direction == 'vertical':
            return self.get_vertical_word(row, col)
        else:
            raise ValueError("Invalid direction")

game = Board(15, 15) # Create a new game board
print(game) # Print the initial empty board
        
    

        
"""
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