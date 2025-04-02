class WordValidator:
    """
    Validates words against a dictionary.
    """
    def __init__(self, dictionary_path="dictionary.txt"):
        with open(dictionary_path, "r") as file:
            self.dictionary = set(word.strip().lower() for word in file)
    
    def validate_word(self, word):
        """
        Check if a word is valid.
        
        Args:
            word (str): The word to validate
            
        Returns:
            bool: True if the word is valid, False otherwise
        """
        return word.lower() in self.dictionary

    def validate_words(self, words):
        """
        Validate a list of words.
        
        Args:
            words (list): List of words to validate
            
        Returns:
            list: List of valid words
        """
        return [word for word in words if self.validate_word(word)]

    def validate_sentence(self, sentence):
        """
        Validate a sentence by checking each word.
        
        Args:
            sentence (str): The sentence to validate
            
        Returns:
            list: List of valid words in the sentence
        """
        words = sentence.split()
        return self.validate_words(words)
    
    def load_custom_dictionary(self, dictionary_path):
        """
        Load a custom dictionary from a file.
        
        Args:
            dictionary_path (str): Path to the custom dictionary file.
        """
        try:
            with open(dictionary_path, "r") as file:
                self.dictionary = set(word.strip().lower() for word in file)
            print(f"Custom dictionary loaded from '{dictionary_path}'.")
        except FileNotFoundError:
            print(f"Error: Dictionary file '{dictionary_path}' not found.")
        except Exception as e:
            print(f"Error loading dictionary: {e}")

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
        return get_close_matches(word.lower(), self.dictionary, n=max_suggestions)