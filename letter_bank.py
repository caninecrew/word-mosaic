import random
import json

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
        self.letter_bank_total = sum(self.letter_bank.values())
    
    def create_player_hand(self, max_size=20):
        """
        Create a new player hand connected to this letter bank.
        
        Args:
            max_size (int): Maximum number of letters the hand can hold
            
        Returns:
            PlayerHand: A new empty player hand associated with this bank
        """
        return PlayerHand(self, max_size)
    
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
            # Add letter to letter_order for each count
            for _ in range(count):
                player_hand.letter_order.append(letter)
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
    
    # Other LetterBank methods remain the same...
    
    def is_available(self, letter):
        """Check if a letter is available in the letter bank."""
        return self.letter_bank.get(letter, 0) > 0
    
    def bank_empty(self):
        """Check if the letter bank is empty."""
        return self.letter_bank_total == 0
    
    def init_letter_bank(self):
        """Initialize the letter bank to its original state."""
        self.letter_bank = self.LETTER_FREQUENCIES.copy()
        self.letter_bank_total = sum(self.letter_bank.values())

    def get_letter_bank(self):
        """Get the current state of the letter bank."""
        return self.letter_bank.copy()
    
    def get_letter_bank_total(self):
        """Get the total number of tiles in the letter bank."""
        return self.letter_bank_total
    
    def get_letter_value(self, letter):
        """Get the point value of a letter."""
        return self.LETTER_VALUES.get(letter, 0)
    
    def get_letter_count(self, letter):
        """Get the count of a letter in the letter bank."""
        return self.letter_bank.get(letter, 0)
    
    def get_letter_counts(self):
        """Get all letter counts in the letter bank.
        
        Returns:
            dict: A dictionary mapping letters to their counts in the bank
        """
        return self.letter_bank.copy()
    
    def get_letter_frequencies(self):
        """Get the frequencies of letters in the letter bank."""
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
    
    def to_json(self):
        """
        Convert letter bank state to a JSON-serializable dictionary.
        
        Returns:
            dict: Letter bank state for serialization
        """
        return {
            "letter_bank": self.letter_bank,
            "letter_bank_total": self.letter_bank_total
        }
    
    @classmethod
    def from_json(cls, data):
        """
        Create a letter bank from serialized data.
        
        Args:
            data (dict): Serialized letter bank data
            
        Returns:
            LetterBank: Reconstructed letter bank
        """
        bank = cls()
        bank.letter_bank = data.get("letter_bank", {})
        bank.letter_bank_total = data.get("letter_bank_total", 0)
        return bank

    def has_letters(self, word):
        """
        Check if the letter bank has the necessary letters to form a word.
        
        Args:
            word (str): The word to check
            
        Returns:
            bool: True if the letter bank has all necessary letters, False otherwise
        """
        word = word.lower()
        temp_bank = self.letter_bank.copy()
        for letter in word:
            if letter not in temp_bank or temp_bank[letter] <= 0:
                return False
            temp_bank[letter] -= 1
        return True
        
    def use_letters(self, word):
        """
        Remove letters from the bank to form the specified word.
        
        Args:
            word (str): The word to form
            
        Returns:
            bool: True if successful, False if not enough letters
            
        Raises:
            ValueError: If the word contains letters not in the bank
        """
        word = word.lower()
        if not self.has_letters(word):
            return False
            
        for letter in word:
            self.letter_bank[letter] -= 1
            self.letter_bank_total -= 1
            # If count is 0, remove the letter from the bank
            if self.letter_bank[letter] == 0:
                del self.letter_bank[letter]
        return True


