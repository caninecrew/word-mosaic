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
        
        # Create letter bank widget and layout once
        self.letter_bank_widget = QWidget()
        self.letter_bank_layout = QHBoxLayout(self.letter_bank_widget)
        self.layout.addWidget(self.letter_bank_widget)
        
        # Populate letter bank
        self.populate_letter_bank()
        
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

                # Add click event
                cell.mousePressEvent = lambda event, r=row, c=col: self.place_letter(r, c)

                # Store cell reference and add to layout
                self.cells[(row, col)] = cell
                board_layout.addWidget(cell, row, col)

        # Add board to main layout
        self.layout.addWidget(board_widget)
            
        def populate_letter_bank(self):
            """Populate the letter bank with player's current letters"""
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
                
                tile = QLabel(display_letter)
                tile.setFixedSize(35, 35)
                tile.setAlignment(Qt.AlignCenter)
                tile.setFrameShape(QFrame.Box)
                tile.setFont(QFont('Arial', 12, QFont.Bold))
                tile.setStyleSheet("background-color: #ffffcc;")
                
                # Pass both the letter and its index to the select_letter method
                tile.mousePressEvent = lambda event, l=letter, idx=i: self.select_letter(l, idx)
                
                self.letter_bank_layout.addWidget(tile)
                self.letter_tiles.append(tile)
    
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
        # Instead of creating a new widget, just repopulate the existing one
        self.populate_letter_bank()
    
    def refresh_board(self):
        """Refresh the board display based on game state"""
        for row in range(15):
            for col in range(15):
                letter = self.game_board.get_letter(row, col)
                if letter:
                    self.cells[(row, col)].setText(letter.upper())
                else:
                    self.cells[(row, col)].setText("")
    
    def select_letter(self, letter, index):
        """Handle letter selection from bank"""
        self.selected_letter = letter
        self.selected_index = index
        self.status_bar.showMessage(f"Selected letter: {letter.upper()}")
        
        # Highlight only the specific clicked tile
        for i, tile in enumerate(self.letter_tiles):
            if i == index:
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
    
    def submit_word(self):
        """Submit the current word and calculate score"""
        # Get all newly placed letters in this turn
        # Validate all words formed
        # Calculate score
        # Replenish player's hand
        # Update score display
        self.status_bar.showMessage("Word submitted successfully!")

    def shuffle_letters(self):
        """Shuffle the player's letter bank"""
        self.player_hand.shuffle_letters()
        self.refresh_letter_bank()
        self.status_bar.showMessage("Letters shuffled")

    def reset_turn(self):
        """Reset the current turn, returning placed letters to hand"""
        # Return all letters placed this turn to the player's hand
        # Clear those letters from the board
        # Reset any tracking of the current turn
        self.refresh_board()
        self.refresh_letter_bank()
        self.status_bar.showMessage("Turn reset")

# Main application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordMosaicApp()
    window.show()
    sys.exit(app.exec_())