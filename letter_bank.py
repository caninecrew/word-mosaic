import random

class LetterBank:
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
        self.letter_bank = self.LETTER_FREQUENCIES.copy() 
        self.letter_bank_total = sum(self.letter_bank.values()) # total number of tiles in the bank

    def draw_tiles(self, num_tiles):
        """Draw a specified number of tiles from the letter bank."""
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
        """Refill the player's hand with tiles from the letter bank."""
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
        """Return tiles back to the letter bank."""
        if letter in self.letter_bank:
            self.letter_bank[letter] += num_tiles
            self.letter_bank_total += num_tiles
        else:
            raise ValueError("Invalid letter returned to the bank.")
        
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
    
    def get_letter_frequencies(self):
        """Get the frequencies of letters in the letter bank."""
        return self.LETTER_FREQUENCIES.copy()
    
    def _get_random_letter(self):
        """Get a random letter from the letter bank."""
        letters = [letter for letter, count in self.letter_bank.items() if count > 0]
        return random.choice(letters) if letters else None
    
class PlayerHand:
    def __init__(self):
        self.hand = {}
        self.hand_total = sum(self.hand.values()) # total number of tiles in the hand

    
        