class PlayerHand:
    """
    Represents a player's current set of letters in the Word Mosaic game.
    
    This class manages the collection of letters a player has available for
    play, including adding, removing, and checking letters in the hand.
    """

    def __init__(self, letter_bank, max_size=20):
        """
        Initialize a player hand with a reference to the letter bank.
        
        Args:
            letter_bank (LetterBank): The letter bank to draw from and return to
            max_size (int): Maximum number of letters the hand can hold
        """
        self.letter_bank = letter_bank
        self.max_size = max_size
        self.hand = {}
        self.hand_total = 0  # Start with 0 since hand is empty
        self.letter_order = []  # Order of letters for display
    
    def fill_initial_hand(self):
        """
        Fill the player's hand with initial letters from the bank.
        
        Returns:
            int: Number of letters added to the hand
        """
        needed = self.max_size - self.hand_total
        return self.refill(needed)
    
    def add_letter(self, letter):
        """
        Add a letter to the player's hand.
        
        Args:
            letter (str): The letter to add
            
        Returns:
            bool: True if the letter was successfully added
        """
        if self.hand_total >= self.max_size:
            return False
            
        if letter in self.hand:
            self.hand[letter] += 1
        else:
            self.hand[letter] = 1
        self.hand_total += 1
        self.letter_order.append(letter)
        return True
    
    def remove_letter(self, letter):
        """
        Remove a letter from the player's hand.
        
        Args:
            letter (str): The letter to remove
            
        Returns:
            bool: True if the letter was successfully removed
        """
        if letter in self.hand and self.hand[letter] > 0:
            self.hand[letter] -= 1
            if self.hand[letter] == 0:
                del self.hand[letter]
            self.hand_total -= 1
            self.letter_order.remove(letter)
            return True
        return False
    
    def refill(self, count=None):
        """
        Refill the player's hand from the letter bank.
        
        Args:
            count (int, optional): Number of letters to draw, or None to fill to max
            
        Returns:
            int: Number of letters added to the hand
        """
        if count is None:
            count = self.max_size - self.hand_total
        
        if count <= 0:
            return 0
            
        drawn_tiles = self.letter_bank.draw_tiles(count)
        added = 0
        
        for letter, letter_count in drawn_tiles.items():
            if letter in self.hand:
                self.hand[letter] += letter_count
            else:
                self.hand[letter] = letter_count
                
            # Add each letter to letter_order
            for _ in range(letter_count):
                self.letter_order.append(letter)
            added += letter_count
            
        self.hand_total += added
        return added
    
    def return_to_bank(self, letter):
        """
        Return a letter from the hand back to the letter bank.
        
        Args:
            letter (str): The letter to return
            
        Returns:
            bool: True if the letter was returned successfully
        """
        if not self.remove_letter(letter):
            return False
            
        try:
            self.letter_bank.return_tiles(letter, 1)
            return True
        except ValueError:
            # If return fails, add the letter back to hand
            self.add_letter(letter)
            return False
    
    def return_all_to_bank(self):
        """
        Return all letters from the hand back to the letter bank.
        
        Returns:
            int: The number of letters returned
        """
        returned = 0
        letters_to_return = self.letter_order.copy()
        
        for letter in letters_to_return:
            if self.return_to_bank(letter):
                returned += 1
                
        return returned
    
    def exchange_letters(self, letters_to_exchange):
        """
        Exchange specified letters with new ones from the bank.
        
        Args:
            letters_to_exchange (list): Letters to exchange
            
        Returns:
            list: New letters received from the bank
        """
        if self.letter_bank.bank_empty():
            return []
            
        # First return the letters to the bank
        for letter in letters_to_exchange:
            if not self.return_to_bank(letter):
                return []
                
        # Then draw the same number of new letters
        count = len(letters_to_exchange)
        drawn = self.refill(count)
        
        # Return the newly drawn letters
        return self.letter_order[-drawn:] if drawn > 0 else []
    
    def can_form_word(self, word):
        """
        Check if a word can be formed with the letters in hand.
        
        Args:
            word (str): The word to check
            
        Returns:
            bool: True if the word can be formed with available letters
        """
        # Make a copy of the hand to check against
        temp_hand = self.hand.copy()
        
        for letter in word:
            if letter not in temp_hand or temp_hand[letter] <= 0:
                return False
            temp_hand[letter] -= 1
            
        return True
    
    def shuffle_letters(self):
        """
        Shuffle the order of letters in the player's hand.

        This doesn't change which letters the player has,
        just rearranges their order in the display.

        Returns:
            bool: True if the shuffle was successful (hand not empty)
        """
        if not self.letter_order:
            return False
            
        # Use Python's random module to shuffle the letter_order list
        random.shuffle(self.letter_order)
        return True

    def get_letter_values(self):
        """
        Get the point values for all letters in hand.
        
        Returns:
            dict: Mapping of letters to their point values
        """
        return {letter: self.letter_bank.get_letter_value(letter) 
                for letter in self.hand}
    
    def to_json(self):
        """
        Convert player hand to a JSON-serializable dictionary.
        
        Returns:
            dict: Player hand state for serialization
        """
        return {
            "hand": self.hand,
            "hand_total": self.hand_total,
            "letter_order": self.letter_order,
            "max_size": self.max_size
        }
    
    @classmethod
    def from_json(cls, data, letter_bank):
        """
        Create a player hand from serialized data.
        
        Args:
            data (dict): Serialized player hand data
            letter_bank (LetterBank): The letter bank to associate with
            
        Returns:
            PlayerHand: Reconstructed player hand
        """
        hand = cls(letter_bank, data.get("max_size", 20))
        hand.hand = data.get("hand", {})
        hand.hand_total = data.get("hand_total", 0)
        hand.letter_order = data.get("letter_order", [])
        return hand


# Test code
if __name__ == "__main__":
    # Create a letter bank
    print("Creating letter bank...")
    bank = LetterBank()
    
    # Create a player hand
    print("\nCreating player hand...")
    player = bank.create_player_hand()
    
    # Fill the hand with initial letters
    print("\nFilling initial hand...")
    added = player.fill_initial_hand()
    print(f"Added {added} letters to hand")
    print(f"Letters in hand: {player.letter_order}")
    
    # Test exchanging letters
    if len(player.letter_order) >= 3:
        print("\nExchanging 3 letters...")
        to_exchange = player.letter_order[:3]
        print(f"Letters to exchange: {to_exchange}")
        new_letters = player.exchange_letters(to_exchange)
        print(f"New letters received: {new_letters}")
        print(f"Updated hand: {player.letter_order}")
    
    # Test word formation
    print("\nTesting word formation...")
    test_words = ["hello", "world", "game"]
    for word in test_words:
        can_form = player.can_form_word(word)
        print(f"Can form '{word}': {can_form}")
    
    # Test returning all letters
    print("\nReturning all letters to bank...")
    returned = player.return_all_to_bank()
    print(f"Returned {returned} letters")
    print(f"Hand is now empty: {player.hand_total == 0}")
    
    print("\nTests completed!")

