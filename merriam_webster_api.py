"""
Merriam-Webster API for Word Mosaic game
Provides functions to validate words against the Merriam-Webster dictionary via API
"""

import os
import requests
from dotenv import load_dotenv
import json
import time

# Load environment variables from .env file
load_dotenv()

class MerriamWebsterAPI:
    """
    API client for validating words against the Merriam-Webster Collegiate Dictionary
    """
    def __init__(self):
        """Initialize the Merriam-Webster API client"""
        # Get API key from environment variable
        self.api_key = os.getenv("MERRIAM_WEBSTER_API_KEY")
        
        # Base URL for the Merriam-Webster Collegiate Dictionary API
        self.base_url = "https://www.dictionaryapi.com/api/v3/references/collegiate/json"
        
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
        if word in self.word_cache:
            return self.word_cache[word]
        
        # If no API key is set, fall back to local validation
        if not self.api_key:
            print("Warning: Merriam-Webster API key not found. Please set MERRIAM_WEBSTER_API_KEY environment variable.")
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
                self.word_cache[word] = is_valid
                
                return is_valid
            else:
                print(f"API Error: Status code {response.status_code}")
                # Fall back to local validation if API fails
                return self._fallback_validation(word)
                
        except Exception as e:
            print(f"Error validating word through Merriam-Webster API: {str(e)}")
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
            print("Warning: Merriam-Webster API key not found. Please set MERRIAM_WEBSTER_API_KEY environment variable.")
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
                
                # Extract the first definition
                first_entry = results[0]
                if 'shortdef' in first_entry and first_entry['shortdef']:
                    return first_entry['shortdef'][0]
                
                return None
            else:
                print(f"API Error: Status code {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting definition through Merriam-Webster API: {str(e)}")
            return None
    
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