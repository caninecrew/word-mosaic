import sys
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, 
    QHBoxLayout, QGridLayout, QFrame, QLineEdit, QMessageBox, QAction, 
    QMenu, QMenuBar, QStatusBar, QRadioButton, QSizePolicy
)
from PyQt5.QtGui import QFont, QIcon, QKeySequence, QDrag
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QMimeData, QPoint
from board import Board
from letter_bank import LetterBank
from scoring import Scoring
from merriam_webster_api import COLLEGIATE, LEARNERS

class ClickableLabel(QLabel):
    """
    A QLabel that emits a signal when clicked.
    """
    clicked = pyqtSignal(int, int)

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.row = None
        self.col = None
        self.setAcceptDrops(True)  # Enable drop events

    def mousePressEvent(self, event):
        if self.row is not None and self.col is not None:
            self.clicked.emit(self.row, self.col)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        if event.mimeData().hasText():
            letter = event.mimeData().text()
            event.accept()
            if self.row is not None and self.col is not None:
                self.clicked.emit(self.row, self.col)
                # The letter will be handled by the parent widget's handle_cell_click

class DraggableLetterLabel(QLabel):
    """
    A specialized QLabel for letters in the letter bank that can be dragged.
    """
    clicked = pyqtSignal(str)

    def __init__(self, letter, value, parent=None):
        super().__init__(letter, parent)
        self.letter = letter
        self.value = value
        self.selected = False
        self.setStyleSheet("background-color: #ffd700; border: 1px solid #c0c0c0; border-radius: 4px;")
        self.setAlignment(Qt.AlignCenter)
        self.setFont(QFont("Arial", 14, QFont.Bold))
        self.setFixedSize(40, 40)
        
        # Add a small value indicator in the corner
        if letter != '0':  # Don't show value for blank tiles
            value_label = QLabel(str(value), self)
            value_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            value_label.setFont(QFont("Arial", 7))
            value_label.setGeometry(25, 25, 15, 15)
            value_label.setStyleSheet("background-color: transparent; border: none;")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.letter)  # Emit clicked signal
            
            # Start drag operation
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.letter)
            drag.setMimeData(mime_data)
            
            # Optionally, set a pixmap for the drag operation
            # pixmap = self.grab()
            # drag.setPixmap(pixmap)
            
            # Execute the drag
            drag.exec_(Qt.CopyAction)
        
    def set_selected(self, selected):
        """Mark this letter as selected or not."""
        self.selected = selected
        if selected:
            self.setStyleSheet("background-color: #ff9966; border: 2px solid #c0c0c0; border-radius: 4px;")
        else:
            self.setStyleSheet("background-color: #ffd700; border: 1px solid #c0c0c0; border-radius: 4px;")

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
        
        # Initialize game state
        self.selected_letter = None  # Currently selected letter from the letter bank
        self.current_turn_tiles = []  # Track tiles placed in the current turn
        self.is_game_over = False
        
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
        self._create_action_frame()  # Renamed from word_entry_frame
        self._create_status_bar()  # Added status bar
        
        # Initialize letters for a new game
        self.update_board_display()
        self.update_letter_bank_display()
        self.update_score_display()
    
    def _create_menu(self):
        """Create the menu bar with game options."""
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
        
        # Use grid layout with fixed spacing
        board_layout = QGridLayout(board_frame)
        board_layout.setSpacing(2)  # Equal spacing between cells
        board_layout.setContentsMargins(10, 10, 10, 10)
        
        # Make the grid maintain equal spacing when resized
        for i in range(self.game.board.rows):
            board_layout.setColumnStretch(i, 1)
            board_layout.setRowStretch(i, 1)
        
        # Create grid of cells for the board
        self.board_cells = []
        for row in range(self.game.board.rows):
            cell_row = []
            for col in range(self.game.board.cols):
                # Create a frame for each cell to contain letter and score
                cell_frame = QFrame()
                cell_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                cell_frame.setMinimumSize(40, 40)  # Minimum size for the cell
                
                # Get special tile info to set background color
                special_tile = self.game.board.get_special_tile_multiplier(row, col)
                if special_tile:
                    if special_tile == "TW":
                        cell_frame.setStyleSheet("background-color: #ff6666; border: 2px solid #c0c0c0; border-radius: 4px;")
                    elif special_tile == "DW":
                        cell_frame.setStyleSheet("background-color: #ff9999; border: 2px solid #c0c0c0; border-radius: 4px;")
                    elif special_tile == "TL":
                        cell_frame.setStyleSheet("background-color: #66b3ff; border: 2px solid #c0c0c0; border-radius: 4px;")
                    elif special_tile == "DL":
                        cell_frame.setStyleSheet("background-color: #99ccff; border: 2px solid #c0c0c0; border-radius: 4px;")
                else:
                    cell_frame.setStyleSheet("background-color: #ffffff; border: 2px solid #c0c0c0; border-radius: 4px;")
                
                # Use layout for each cell to position letter and score
                cell_layout = QGridLayout(cell_frame)
                cell_layout.setContentsMargins(2, 2, 2, 2)
                cell_layout.setSpacing(0)
                
                # Create cell label for the letter
                cell = ClickableLabel("")
                cell.setAlignment(Qt.AlignCenter)
                cell.setFont(QFont("Arial", 16, QFont.Bold))
                cell.setStyleSheet("background-color: transparent; border: none;")
                cell_layout.addWidget(cell, 0, 0, 1, 1, Qt.AlignCenter)
                
                # Add score label to the bottom right
                score_label = QLabel("")
                score_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
                score_label.setFont(QFont("Arial", 7))
                score_label.setStyleSheet("background-color: transparent; border: none;")
                cell_layout.addWidget(score_label, 0, 0, 1, 1, Qt.AlignRight | Qt.AlignBottom)
                
                # Connect click event to handler
                cell.clicked.connect(self.handle_cell_click)
                cell.row = row
                cell.col = col
                
                # Store both labels for later access
                cell.score_label = score_label
                
                board_layout.addWidget(cell_frame, row, col)
                cell_row.append(cell)
            self.board_cells.append(cell_row)
        
        # Make the board frame expand to fill available space
        board_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
        self.main_layout.addWidget(board_frame)
        
    def handle_cell_click(self, row, col):
        """Handle click on a board cell."""
        # If a letter is selected from the letter bank
        if self.selected_letter:
            # Try to place the letter on the board
            try:
                self.game.board.place_letter(self.selected_letter, row, col)
                
                # Remove the letter from the player's hand
                self.game.letter_bank.use_letters(self.selected_letter)
                
                # Add to the current turn's tiles
                self.current_turn_tiles.append((row, col, self.selected_letter))
                
                # Update displays
                self.update_board_display()
                self.update_letter_bank_display()
                
                # Reset selected letter
                self.selected_letter = None
                
                # After placing, check for valid words
                self._check_for_words()
                
                self.status_bar.showMessage(f"Letter placed at position ({row}, {col})")
            except ValueError as e:
                self.status_bar.showMessage(f"Cannot place letter: {str(e)}")
        else:
            # If no letter is selected, check if there's a letter on the cell that can be removed
            letter_removed = False
            for i, (r, c, letter) in enumerate(self.current_turn_tiles):
                if r == row and c == col:
                    # Remove the letter from the board
                    self.game.board.clear_position(row, col)
                    
                    # Return the letter to the player's hand
                    self.game.letter_bank.add_letter(letter)
                    
                    # Remove from current turn tiles
                    self.current_turn_tiles.pop(i)
                    
                    # Update displays
                    self.update_board_display()
                    self.update_letter_bank_display()
                    
                    self.status_bar.showMessage(f"Letter removed from position ({row}, {col})")
                    letter_removed = True
                    break
                    
            if not letter_removed:
                self.status_bar.showMessage("Select a letter first, then click on the board to place it")
    
    def _create_letter_bank_frame(self):
        """Create the frame that displays available letters."""
        letter_bank_widget = QWidget()
        letter_bank_layout = QVBoxLayout(letter_bank_widget)
        letter_bank_layout.setContentsMargins(0, 10, 0, 10)
        
        # Label
        label = QLabel("Available Letters:")
        label.setFont(QFont("Arial", 12))
        letter_bank_layout.addWidget(label)
        
        # Create letter bank frame with a horizontal layout
        self.letter_bank_frame = QWidget()
        self.letter_bank_layout = QHBoxLayout(self.letter_bank_frame)
        self.letter_bank_layout.setSpacing(5)
        self.letter_bank_layout.setAlignment(Qt.AlignCenter)
        
        letter_bank_layout.addWidget(self.letter_bank_frame)
        self.main_layout.addWidget(letter_bank_widget)
    
    def _create_action_frame(self):
        """Create buttons for game actions like end turn and shuffle."""
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(0, 10, 0, 10)
        action_layout.setAlignment(Qt.AlignCenter)
        
        # End Turn button
        end_turn_button = QPushButton("End Turn")
        end_turn_button.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; padding: 8px 15px;")
        end_turn_button.clicked.connect(self.end_turn)
        action_layout.addWidget(end_turn_button)
        
        # Shuffle button
        shuffle_button = QPushButton("Shuffle Letters")
        shuffle_button.setStyleSheet("background-color: #2196f3; color: white; font-weight: bold; padding: 8px 15px;")
        shuffle_button.clicked.connect(self.shuffle_letters)
        action_layout.addWidget(shuffle_button)
        
        self.main_layout.addWidget(action_widget)
        
    def _create_status_bar(self):
        """Create a status bar for game messages."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to play!")
        
    def select_letter(self, letter):
        """Handle selection of a letter from the letter bank."""
        # If another letter was already selected, deselect it first
        if self.selected_letter:
            for letter_label in self.letter_labels:
                if letter_label.letter == self.selected_letter:
                    letter_label.set_selected(False)
                    break
        
        # Update the selected letter
        if self.selected_letter == letter:  # If clicking the same letter, deselect it
            self.selected_letter = None
            self.status_bar.showMessage("Letter deselected")
        else:
            self.selected_letter = letter
            # Update the visual selection state
            for letter_label in self.letter_labels:
                if letter_label.letter == letter:
                    letter_label.set_selected(True)
                    self.status_bar.showMessage(f"Selected letter: {letter}")
                    break
    
    def update_board_display(self):
        """Update the board display based on the current game state."""
        for row in range(self.game.board.rows):
            for col in range(self.game.board.cols):
                cell = self.board_cells[row][col]
                letter = self.game.board.board[row][col]
                
                # For blank tiles, display nothing (not '0')
                if letter == '0':
                    cell.setText("")
                    cell.score_label.setText("")
                else:
                    cell.setText(letter)
                    # If the cell has a letter, show its score value in the corner
                    if letter:
                        score = self.game.letter_bank.get_letter_value(letter.lower()) if letter else ""
                        cell.score_label.setText(str(score))
                    else:
                        cell.score_label.setText("")
    
    def update_letter_bank_display(self):
        """Update the letter bank display with current available letters."""
        # Clear current letters
        while self.letter_bank_layout.count():
            item = self.letter_bank_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        
        # Get available letters from the game
        available_letters = self.game.letter_bank.get_available_letters()
        
        # Create new letter labels
        self.letter_labels = []
        for letter in available_letters:
            # Show blank tiles as empty but still selectable
            display_letter = letter if letter != '0' else " "
            letter_value = self.game.letter_bank.get_letter_value(letter)
            
            letter_label = DraggableLetterLabel(letter, letter_value)
            letter_label.setText(display_letter)
            letter_label.clicked.connect(self.select_letter)
            
            # If this letter is currently selected, mark it
            if self.selected_letter == letter:
                letter_label.set_selected(True)
            
            self.letter_bank_layout.addWidget(letter_label)
            self.letter_labels.append(letter_label)
    
    def update_score_display(self):
        """Update the score display."""
        self.score_label.setText(f"Score: {self.game.score}")
    
    def end_turn(self):
        """End the current turn and process the words formed."""
        if not self.current_turn_tiles:
            self.status_bar.showMessage("No letters placed this turn")
            return

        # Get all words formed
        words = self.game.board.get_all_words()
        valid_words = []
        invalid_words = []

        for word, positions in words:
            if len(word) > 1:  # Only consider words with at least 2 letters
                if self.game.word_validator.validate_word(word):
                    valid_words.append((word, positions))
                else:
                    invalid_words.append(word)

        if invalid_words:
            QMessageBox.warning(self, "Invalid Words", 
                f"The following words are not valid: {', '.join(invalid_words)}\n\nPlease try again.")
            return

        # Display words formed, their scores, and definitions
        turn_score = 0
        words_summary = "Words formed this turn:\n"
        for word, positions in valid_words:
            word_score = self.game.scoring.calculate_word_score(word, positions)
            turn_score += word_score
            definition = self.game.get_word_definition(word)
            words_summary += f"- {word}: {word_score} points\n  Definition: {definition}\n"

        words_summary += f"\nTotal score this turn: {turn_score}"
        self.status_bar.showMessage(words_summary)

        # Update game state
        self.game.score += turn_score
        self.update_score_display()

        # Add words to played words list
        for word, _ in valid_words:
            if word not in self.game.played_words:
                self.game.played_words.append(word)

        # Clear the current turn's tiles
        self.current_turn_tiles = []

        # Refill the player's hand
        self.game.letter_bank.refill_hand()
        self.update_letter_bank_display()

        # Update the GUI to show words and definitions
        self.update_words_display(valid_words)

    def update_words_display(self, valid_words):
        """Update the GUI to show words formed and their definitions."""
        if not hasattr(self, 'words_display_label'):
            self.words_display_label = QLabel()
            self.words_display_label.setFont(QFont("Arial", 12))
            self.words_display_label.setStyleSheet("background-color: #ffffff; padding: 10px; border: 1px solid #c0c0c0;")
            self.main_layout.addWidget(self.words_display_label)

        words_text = "<b>Words Formed:</b><br>"
        for word, _ in valid_words:
            definition = self.game.get_word_definition(word)
            words_text += f"<b>{word}</b>: {definition}<br>"

        self.words_display_label.setText(words_text)
    
    def shuffle_letters(self):
        """Shuffle the letters in the player's hand."""
        if self.game.letter_bank.player_hand.shuffle_letters():
            self.update_letter_bank_display()
            self.status_bar.showMessage("Letters shuffled!")
        else:
            self.status_bar.showMessage("No letters to shuffle!")
    
    def _check_for_words(self):
        """Check if any words have been formed with the placed letters."""
        words = self.game.board.get_all_words()
        for word, positions in words:
            if len(word) > 1:  # Only consider words with at least 2 letters
                # Validate the word
                if self.game.word_validator.validate_word(word):
                    word_score = self.game.scoring.calculate_word_score(word, positions)
                    self.status_bar.showMessage(f"Formed valid word: '{word}' for {word_score} points")
                else:
                    self.status_bar.showMessage(f"Warning: '{word}' is not a valid word")
    
    def new_game(self):
        """Start a new game."""
        self.game.new_game()
        self.update_board_display()
        self.update_letter_bank_display()
        self.update_score_display()
        self.status_bar.showMessage("New game started!")
        
    def show_high_scores(self):
        """Show high scores dialog."""
        QMessageBox.information(self, "High Scores", "High scores feature coming soon!")
        
    def change_dictionary(self, dictionary_type):
        """Change the dictionary type."""
        info = self.game.word_validator.switch_dictionary(dictionary_type)
        self.selected_dictionary = dictionary_type
        
        # Update the dictionary actions
        for action in self.dictionary_actions:
            action.setChecked(False)
            
        if dictionary_type == COLLEGIATE:
            self.dictionary_actions[0].setChecked(True)
        else:
            self.dictionary_actions[1].setChecked(True)
            
        self.dictionary_label.setText(f"Dictionary: {self.game.word_validator.dictionary_name}")
        self.status_bar.showMessage(f"Switched to {info.get('name', dictionary_type)} dictionary.")
        
    def show_rules(self):
        """Show game rules."""
        rules_text = """
        <h2>Word Mosaic Rules</h2>
        <ol>
            <li><b>Setup:</b> Start with 20 letters and an empty 15x15 grid</li>
            <li><b>First Word:</b> Your first word must cross the center tile</li>
            <li><b>Word Placement:</b> All words must read left-to-right or top-to-bottom</li>
            <li><b>Connections:</b> Every new word must connect to at least one existing word</li>
            <li><b>Valid Words:</b> All created words must be valid English words</li>
            <li><b>Letter Replenishment:</b> Gain new letters after successful placement</li>
            <li><b>Game End:</b> The game ends when no more valid placements are possible</li>
        </ol>
        <p>Special tiles can multiply letter or word scores!</p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Game Rules")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(rules_text)
        msg_box.exec_()
        
    def show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>Word Mosaic</h2>
        <p>Version 1.0</p>
        <p>A single-player word strategy game built with Python and PyQt5.</p>
        <p>© 2025 Samuel Rumbley</p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about_text)
        msg_box.exec_()
        
    def show_dictionary_status(self):
        """Show dictionary status."""
        info = self.game.word_validator.get_dictionary_info()
        
        status_text = f"""
        <h2>Dictionary Status</h2>
        <p><b>Current Dictionary:</b> {info.get('name', 'Unknown')}</p>
        <p><b>API Status:</b> {'Connected' if info.get('api_available', False) else 'Not Connected'}</p>
        <p><b>Local Dictionary:</b> {info.get('db_word_count', 0)} words available offline</p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Dictionary Status")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(status_text)
        msg_box.exec_()

# Main application entry point
if __name__ == "__main__":
    from main import Game, special_tiles
    
    app = QApplication(sys.argv)
    game = Game()
    window = WordMosaicApp(game)
    window.show()
    sys.exit(app.exec_())