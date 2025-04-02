class Board:
    """
    Represents the game board for Word Mosaic.
    
    The board is a grid of rows x cols cells where letters can be placed
    to form words. It includes special tiles that provide score multipliers.
    """
    def __init__(self, rows, cols):
        """
        Initialize a new game board with the specified dimensions.
        
        Args:
            rows (int): Number of rows in the board
            cols (int): Number of columns in the board
        """
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
        # Extract a complete word given a position and direction
        if direction == 'horizontal': 
            return self.get_horizontal_word(row, col)
        elif direction == 'vertical':
            return self.get_vertical_word(row, col)
        else:
            raise ValueError("Invalid direction")
        
    def get_all_words(self):
        # Find all words on the board
        words = []
        for row in range(self.rows): # Loop through each row
            for col in range(self.cols): # Loop through each column
                if self.is_occupied(row, col):
                    # Get horizontal and vertical words
                    words.append(self.get_horizontal_word(row, col)) # Add horizontal word
                    words.append(self.get_vertical_word(row, col)) # Add vertical word
        return list(set(words)) # Return unique words found
    
    def get_words_formed(self, row, col, letter):
        # Find all words formed by placing a new letter(s)
        words = []
        if self.is_valid_position(row, col) and not self.is_occupied(row, col): # Check if the position is valid and not occupied
            self.place_letter(letter, row, col) # Place the letter
            words.append(self.get_horizontal_word(row, col)) # Add horizontal word
            words.append(self.get_vertical_word(row, col)) # Add vertical word
            self.clear_position(row, col) # Clear the position after checking
        return list(set(words)) # Return unique words formed
    
    def get_occupied_positions(self):
        # List all occupied positions on the board
        occupied_positions = []
        for row in range(self.rows): # Loop through each row
            for col in range(self.cols): # Loop through each column
                if self.is_occupied(row, col): # Check if the position is occupied
                    occupied_positions.append((row, col)) # Add occupied position to the list
        return occupied_positions # Return the list of occupied positions
    
    def calculate_coverage(self):
        # Calculate the percentage of the board that is filled
        total_positions = self.rows * self.cols # Total number of positions on the board
        occupied_positions = len(self.get_occupied_positions()) # Count occupied positions
        return (occupied_positions / total_positions) * 100
    
    def find_valid_placements(self, letter):
        # Identify legal positions for placing new letters
        valid_positions = []
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.is_occupied(row, col) and self.has_adjacent_letter(row, col):
                    valid_positions.append((row, col))
        return valid_positions
    
    def get_special_tiles(self):
        # Retrieve special tiles and their multipliers
        return {pos: self.special_tiles[pos] for pos in self.special_tiles if not self.special_tiles_occupied[pos]} # Return unoccupied special tiles
    
    def get_special_tile_multiplier(self, row, col):
        # Get the multiplier for a special tile at the specified position
        return self.special_tiles.get((row, col), None)
    
    def get_state(self):
        # Return the current state of the board
        return {
            'board': self.board,
            'special_tiles': self.special_tiles_occupied,
            'center': self.center,
            'coverage': self.calculate_coverage()
        }
    
    def is_valid_placement(self, letter, row, col, first_play=False):
        """Check if placing a letter follows all game rules."""
        # Check basic requirements
        if not self.is_valid_position(row, col) or self.is_occupied(row, col): # Check if the position is valid and not occupied
            return False
            
        # First play must cross center
        if first_play and (row != self.center[0] or col != self.center[1]): # Check if first play is at the center
            return False
            
        # After first play, must connect to existing mosaic
        if not first_play and not self.has_adjacent_letter(row, col):
            return False
            
        return True
    
    def is_valid_word_placement(self, word, row, col, direction):
        """Check if an entire word can be validly placed."""
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
        """Place an entire word on the board."""
        if not self.is_valid_word_placement(word, row, col, direction): # Check if the word can be placed
            return False
            
        # Place each letter
        for i, letter in enumerate(word): # Loop through each letter in the word
            r, c = (row, col + i) if direction == 'horizontal' else (row + i, col)
            if not self.is_occupied(r, c):  # Only place if not already occupied
                self.place_letter(letter, r, c)
                
        return True
    
    def get_board_2d(self):
        """Return the board as a 2D array for easier display."""
        board_2d = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                row.append(self.board[r * self.cols + c])
            board_2d.append(row)
        return board_2d

if __name__ == "__main__":
    # Create a new game board and display it

    game = Board(15, 15) # Create a new game board
    
    game.place_letter('A', 7, 7) # Place a letter on the board
    game.place_letter('B', 7, 8) # Place another letter
    game.place_letter('C', 7, 9) # Place a third letter

    print(game) # Print the initial empty board

