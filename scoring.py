
class Scoring:
    def __init__(self, special_tiles):
        """
        Initialize the Scoring class with special tile information.

        Args:
            special_tiles (dict): Dictionary containing special tile information (e.g., positions and types of special tiles).
        """
        self.special_tiles = special_tiles  # Special tile information (e.g., TW, DW, TL, DL)
        self.letter_scores = {}  # Dictionary mapping letters to their scores (e.g., {'A': 1, 'B': 3, 'Z': 10})
        self.total_score = 0  # Total score accumulated by the player
        self.bingo_bonus = 50  # Bonus score for using all 7 tiles in a single turn
        self.word_scores = {}  # Dictionary to store scores of individual words formed during a turn

    def calculate_word_score(self, word, positions):
        """
        Calculate the score for a single word based on the letters and their positions on the board.

        Args:
            word (str): The word to calculate the score for.
            positions (list): A list of (row, col) tuples representing the positions of the letters in the word.

        Returns:
            int: The calculated score for the word.
        """
        word_score = 0
        word_multiplier = 1

        for i, letter in enumerate(word):
            position = positions[i]
            letter_score = self.get_letter_score(letter)

            # Check if the position has a special tile
            if position in self.special_tiles:
                special_tile = self.special_tiles[position]
                if special_tile == 'DL':  # Double Letter
                    letter_score *= 2
                elif special_tile == 'TL':  # Triple Letter
                    letter_score *= 3
                elif special_tile == 'DW':  # Double Word
                    word_multiplier *= 2
                elif special_tile == 'TW':  # Triple Word
                    word_multiplier *= 3

            word_score += letter_score

        # Apply word multiplier
        word_score *= word_multiplier

        return word_score

    def calculate_turn_score(self, words):
        """
        Calculate the total score for all words formed during a turn.

        Args:
            words (list): A list of tuples, where each tuple contains:
                        - word (str): The word formed.
                        - positions (list): A list of (row, col) tuples representing the positions of the letters in the word.

        Returns:
            int: The total score for the turn.
        """
        turn_score = 0

        for word, positions in words:
            # Calculate the score for each word
            word_score = self.calculate_word_score(word, positions)
            self.word_scores[word] = word_score  # Store the score for the word
            turn_score += word_score

            # Check for bingo bonus
            if self.is_bingo(word):
                turn_score += self.bingo_bonus

        # Update the total score
        self.total_score += turn_score

        return turn_score

    def get_letter_score(self, letter):
        """
        Retrieve the score for a given letter.

        Args:
            letter (str): The letter to retrieve the score for.

        Returns:
            int: The score of the letter.
        """
        return self.letter_scores.get(letter.upper(), 0)  # Default to 0 if the letter is not found


    def apply_special_tiles(self, word, positions):
        """
        Apply special tile multipliers to a word.

        Args:
            word (str): The word to apply special tiles to.
            positions (list): A list of (row, col) tuples representing the positions of the letters in the word.

        Returns:
            int: The modified score for the word after applying special tiles.
        """
        word_score = 0
        word_multiplier = 1

        for i, letter in enumerate(word):
            position = positions[i]
            letter_score = self.get_letter_score(letter)

            # Check if the position has a special tile
            if position in self.special_tiles:
                special_tile = self.special_tiles[position]
                if special_tile == 'DL':  # Double Letter
                    letter_score *= 2
                elif special_tile == 'TL':  # Triple Letter
                    letter_score *= 3
                elif special_tile == 'DW':  # Double Word
                    word_multiplier *= 2
                elif special_tile == 'TW':  # Triple Word
                    word_multiplier *= 3

            word_score += letter_score

        # Apply word multiplier
        word_score *= word_multiplier

        return word_score


    def is_bingo(self, word):
        """
        Check if the word qualifies for a bingo bonus.

        Args:
            word (str): The word to check.

        Returns:
            bool: True if the word uses all 7 tiles, False otherwise.
        """
        return len(word) == 7


    def get_total_score(self):
        """
        Retrieve the total score accumulated by the player.

        Returns:
            int: The total score.
        """
        return self.total_score


    def reset_score(self):
        """
        Reset the player's total score and word scores.
        """
        self.total_score = 0
        self.word_scores.clear()


    def load_letter_score(self, letter_score_file):
        """
        Load letter scores from a configuration file.

        Args:
            letter_score_file (str): Path to the file containing letter scores.
        """
        import json
        with open(letter_score_file, "r") as file:
            self.letter_scores = json.load(file)


    def validate_word_positions(self, word, positions):
        """
        Ensure the word's positions align with the board's rules.

        Args:
            word (str): The word to validate.
            positions (list): A list of (row, col) tuples representing the positions of the letters in the word.

        Returns:
            bool: True if the word is placed in a straight line, False otherwise.
        """
        rows = [pos[0] for pos in positions]
        cols = [pos[1] for pos in positions]

        # Check if all rows are the same (horizontal word) or all columns are the same (vertical word)
        return len(set(rows)) == 1 or len(set(cols)) == 1