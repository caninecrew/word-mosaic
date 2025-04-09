class Scoring:
    def __init__(self, special_tiles, letter_scores):
        """
        Initialize the Scoring class with special tile information and letter scores.

        Args:
            special_tiles (dict): Dictionary containing special tile information (e.g., positions and types of special tiles).
            letter_scores (dict): Dictionary mapping letters to their scores (e.g., {'A': 1, 'B': 3, 'Z': 10}).
        """
        self.special_tiles = special_tiles  # Special tile information (e.g., TW, DW, TL, DL)
        self.letter_scores = letter_scores  # Letter scores for scoring
        self.total_score = 0  # Total score accumulated by the player
        self.bingo_bonus = 50  # Bonus score for using all 7 tiles in a single turn
        self.word_scores = {}  # Dictionary to store scores of individual words formed during a turn
        
        # Track game statistics
        self.total_words_formed = 0
        self.longest_word = ""
        self.highest_scoring_word = ""
        self.highest_word_score = 0
        self.turns_played = 0
        self.tiles_placed = 0
        self.words_by_length = {}  # Dictionary to track words by length {length: count}

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
        length_bonus = 1.0  # Default multiplier (no bonus)

        # Apply length-based bonus multipliers
        if len(word) >= 7:
            length_bonus = 3.0  # 3x multiplier for 7+ letter words
        elif len(word) == 6:
            length_bonus = 2.0  # 2x multiplier for 6-letter words
        elif len(word) == 5:
            length_bonus = 1.5  # 1.5x multiplier for 5-letter words

        # Calculate base score from letters and special tiles
        for i, letter in enumerate(word):
            position = positions[i]
            letter_score = self.get_letter_score(letter)
            print(f"Processing letter: {letter}, position: {position}, letter_score: {letter_score}")  # Debugging statement

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

        # Apply word multiplier (from special tiles)
        word_score *= word_multiplier
        
        # Apply length bonus
        final_score = int(word_score * length_bonus)
        
        print(f"Word: {word}, Base score: {word_score}, Length bonus: {length_bonus}x, Final score: {final_score}")
        
        return final_score

    def calculate_turn_score(self, words, board_positions=None):
        """
        Calculate the total score for all words formed during a turn.

        Args:
            words (list): A list of tuples, where each tuple contains:
                        - word (str): The word formed.
                        - positions (list): A list of (row, col) tuples representing the positions of the letters in the word.
            board_positions (list, optional): A list of (row, col) tuples of existing letter positions on the board.
                                             Used to calculate connection bonuses.

        Returns:
            int: The total score for the turn.
        """
        turn_score = 0
        
        # If board_positions not provided, we can't calculate connection bonuses
        if board_positions is None:
            board_positions = []
            
        # Get positions of all letters in the words being submitted
        current_word_positions = []
        for _, positions in words:
            current_word_positions.extend(positions)

        # Remove current word positions from existing positions to avoid counting self-connections
        existing_positions = [pos for pos in board_positions if pos not in current_word_positions]

        for word, positions in words:
            print(f"Calculating score for word: {word}, positions: {positions}")  # Debugging statement
            
            # Calculate the score for the word
            word_score = self.calculate_word_score(word, positions)
            
            # Add connection bonus if we have existing positions to check against
            if existing_positions:
                connection_bonus = self.calculate_connection_bonus(positions, existing_positions)
                word_score += connection_bonus
                
            self.word_scores[word] = word_score  # Store the score for the word
            turn_score += word_score

            # Check for bingo bonus
            if self.is_bingo(word):
                bingo_bonus = self.bingo_bonus
                turn_score += bingo_bonus
                print(f"Bingo bonus: {bingo_bonus} points for using 7 letters")
                
            # Update statistics
            self.total_words_formed += 1
            self.tiles_placed += len(positions)
            
            # Update word length distribution
            word_length = len(word)
            if word_length in self.words_by_length:
                self.words_by_length[word_length] += 1
            else:
                self.words_by_length[word_length] = 1
            
            # Check if this is the longest word so far
            if len(word) > len(self.longest_word):
                self.longest_word = word
                
            # Check if this is the highest scoring word so far
            if word_score > self.highest_word_score:
                self.highest_word_score = word_score
                self.highest_scoring_word = word

        # Update the total score
        self.total_score += turn_score
        self.turns_played += 1

        print(f"Turn score: {turn_score}, Total score: {self.total_score}")  # Debugging statement

        return turn_score

    def get_letter_score(self, letter):
        """
        Retrieve the score for a given letter.

        Args:
            letter (str): The letter to retrieve the score for.

        Returns:
            int: The score of the letter.
        """
        print(f"Getting score for letter: {letter}")  # Debugging statement
        return self.letter_scores.get(letter.lower(), 0)  # Default to 0 if the letter is not found


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

    def calculate_connection_bonus(self, positions, existing_positions):
        """
        Calculate bonus points for connections with existing words.
        
        Args:
            positions (list): A list of (row, col) tuples for the new word.
            existing_positions (list): A list of (row, col) tuples for existing letters on the board.
            
        Returns:
            int: Bonus points for connections (2 points per connection)
        """
        # Find intersections between the new word and existing letters
        intersections = set(positions).intersection(set(existing_positions))
        connection_points = len(intersections) * 2  # 2 points per connection
        
        if connection_points > 0:
            print(f"Connection bonus: {connection_points} points for {len(intersections)} intersections")
            
        return connection_points
        
    def calculate_coverage_bonus(self, coverage_percentage):
        """
        Calculate bonus points for board coverage at end of game.
        
        Args:
            coverage_percentage (float): The percentage of the board that is covered with letters (0-100).
            
        Returns:
            int: Bonus points for board coverage
        """
        # Coverage bonuses:
        # - 30% coverage: 50 points
        # - 40% coverage: 100 points
        # - 50% coverage: 200 points
        # - 60% coverage: 350 points
        # - 70% coverage: 500 points
        # - 80% coverage: 750 points
        # - 90% coverage: 1000 points
        # - 100% coverage: 2000 points
        
        coverage_bonus = 0
        
        if coverage_percentage >= 100:
            coverage_bonus = 2000
        elif coverage_percentage >= 90:
            coverage_bonus = 1000
        elif coverage_percentage >= 80:
            coverage_bonus = 750
        elif coverage_percentage >= 70:
            coverage_bonus = 500
        elif coverage_percentage >= 60:
            coverage_bonus = 350
        elif coverage_percentage >= 50:
            coverage_bonus = 200
        elif coverage_percentage >= 40:
            coverage_bonus = 100
        elif coverage_percentage >= 30:
            coverage_bonus = 50
            
        print(f"Coverage bonus: {coverage_bonus} points for {coverage_percentage:.1f}% board coverage")
        return coverage_bonus
    
    def calculate_efficiency_bonus(self, letters_used, total_score):
        """
        Calculate bonus points for efficient use of letters.
        
        Args:
            letters_used (int): The total number of letters used.
            total_score (int): The total score accumulated.
            
        Returns:
            int: Bonus points for letter efficiency
        """
        # Only award efficiency bonus if enough letters were used
        if letters_used < 30:
            return 0
            
        # Calculate average points per letter
        avg_points_per_letter = total_score / letters_used
        
        # Efficiency bonuses:
        # - 4 points/letter: 50 points
        # - 5 points/letter: 100 points
        # - 6 points/letter: 200 points
        # - 7 points/letter: 300 points
        # - 8+ points/letter: 500 points
        
        efficiency_bonus = 0
        
        if avg_points_per_letter >= 8:
            efficiency_bonus = 500
        elif avg_points_per_letter >= 7:
            efficiency_bonus = 300
        elif avg_points_per_letter >= 6:
            efficiency_bonus = 200
        elif avg_points_per_letter >= 5:
            efficiency_bonus = 100
        elif avg_points_per_letter >= 4:
            efficiency_bonus = 50
            
        print(f"Efficiency bonus: {efficiency_bonus} points for {avg_points_per_letter:.1f} points per letter")
        return efficiency_bonus
    
    def calculate_complexity_bonus(self, words_by_length):
        """
        Calculate bonus points for playing complex (longer) words.
        
        Args:
            words_by_length (dict): Dictionary mapping word length to count of words with that length.
            
        Returns:
            int: Bonus points for word complexity
        """
        complexity_bonus = 0
        
        # Award points for words of different lengths
        # Longer words are worth more
        for length, count in words_by_length.items():
            if length >= 7:
                # 50 points per 7+ letter word
                complexity_bonus += count * 50
            elif length == 6:
                # 20 points per 6-letter word
                complexity_bonus += count * 20
            elif length == 5:
                # 10 points per 5-letter word
                complexity_bonus += count * 10
                
        print(f"Complexity bonus: {complexity_bonus} points")
        return complexity_bonus
    
    def calculate_end_game_bonus(self, coverage_percentage, letters_used):
        """
        Calculate total end-game bonus based on board coverage, efficiency, and word complexity.
        
        Args:
            coverage_percentage (float): The percentage of the board that is covered (0-100).
            letters_used (int): The total number of letters used during the game.
            
        Returns:
            tuple: (total_bonus, breakdown) where breakdown is a dictionary of bonus categories and points
        """
        # Calculate individual bonuses
        coverage_bonus = self.calculate_coverage_bonus(coverage_percentage)
        efficiency_bonus = self.calculate_efficiency_bonus(letters_used, self.total_score)
        complexity_bonus = self.calculate_complexity_bonus(self.words_by_length)
        
        # Calculate total bonus
        total_bonus = coverage_bonus + efficiency_bonus + complexity_bonus
        
        # Create a breakdown of bonuses
        bonus_breakdown = {
            "coverage": coverage_bonus,
            "efficiency": efficiency_bonus,
            "complexity": complexity_bonus,
            "total": total_bonus
        }
        
        return total_bonus, bonus_breakdown
    
    def get_statistics(self):
        """
        Get comprehensive game statistics.
        
        Returns:
            dict: A dictionary containing various game statistics
        """
        stats = {
            "total_score": self.total_score,
            "total_words": self.total_words_formed,
            "longest_word": self.longest_word,
            "highest_scoring_word": self.highest_scoring_word,
            "highest_word_score": self.highest_word_score,
            "turns_played": self.turns_played,
            "tiles_placed": self.tiles_placed,
            "words_by_length": self.words_by_length,
            "avg_word_length": sum(length * count for length, count in self.words_by_length.items()) / 
                              max(1, self.total_words_formed) if self.total_words_formed else 0,
            "avg_score_per_word": self.total_score / max(1, self.total_words_formed) if self.total_words_formed else 0,
            "avg_score_per_turn": self.total_score / max(1, self.turns_played) if self.turns_played else 0,
            "avg_score_per_tile": self.total_score / max(1, self.tiles_placed) if self.tiles_placed else 0
        }
        
        return stats