"""
Dictionary API for Word Mosaic game
Provides functions to fetch word definitions from external dictionary APIs
"""

import requests
import json
from urllib.parse import quote_plus
import sqlite3
import os

# Dictionary of cached definitions to avoid repeated API calls
cached_definitions = {}

def fetch_definition(word):
    """
    Fetch definition for a word from a dictionary API or local cache
    
    Args:
        word (str): The word to look up
        
    Returns:
        str: The definition of the word, or a message if not found
    """
    # Convert to lowercase for consistency
    word = word.lower().strip()
    
    # Return from cache if available
    if word in cached_definitions:
        return cached_definitions[word]
    
    # First, try the local SQLite database for a cached definition
    definition = get_local_definition(word)
    if definition:
        cached_definitions[word] = definition
        return definition
    
    # If not in local cache, try Free Dictionary API
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote_plus(word)}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and isinstance(data, list) and len(data) > 0:
                meanings = data[0].get('meanings', [])
                
                if meanings:
                    # Get the first definition
                    definition_text = meanings[0].get('definitions', [{}])[0].get('definition', '')
                    part_of_speech = meanings[0].get('partOfSpeech', '')
                    
                    # Format the definition
                    definition = f"{part_of_speech}: {definition_text}" if part_of_speech else definition_text
                    
                    # Cache the definition locally
                    cache_definition(word, definition)
                    cached_definitions[word] = definition
                    return definition
        
        # If API fails or no definition found, provide a default message
        default_message = f"No definition available for '{word}'"
        cached_definitions[word] = default_message
        return default_message
        
    except Exception as e:
        # Handle any errors (timeout, connection issues, etc.)
        return f"Could not retrieve definition for '{word}': {str(e)}"

def format_definitions(words):
    """
    Format definitions for multiple words into a readable string
    
    Args:
        words (list): List of words to define
        
    Returns:
        str: Formatted string with word definitions
    """
    if not words:
        return "No words to define."
    
    formatted_text = ""
    for word in words:
        definition = fetch_definition(word)
        formatted_text += f"<b>{word.upper()}</b>: {definition}<br><br>"
    
    return formatted_text

def create_definitions_database():
    """
    Create a SQLite database to store word definitions
    """
    db_path = os.path.join(os.path.dirname(__file__), "definitions.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the definitions table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS definitions (
            word TEXT PRIMARY KEY,
            definition TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_local_definition(word):
    """
    Get a definition from the local SQLite database
    
    Args:
        word (str): The word to look up
        
    Returns:
        str: The definition if found, None otherwise
    """
    try:
        db_path = os.path.join(os.path.dirname(__file__), "definitions.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT definition FROM definitions WHERE word = ?", (word,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0]
        return None
    except Exception:
        return None

def cache_definition(word, definition):
    """
    Cache a definition in the local SQLite database
    
    Args:
        word (str): The word to cache
        definition (str): The definition to cache
    """
    try:
        db_path = os.path.join(os.path.dirname(__file__), "definitions.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create the table if it doesn't exist
        create_definitions_database()
        
        # Insert or replace the definition
        cursor.execute("""
            INSERT OR REPLACE INTO definitions (word, definition)
            VALUES (?, ?)
        """, (word, definition))
        
        conn.commit()
        conn.close()
    except Exception:
        pass  # Silently fail if we can't cache the definition

# Initialize the definitions database
create_definitions_database()