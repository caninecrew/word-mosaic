from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, 
    QHBoxLayout, QGridLayout, QFrame, QLineEdit, QMessageBox, QAction, 
    QMenu, QMenuBar, QStatusBar, QRadioButton
)
from PyQt5.QtGui import QFont, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QSize
from board import Board
from letter_bank import LetterBank
from scoring import Scoring
from merriam_webster_api import COLLEGIATE, LEARNERS

class WordMosaicApp(QMainWindow):
    """
    Graphical User Interface for Word Mosaic game using PyQt5
    """
    def __init__(self, game):
        """
        Initialize the GUI with the game logic.
        
        Args:
            game: Game object containing the game logic
        """
        super().__init__()
        self.game = game
        
        # Set window properties
        self.setWindowTitle("Word Mosaic")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f5f5f5;")
        
        # Dictionary setting
        self.selected_dictionary = self.game.word_validator.dictionary_type
        
        # Create main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        
        # Create UI elements
        self._create_menu()
        self._create_top_frame()
        self._create_board_frame()
        self._create_letter_bank_frame()
        self._create_word_entry_frame()
        self._create_status_frame()
        
        # Initialize letters for a new game
        self.update_board_display()
        self.update_letter_bank_display()
        self.update_score_display()
    
    def _create_menu(self):
        """Create the menu bar with game options."""
        # Create menubar
        menubar = self.menuBar()
        
        # Game menu
        game_menu = menubar.addMenu('&Game')
        
        new_game_action = QAction('&New Game', self)
        new_game_action.setShortcut(QKeySequence("Ctrl+N"))
        new_game_action.triggered.connect(self.new_game)
        game_menu.addAction(new_game_action)
        
        high_scores_action = QAction('&High Scores', self)
        high_scores_action.triggered.connect(self.show_high_scores)
        game_menu.addAction(high_scores_action)
        
        game_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        game_menu.addAction(exit_action)
        
        # Options menu
        options_menu = menubar.addMenu('&Options')
        
        # Dictionary submenu
        dictionary_menu = QMenu('&Dictionary', self)
        options_menu.addMenu(dictionary_menu)
        
        collegiate_action = QAction('&Collegiate Dictionary', self)
        collegiate_action.setCheckable(True)
        collegiate_action.setChecked(self.selected_dictionary == COLLEGIATE)
        collegiate_action.triggered.connect(lambda: self.change_dictionary(COLLEGIATE))
        dictionary_menu.addAction(collegiate_action)
        
        learners_action = QAction("&Learner's Dictionary", self)
        learners_action.setCheckable(True)
        learners_action.setChecked(self.selected_dictionary == LEARNERS)
        learners_action.triggered.connect(lambda: self.change_dictionary(LEARNERS))
        dictionary_menu.addAction(learners_action)
        
        self.dictionary_actions = [collegiate_action, learners_action]
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        rules_action = QAction('&Rules', self)
        rules_action.setShortcut(QKeySequence("F1"))
        rules_action.triggered.connect(self.show_rules)
        help_menu.addAction(rules_action)
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        dict_status_action = QAction('&Dictionary Status', self)
        dict_status_action.triggered.connect(self.show_dictionary_status)
        help_menu.addAction(dict_status_action)
    
    def _create_top_frame(self):
        """Create the top frame with game info."""
        top_frame = QWidget()
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(0, 0, 0, 10)
        
        # Score display
        self.score_label = QLabel("Score: 0")
        self.score_label.setFont(QFont("Arial", 16))
        top_layout.addWidget(self.score_label, 1, Qt.AlignLeft)
        
        # Dictionary indicator
        self.dictionary_label = QLabel(f"Dictionary: {self.game.word_validator.dictionary_name}")
        self.dictionary_label.setFont(QFont("Arial", 12))
        top_layout.addWidget(self.dictionary_label, 0, Qt.AlignRight)
        
        self.main_layout.addWidget(top_frame)
    
    def _create_board_frame(self):
        """Create the frame that displays the game board."""
        board_frame = QFrame()
        board_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        board_frame.setStyleSheet("background-color: #e0e0e0;")
        
        board_layout = QGridLayout(board_frame)
        board_layout.setSpacing(2)
        
        # Create grid of cells for the board
        self.board_cells = []
        for row in range(self.game.board.size):
            cell_row = []
            for col in range(self.game.board.size):
                cell = QLabel()
                cell.setFixedSize(40, 40)
                cell.setAlignment(Qt.AlignCenter)
                cell.setFont(QFont("Arial", 16, QFont.Bold))
                cell.setStyleSheet(
                    "background-color: #ffffff; border: 2px solid #c0c0c0; border-radius: 4px;"
                )
                board_layout.addWidget(cell, row, col)
                cell_row.append(cell)
            self.board_cells.append(cell_row)
            
        self.main_layout.addWidget(board_frame)
    
    def _create_letter_bank_frame(self):
        """Create the frame that displays available letters."""
        letter_bank_widget = QWidget()
        letter_bank_layout = QVBoxLayout(letter_bank_widget)
        letter_bank_layout.setContentsMargins(0, 10, 0, 10)
        
        # Label
        label = QLabel("Available Letters:")
        label.setFont(QFont("Arial", 12))
        letter_bank_layout.addWidget(label)
        
        # Track tiles placed in the current turn
        self.current_turn_tiles = []
        
        # Track game over state
        self.is_game_over = False
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Will use flow layout for tiles - we'll create a layout in the update method
        self.letter_bank_layout = QHBoxLayout(self.letter_bank_frame)
        
        letter_bank_layout.addWidget(self.letter_bank_frame)
        self.main_layout.addWidget(letter_bank_widget)
    
    def _create_word_entry_frame(self):
        """Create the frame for entering words."""
        word_entry_widget = QWidget()
        word_entry_layout = QHBoxLayout(word_entry_widget)
        word_entry_layout.setContentsMargins(0, 10, 0, 10)
        
        # Label
        label = QLabel("Enter Word:")
        label.setFont(QFont("Arial", 12))
        word_entry_layout.addWidget(label)
        
        # Text field
        self.word_entry = QLineEdit()
        self.word_entry.setFont(QFont("Arial", 14))
        self.word_entry.returnPressed.connect(self.submit_word)
        word_entry_layout.addWidget(self.word_entry)
        
        # Submit button
        submit_button = QPushButton("Submit")
        submit_button.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; padding: 5px 10px;")
        submit_button.clicked.connect(self.submit_word)
        word_entry_layout.addWidget(submit_button)
        
        self.main_layout.addWidget(word_entry_widget)
    
    def _create_status_frame(self):
        """Create the status bar at the bottom."""
        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Arial", 10))
        self.statusBar.showMessage("Welcome to Word Mosaic!")
        self.setStatusBar(self.statusBar)
    
    def show(self):
        """Override show method to focus on word entry field"""
        super().show()
        self.word_entry.setFocus()
    
    def submit_word(self):
        """Handle submission of a word."""
        word = self.word_entry.text().strip().upper()
        
        if not word:
            return
        
        result = self.game.play_word(word)
        
        if result['valid']:
            self.show_status(f"Word '{word}' played for {result['score']} points!")
            self.update_board_display()
            self.update_letter_bank_display()
            self.update_score_display()
            self.word_entry.clear()
            
            # Show definition if available
            definition = self.game.get_word_definition(word.lower())
            if definition:
                self.show_definition(word, definition)
        else:
            self.show_status(f"Invalid word: {result['reason']}")
    
    def update_board_display(self):
        """Update the board display to reflect the current game state."""
        board = self.game.board
        
        for row in range(board.size):
            for col in range(board.size):
                letter = board.get_letter(row, col)
                cell = self.board_cells[row][col]
                
                if letter:
                    cell.setText(letter)
                    cell.setStyleSheet("background-color: #ffeb3b; border: 2px solid #c0c0c0; border-radius: 4px;")
                else:
                    cell.setText("")
                    cell.setStyleSheet("background-color: #ffffff; border: 2px solid #c0c0c0; border-radius: 4px;")
    
    def update_letter_bank_display(self):
        """Update the letter bank display to show available letters."""
        # Clear existing letters
        while self.letter_bank_layout.count():
            item = self.letter_bank_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Create new letter tiles
        for letter, count in sorted(self.game.letter_bank.get_letter_counts().items()):
            if count > 0:
                for _ in range(count):
                    tile = QLabel(letter)
                    tile.setFixedSize(30, 30)
                    tile.setAlignment(Qt.AlignCenter)
                    tile.setFont(QFont("Arial", 14, QFont.Bold))
                    tile.setStyleSheet(
                        "background-color: #2196f3; color: white; border: 1px solid #0b7dda; border-radius: 4px;"
                    )
                    self.letter_bank_layout.addWidget(tile)
        
        # Add a stretchable space at the end
        self.letter_bank_layout.addStretch(1)
    
    def update_score_display(self):
        """Update the score display."""
        self.score_label.setText(f"Score: {self.game.score}")
    
    def new_game(self):
        """Start a new game."""
        reply = QMessageBox.question(
            self, 'New Game', 
            "Start a new game?", 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.game.new_game()
            self.update_board_display()
            self.update_letter_bank_display()
            self.update_score_display()
            self.show_status("New game started!")
    
    def show_high_scores(self):
        """Show the high scores dialog."""
        # Placeholder - implement high scores later
        QMessageBox.information(self, "High Scores", "Feature coming soon!")
    
    def show_rules(self):
        """Show the game rules dialog."""
        rules = """
        Word Mosaic Rules:
        
        1. Use the available letters to form words.
        2. Words must be at least 3 letters long.
        3. Each turn, place one word on the board.
        4. Words can be placed horizontally or vertically.
        5. Words must connect with existing letters on the board.
        6. All formed words must be valid dictionary words.
        7. Score points based on word length and letter values.
        
        Good luck!
        """
        QMessageBox.information(self, "Game Rules", rules)
    
    def show_about(self):
        """Show the about dialog."""
        about_text = """
        Word Mosaic
        
        A word game inspired by Scrabble, but with a twist.
        
        # Placeholder for definitions content
        self.definitions_content = QLabel("")
        self.definitions_content.setFont(QFont('Arial', 10))
        self.definitions_content.setWordWrap(True)
        definitions_layout.addWidget(self.definitions_content)
        
        # Add definitions widget to main layout
        self.layout.addWidget(definitions_widget)
    
    def clear_definitions(self):
        """
        Clear the definitions display completely.
        This ensures all definitions are removed from the display.
        """
        print("[DEBUG] In clear_definitions(): Attempting to clear definitions display")
        # Try multiple approaches to ensure the display is cleared
        self.definitions_content.clear()
        self.definitions_content.setText("")
        
        # Force a repaint to ensure the UI is updated
        self.definitions_content.repaint()
        print("[DEBUG] Definitions display should now be empty")
    
    def refresh_letter_bank(self):
        """
        QMessageBox.information(self, "About", about_text)
    
    def show_status(self, message):
        """Update the status bar with a message."""
        self.statusBar.showMessage(message)
    
    def show_definition(self, word, definition):
        """Show a popup with the word's definition."""
        QMessageBox.information(self, f"Definition of {word}", definition)
    
    def show_dictionary_status(self):
        """Show information about the current dictionary."""
        info = self.game.word_validator.get_dictionary_info()
        status_text = f"""
        Current Dictionary: {info['name']}
        
        API Key Available: {'Yes' if info['has_api_key'] else 'No - Using Fallback Dictionary'}
        
        You can change dictionaries in Options > Dictionary menu.
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
            self.cells[(row, col)].setStyleSheet("background-color: #ffffcc;")
            self.cells[(row, col)].letter_display.setFont(QFont('Arial', 22, QFont.Bold))  # Match DraggableTile font size
            
            # Set point value for the letter
            point_value = LetterBank.LETTER_VALUES.get(self.selected_letter.lower(), 0)
            self.cells[(row, col)].setPointValue(point_value)

            # Mark special tile as occupied if applicable
            if (row, col) in self.game_board.special_tiles:
                self.game_board.special_tiles_occupied[(row, col)] = True

            # Remove from player's hand
            self.player_hand.remove_letter(self.selected_letter)

            # Add to current turn tiles
            self.current_turn_tiles.append((row, col))

            # Clear selection
            self.selected_letter = None

            # Update letter bank display
            self.refresh_letter_bank()

            # Update status
            self.status_bar.showMessage(f"Placed letter at position ({row}, {col})")

        except ValueError as e:
            self.status_bar.showMessage(f"Invalid placement: {str(e)}")
    
    def change_dictionary(self, dict_type):
        """Change the dictionary being used."""
        self.selected_dictionary = dict_type
        info = self.game.word_validator.switch_dictionary(dict_type)
        
        # Update checked state of menu items
        for action in self.dictionary_actions:
            if action.text() == '&Collegiate Dictionary' and dict_type == COLLEGIATE:
                action.setChecked(True)
            elif action.text() == "&Learner's Dictionary" and dict_type == LEARNERS:
                action.setChecked(True)
            else:
                action.setChecked(False)
        
        # Update dictionary label and status
        self.dictionary_label.setText(f"Dictionary: {info['name']}")
        self.show_status(f"Switched to {info['name']}")

            # Try to place the letter using game logic
            self.game_board.place_letter(letter, row, col)

            # Update the visual board with the letter, using consistent styling
            self.cells[(row, col)].setText(letter.upper())
            self.cells[(row, col)].setStyleSheet("background-color: #ffffcc;")
            self.cells[(row, col)].letter_display.setFont(QFont('Arial', 22, QFont.Bold))  # Match DraggableTile font size
            
            # Set point value for the letter
            point_value = LetterBank.LETTER_VALUES.get(letter.lower(), 0)
            self.cells[(row, col)].setPointValue(point_value)

            # Mark special tile as occupied if applicable
            if (row, col) in self.game_board.special_tiles:
                self.game_board.special_tiles_occupied[(row, col)] = True

            # Remove the original letter from player's hand (whether blank '0' or regular)
            self.player_hand.remove_letter(original_letter)

            # Add to current turn tiles
            self.current_turn_tiles.append((row, col))

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
            print("[DEBUG] Starting word submission")
            
            # Clear all definitions immediately when submit button is clicked
            print("[DEBUG] Clearing definitions display")
            self.clear_definitions()
            print("[DEBUG] Definitions display cleared")
            
            # Get the words formed during the turn
            words_formed = self.game_board.get_all_words()
            print(f"[DEBUG] Words formed: {len(words_formed)} word(s)")

            if not words_formed:
                self.status_bar.showMessage("No valid words formed")
                return

            # Track letters to return to player's hand if invalid words are found
            letters_to_return = []
            positions_to_clear = []
            valid_words = []

            # Validate word positions and check if words are valid
            for word_data in words_formed:
                word, positions = word_data
                print(f"[DEBUG] Validating word: {word}")

                # Convert word to uppercase for validation or display
                word_upper = word.upper()

                if not self.game_board.validate_word_positions(word, positions):
                    self.status_bar.showMessage(f"Invalid word placement: {word_upper}")
                    return

                # Validate using Merriam-Webster API
                if not self.game_board.validate_word(word):
                    print(f"[DEBUG] Invalid word detected: {word_upper}")
                    self.status_bar.showMessage(f"Invalid word: {word_upper}. Tiles returned to your hand.")
                    
                    # Get letters at positions from current turn only
                    for row, col in positions:
                        if (row, col) in self.current_turn_tiles:
                            letter = self.game_board.get_letter(row, col)
                            if letter:
                                letters_to_return.append(letter)
                                positions_to_clear.append((row, col))
                else:
                    print(f"[DEBUG] Valid word found: {word_upper}")
                    valid_words.append(word_data)

            # Clear invalid word positions from board (only current turn tiles)
            for row, col in positions_to_clear:
                self.game_board.clear_position(row, col)
                if (row, col) in self.current_turn_tiles:
                    self.current_turn_tiles.remove((row, col))

            # Return letters to player's hand
            for letter in letters_to_return:
                self.player_hand.add_letter(letter.lower())  # Use lowercase for consistency

            # If letters were returned to the player's hand, refresh display and return
            if letters_to_return:
                print(f"[DEBUG] Returning {len(letters_to_return)} invalid letters to player's hand")
                self.refresh_board()
                self.refresh_letter_bank()
                return

            # If no valid words remain after clearing invalid tiles, refresh display and return
            if not valid_words:
                print("[DEBUG] No valid words remained after validation")
                self.refresh_board()
                self.refresh_letter_bank()
                return

            # Calculate the turn score based on valid words only
            print(f"[DEBUG] Calculating turn score for {len(valid_words)} valid word(s)")
            turn_score = self.game_board.calculate_turn_score(valid_words)
            
            # Update total score
            self.score += turn_score
            print(f"[DEBUG] Score updated: {self.score}")
            self.score_value.setText(str(self.score))
            
            # Get definitions for the words in this turn only
            from dictionary_api import format_definitions
            word_list = [word for word, _ in valid_words]
            print(f"[DEBUG] Getting definitions for: {word_list}")
            formatted_definitions = format_definitions(word_list)
            
            # Set new definitions with header indicating these are from the current turn
            print("[DEBUG] Setting new definitions in display")
            current_turn_text = f"<p><b>Current Turn Words:</b></p>{formatted_definitions}"
            self.definitions_content.setText(current_turn_text)
            self.definitions_content.setTextFormat(Qt.RichText)
            print("[DEBUG] Definitions display updated")

            # Replenish player's hand, accounting for returned tiles
            print(f"[DEBUG] Replenishing player's hand")
            
            # Calculate how many new letters needed after accounting for returned tiles
            needed_letters = max(0, len(self.current_turn_tiles) - len(letters_to_return))
            letters_added = self.player_hand.refill(needed_letters)
            
            print(f"[DEBUG] Letters added to player's hand: {letters_added}")

            # Update letter bank display
            print("[DEBUG] Refreshing letter bank display")
            self.refresh_letter_bank()

            # Update the board and status
            print("[DEBUG] Refreshing board display")
            self.refresh_board()
            
            # Clear the current turn tiles list since the turn is complete
            self.current_turn_tiles = []
            
            # Update status message
            self.status_bar.showMessage(f"Turn completed! Score: {turn_score}")
            print("[DEBUG] Word submission completed successfully")
            
            # Check if the game is over after this turn
            if self.check_game_over():
                print("[DEBUG] Game over detected!")
                self.show_game_over_dialog()

        except Exception as e:
            print(f"[ERROR] Error submitting word: {str(e)}")
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

    def check_game_over(self):
        """
        Check if the game is over.
        
        Game is over when:
        1. The letter bank is empty (no more letters to draw)
        2. AND there are no valid placements for any letters in the player's hand
        
        Returns:
            bool: True if the game is over, False otherwise
        """
        # If already in game over state, return True
        if self.is_game_over:
            return True
            
        # First check if letter bank is empty
        if not self.letter_bank.bank_empty():
            return False  # Still has letters in the bank
        
        # Get the player's current letters
        player_letters = self.player_hand.letter_order
        
        if not player_letters:
            # No letters in hand and bank is empty - game over
            self.is_game_over = True
            return True
            
        # Check if there are any valid placements for the player's letters
        has_valid_moves = False
        for letter in player_letters:
            # Check all potentially valid positions
            for row in range(self.game_board.rows):
                for col in range(self.game_board.cols):
                    if not self.game_board.is_occupied(row, col) and self.game_board.has_adjacent_letter(row, col):
                        # This is a valid position to place a letter - check if it forms valid words
                        try:
                            # Temporarily place the letter
                            self.game_board.place_letter(letter, row, col)
                            
                            # Get all words formed by this placement
                            words_formed = self.game_board.get_all_words()
                            
                            # Check if any of the words formed are valid
                            for word, _ in words_formed:
                                if self.game_board.validate_word(word):
                                    has_valid_moves = True
                                    break
                                    
                            # Remove the temporary letter
                            self.game_board.clear_position(row, col)
                            
                            if has_valid_moves:
                                return False  # Found a valid move, game is not over
                        except ValueError:
                            # Invalid placement, continue checking other positions
                            continue
                            
        # No valid moves found and letter bank is empty - game over
        self.is_game_over = True
        return True

    def show_game_over_dialog(self):
        """
        Show a game over dialog with the final score and statistics.
        """
        from PyQt5.QtWidgets import QMessageBox
        
        # Calculate board coverage
        board_coverage = round(self.game_board.calculate_coverage(), 1)
        
        # Get all words formed on the board
        all_words = self.game_board.get_all_words()
        word_count = len(all_words)
        
        # Calculate longest word
        longest_word = ""
        for word, _ in all_words:
            if len(word) > len(longest_word):
                longest_word = word
        
        # Create message box
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Game Over")
        
        # Set the game over message with statistics
        game_over_html = f"""
        <h2>Game Over!</h2>
        <p>No more moves available.</p>
        <h3>Final Score: {self.score}</h3>
        <p><b>Statistics:</b></p>
        <ul>
            <li>Board Coverage: {board_coverage}%</li>
            <li>Words Placed: {word_count}</li>
            <li>Longest Word: {longest_word.upper()} ({len(longest_word)} letters)</li>
        </ul>
        <p>Thanks for playing Word Mosaic!</p>
        """
        
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(game_over_html)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
        # Update status bar
        self.status_bar.showMessage(f"Game Over! Final Score: {self.score}")
        
        # Disable buttons
        for button in self.findChildren(QPushButton):
            if button.text() in ["Submit Word", "Shuffle Letters"]:
                button.setEnabled(False)

# Main application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordMosaicApp()
    window.show()
    sys.exit(app.exec_())