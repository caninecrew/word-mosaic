import sqlite3

class WordValidator:
    """
    Validates words against a dictionary stored in an SQLite database.
    """
    def __init__(self, db_path="dictionary.db"):
        try:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            # Test if the dictionary table exists
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dictionary'")
            if not self.cursor.fetchone():
                print(f"Warning: Dictionary table not found in {db_path}")
                self._create_fallback_dictionary()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            self._create_fallback_dictionary()

    def _create_fallback_dictionary(self):
        """Create an in-memory fallback dictionary with common English words"""
        print("Creating fallback in-memory dictionary")
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE dictionary (word TEXT PRIMARY KEY)")
        
        # Add some common English words as fallback
        common_words = [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "it",
            "for", "not", "on", "with", "he", "as", "you", "do", "at", "this",
            "but", "his", "by", "from", "they", "we", "say", "her", "she", "or",
            "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "game", "play", "word", "letter", "score", "board", "tiles", "win"
        ]
        self.cursor.executemany("INSERT INTO dictionary VALUES (?)", [(w,) for w in common_words])
        self.conn.commit()

    def validate_word(self, word):
        """
        Check if a word is valid.

        Args:
            word (str): The word to validate

        Returns:
            bool: True if the word is valid, False otherwise
        """
        self.cursor.execute("SELECT 1 FROM dictionary WHERE word = ?", (word.lower(),))
        return self.cursor.fetchone() is not None

    def validate_words(self, words):
        """
        Validate a list of words.

        Args:
            words (list): List of words to validate

        Returns:
            list: List of valid words
        """
        return [word for word in words if self.validate_word(word)]

    def suggest_words(self, word, max_suggestions=5):
        """
        Suggest similar words from the dictionary for an invalid word.

        Args:
            word (str): The invalid word.
            max_suggestions (int): Maximum number of suggestions to return.

        Returns:
            list: A list of suggested words.
        """
        from difflib import get_close_matches

        # Fetch all words from the database
        self.cursor.execute("SELECT word FROM dictionary")
        all_words = [row[0] for row in self.cursor.fetchall()]

        return get_close_matches(word.lower(), all_words, n=max_suggestions)

    def dictionary_size(self):
        """
        Get the number of words in the dictionary.

        Returns:
            int: The number of words in the dictionary.
        """
        self.cursor.execute("SELECT COUNT(*) FROM dictionary")
        return self.cursor.fetchone()[0]

    def close(self):
        """Close the database connection."""
        self.conn.close()