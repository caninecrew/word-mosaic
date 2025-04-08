"""
Scrabble API for Word Mosaic game
Provides functions to validate words against the Scrabble dictionary via API
"""

import os
import requests
from dotenv import load_dotenv
import json
import time

# Load environment variables from .env file
load_dotenv()

class ScrabbleAPI:
    """
    API client for validating words against the Scrabble dictionary
    """
    def __init__(self):
        """Initialize the Scrabble API client"""
        # Get API key from environment variable
        self.api_key = os.getenv("SCRABBLE_API_KEY")
        
        # Base URL for the Scrabble API
        self.base_url = "https://scrabble-dictionary.p.rapidapi.com/check"
        
        # Headers for the API request
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "scrabble-dictionary.p.rapidapi.com"
        }
        
        # Cache for validated words to reduce API calls
        self.word_cache = {}
        
        # Rate limiting parameters
        self.last_request_time = 0
        self.min_request_interval = 0.5  # Minimum time between requests in seconds

    def validate_word(self, word):
        """
        Check if a word is valid in the Scrabble dictionary.

        Args:
            word (str): The word to validate

        Returns:
            bool: True if the word is valid in Scrabble, False otherwise
        """
        # Convert to lowercase for consistency
        word = word.lower().strip()
        
        # Check cache first to avoid unnecessary API calls
        if word in self.word_cache:
            return self.word_cache[word]
        
        # If no API key is set, fall back to local validation
        if not self.api_key:
            print("Warning: Scrabble API key not found. Please set SCRABBLE_API_KEY environment variable.")
            return self._fallback_validation(word)
        
        try:
            # Implement rate limiting
            self._respect_rate_limit()
            
            # Make the API request
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params={"word": word}
            )
            
            # Update last request time
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                # Parse the response
                result = response.json()
                is_valid = result.get("isValid", False)
                
                # Cache the result
                self.word_cache[word] = is_valid
                
                return is_valid
            else:
                print(f"API Error: Status code {response.status_code}")
                # Fall back to local validation if API fails
                return self._fallback_validation(word)
                
        except Exception as e:
            print(f"Error validating word through Scrabble API: {str(e)}")
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