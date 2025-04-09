from board import Board
from letter_bank import LetterBank
from scoring import Scoring
from word_validator import WordValidator

class Game:
    """
    Main game logic for Word Mosaic
    """
    def __init__(self):
        """Initialize the game components"""
        self.board = Board()
        self.letter_bank = LetterBank()
        self.word_validator = WordValidator()
        self.scoring = Scoring()
        self.current_score = 0
        self.played_words = []
        self.current_turn_letters = []  # Track letters placed in the current turn
        self.current_turn_positions = []  # Track positions of letters placed in current turn
        self.turn_number = 1
        self.first_play = True

    def reset(self):
        """Reset the game to starting state"""
        self.board.reset()
        self.letter_bank = LetterBank()
        self.current_score = 0
        self.played_words = []
        self.current_turn_letters = []
        self.current_turn_positions = []
        self.turn_number = 1
        self.first_play = True

    def place_letter(self, letter, row, col):
        """
        Place a letter on the board
        
        Args:
            letter (str): Letter to place
            row (int): Row position
            col (int): Column position
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if the position is valid and available
            if not self.board.is_position_empty(row, col):
                return False
                
            # Place the letter
            self.board.place_letter(letter, row, col)
            
            # Track the letter placement for this turn
            self.current_turn_letters.append(letter)
            self.current_turn_positions.append((row, col))
            
            return True
        except ValueError:
            return False
            
    def remove_letter(self, row, col):
        """
        Remove a letter from the board and return it to player's hand
        
        Args:
            row (int): Row position
            col (int): Column position
            
        Returns:
            str: The letter removed, or None if no letter at position
        """
        letter = self.board.get_letter(row, col)
        
        if letter == '0':  # No letter at this position
            return None
            
        # Check if this letter was placed in the current turn
        position = (row, col)
        if position in self.current_turn_positions:
            index = self.current_turn_positions.index(position)
            self.current_turn_letters.pop(index)
            self.current_turn_positions.pop(index)
            
            # Clear the position on the board
            self.board.clear_position(row, col)
            
            # Return the letter to the player's hand
            self.letter_bank.add_letter(letter)
            
            return letter
            
        return None  # Can't remove letters from previous turns
        
    def end_turn(self):
        """
        End the current turn, validate words, update score
        
        Returns:
            dict: Result of the turn with information about validity, score, and words formed
        """
        # Ensure at least one letter was placed
        if not self.current_turn_letters:
            return {
                'valid': False,
                'reason': 'No letters placed'
            }
            
        # Check if first play includes center position
        if self.first_play:
            center_played = False
            center_row = self.board.rows // 2
            center_col = self.board.cols // 2
            
            for row, col in self.current_turn_positions:
                if row == center_row and col == center_col:
                    center_played = True
                    break
                    
            if not center_played:
                return {
                    'valid': False,
                    'reason': 'First play must include the center position'
                }
                
        # Check if all letters in current turn are in same row or column
        same_row = all(pos[0] == self.current_turn_positions[0][0] for pos in self.current_turn_positions)
        same_col = all(pos[1] == self.current_turn_positions[0][1] for pos in self.current_turn_positions)
        
        if not (same_row or same_col):
            return {
                'valid': False,
                'reason': 'All letters must be placed in the same row or column'
            }
            
        # After first turn, ensure new letters connect to existing ones
        if not self.first_play:
            connected = False
            for row, col in self.current_turn_positions:
                if self.board.is_connected(row, col):
                    connected = True
                    break
                    
            if not connected:
                return {
                    'valid': False,
                    'reason': 'New letters must connect to existing letters'
                }
                
        # Get all words formed by the current play
        words = self.board.get_all_words()
        valid_words = []
        invalid_words = []
        
        for word, positions in words:
            # Check if this word includes any newly placed letter
            includes_new_letter = any((row, col) in self.current_turn_positions for row, col in positions)
            
            if includes_new_letter:
                if self.word_validator.validate_word(word):
                    valid_words.append((word, positions))
                else:
                    invalid_words.append((word, positions))
                    
        # If any invalid words were formed, undo the turn
        if invalid_words:
            return {
                'valid': False,
                'reason': f"Invalid word(s): {', '.join(w[0] for w in invalid_words)}",
                'invalid_words': invalid_words
            }
            
        # If no valid words were formed, undo the turn
        if not valid_words:
            return {
                'valid': False,
                'reason': 'No valid words formed'
            }
            
        # Calculate score for the turn
        turn_score = 0
        for word, positions in valid_words:
            word_score = self.scoring.calculate_word_score(word, positions, self.board)
            turn_score += word_score
            
        # First play gets double score as bonus
        if self.first_play:
            turn_score *= 2
            self.first_play = False
            
        # Update overall score
        self.current_score += turn_score
        
        # Add words to played words list
        self.played_words.extend([word[0] for word in valid_words])
        
        # Remove letters from player's hand that were used in this turn
        for letter in self.current_turn_letters:
            self.letter_bank.player_hand.use_letter(letter)
            
        # Refill the player's hand
        self.letter_bank.player_hand.refill()
        
        # Reset current turn tracking
        self.current_turn_letters = []
        self.current_turn_positions = []
        
        # Increment turn counter
        self.turn_number += 1
        
        return {
            'valid': True,
            'score': turn_score,
            'total_score': self.current_score,
            'words': valid_words
        }
    
    def cancel_turn(self):
        """
        Cancel the current turn and return all letters to hand
        
        Returns:
            bool: True if successful
        """
        # Clear all letters placed in this turn from the board
        for row, col in self.current_turn_positions:
            letter = self.board.get_letter(row, col)
            self.board.clear_position(row, col)
            
            # Return letter to player's hand
            self.letter_bank.add_letter(letter)
            
        # Reset current turn tracking
        self.current_turn_letters = []
        self.current_turn_positions = []
        
        return True
        
    def shuffle_hand(self):
        """
        Shuffle the player's hand
        
        Returns:
            bool: True if successful, False if no letters in hand
        """
        return self.letter_bank.player_hand.shuffle_letters()
        
    def get_letters_in_hand(self):
        """
        Get the letters in the player's hand
        
        Returns:
            list: Letters in hand
        """
        return self.letter_bank.player_hand.get_letters()
        
    def exchange_letters(self, letters_to_exchange):
        """
        Exchange selected letters for new ones
        
        Args:
            letters_to_exchange (list): Letters to exchange
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if we have enough letters in the bag
        if len(letters_to_exchange) > self.letter_bank.remaining_letters():
            return False
            
        # Check if all letters are in the player's hand
        hand = self.letter_bank.player_hand.get_letters()
        hand_copy = hand.copy()  # Work with a copy to handle duplicate letters correctly
        
        for letter in letters_to_exchange:
            if letter in hand_copy:
                hand_copy.remove(letter)
            else:
                return False
                
        # Remove letters from hand
        for letter in letters_to_exchange:
            self.letter_bank.player_hand.use_letter(letter)
            self.letter_bank.return_letter(letter)
            
        # Draw new letters
        self.letter_bank.player_hand.refill()
        
        return True