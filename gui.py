import tkinter as tk
from tkinter import messagebox, simpledialog
import tkinter.ttk as ttk
from board import Board
from letter_bank import LetterBank
from scoring import Scoring
from merriam_webster_api import COLLEGIATE, LEARNERS

class GUI:
    """
    Graphical User Interface for Word Mosaic game
    """
    def __init__(self, game):
        """
        Initialize the GUI with the game logic.
        
        Args:
            game: Game object containing the game logic
        """
        self.game = game
        self.root = tk.Tk()
        self.root.title("Word Mosaic")
        self.root.configure(bg="#f5f5f5")
        
        # Dictionary setting
        self.selected_dictionary = tk.StringVar(value=game.word_validator.dictionary_type)
        
        # Main frame
        self.main_frame = tk.Frame(self.root, bg="#f5f5f5")
        self.main_frame.pack(padx=20, pady=20)
        
        # Create UI elements
        self._create_menu()
        self._create_top_frame()
        self._create_board_frame()
        self._create_letter_bank_frame()
        self._create_word_entry_frame()
        self._create_status_frame()
        
        # Initialize letters for a new game
        self.update_letter_bank_display()
        self.update_board_display()
        self.update_score_display()
        
        # Bind keyboard shortcuts
        self._bind_shortcuts()
        
    def _create_menu(self):
        """Create the menu bar with game options."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=self.new_game)
        game_menu.add_command(label="Show High Scores", command=self.show_high_scores)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.quit)
        
        # Options menu
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Options", menu=options_menu)
        
        # Dictionary submenu
        dictionary_menu = tk.Menu(options_menu, tearoff=0)
        options_menu.add_cascade(label="Dictionary", menu=dictionary_menu)
        dictionary_menu.add_radiobutton(label="Collegiate Dictionary", 
                                       variable=self.selected_dictionary, 
                                       value=COLLEGIATE,
                                       command=self.change_dictionary)
        dictionary_menu.add_radiobutton(label="Learner's Dictionary", 
                                       variable=self.selected_dictionary, 
                                       value=LEARNERS,
                                       command=self.change_dictionary)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Rules", command=self.show_rules)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Dictionary Status", command=self.show_dictionary_status)
    
    def _create_top_frame(self):
        """Create the top frame with game info."""
        top_frame = tk.Frame(self.main_frame, bg="#f5f5f5")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Score display
        self.score_label = tk.Label(top_frame, text="Score: 0", font=("Helvetica", 16), bg="#f5f5f5")
        self.score_label.pack(side=tk.LEFT)
        
        # Dictionary indicator
        self.dictionary_label = tk.Label(
            top_frame, 
            text=f"Dictionary: {self.game.word_validator.dictionary_name}", 
            font=("Helvetica", 12), 
            bg="#f5f5f5"
        )
        self.dictionary_label.pack(side=tk.RIGHT)
    
    def _create_board_frame(self):
        """Create the frame that displays the game board."""
        board_frame = tk.Frame(self.main_frame, bg="#e0e0e0", bd=2, relief=tk.RIDGE)
        board_frame.pack(pady=10)
        
        # Create grid of cells for the board
        self.board_cells = []
        for row in range(self.game.board.size):
            cell_row = []
            for col in range(self.game.board.size):
                cell = tk.Label(
                    board_frame,
                    width=3,
                    height=1,
                    font=("Helvetica", 16, "bold"),
                    bg="#ffffff",
                    bd=2,
                    relief=tk.GROOVE
                )
                cell.grid(row=row, column=col, padx=2, pady=2)
                cell_row.append(cell)
            self.board_cells.append(cell_row)
    
    def _create_letter_bank_frame(self):
        """Create the frame that displays available letters."""
        letter_bank_frame = tk.Frame(self.main_frame, bg="#f5f5f5")
        letter_bank_frame.pack(pady=10)
        
        tk.Label(letter_bank_frame, text="Available Letters:", font=("Helvetica", 12), bg="#f5f5f5").pack(anchor=tk.W)
        
        self.letter_bank_display = tk.Frame(letter_bank_frame, bg="#f0f0f0", bd=2, relief=tk.SUNKEN)
        self.letter_bank_display.pack(fill=tk.X, expand=True)
        
        # Letter tiles will be created in update_letter_bank_display
    
    def _create_word_entry_frame(self):
        """Create the frame for entering words."""
        word_entry_frame = tk.Frame(self.main_frame, bg="#f5f5f5")
        word_entry_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(word_entry_frame, text="Enter Word:", font=("Helvetica", 12), bg="#f5f5f5").pack(side=tk.LEFT)
        
        self.word_entry = tk.Entry(word_entry_frame, font=("Helvetica", 14))
        self.word_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.word_entry.focus_set()
        
        submit_button = tk.Button(
            word_entry_frame,
            text="Submit",
            command=self.submit_word,
            bg="#4caf50",
            fg="white",
            font=("Helvetica", 10, "bold")
        )
        submit_button.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to submit
        self.word_entry.bind("<Return>", lambda event: self.submit_word())
    
    def _create_status_frame(self):
        """Create the status bar at the bottom."""
        status_frame = tk.Frame(self.main_frame, bg="#f5f5f5")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        self.status_label = tk.Label(
            status_frame,
            text="Welcome to Word Mosaic!",
            font=("Helvetica", 10),
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X)
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.root.bind("<Control-n>", lambda event: self.new_game())
        self.root.bind("<F1>", lambda event: self.show_rules())
    
    def start(self):
        """Start the GUI main loop."""
        self.root.mainloop()
    
    def submit_word(self):
        """Handle submission of a word."""
        word = self.word_entry.get().strip().upper()
        
        if not word:
            return
        
        result = self.game.play_word(word)
        
        if result['valid']:
            self.show_status(f"Word '{word}' played for {result['score']} points!")
            self.update_board_display()
            self.update_letter_bank_display()
            self.update_score_display()
            self.word_entry.delete(0, tk.END)
            
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
                    cell.config(text=letter, bg="#ffeb3b")  # Yellow for placed letters
                else:
                    cell.config(text="", bg="#ffffff")  # White for empty cells
    
    def update_letter_bank_display(self):
        """Update the letter bank display to show available letters."""
        # Clear existing letters
        for widget in self.letter_bank_display.winfo_children():
            widget.destroy()
        
        # Create new letter tiles
        for letter, count in sorted(self.game.letter_bank.get_letter_counts().items()):
            if count > 0:
                for _ in range(count):
                    tile = tk.Label(
                        self.letter_bank_display,
                        text=letter,
                        font=("Helvetica", 14, "bold"),
                        width=2,
                        height=1,
                        bg="#2196f3",  # Blue for available letters
                        fg="white",
                        bd=1,
                        relief=tk.RAISED
                    )
                    tile.pack(side=tk.LEFT, padx=2, pady=2)
    
    def update_score_display(self):
        """Update the score display."""
        self.score_label.config(text=f"Score: {self.game.score}")
    
    def new_game(self):
        """Start a new game."""
        if messagebox.askyesno("New Game", "Start a new game?"):
            self.game.new_game()
            self.update_board_display()
            self.update_letter_bank_display()
            self.update_score_display()
            self.show_status("New game started!")
    
    def show_high_scores(self):
        """Show the high scores dialog."""
        # Placeholder - implement high scores later
        messagebox.showinfo("High Scores", "Feature coming soon!")
    
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
        messagebox.showinfo("Game Rules", rules)
    
    def show_about(self):
        """Show the about dialog."""
        about_text = """
        Word Mosaic
        
        A word game inspired by Scrabble, but with a twist.
        
        Created with ♥
        """
        messagebox.showinfo("About", about_text)
    
    def show_status(self, message):
        """Update the status bar with a message."""
        self.status_label.config(text=message)
    
    def show_definition(self, word, definition):
        """Show a popup with the word's definition."""
        messagebox.showinfo(f"Definition of {word}", definition)
    
    def show_dictionary_status(self):
        """Show information about the current dictionary."""
        info = self.game.word_validator.get_dictionary_info()
        status_text = f"""
        Current Dictionary: {info['name']}
        
        API Key Available: {'Yes' if info['has_api_key'] else 'No - Using Fallback Dictionary'}
        
        You can change dictionaries in Options > Dictionary menu.
        """
        messagebox.showinfo("Dictionary Status", status_text)
    
    def change_dictionary(self):
        """Change the dictionary being used."""
        new_dict_type = self.selected_dictionary.get()
        info = self.game.word_validator.switch_dictionary(new_dict_type)
        
        self.dictionary_label.config(text=f"Dictionary: {info['name']}")
        self.show_status(f"Switched to {info['name']}")