from board import Board
from letter_bank import LetterBank, PlayerHand

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QGridLayout, QLabel, QFrame, QHBoxLayout, QStatusBar, QPushButton)
from PyQt5.QtCore import Qt, QMimeData, QPoint, QEvent
from PyQt5.QtGui import QFont, QDrag, QPixmap, QPainter
from PyQt5.QtWidgets import QInputDialog

class DraggableTile(QLabel):
    """
    Custom QLabel subclass that implements drag functionality for letter tiles.
    This allows players to drag letters directly from their tile rack to the board.
    """
    
    def __init__(self, text, letter, index, parent=None):
        """
        Initialize a draggable tile.
        
        Args:
            text (str): The text to display on the tile
            letter (str): The underlying letter (may be different from displayed text for blank tiles)
            index (int): The index of this tile in the player's hand
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.letter = letter
        self.index = index
        self.setFixedSize(35, 35)
        self.setAlignment(Qt.AlignCenter)
        self.setFrameShape(QFrame.Box)
        self.setFont(QFont('Arial', 12, QFont.Bold))
        self.setStyleSheet("background-color: #ffffcc;")
        
        # Enable mouse tracking for this widget
        self.setMouseTracking(True)
        
    def mousePressEvent(self, event):
        """Handle mouse press events for tile selection and initiating drag."""
        if event.button() == Qt.LeftButton:
            # If just clicked (not dragged), access the main window to call select_letter
            main_window = self.window()
            if hasattr(main_window, 'select_letter'):
                main_window.select_letter(self.letter, self.index)
            
            # Store the position for potential drag
            self.drag_start_position = event.pos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events to initiate dragging."""
        # Check if left button is pressed and if we've moved far enough to start a drag
        if not (event.buttons() & Qt.LeftButton):
            return
            
        if not hasattr(self, 'drag_start_position'):
            return
            
        # Minimum distance to register as a drag rather than a click
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
            
        # Start drag
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Store the letter and index data
        mime_data.setText(f"{self.letter},{self.index}")
        drag.setMimeData(mime_data)
        
        # Create a pixmap for visual feedback during drag
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        self.render(painter)
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        
        # Execute the drag
        drag.exec_(Qt.CopyAction)

