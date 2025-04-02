import sqlite3

def create_database(txt_file, db_file):
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
    with open(txt_file, "r") as file:
        words = [line.strip().lower() for line in file if line.strip()]
        cursor.executemany("INSERT OR IGNORE INTO dictionary (word) VALUES (?)", [(word,) for word in words])

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Usage
create_database("dictionary.txt", "dictionary.db")

