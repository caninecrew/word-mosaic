"""
Merriam-Webster API for Word Mosaic game
Provides functions to validate words against the Merriam-Webster dictionaries via API
"""

import os
import requests
from dotenv import load_dotenv
import json
import time

# Load environment variables from .env file
load_dotenv()

class DictionaryType:
    """
    Enumeration of available dictionary types
    """
    COLLEGIATE = "collegiate"
    LEARNERS = "learners"

class MerriamWebsterAPI:
    """
    API client for validating words against Merriam-Webster dictionaries
    """
    def __init__(self, dictionary_type=DictionaryType.COLLEGIATE):
        """
        Initialize the Merriam-Webster API client
        
        Args:
            dictionary_type: The type of dictionary to use (collegiate or learners)
        """
        # Set dictionary type
        self.dictionary_type = dictionary_type
        
        # Get API key from environment variable based on dictionary type
        if dictionary_type == DictionaryType.COLLEGIATE:
            self.api_key = os.getenv("MW_COLLEGIATE_API_KEY")
            # Base URL for the Merriam-Webster Collegiate Dictionary API
            self.base_url = "https://www.dictionaryapi.com/api/v3/references/collegiate/json"
        else:  # Learners dictionary
            self.api_key = os.getenv("MW_LEARNERS_API_KEY")
            # Base URL for the Merriam-Webster Learner's Dictionary API
            self.base_url = "https://www.dictionaryapi.com/api/v3/references/learners/json"
        
        # Cache for validated words to reduce API calls
        self.word_cache = {}
        
        # Rate limiting parameters
        self.last_request_time = 0
        self.min_request_interval = 0.2  # Minimum time between requests in seconds

    def validate_word(self, word):
        """
        Check if a word is valid in the Merriam-Webster dictionary.

        Args:
            word (str): The word to validate

        Returns:
            bool: True if the word is valid, False otherwise
        """
        # Convert to lowercase for consistency
        word = word.lower().strip()
        
        # Check cache first to avoid unnecessary API calls
        cache_key = f"{self.dictionary_type}:{word}"
        if cache_key in self.word_cache:
            return self.word_cache[cache_key]
        
        # If no API key is set, fall back to local validation
        if not self.api_key:
            dict_name = "Collegiate" if self.dictionary_type == DictionaryType.COLLEGIATE else "Learner's"
            print(f"Warning: Merriam-Webster {dict_name} API key not found. Please set the appropriate environment variable.")
            return self._fallback_validation(word)
        
        try:
            # Implement rate limiting
            self._respect_rate_limit()
            
            # Construct the API URL
            url = f"{self.base_url}/{word}?key={self.api_key}"
            
            # Make the API request
            response = requests.get(url)
            
            # Update last request time
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                # Parse the response
                results = response.json()
                
                # Check if the word was found in the dictionary
                is_valid = False
                
                if results:
                    # Check if we got a list of strings (suggestions) or actual entries
                    if isinstance(results[0], str):
                        # We got suggestions, not actual entries
                        is_valid = False
                    else:
                        # We got actual dictionary entries - word is valid
                        is_valid = True
                
                # Cache the result
                self.word_cache[cache_key] = is_valid
                
                return is_valid
            else:
                print(f"API Error: Status code {response.status_code}")
                # Fall back to local validation if API fails
                return self._fallback_validation(word)
                
        except Exception as e:
            dict_name = "Collegiate" if self.dictionary_type == DictionaryType.COLLEGIATE else "Learner's"
            print(f"Error validating word through Merriam-Webster {dict_name} API: {str(e)}")
            # Fall back to local validation in case of error
            return self._fallback_validation(word)
    
    def validate_words(self, words):
        """
        Validate a list of words.

        Args:
            words (list): List of words to validate

        Returns:
            list: List of valid words
        """
        return [word for word in words if self.validate_word(word)]
    
    def get_definition(self, word):
        """
        Get the definition of a word from the Merriam-Webster dictionary.

        Args:
            word (str): The word to look up

        Returns:
            str: The definition of the word, or None if not found
        """
        # Normalize word
        word = word.lower().strip()
        
        # If no API key is set, return None
        if not self.api_key:
            dict_name = "Collegiate" if self.dictionary_type == DictionaryType.COLLEGIATE else "Learner's"
            print(f"Warning: Merriam-Webster {dict_name} API key not found. Please set the appropriate environment variable.")
            return None
        
        try:
            # Implement rate limiting
            self._respect_rate_limit()
            
            # Construct the API URL
            url = f"{self.base_url}/{word}?key={self.api_key}"
            
            # Make the API request
            response = requests.get(url)
            
            # Update last request time
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                # Parse the response
                results = response.json()
                
                # If no results or just suggestions, return None
                if not results or isinstance(results[0], str):
                    return None
                
                # Extract the definitions based on dictionary type
                first_entry = results[0]
                if self.dictionary_type == DictionaryType.COLLEGIATE:
                    if 'shortdef' in first_entry and first_entry['shortdef']:
                        return first_entry['shortdef'][0]
                else:  # Learner's dictionary has a slightly different format
                    if 'def' in first_entry and first_entry['def']:
                        senses = first_entry['def'][0].get('sseq', [])
                        if senses and len(senses) > 0:
                            # Extract the first definition from the structure
                            # Learner's dictionary has a more complex structure
                            for sense_group in senses:
                                for sense in sense_group:
                                    if len(sense) > 1 and isinstance(sense[1], dict):
                                        if 'dt' in sense[1]:
                                            dt = sense[1]['dt']
                                            for d in dt:
                                                if d[0] == 'text':
                                                    return d[1]
                
                return None
            else:
                print(f"API Error: Status code {response.status_code}")
                return None
                
        except Exception as e:
            dict_name = "Collegiate" if self.dictionary_type == DictionaryType.COLLEGIATE else "Learner's"
            print(f"Error getting definition through Merriam-Webster {dict_name} API: {str(e)}")
            return None
    
    def get_dictionary_type(self):
        """
        Get the current dictionary type
        
        Returns:
            str: The current dictionary type
        """
        return self.dictionary_type
    
    def set_dictionary_type(self, dictionary_type):
        """
        Set the dictionary type
        
        Args:
            dictionary_type: The type of dictionary to use
        """
        if dictionary_type != self.dictionary_type:
            self.dictionary_type = dictionary_type
            
            # Update API key and base URL based on the new dictionary type
            if dictionary_type == DictionaryType.COLLEGIATE:
                self.api_key = os.getenv("MW_COLLEGIATE_API_KEY")
                self.base_url = "https://www.dictionaryapi.com/api/v3/references/collegiate/json"
            else:  # Learners dictionary
                self.api_key = os.getenv("MW_LEARNERS_API_KEY")
                self.base_url = "https://www.dictionaryapi.com/api/v3/references/learners/json"
    
    def _respect_rate_limit(self):
        """
        Ensure we don't exceed API rate limits by adding delays if needed
        """
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            # Sleep to respect rate limiting
            time.sleep(self.min_request_interval - elapsed)
    
    def _fallback_validation(self, word):
        """
        Fallback method for word validation when the API is unavailable
        Uses common word-length heuristics and common English words
        
        Args:
            word (str): The word to validate
            
        Returns:
            bool: True if the word is likely valid, False otherwise
        """
        # Very simple fallback: consider common word lengths and patterns
        if len(word) < 2:  # Only 'a' and 'i' are valid 1-letter English words
            return word in ['a', 'i']
        
        # For longer words, check against a small set of common English words
        common_words = {
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "it",
            "for", "not", "on", "with", "he", "as", "you", "do", "at", "this",
            "but", "his", "by", "from", "they", "we", "say", "her", "she", "or",
            "an", "will", "my", "one", "all", "would", "there", "their", "what",
            "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
            "game", "play", "word", "letter", "score", "board", "tiles", "win"
        }
        
        return word.lower() in common_words