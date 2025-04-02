import random

class LetterBank:
    """
    Manages the distribution and tracking of letters for the Word Mosaic game.
    
    This class handles the letter pool, including drawing letters randomly
    based on English language frequency, tracking remaining letters,
    and managing letter values for scoring.
    """
    
    # Letter distribution based on English language frequency from the Scrabble game
    LETTER_FREQUENCIES = {
        'a': 9,  'b': 2,  'c': 2,  'd': 4,  'e': 12, 'f': 2,  'g': 3,
        'h': 6,  'i': 9,  'j': 1,  'k': 1,  'l': 4,  'm': 2,  'n': 6,
        'o': 8,  'p': 2,  'q': 1,  'r': 6,  's': 4,  't': 6,  'u': 4,
        'v': 2,  'w': 2,  'x': 1,  'y': 2,  'z': 1,  '0': 2,  # blank tiles
    }
    
    # Point values for each letter based on Scrabble scoring
    LETTER_VALUES = {
        'a': 1,  'b': 3,  'c': 3,  'd': 2,  'e': 1,  'f': 4,  'g': 2,
        'h': 4,  'i': 1,  'j': 8,  'k': 5,  'l': 1,  'm': 3,  'n': 1,
        'o': 1,  'p': 3,  'q': 10, 'r': 1,  's': 1,  't': 1,  'u': 1,
        'v': 4,  'w': 4,  'x': 8,  'y': 4,  'z': 10, '0': 0,  # blank values
    }
    
    def __init__(self):
        """
        Initialize the letter bank with the standard distribution.
        
        Creates a new letter bank with the default Scrabble-based letter
        distribution and counts the total number of tiles available.
        """
        self.letter_bank = self.LETTER_FREQUENCIES.copy() 
        self.letter_bank_total = sum(self.letter_bank.values()) # total number of tiles in the bank

    def draw_tiles(self, num_tiles):
        """
        Draw a specified number of tiles from the letter bank.
        
        Args:
            num_tiles (int): The number of tiles to draw
            
        Returns:
            dict: A dictionary mapping letters to counts of drawn tiles
            
        Note:
            If there are not enough tiles remaining, draws as many as possible.
        """
        drawn_tiles = {}
        for _ in range(num_tiles):
            if self.letter_bank_total == 0:
                break
            letter = self._get_random_letter()
            if letter in drawn_tiles:
                drawn_tiles[letter] += 1
            else:
                drawn_tiles[letter] = 1
            self.letter_bank[letter] -= 1
            self.letter_bank_total -= 1
        return drawn_tiles
    
    def refill_hand(self, player_hand, num_tiles):
        """
        Refill the player's hand with tiles from the letter bank.
        
        Args:
            player_hand (PlayerHand): The player's hand to refill
            num_tiles (int): The number of tiles to add to the hand
            
        Returns:
            bool: True if tiles were successfully added, False if bank is empty
            
        Note:
            Adds the drawn tiles directly to the player's hand and updates their total.
        """
        if self.letter_bank_total == 0:
            return False
        drawn_tiles = self.draw_tiles(num_tiles)
        for letter, count in drawn_tiles.items():
            if letter in player_hand.hand:
                player_hand.hand[letter] += count
            else:
                player_hand.hand[letter] = count
        player_hand.hand_total += sum(drawn_tiles.values())
        return True
    
    def return_tiles(self, letter, num_tiles):
        """
        Return tiles back to the letter bank.
        
        Args:
            letter (str): The letter to return
            num_tiles (int): The number of tiles to return
            
        Raises:
            ValueError: If an invalid letter is returned to the bank
            
        Note:
            Updates the bank's inventory and total count.
        """
        if letter in self.letter_bank:
            self.letter_bank[letter] += num_tiles
            self.letter_bank_total += num_tiles
        else:
            raise ValueError("Invalid letter returned to the bank.")
        
    def is_available(self, letter):
        """
        Check if a letter is available in the letter bank.
        
        Args:
            letter (str): The letter to check
            
        Returns:
            bool: True if the letter is available, False otherwise
        """
        return self.letter_bank.get(letter, 0) > 0
    
    def bank_empty(self):
        """
        Check if the letter bank is empty.
        
        Returns:
            bool: True if the bank is empty, False otherwise
        """
        return self.letter_bank_total == 0
    
    def init_letter_bank(self):
        """
        Initialize the letter bank to its original state.
        
        Resets all letter counts to their original frequencies.
        """
        self.letter_bank = self.LETTER_FREQUENCIES.copy()
        self.letter_bank_total = sum(self.letter_bank.values())

    def get_letter_bank(self):
        """
        Get the current state of the letter bank.
        
        Returns:
            dict: A copy of the letter bank's current state
        """
        return self.letter_bank.copy()
    
    def get_letter_bank_total(self):
        """
        Get the total number of tiles in the letter bank.
        
        Returns:
            int: The total number of tiles remaining in the bank
        """
        return self.letter_bank_total
    
    def get_letter_value(self, letter):
        """
        Get the point value of a letter.
        
        Args:
            letter (str): The letter to get the value for
            
        Returns:
            int: The point value of the letter, or 0 if not found
        """
        return self.LETTER_VALUES.get(letter, 0)
    
    def get_letter_count(self, letter):
        """
        Get the count of a letter in the letter bank.
        
        Args:
            letter (str): The letter to check
            
        Returns:
            int: The number of tiles of that letter remaining in the bank
        """
        return self.letter_bank.get(letter, 0)
    
    def get_letter_frequencies(self):
        """
        Get the frequencies of letters in the letter bank.
        
        Returns:
            dict: A copy of the initial letter distribution
        """
        return self.LETTER_FREQUENCIES.copy()
    
    def _get_random_letter(self):
        """
        Get a random letter from the letter bank.
        
        Returns:
            str or None: A randomly chosen letter that's available in the bank,
                        or None if the bank is empty
                        
        Note:
            This is an internal helper method used by draw_tiles.
        """
        letters = [letter for letter, count in self.letter_bank.items() if count > 0]
        return random.choice(letters) if letters else None
    
class PlayerHand:
    def __init__(self):
        self.hand = {}
        self.hand_total = sum(self.hand.values()) # total number of tiles in the hand

    
        