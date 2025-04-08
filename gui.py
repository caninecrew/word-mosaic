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
        
        # Letter bank display frame
        self.letter_bank_frame = QFrame()
        self.letter_bank_frame.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.letter_bank_frame.setStyleSheet("background-color: #f0f0f0;")
        
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
        
        Created with ♥
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
        QMessageBox.information(self, "Dictionary Status", status_text)
    
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

# Keep the legacy class name as an alias for backward compatibility
GUI = WordMosaicApp