class DroppableCell(QLabel):
    """
    Custom QLabel subclass that accepts dropped letter tiles on the board.
    """
    
    def __init__(self, row, col, parent=None):
        """
        Initialize a droppable cell on the game board.
        
        Args:
            row (int): The row index of this cell
            col (int): The column index of this cell
            parent: Parent widget
        """
        super().__init__(parent)
        self.row = row
        self.col = col
        self.setFixedSize(40, 40)
        self.setAlignment(Qt.AlignCenter)
        self.setFrameShape(QFrame.Box)
        
        # Store original style for resetting after drag operations
        self.original_style = None
        self.original_text = None
        self.original_font = None
        
        # Enable drop events
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        """Handle mouse clicks to place selected letters (for click-twice functionality)"""
        if event.button() == Qt.LeftButton:
            # Access main window to handle the letter placement
            main_window = self.window()
            if hasattr(main_window, 'place_letter'):
                main_window.place_letter(self.row, self.col)
                
        super().mousePressEvent(event)
        
    def saveOriginalState(self):
        """Save the current style, text and font to restore later."""
        self.original_style = self.styleSheet()
        self.original_text = self.text()
        self.original_font = self.font()
        
    def restoreOriginalState(self):
        """Restore the original style, text and font."""
        if self.original_style is not None:
            self.setStyleSheet(self.original_style)
            self.setText(self.original_text)
            self.setFont(self.original_font)
            # Clear saved state
            self.original_style = None
            self.original_text = None
            self.original_font = None
        
    def dragEnterEvent(self, event):
        """Accept the drag enter event if it has text data (our letter info)."""
        if event.mimeData().hasText():
            # Save current state before changing appearance
            self.saveOriginalState()
            
            # Visual feedback - highlight the cell with a dashed border
            self.setStyleSheet("border: 2px dashed #333; background-color: #e6ffcc;")
            event.acceptProposedAction()
    
    def dragLeaveEvent(self, event):
        """Reset visual styling when drag leaves the cell."""
        # Restore original state
        self.restoreOriginalState()
        
    def dragMoveEvent(self, event):
        """Handle drag move events to maintain visual feedback."""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Handle the drop of a letter tile onto this cell."""
        if event.mimeData().hasText():
            # Restore original state as the tile will be placed by the game logic
            self.restoreOriginalState()
            
            # Extract the letter and index from mime data
            data = event.mimeData().text().split(',')
            if len(data) == 2:
                letter, index = data
                index = int(index)
                
                # Call the game's place_letter method with this cell's coordinates
                main_window = self.window()
                if hasattr(main_window, 'place_tile_from_drop'):
                    main_window.place_tile_from_drop(letter, index, self.row, self.col)
                
            event.acceptProposedAction()

class WordMosaicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Word Mosaic")
        self.setGeometry(100, 100, 800, 600)

        # Define special tiles
        special_tiles = {
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

        # Initialize game components
        self.game_board = Board(15, 15, special_tiles)  # Pass special_tiles here
        self.letter_bank = LetterBank()
        self.player_hand = self.letter_bank.create_player_hand()
        self.player_hand.fill_initial_hand()
        self.score = 0
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Welcome to Word Mosaic!")
        
        # Initialize UI components
        self.init_ui()
        
    def init_ui(self):
        """
        Initialize the user interface components.
        This includes creating the score display, game board, letter bank, and control buttons.
        """
        # Create score display
        self.create_score_display()
        
        # Create game board
        self.create_game_board()
        
        # Create letter bank widget and layout once
        self.letter_bank_widget = QWidget()
        self.letter_bank_layout = QHBoxLayout(self.letter_bank_widget)
        self.layout.addWidget(self.letter_bank_widget)
        
        # Populate letter bank
        self.populate_letter_bank()
        
        # Create control buttons
        self.create_control_buttons()
        
        # Create definitions display
        self.create_definitions_display()
    
    def create_score_display(self):
        """
        Create a simple score display at the top of the window.
        Displays the current score of the player.
        """
        score_widget = QWidget()
        score_layout = QHBoxLayout(score_widget)
        
        # Score label
        score_title = QLabel("Score:")
        score_title.setFont(QFont('Arial', 14))
        score_layout.addWidget(score_title)
        
        # Actual score value
        self.score_value = QLabel("0")
        self.score_value.setFont(QFont('Arial', 14, QFont.Bold))
        score_layout.addWidget(self.score_value)
        
        # Add spacer to push score to left
        score_layout.addStretch()
        
        # Add score widget to main layout
        self.layout.addWidget(score_widget)
        
    def create_game_board(self):
        """
        Create a 15x15 grid for the game board.
        Each cell is represented as a QLabel and can display letters or special tile markers.
        """
        board_widget = QWidget()
        board_layout = QGridLayout(board_widget)
        board_layout.setSpacing(2)  # Space between cells

        # Create 15x15 grid of cells
        self.cells = {}
        for row in range(15):
            for col in range(15):
                cell = DroppableCell(row, col, board_widget)
                cell.setFixedSize(40, 40)  # Fixed cell size
                cell.setAlignment(Qt.AlignCenter)
                cell.setFrameShape(QFrame.Box)  # Add border

                # Highlight special tiles
                special_tile = self.game_board.get_special_tile_multiplier(row, col)
                if special_tile == 'TW':
                    cell.setStyleSheet("background-color: #ff9999;")  # Triple Word
                    cell.setText("TW")
                    cell.setFont(QFont('Arial', 10, QFont.Bold))  # Smaller font for special tiles
                elif special_tile == 'DW':
                    cell.setStyleSheet("background-color: #ffcc99;")  # Double Word
                    cell.setText("DW")
                    cell.setFont(QFont('Arial', 10, QFont.Bold))  # Smaller font for special tiles
                elif special_tile == 'TL':
                    cell.setStyleSheet("background-color: #9999ff;")  # Triple Letter
                    cell.setText("TL")
                    cell.setFont(QFont('Arial', 10, QFont.Bold))  # Smaller font for special tiles
                elif special_tile == 'DL':
                    cell.setStyleSheet("background-color: #99ccff;")  # Double Letter
                    cell.setText("DL")
                    cell.setFont(QFont('Arial', 10, QFont.Bold))  # Smaller font for special tiles
                elif row == 7 and col == 7:
                    cell.setStyleSheet("background-color: #ffcccc;")  # Center tile
                    cell.setFont(QFont('Arial', 10, QFont.Bold))  # Smaller font for center tile

                # Store cell reference and add to layout
                self.cells[(row, col)] = cell
                board_layout.addWidget(cell, row, col)

        # Add board to main layout
        self.layout.addWidget(board_widget)
            
    def populate_letter_bank(self):
        """
        Populate the letter bank with the player's current letters.
        Clears the existing letter bank and repopulates it with the current hand.
        """
        # Clear existing widgets
        while self.letter_bank_layout.count():
            item = self.letter_bank_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add a label for the letter bank
        bank_label = QLabel("Your Letters:")
        bank_label.setFont(QFont('Arial', 12))
        self.letter_bank_layout.addWidget(bank_label)
        
        # Get actual letters from player hand
        self.letter_tiles = []
        player_letters = self.player_hand.letter_order
        
        for i, letter in enumerate(player_letters):
            # Handle blank tiles explicitly
            display_letter = "" if letter == "0" else letter.upper()
            
            tile = DraggableTile(display_letter, letter, i, self.letter_bank_widget)
            
            self.letter_bank_layout.addWidget(tile)
            self.letter_tiles.append(tile)
    
    def create_control_buttons(self):
        """
        Create control buttons for the game.
        Includes buttons for submitting a word and shuffling letters.
        """
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        
        # Submit word button
        submit_button = QPushButton("Submit Word")
        submit_button.clicked.connect(self.submit_word)
        buttons_layout.addWidget(submit_button)
        
        # Shuffle letters button
        shuffle_button = QPushButton("Shuffle Letters")
        shuffle_button.clicked.connect(self.shuffle_letters)
        buttons_layout.addWidget(shuffle_button)
        
        # Add buttons widget to main layout
        self.layout.addWidget(buttons_widget)
    
    def create_definitions_display(self):
        """
        Create a widget to display word definitions.
        """
        definitions_widget = QWidget()
        definitions_layout = QVBoxLayout(definitions_widget)
        
        # Definitions label
        definitions_label = QLabel("Word Definitions:")
        definitions_label.setFont(QFont('Arial', 12))
        definitions_layout.addWidget(definitions_label)
        
        # Placeholder for definitions content
        self.definitions_content = QLabel("")
        self.definitions_content.setFont(QFont('Arial', 10))
        self.definitions_content.setWordWrap(True)
        definitions_layout.addWidget(self.definitions_content)
        
        # Add definitions widget to main layout
        self.layout.addWidget(definitions_widget)
    
    def refresh_letter_bank(self):
        """
        Refresh the letter bank display.
        Clears and repopulates the letter bank with the current hand.
        """
        self.populate_letter_bank()
    
    def refresh_board(self):
        """
        Refresh the board display based on the current game state.
        Updates the letters and special tile markers on the board.
        """
        for row in range(15):
            for col in range(15):
                letter = self.game_board.get_letter(row, col)
                if letter:
                    # Display the letter if present, using letter bank color and consistent font
                    self.cells[(row, col)].setText(letter.upper())
                    self.cells[(row, col)].setStyleSheet("background-color: #ffffcc; font-weight: bold;")
                    self.cells[(row, col)].setFont(QFont('Arial', 14, QFont.Bold))  # Consistent font for all placed letters
                else:
                    # Check if the cell is a special tile
                    special_tile = self.game_board.get_special_tile_multiplier(row, col)
                    if special_tile == 'TW':
                        self.cells[(row, col)].setText("TW")
                        self.cells[(row, col)].setStyleSheet("background-color: #ff9999;")  # Triple Word
                        self.cells[(row, col)].setFont(QFont('Arial', 10, QFont.Bold))  # Smaller font for special tiles
                    elif special_tile == 'DW':
                        self.cells[(row, col)].setText("DW")
                        self.cells[(row, col)].setStyleSheet("background-color: #ffcc99;")  # Double Word
                        self.cells[(row, col)].setFont(QFont('Arial', 10, QFont.Bold))  # Smaller font for special tiles
                    elif special_tile == 'TL':
                        self.cells[(row, col)].setText("TL")
                        self.cells[(row, col)].setStyleSheet("background-color: #9999ff;")  # Triple Letter
                        self.cells[(row, col)].setFont(QFont('Arial', 10, QFont.Bold))  # Smaller font for special tiles
                    elif special_tile == 'DL':
                        self.cells[(row, col)].setText("DL")
                        self.cells[(row, col)].setStyleSheet("background-color: #99ccff;")  # Double Letter
                        self.cells[(row, col)].setFont(QFont('Arial', 10, QFont.Bold))  # Smaller font for special tiles
                    else:
                        # Clear the cell if it's not a special tile
                        self.cells[(row, col)].setText("")
                        self.cells[(row, col)].setStyleSheet("")  # Reset to default background
                        self.cells[(row, col)].setFont(QFont('Arial', 10))  # Reset font for empty cells
    
    def select_letter(self, letter, index):
        """
        Handle letter selection from the letter bank.
        Highlights the selected letter and updates the status bar.
        """
        if letter == '0':  # Blank tile
            # Prompt the user to choose a letter for the blank tile
            chosen_letter, ok = QInputDialog.getText(self, "Choose Letter", "Enter a letter for the blank tile:")
            if ok and chosen_letter.isalpha() and len(chosen_letter) == 1:
                self.selected_letter = chosen_letter.lower()  # Store the chosen letter
                self.status_bar.showMessage(f"Selected blank tile as: {chosen_letter.upper()}")
            else:
                self.status_bar.showMessage("Invalid input. Please select a valid letter.")
                return
        else:
            self.selected_letter = letter

        self.selected_index = index
        self.status_bar.showMessage(f"Selected letter: {self.selected_letter.upper()}")

        # Highlight only the specific clicked tile
        for i, tile in enumerate(self.letter_tiles):
            if i == index:
                tile.setStyleSheet("background-color: #ffcc66; border: 2px solid black;")
            else:
                tile.setStyleSheet("background-color: #ffffcc;")
    
    def place_letter(self, row, col):
        """
        Handle letter placement on the board.
        Places the selected letter on the specified cell and updates the game state.
        """
        if not hasattr(self, 'selected_letter') or not self.selected_letter:
            self.status_bar.showMessage("Please select a letter first")
            return

        try:
            # Try to place the letter using your game logic
            self.game_board.place_letter(self.selected_letter, row, col)

            # Update the visual board with the letter, using consistent styling
            self.cells[(row, col)].setText(self.selected_letter.upper())
            self.cells[(row, col)].setStyleSheet("background-color: #ffffcc; font-weight: bold;")
            self.cells[(row, col)].setFont(QFont('Arial', 14, QFont.Bold))  # Consistent font for all placed letters

            # Mark special tile as occupied if applicable
            if (row, col) in self.game_board.special_tiles:
                self.game_board.special_tiles_occupied[(row, col)] = True

            # Remove from player's hand
            self.player_hand.remove_letter(self.selected_letter)

            # Clear selection
            self.selected_letter = None

            # Update letter bank display
            self.refresh_letter_bank()

            # Update status
            self.status_bar.showMessage(f"Placed letter at position ({row}, {col})")

        except ValueError as e:
            self.status_bar.showMessage(f"Invalid placement: {str(e)}")
    
    def place_tile_from_drop(self, letter, index, row, col):
        """
        Place a letter on the board after it was dragged and dropped.
        This is similar to place_letter but triggered by drag-and-drop.
        
        Args:
            letter (str): The letter to place
            index (int): The index of the letter in the player's hand
            row (int): The row to place the letter at
            col (int): The column to place the letter at
        """
        try:
            # Store original letter (for removing from hand later)
            original_letter = letter
            
            # First validate the position is valid and unoccupied
            # This ensures we only ask for blank input if the position is within board boundaries
            if not self.game_board.is_valid_position(row, col):
                raise ValueError(f"Position ({row}, {col}) is outside the board boundaries")
                
            if self.game_board.is_occupied(row, col):
                raise ValueError(f"Position ({row}, {col}) is already occupied")
                
            # Handle blank tiles after validating the position
            if letter == '0':
                # Prompt the user to choose a letter for the blank tile
                chosen_letter, ok = QInputDialog.getText(self, "Choose Letter", "Enter a letter for the blank tile:")
                if ok and chosen_letter.isalpha() and len(chosen_letter) == 1:
                    letter = chosen_letter.lower()  # Use the chosen letter
                else:
                    self.status_bar.showMessage("Invalid input. Drag cancelled.")
                    return

            # Try to place the letter using game logic
            self.game_board.place_letter(letter, row, col)

            # Update the visual board with the letter, using consistent styling
            self.cells[(row, col)].setText(letter.upper())
            self.cells[(row, col)].setStyleSheet("background-color: #ffffcc; font-weight: bold;")
            self.cells[(row, col)].setFont(QFont('Arial', 14, QFont.Bold))

            # Mark special tile as occupied if applicable
            if (row, col) in self.game_board.special_tiles:
                self.game_board.special_tiles_occupied[(row, col)] = True

            # Remove the original letter from player's hand (whether blank '0' or regular)
            self.player_hand.remove_letter(original_letter)

            # Update letter bank display
            self.refresh_letter_bank()

            # Update status
            self.status_bar.showMessage(f"Placed letter at position ({row}, {col})")

        except ValueError as e:
            self.status_bar.showMessage(f"Invalid placement: {str(e)}")
    
    def submit_word(self):
        """
        Submit the current word and calculate the score.
        Validates the word, updates the score, and replenishes the player's hand.
        """
        try:
            print("=== Starting word submission ===")
            # Get the words formed during the turn
            words_formed = self.game_board.get_all_words()  # List of (word, positions) tuples
            print(f"Words formed: {words_formed}")  # Debugging statement

            # Validate word positions
            for word_data in words_formed:
                word, positions = word_data
                print(f"Validating word: {word}, positions: {positions}")  # Debugging statement

                # Ensure 'word' is a string before calling .upper()
                if not isinstance(word, str):
                    raise TypeError(f"Expected 'word' to be a string, but got {type(word).__name__}: {word}")

                # Convert word to uppercase for validation or display
                word = word.upper()

                print(f"Submitting word: {word}, positions: {positions}")  # Debugging statement
                print(f"Current score before submission: {self.score}")  # Debugging statement

                if not self.game_board.validate_word_positions(word, positions):
                    self.status_bar.showMessage(f"Invalid word placement: {word}")
                    return

            # Calculate the turn score
            print("Calculating turn score...")
            turn_score = self.game_board.calculate_turn_score(words_formed)
            print(f"Turn score calculated: {turn_score}")
            
            # Update total score
            self.score += turn_score
            print(f"Updated total score: {self.score}")
            self.score_value.setText(str(self.score))
            print(f"Score display updated to: {self.score_value.text()}")

            # Get definitions for the words
            from dictionary_api import format_definitions
            word_list = [word for word, _ in words_formed]
            formatted_definitions = format_definitions(word_list)
            self.definitions_content.setText(formatted_definitions)
            self.definitions_content.setTextFormat(Qt.RichText)

            # Replenish player's hand
            print(f"Replenishing player's hand with {len(words_formed)} new letters...")
            print(f"Player hand before refill: {self.player_hand.letter_order}")
            letters_added = self.player_hand.refill(len(words_formed))
            print(f"Player hand after refill: {self.player_hand.letter_order}")
            print(f"Letters added: {letters_added}")

            # Update letter bank display
            print("Refreshing letter bank display...")
            self.refresh_letter_bank()

            # Update the board and status
            print("Refreshing board display...")
            self.refresh_board()
            
            # Update status message
            print(f"Setting status message: Turn completed! Score: {turn_score}")
            self.status_bar.showMessage(f"Turn completed! Score: {turn_score}")
            print("=== Word submission completed ===")

        except Exception as e:
            print(f"Error submitting word: {str(e)}")
            import traceback
            traceback.print_exc()
            self.status_bar.showMessage(f"Error submitting word: {str(e)}")

    def shuffle_letters(self):
        """
        Shuffle the player's letter bank.
        Updates the letter bank display and shows a status message.
        """
        self.player_hand.shuffle_letters()
        self.refresh_letter_bank()
        self.status_bar.showMessage("Letters shuffled")

# Main application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordMosaicApp()
    window.show()
    sys.exit(app.exec_())