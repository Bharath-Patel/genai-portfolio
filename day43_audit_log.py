import sqlite3
from datetime import datetime

DB_FILE = "audit_log.db"

def init_db():
    """ creates the table audit_log , it it doesn't exist. """
    conn = sqlite3.connect(DB_FILE) #opens (or creates, if it doesn't exist yet) a database file on disk named audit_log.db, and gives you back a connection object
    cursor = conn.cursor() #cursor is the actual tool you use to run commands against the database, once connected.
    cursor.execute( #runs a raw SQL command
        """ 
        CREATE TABLE IF NOT EXISTS audit_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user_role TEXT NOT NULL,
        question TEXT NOT NULL,
        status TEXT NOT NULL,
        sources_used TEXT,
        answer TEXT )
        """
    )
    conn.commit() #finalizes and saves whatever changes you just made
    conn.close() #Closes the connection

def log_query(user_role: str, question:str, status:str, sources_used: str, answer:str):
    """Appends one new audit record - never modifies or deletes existing rows."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO audit_log(timestamp,user_role,question,status,sources_used,answer)
        VALUES (?,?,?,?,?,?)
    """,(
        datetime.now().isoformat(),
        user_role,
        question,
        status,
        ','.join(sources_used), #sources_used column is defined as TEXT
        answer
    ))
    conn.commit()
    conn.close()

def get_all_logs():
    """"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(""" SELECT * FROM audit_log ORDER BY timestamp DESC """)
    rows = cursor.fetchall() #pulls results from select query back into Python as a list of tuples, one tuple per row.
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    for row in get_all_logs():
        print(row)
    print("Audit log database ready.")