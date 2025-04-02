import sqlite3

class WordValidator:
    """
    Validates words against a dictionary stored in an SQLite database.
    """
    def __init__(self, db_path="dictionary.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

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