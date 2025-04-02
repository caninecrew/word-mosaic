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
                            QGridLayout, QLabel, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class WordMosaicApp(QMainWindow): # Main application class
    def __init__(self): # Constructor method
        super().__init__() # Call the parent constructor
        
        # Set window properties
        self.setWindowTitle("Word Mosaic")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height
        
        # Create central widget and layout
        self.central_widget = QWidget() # Central widget for the main window
        self.setCentralWidget(self.central_widget) # Set the central widget
        self.layout = QVBoxLayout(self.central_widget) # Vertical layout for the central widget
        
        # Initialize UI components
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface components"""
        self.create_game_board()

    def create_game_board(self):
        """Create a simple 15x15 game board"""
        board_widget = QWidget() # Create a widget for the game board
        board_layout = QGridLayout(board_widget) # Use GridLayout for a grid
        board_layout.setSpacing(2) # Set spacing between cells - fix: call on layout not widget

        # Create a 15x15 grid of buttons (or labels) for the game board
        self.cells = {} # Dictionary to hold the cell widgets
        for row in range(15):
            for col in range(15):
                cell = QLabel()
                cell.setFixedSize(40, 40) # Set fixed size for each cell
                cell.setAlignment(Qt.AlignCenter) # Center align the text in the cell
                cell.setFrameShape(QFrame.Box) # Fix: setFrameShape instead of setFrameStyle
                cell.setFont(QFont("Arial", 12)) # Fix: Add font size parameter

                # Highlight center cell
                if (row == 7 and col == 7):
                    cell.setStyleSheet("background-color: lightblue;")
                else:
                    cell.setStyleSheet("background-color: white;")

                # Store cell reference and add to layout
                self.cells[(row, col)] = cell
                board_layout.addWidget(cell, row, col) # Fix: Use grid layout properly

        # Add the game board widget to the main layout
        self.layout.addWidget(board_widget)

# Main application entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordMosaicApp()
    window.show()
    sys.exit(app.exec_())