import sqlite3
import urllib.request
import os

def download_word_list(url="https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt", 
                       output_file="dictionary.txt"):
    """
    Download a word list from a URL if it doesn't exist locally.
    
    Args:
        url (str): URL to download the word list from
        output_file (str): Local file to save the word list to
    """
    if not os.path.exists(output_file):
        print(f"Downloading word list from {url}...")
        try:
            urllib.request.urlretrieve(url, output_file)
            print(f"Word list downloaded to {output_file}")
        except Exception as e:
            print(f"Error downloading word list: {e}")
            return False
    else:
        print(f"Using existing word list at {output_file}")
    return True

def create_database(txt_file="dictionary.txt", db_file="dictionary.db"):
    """
    Create an SQLite database from a text file containing a list of words.
    
    Args:
        txt_file (str): Path to the text file containing words
        db_file (str): Path to the SQLite database file to create
    """
    # First ensure we have a word list
    if not os.path.exists(txt_file):
        success = download_word_list(output_file=txt_file)
        if not success:
            print("Failed to obtain word list. Cannot create dictionary database.")
            return

    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create the dictionary table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dictionary (
            word TEXT PRIMARY KEY
        )
    """)

    # Read words from the text file and insert them into the database
    word_count = 0
    with open(txt_file, "r", encoding="utf-8") as file:
        words = []
        batch_size = 1000  # Process in batches for efficiency
        
        for line in file:
            word = line.strip().lower()
            if word and len(word) >= 2 and word.isalpha():  # Only add words with 2+ letters
                words.append((word,))
                word_count += 1
                
                if len(words) >= batch_size:
                    cursor.executemany("INSERT OR IGNORE INTO dictionary (word) VALUES (?)", words)
                    words = []
        
        # Insert any remaining words
        if words:
            cursor.executemany("INSERT OR IGNORE INTO dictionary (word) VALUES (?)", words)

    # Commit changes and close the connection
    conn.commit()
    
    # Verify the word count
    cursor.execute("SELECT COUNT(*) FROM dictionary")
    db_word_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"Dictionary database created with {db_word_count} words")
    return db_word_count

def add_definition_column():
    """
    Add a 'definition' column to the dictionary table if it doesn't exist.
    """
    conn = sqlite3.connect("dictionary.db")
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE dictionary ADD COLUMN definition TEXT")
        conn.commit()
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("[DEBUG] 'definition' column already exists.")
        else:
            raise
    finally:
        conn.close()

def create_definitions_db(db_file="definitions.db"):
    """
    Create the definitions database if it doesn't exist.

    Args:
        db_file (str): Path to the SQLite database file to create.
    """
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create the definitions table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS definitions (
            word TEXT PRIMARY KEY,
            definition TEXT,
            part_of_speech TEXT,
            is_valid BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()

# Run if this file is executed directly
if __name__ == "__main__":
    # Ensure the 'definition' column exists
    add_definition_column()
    create_database()
    # Ensure the definitions database exists
    create_definitions_db()

