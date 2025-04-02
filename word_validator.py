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