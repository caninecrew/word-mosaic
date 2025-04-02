"""
## 🎮 User Interface - PyQt5
- [X] Design main game board layout
- [X] Create letter bank display
- [ ] Implement drag-and-drop letter placement
- [ ] Design score tracking display
- [ ] Add visual feedback for valid/invalid placements
- [ ] Create game menu and controls"
"""
from board import Board
from letter_bank import LetterBank, PlayerHand

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QGridLayout, QLabel, QFrame, QHBoxLayout, QStatusBar, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class WordMosaicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Word Mosaic")
        self.setGeometry(100, 100, 800, 600)

        # Initialize game components
        self.game_board = Board(15, 15)
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
        """Initialize the user interface components"""
        # Create score display
        self.create_score_display()
        
        # Create game board
        self.create_game_board()
        
        # Create letter bank
        self.create_letter_bank()
        
        # Create control buttons
        self.create_control_buttons()
    
    def create_score_display(self):
        """Create a simple score display"""
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
        """Create a simple 15x15 grid for the game board"""
        board_widget = QWidget()
        board_layout = QGridLayout(board_widget)
        board_layout.setSpacing(2)  # Space between cells
        
        # Create 15x15 grid of cells
        self.cells = {}
        for row in range(15):
            for col in range(15):
                cell = QLabel()
                cell.setFixedSize(40, 40)  # Fixed cell size
                cell.setAlignment(Qt.AlignCenter)
                cell.setFrameShape(QFrame.Box)  # Add border
                cell.setFont(QFont('Arial', 14, QFont.Bold))
                
                # Highlight center cell
                if row == 7 and col == 7:
                    cell.setStyleSheet("background-color: #ffcccc;")
                    
                # Add click event
                cell.mousePressEvent = lambda event, r=row, c=col: self.place_letter(r, c)
                
                # Store cell reference and add to layout
                self.cells[(row, col)] = cell
                board_layout.addWidget(cell, row, col)
        
        # Add board to main layout
        self.layout.addWidget(board_widget)
        
    def create_letter_bank(self):
        """Create display for player's letters"""
        letter_bank_widget = QWidget()
        self.letter_bank_layout = QHBoxLayout(letter_bank_widget)
        
        # Add a label for the letter bank
        bank_label = QLabel("Your Letters:")
        bank_label.setFont(QFont('Arial', 12))
        self.letter_bank_layout.addWidget(bank_label)
        
        # Get actual letters from player hand
        self.letter_tiles = []
        player_letters = self.player_hand.letter_order
        
        for letter in player_letters:
            tile = QLabel(letter.upper())
            tile.setFixedSize(35, 35)
            tile.setAlignment(Qt.AlignCenter)
            tile.setFrameShape(QFrame.Box)
            tile.setFont(QFont('Arial', 12, QFont.Bold))
            tile.setStyleSheet("background-color: #ffffcc;")
            
            # Fix the click event with proper lambda capture
            tile.mousePressEvent = lambda event, letter=letter: self.select_letter(letter)
            
            self.letter_bank_layout.addWidget(tile)
            self.letter_tiles.append(tile)
        
        # Add letter bank to main layout
        self.layout.addWidget(letter_bank_widget)
    
    def create_control_buttons(self):
        """Create game control buttons"""
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
        
        # Reset turn button
        reset_button = QPushButton("Reset Turn")
        reset_button.clicked.connect(self.reset_turn)
        buttons_layout.addWidget(reset_button)
        
        # Add buttons widget to main layout
        self.layout.addWidget(buttons_widget)
    
    def refresh_letter_bank(self):
        """Refresh the letter bank display"""
        # Clear existing letter bank
        for i in reversed(range(self.letter_bank_layout.count())): 
            self.letter_bank_layout.itemAt(i).widget().deleteLater()
        
        # Re-create letter bank
        self.create_letter_bank()
    
    def refresh_board(self):
        """Refresh the board display based on game state"""
        for row in range(15):
            for col in range(15):
                letter = self.game_board.get_letter(row, col)
                if letter:
                    self.cells[(row, col)].setText(letter.upper())
                else:
                    self.cells[(row, col)].setText("")
    
    def select_letter(self, letter):
        """Handle letter selection from bank"""
        self.selected_letter = letter
        self.status_bar.showMessage(f"Selected letter: {letter.upper()}")
        
        # Highlight the selected letter tile
        for tile in self.letter_tiles:
            if tile.text() == letter.upper():
                tile.setStyleSheet("background-color: #ffcc66; border: 2px solid black;")
            else:
                tile.setStyleSheet("background-color: #ffffcc;")
    
    def place_letter(self, row, col):
        """Handle letter placement on the board"""
        if not hasattr(self, 'selected_letter') or not self.selected_letter:
            self.status_bar.showMessage("Please select a letter first")
            return
            
        try:
            # Try to place the letter using your game logic
            self.game_board.place_letter(self.selected_letter, row, col)
            
            # Update the visual board
            self.cells[(row, col)].setText(self.selected_letter.upper())
            
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

# Main application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordMosaicApp()
    window.show()
    sys.exit(app.exec_())