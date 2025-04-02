"""
## 🎮 User Interface - PyQt5
- [ ] Design main game board layout
- [ ] Create letter bank display
- [ ] Implement drag-and-drop letter placement
- [ ] Design score tracking display
- [ ] Add visual feedback for valid/invalid placements
- [ ] Create game menu and controls"
"""

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QGridLayout, QLabel, QFrame, QHBoxLayout, QStatusBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class WordMosaicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Word Mosaic")
        self.setGeometry(100, 100, 800, 600)
        
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
                    
                # Store cell reference and add to layout
                self.cells[(row, col)] = cell
                board_layout.addWidget(cell, row, col)
        
        # Add board to main layout
        self.layout.addWidget(board_widget)
        
    def create_letter_bank(self):
        """Create a simple display for available letters"""
        letter_bank_widget = QWidget()
        letter_bank_layout = QHBoxLayout(letter_bank_widget)
        
        # Add a label for the letter bank
        bank_label = QLabel("Your Letters:")
        bank_label.setFont(QFont('Arial', 12))
        letter_bank_layout.addWidget(bank_label)
        
        # Create some sample letters for now
        sample_letters = "ABCDEFGHIJKLMNOPQRST"
        self.letter_tiles = []
        
        for letter in sample_letters:
            tile = QLabel(letter)
            tile.setFixedSize(35, 35)
            tile.setAlignment(Qt.AlignCenter)
            tile.setFrameShape(QFrame.Box)
            tile.setFont(QFont('Arial', 12, QFont.Bold))
            tile.setStyleSheet("background-color: #ffffcc;")
            
            letter_bank_layout.addWidget(tile)
            self.letter_tiles.append(tile)
        
        # Add letter bank to main layout
        self.layout.addWidget(letter_bank_widget)
        
    def update_score(self, new_score):
        """Update the displayed score"""
        self.score_value.setText(str(new_score))

# Main application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordMosaicApp()
    window.show()
    sys.exit(app.exec_())