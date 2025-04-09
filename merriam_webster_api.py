"""
Merriam-Webster Dictionary API for Word Mosaic game
Provides functions to fetch word definitions and validate words using the Merriam-Webster API
"""

import requests
import json
from urllib.parse import quote_plus
import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define constants for dictionary types
COLLEGIATE = "collegiate"
LEARNERS = "learners"

# Export constants for external use
__all__ = ["COLLEGIATE", "LEARNERS", "MerriamWebsterAPI", "merriam_webster"]

# Dictionary of cached validation results to avoid repeated API calls
cached_validations = {}

class MerriamWebsterAPI:
    """
    Class to handle interactions with the Merriam-Webster Dictionary API
    """
    def __init__(self, api_key=None, dictionary_type=None):
        """
        Initialize the Merriam-Webster API client
        
        Args:
            api_key (str): The API key for Merriam-Webster Dictionary API
            dictionary_type (str): The dictionary to use (collegiate or learners)
        """
        # Use provided dictionary type or get from environment
        self.dictionary_type = dictionary_type or os.environ.get('DEFAULT_DICTIONARY', 'COLLEGIATE')
        
        # Convert dictionary type to lowercase for API URL
        dict_type_lower = self.dictionary_type.lower()
        if dict_type_lower == 'collegiate':
            # Use Collegiate dictionary API key
            self.api_key = api_key or os.environ.get('MERRIAM_WEBSTER_COLLEGIATE_API_KEY')
            self.dictionary_url_part = "collegiate"
        elif dict_type_lower == 'learners':
            # Use Learner's dictionary API key
            self.api_key = api_key or os.environ.get('MERRIAM_WEBSTER_LEARNERS_API_KEY')
            self.dictionary_url_part = "learners"
        else:
            # Default to Collegiate
            self.api_key = api_key or os.environ.get('MERRIAM_WEBSTER_COLLEGIATE_API_KEY')
            self.dictionary_url_part = "collegiate"
        
        if not self.api_key:
            print(f"Warning: No Merriam-Webster API key provided for {self.dictionary_type} dictionary.")
            print(f"Set MERRIAM_WEBSTER_{self.dictionary_type}_API_KEY environment variable.")
        
        self.base_url = f"https://www.dictionaryapi.com/api/v3/references/{self.dictionary_url_part}/json/"
        
        # Initialize the definitions database
        self.create_definitions_database()

    def create_definitions_database(self):
        """
        Create a SQLite database to store word definitions from Merriam-Webster
        """
        db_path = os.path.join(os.path.dirname(__file__), "definitions.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create the definitions table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS merriam_webster_definitions (
                word TEXT PRIMARY KEY,
                definition TEXT,
                is_valid BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def is_valid_word(self, word):
        """
        Check if a word exists in the Merriam-Webster dictionary and is not an abbreviation
        
        Args:
            word (str): The word to validate
            
        Returns:
            bool: True if the word is valid and not an abbreviation, False otherwise
        """
        # Convert to lowercase for consistency
        word = word.lower().strip()
        
        print(f"[DEBUG MW API] Checking if '{word}' is valid")
        
        # Return from cache if available
        if word in cached_validations:
            print(f"[DEBUG MW API] Found '{word}' in cache: {cached_validations[word]}")
            return cached_validations[word]
        
        # First, try the local SQLite database for cached validation
        is_valid = self._get_cached_validation(word)
        if is_valid is not None:
            print(f"[DEBUG MW API] Found '{word}' in local DB cache: {is_valid}")
            cached_validations[word] = is_valid
            return is_valid
        
        # If not in local cache, try Merriam-Webster API
        if not self.api_key:
            # No API key available, return None to indicate fallback needed
            print(f"[DEBUG MW API] No API key for '{word}', returning None")
            return None
            
        try:
            url = f"{self.base_url}{quote_plus(word)}?key={self.api_key}"
            print(f"[DEBUG MW API] Requesting URL for '{word}': {url}")
            response = requests.get(url, timeout=5)
            
            print(f"[DEBUG MW API] Response status for '{word}': {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"[DEBUG MW API] Response data type: {type(data)}, length: {len(data) if isinstance(data, list) else 'N/A'}")
                
                # Check if we got a valid dictionary entry (not just suggestions)
                has_valid_definition = False
                all_entries_are_abbreviations = True
                
                if data and isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict) and 'meta' in entry:
                            print(f"[DEBUG MW API] Found dictionary entry with meta for '{word}'")
                            # Check if this entry is an abbreviation
                            functional_label = entry.get('fl', '').lower()
                            
                            print(f"[DEBUG MW API] Functional label for '{word}': {functional_label}")
                            
                            # Check if this is a valid non-abbreviation definition
                            is_abbreviation_entry = ('abbr' in functional_label or 
                                'abbreviation' in functional_label or
                                'acronym' in functional_label)
                            
                            # If we find at least one non-abbreviation entry, set flag
                            if not is_abbreviation_entry:
                                all_entries_are_abbreviations = False
                                
                                # Also check definitions for abbreviation indicators
                                if 'def' in entry:
                                    definition_text = json.dumps(entry['def']).lower()
                                    print(f"[DEBUG MW API] Definition contains abbreviation indicators? {'yes' if ('abbreviation' in definition_text or 'abbr.' in definition_text or 'acronym' in definition_text) else 'no'}")
                                    if ('abbreviation' in definition_text or
                                        'abbr.' in definition_text or
                                        'acronym' in definition_text):
                                        # Skip this definition if it mentions abbreviation
                                        continue
                                
                                # Mark as valid if we found a non-abbreviation definition
                                has_valid_definition = True
                                print(f"[DEBUG MW API] Found valid non-abbreviation definition for '{word}'")
                        
                    # If no dictionary entries found, it's not a valid word
                    if not has_valid_definition:
                        print(f"[DEBUG MW API] No valid definitions found for '{word}'")
                        is_valid = False
                    elif all_entries_are_abbreviations:
                        # If all entries are abbreviations, mark as invalid
                        print(f"[DEBUG MW API] '{word}' only has abbreviation definitions")
                        is_valid = False
                    else:
                        # Word has at least one valid non-abbreviation definition
                        print(f"[DEBUG MW API] '{word}' has valid non-abbreviation definitions")
                        is_valid = True
                else:
                    print(f"[DEBUG MW API] Received suggestions or empty response for '{word}'")
                    is_valid = False
                
                print(f"[DEBUG MW API] Final validation result for '{word}': {is_valid}")
                
                # Cache the validation result
                self._cache_validation(word, is_valid)
                cached_validations[word] = is_valid
                return is_valid
            
            # API call failed
            print(f"[DEBUG MW API] API call failed for '{word}' with status code {response.status_code}")
            return None
            
        except Exception as e:
            # Handle any errors (timeout, connection issues, etc.)
            print(f"[DEBUG MW API] Error for '{word}': {str(e)}")
            return None

    def fetch_definition(self, word):
        """
        Fetch definition for a word from Merriam-Webster dictionary
        
        Args:
            word (str): The word to look up
            
        Returns:
            str: The definition of the word, or None if not found or API fails
        """
        # Convert to lowercase for consistency
        word = word.lower().strip()
        
        # First, check if we have a cached definition
        definition = self._get_cached_definition(word)
        if definition:
            return definition
            
        # If not in cache and no API key, return None
        if not self.api_key:
            return None
            
        try:
            url = f"{self.base_url}{quote_plus(word)}?key={self.api_key}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process the dictionary data
                if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and 'shortdef' in data[0]:
                    # Get the first definition
                    definitions = data[0]['shortdef']
                    if definitions:
                        # Join multiple definitions
                        definition = "; ".join(definitions)
                        
                        # Get part of speech if available
                        part_of_speech = data[0].get('fl', '')
                        formatted_def = f"{part_of_speech}: {definition}" if part_of_speech else definition
                        
                        # Cache the definition locally
                        self._cache_definition(word, formatted_def)
                        return formatted_def
            
            # API failed or no definition found
            return None
            
        except Exception as e:
            # Handle any errors
            print(f"Merriam-Webster API error for definition of '{word}': {str(e)}")
            return None

    def _get_cached_validation(self, word):
        """
        Get cached validation result from SQLite database
        
        Args:
            word (str): The word to check
            
        Returns:
            bool or None: True if valid, False if invalid, None if not cached
        """
        try:
            db_path = os.path.join(os.path.dirname(__file__), "definitions.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT is_valid FROM merriam_webster_definitions WHERE word = ?", (word,))
            result = cursor.fetchone()
            conn.close()
            
            if result is not None:
                return bool(result[0])
            return None
        except Exception:
            return None

    def _get_cached_definition(self, word):
        """
        Get cached definition from SQLite database
        
        Args:
            word (str): The word to look up
            
        Returns:
            str or None: Definition if found, None otherwise
        """
        try:
            db_path = os.path.join(os.path.dirname(__file__), "definitions.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT definition FROM merriam_webster_definitions WHERE word = ?", (word,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return result[0]
            return None
        except Exception:
            return None

    def _cache_validation(self, word, is_valid):
        """
        Cache validation result in SQLite database
        
        Args:
            word (str): The word to cache
            is_valid (bool): Whether the word is valid
        """
        try:
            db_path = os.path.join(os.path.dirname(__file__), "definitions.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Insert or replace the validation result
            cursor.execute("""
                INSERT OR REPLACE INTO merriam_webster_definitions (word, is_valid)
                VALUES (?, ?)
            """, (word, is_valid))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error caching validation: {e}")

    def _cache_definition(self, word, definition):
        """
        Cache definition in SQLite database
        
        Args:
            word (str): The word to cache
            definition (str): The definition to cache
        """
        try:
            db_path = os.path.join(os.path.dirname(__file__), "definitions.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Insert or replace the definition
            cursor.execute("""
                INSERT OR REPLACE INTO merriam_webster_definitions (word, definition, is_valid)
                VALUES (?, ?, 1)
            """, (word, definition))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error caching definition: {e}")

    def get_dictionary_info(self):
        """
        Get information about the current dictionary
        
        Returns:
            dict: Dictionary information including name, API availability, and dictionary type
        """
        # Set the dictionary display name based on type
        if self.dictionary_url_part == "collegiate":
            name = "Merriam-Webster's Collegiate® Dictionary"
        elif self.dictionary_url_part == "learners":
            name = "Merriam-Webster's Learner's Dictionary"
        else:
            name = f"Merriam-Webster {self.dictionary_url_part.capitalize()}"
            
        # Build the information dictionary
        info = {
            'name': name,
            'type': self.dictionary_type,
            'api_available': bool(self.api_key),
            'url_part': self.dictionary_url_part
        }
            
        return info

# Create a global instance with default settings
merriam_webster = MerriamWebsterAPI()