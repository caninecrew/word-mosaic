import sqlite3
from merriam_webster_api import merriam_webster, MerriamWebsterAPI

class WordValidator:
    """
    Validates words against Merriam-Webster Dictionary API (primary) and 
    local SQLite database (fallback).
    """
    def __init__(self, dictionary_type=None, db_path="dictionary.db"):
        """
        Initialize the word validator with the specified dictionary type
        
        Args:
            dictionary_type (str, optional): Type of dictionary to use (COLLEGIATE or LEARNERS)
            db_path (str, optional): Path to SQLite dictionary database for fallback
        """
        # Initialize the Merriam-Webster API client with the specified dictionary type
        self.mw_api = MerriamWebsterAPI(dictionary_type)
        self.dictionary_type = self.mw_api.dictionary_type
        self.dictionary_name = self.mw_api.name
        
        # Also maintain the SQLite connection as fallback
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
            "game", "play", "word", "letter", "score", "board", "tiles", "win",
            "dare", "date", "data", "dark", "dash", "darn", "dart"  # Added additional common d-words
        ]
        self.cursor.executemany("INSERT INTO dictionary VALUES (?)", [(w,) for w in common_words])
        self.conn.commit()

    def validate_word(self, word):
        """
        Check if a word is valid using Merriam-Webster API first, then fallback to local database.

        Args:
            word (str): The word to validate

        Returns:
            bool: True if the word is valid, False otherwise
        """
        print(f"[DEBUG VALIDATOR] Validating word: '{word}'")
        
        # First try Merriam-Webster API
        api_result = merriam_webster.is_valid_word(word.lower())
        print(f"[DEBUG VALIDATOR] Merriam-Webster API result for '{word}': {api_result}")
        
        # If API provides a definite answer, return it
        if api_result is not None:
            return api_result
        
        # Fallback to local database
        self.cursor.execute("SELECT 1 FROM dictionary WHERE word = ?", (word.lower(),))
        db_result = self.cursor.fetchone() is not None
        print(f"[DEBUG VALIDATOR] Local dictionary result for '{word}': {db_result}")
        
        return db_result

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

    def get_definition(self, word):
        """
        Get the definition of a word.
        
        Args:
            word (str): The word to define
            
        Returns:
            str: The definition of the word, or None if not found
        """
        # Try to get definition from Merriam-Webster API
        return self.mw_api.get_definition(word)

    def dictionary_size(self):
        """
        Get the number of words in the dictionary.

        Returns:
            int: The number of words in the dictionary.
        """
        self.cursor.execute("SELECT COUNT(*) FROM dictionary")
        return self.cursor.fetchone()[0]
    
    def switch_dictionary(self, dictionary_type):
        """
        Switch to a different dictionary type
        
        Args:
            dictionary_type (str): The dictionary type to switch to (COLLEGIATE or LEARNERS)
            
        Returns:
            dict: Information about the new dictionary
        """
        self.mw_api = MerriamWebsterAPI(dictionary_type)
        self.dictionary_type = self.mw_api.dictionary_type
        self.dictionary_name = self.mw_api.name
        return self.mw_api.get_dictionary_info()
    
    def get_dictionary_info(self):
        """
        Get information about the current dictionary
        
        Returns:
            dict: Dictionary information including name, API availability, and word count
        """
        # Get basic information about the dictionary
        info = {
            'name': self.dictionary_name,
            'type': self.dictionary_type,
            'api_available': hasattr(self.mw_api, 'api_key') and bool(self.mw_api.api_key)
        }
        
        # Get the count of words in the local database
        try:
            self.cursor.execute("SELECT COUNT(*) FROM dictionary")
            info['db_word_count'] = self.cursor.fetchone()[0]
        except (sqlite3.Error, AttributeError):
            info['db_word_count'] = 0
            
        return info

    def close(self):
        """Close the database connection."""
        self.conn.close()