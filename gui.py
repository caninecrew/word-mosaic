import sys
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
        
        # Create letter bank frame
        self.letter_bank_frame = QWidget()
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
        """
        Submit the current word and calculate the score.
        Validates the word, updates the score, and replenishes the player's hand.
        """
        try:
            print("[DEBUG] Starting word submission")
            
            # Get the word from the text field
            word = self.word_entry.text().strip().lower()
            if not word:
                self.statusBar.showMessage("Please enter a word")
                return
            
            # Clear all definitions immediately when submit button is clicked
            print("[DEBUG] Clearing definitions display")
            self.clear_definitions()
            print("[DEBUG] Definitions display cleared")
            
            # Try to play the word using the game logic
            result = self.game.play_word(word)
            
            if not result['valid']:
                self.statusBar.showMessage(f"Invalid word: {result['reason']}")
                return
            
            # Word was valid and played successfully
            # Update the score display
            self.update_score_display()
            
            # Clear the word entry field
            self.word_entry.clear()
            
            # Update the board and letter bank displays
            self.update_board_display()
            self.update_letter_bank_display()
            
            # Show success message
            self.statusBar.showMessage(f"Word '{word.upper()}' played for {result['score']} points!")
            
            # Check if game is over
            if self.check_game_over():
                self.show_game_over_dialog()
            
        except Exception as e:
            print(f"[ERROR] Error submitting word: {str(e)}")
            import traceback
            traceback.print_exc()
            self.statusBar.showMessage(f"Error submitting word: {str(e)}")

    def shuffle_letters(self):
        """
        Shuffle the player's letter bank.
        Updates the letter bank display and shows a status message.
        """
        # Create a player hand and shuffle it
        player_hand = self.game.letter_bank.create_player_hand(20)
        player_hand.fill_initial_hand()
        player_hand.shuffle_letters()
        
        # Update display
        self.update_letter_bank_display()
        self.statusBar.showMessage("Letters shuffled")

    def check_game_over(self):
        """
        Check if the game is over.
        
        Game is over when:
        1. The letter bank is empty (no more letters to draw)
        2. AND there are no valid placements for any letters in the player's hand
        
        Returns:
            bool: True if the game is over, False otherwise
        """
        # For this simple implementation, just check if the letter bank is empty
        # In a more advanced implementation, we would check for valid moves as well
        return self.game.letter_bank.bank_empty()

    def show_game_over_dialog(self):
        """
        Show a game over dialog with the final score and statistics.
        """
        from PyQt5.QtWidgets import QMessageBox
        
        # Create message box
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Game Over")
        
        # Set the game over message with statistics
        game_over_html = f"""
        <h2>Game Over!</h2>
        <p>No more moves available.</p>
        <h3>Final Score: {self.game.score}</h3>
        <p><b>Statistics:</b></p>
        <ul>
            <li>Words Played: {len(self.game.played_words)}</li>
        </ul>
        <p>Thanks for playing Word Mosaic!</p>
        """
        
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(game_over_html)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
        
        # Update status bar
        self.statusBar.showMessage(f"Game Over! Final Score: {self.game.score}")
        
        # Disable buttons
        for button in self.findChildren(QPushButton):
            if button.text() in ["Submit Word", "Shuffle Letters"]:
                button.setEnabled(False)

    def update_board_display(self):
        """Update the board display to reflect the current state of the game board."""
        for row in range(self.game.board.rows):
            for col in range(self.game.board.cols):
                cell = self.board_cells[row][col]
                letter = self.game.board.get_letter(row, col)
                
                if letter:
                    cell.setText(letter)
                    # Highlight special tiles
                    if (row, col) in self.game.board.special_tiles:
                        tile_type = self.game.board.special_tiles[(row, col)]
                        if tile_type == 'TW':
                            cell.setStyleSheet("background-color: #ff6666; border: 2px solid #c0c0c0;")
                        elif tile_type == 'DW':
                            cell.setStyleSheet("background-color: #ff9999; border: 2px solid #c0c0c0;")
                        elif tile_type == 'TL':
                            cell.setStyleSheet("background-color: #66b3ff; border: 2px solid #c0c0c0;")
                        elif tile_type == 'DL':
                            cell.setStyleSheet("background-color: #99ccff; border: 2px solid #c0c0c0;")
                    else:
                        cell.setStyleSheet("background-color: #ffffff; border: 2px solid #c0c0c0;")
                else:
                    cell.setText("")
                    # Show special tiles
                    if (row, col) in self.game.board.special_tiles:
                        tile_type = self.game.board.special_tiles[(row, col)]
                        if tile_type == 'TW':
                            cell.setStyleSheet("background-color: #ff6666; border: 2px solid #c0c0c0;")
                        elif tile_type == 'DW':
                            cell.setStyleSheet("background-color: #ff9999; border: 2px solid #c0c0c0;")
                        elif tile_type == 'TL':
                            cell.setStyleSheet("background-color: #66b3ff; border: 2px solid #c0c0c0;")
                        elif tile_type == 'DL':
                            cell.setStyleSheet("background-color: #99ccff; border: 2px solid #c0c0c0;")
                    else:
                        cell.setStyleSheet("background-color: #ffffff; border: 2px solid #c0c0c0;")

    def update_letter_bank_display(self):
        """Update the letter bank display with the current available letters."""
        # Clear existing letter bank layout
        while self.letter_bank_layout.count():
            item = self.letter_bank_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Get the player's letter bank
        player_hand = self.game.letter_bank.create_player_hand(20)
        player_hand.fill_initial_hand()
        
        # Add letters to the display
        for letter in player_hand.letter_order:
            letter_label = QLabel(letter.upper())
            letter_label.setFixedSize(30, 30)
            letter_label.setAlignment(Qt.AlignCenter)
            letter_label.setFont(QFont("Arial", 14, QFont.Bold))
            letter_label.setStyleSheet("background-color: #ffd700; border: 1px solid #c0c0c0; border-radius: 4px;")
            self.letter_bank_layout.addWidget(letter_label)

    def update_score_display(self):
        """Update the score display with the current score."""
        self.score_label.setText(f"Score: {self.game.score}")

    def clear_definitions(self):
        """Clear the definitions display."""
        # In a real implementation, this would clear a text display area for definitions
        pass
    
    def refresh_board(self):
        """Refresh the board display."""
        self.update_board_display()
    
    def refresh_letter_bank(self):
        """Refresh the letter bank display."""
        self.update_letter_bank_display()
    
    def new_game(self):
        """Start a new game."""
        self.game.new_game()
        self.update_board_display()
        self.update_letter_bank_display()
        self.update_score_display()
        self.statusBar.showMessage("New game started!")
        
    def show_high_scores(self):
        """Show high scores dialog."""
        # Placeholder implementation
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
        self.statusBar.showMessage(f"Switched to {info.get('name', dictionary_type)} dictionary.")
        
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