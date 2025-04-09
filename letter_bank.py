import random
from collections import defaultdict

class PlayerHand:
    """
    Represents a player's current hand of letters
    """
    def __init__(self, letter_bank, hand_size=7):
        """
        Initialize a player's hand
        
        Args:
            letter_bank (LetterBank): The letter bank to draw from
            hand_size (int): The number of letters to maintain in the hand
        """
        self.letter_bank = letter_bank
        self.hand_size = hand_size
        self.letters = []
        self.refill()
        
    def refill(self):
        """
        Refill the player's hand up to the hand size with letters from the bank
        
        Returns:
            bool: True if at least one letter was added, False otherwise
        """
        if len(self.letters) >= self.hand_size:
            return False
            
        letters_added = 0
        while len(self.letters) < self.hand_size and self.letter_bank.letters_available():
            letter = self.letter_bank.draw_letter()
            if letter:
                self.letters.append(letter)
                letters_added += 1
        
        return letters_added > 0
        
    def use_letter(self, letter):
        """
        Remove a letter from the player's hand when it's used
        
        Args:
            letter (str): The letter to remove
            
        Returns:
            bool: True if the letter was found and removed, False otherwise
        """
        if letter in self.letters:
            self.letters.remove(letter)
            return True
        return False
        
    def add_letter(self, letter):
        """
        Add a letter back to the player's hand (e.g., when removing from board)
        
        Args:
            letter (str): The letter to add
        """
        if len(self.letters) < self.hand_size:
            self.letters.append(letter)
            
    def get_letters(self):
        """
        Get the current letters in the hand
        
        Returns:
            list: The letters in the player's hand
        """
        return self.letters
        
    def shuffle_letters(self):
        """
        Shuffle the letters in the player's hand
        
        Returns:
            bool: True if shuffled, False if empty hand
        """
        if not self.letters:
            return False
            
        random.shuffle(self.letters)
        return True

class LetterBank:
    """
    Manages the letters available in the game
    """
    def __init__(self, distribution=None, values=None):
        """
        Initialize the letter bank with a distribution of letters.
        
        Args:
            distribution (dict): The distribution of letters {letter: count}
            values (dict): The point value of each letter {letter: points}
        """
        # Default Scrabble-like distribution
        self.distribution = distribution or {
            'a': 9, 'b': 2, 'c': 2, 'd': 4, 'e': 12, 'f': 2, 'g': 3, 'h': 2, 'i': 9,
            'j': 1, 'k': 1, 'l': 4, 'm': 2, 'n': 6, 'o': 8, 'p': 2, 'q': 1, 'r': 6,
            's': 4, 't': 6, 'u': 4, 'v': 2, 'w': 2, 'x': 1, 'y': 2, 'z': 1, '0': 2  # '0' represents blank tiles
        }
        
        # Default Scrabble-like letter values
        self.values = values or {
            'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4, 'i': 1,
            'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3, 'q': 10, 'r': 1,
            's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8, 'y': 4, 'z': 10, '0': 0  # Blank tiles are worth 0
        }
        
        self.reset()
        
        # Create player's hand
        self.player_hand = PlayerHand(self)
        
    def reset(self):
        """
        Reset the letter bank to its initial state
        """
        # Initialize bag of letters based on distribution
        self.bag = []
        for letter, count in self.distribution.items():
            self.bag.extend([letter] * count)
        
        # Shuffle the bag
        random.shuffle(self.bag)
        
    def draw_letter(self):
        """
        Draw a random letter from the bag and remove it
        
        Returns:
            str: A random letter, or None if the bag is empty
        """
        if not self.bag:
            return None
        
        return self.bag.pop()
        
    def draw_letters(self, count):
        """
        Draw multiple random letters from the bag
        
        Args:
            count (int): Number of letters to draw
            
        Returns:
            list: The drawn letters
        """
        letters = []
        for _ in range(min(count, len(self.bag))):
            letter = self.draw_letter()
            if letter:
                letters.append(letter)
        return letters
        
    def return_letter(self, letter):
        """
        Return a letter to the bag
        
        Args:
            letter (str): The letter to return
        """
        self.bag.append(letter)
        random.shuffle(self.bag)
        
    def get_letter_value(self, letter):
        """
        Get the point value of a letter
        
        Args:
            letter (str): The letter to get the value for
            
        Returns:
            int: The point value
        """
        return self.values.get(letter.lower(), 0)
        
    def remaining_letters(self):
        """
        Get the count of remaining letters in the bag
        
        Returns:
            int: Count of letters remaining
        """
        return len(self.bag)
        
    def letters_available(self):
        """
        Check if there are any letters left in the bag
        
        Returns:
            bool: True if letters are available, False otherwise
        """
        return len(self.bag) > 0
        
    def get_available_letters(self):
        """
        Get the list of letters available to the player (in hand)
        
        Returns:
            list: Letters in player's hand
        """
        return self.player_hand.get_letters()
        
    def add_letter(self, letter):
        """
        Add a letter back to the player's hand
        
        Args:
            letter (str): The letter to add
        """
        self.player_hand.add_letter(letter)
        
    def use_letters(self, letter):
        """
        Use a letter from the player's hand
        
        Args:
            letter (str): The letter to use
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.player_hand.use_letter(letter)

