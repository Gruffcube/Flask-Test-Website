import sqlite3 as sq
from pathlib import Path
import hashlib
from contextlib import contextmanager
from secrets import token_hex
import time
import os


@contextmanager
def get_db_connection():
    CURRENT_DIR = Path(__file__).resolve().parent.parent.parent
    
    DATABASE_FILE = CURRENT_DIR / 'instance' / 'user_database.db'
    
    print(f"Database file: {DATABASE_FILE}")
    
    os.makedirs(DATABASE_FILE.parent, exist_ok=True)
    
    conn = sq.connect(DATABASE_FILE)
    
    conn.row_factory = sq.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    
    try:
        yield conn 
    
    finally:
        conn.close()



def init_db():
    with get_db_connection() as conn:
        conn.executescript("""
        
            CREATE TABLE IF NOT EXISTS user_accounts (
            
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email_address TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            );
            
            
            CREATE TABLE IF NOT EXISTS user_access_tokens (
            
                token_id INTEGER PRIMARY KEY,
                user_id  INTEGER REFERENCES user_accounts(user_id) ON DELETE CASCADE,
                token_contents_hash TEXT NOT NULL,
                time_created INTEGER NOT NULL,
                time_used INTEGER NOT NULL
            );
            
        """)
        
        conn.commit()



def create_account(fname, lname, email, password):
    fname = fname.strip().lower()
    lname = lname.strip().lower()
    email = email.strip().lower()
    password = password.strip()
    
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    del password
    
    with get_db_connection() as conn:
        try:
            cursor = conn.execute("""
                INSERT INTO user_accounts (first_name, last_name, email_address, password_hash) VALUES (?,?,?,?)
            """, (fname, lname, email, password_hash))
            
            user_id = cursor.lastrowid
        
        except sq.IntegrityError:
            return ("Email is already in use", "error")
        
        
        else:
            conn.commit()
            return (user_id, 'success')



def create_user_access_token(user_id):
    token = token_hex(64)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    now = time.time()
        
    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO user_access_tokens (user_id, token_contents_hash, time_created, time_used) VALUES (?,?,?,?)
        """, (user_id, token_hash, now, now))
        
        conn.commit()
        
        return token



def verify_user_access_token(user_id, token):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    now = time.time()
    
    with get_db_connection() as conn:
        conn.execute("""
            DELETE FROM user_access_tokens WHERE
            time_used < ? OR
            time_created < ?;
            
        """, (now - INACTIVE_TOKEN_LIFESPAN, now - MAX_TOKEN_LIFESPAN))
        
        valid = bool(conn.execute("""
            SELECT EXISTS (SELECT 1 FROM user_access_tokens WHERE 
            user_id = ? AND 
            token_contents_hash = ?
            );
        
        """, (user_id, token_hash)).fetchone()[0])
        
        if valid:
            conn.execute("""
                UPDATE user_access_tokens 
                SET time_used = ?
                WHERE user_id = ? AND token_contents_hash = ?
            """, (now, user_id, token_hash))
            
        conn.commit()
    
    return valid
        


def try_log_in(email, password):
    email = email.strip().lower()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    with get_db_connection() as conn:
        fetched_account = conn.execute("""
            SELECT user_id FROM user_accounts WHERE
                email_address = ? AND 
                password_hash = ?;
        """, (email, password_hash)).fetchone()
        
        if fetched_account is not None:
            user_id = fetched_account['user_id']
            token = create_user_access_token(user_id)
            
            return ((user_id, token), 'success')
        
        else:
            return ('Email or password is incorrect', 'error')



def remove_access_token(user_id, token):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    with get_db_connection() as conn:
        conn.execute("""
            DELETE FROM user_access_tokens WHERE
            user_id = ? AND
            token_contents_hash = ?;
        """, (user_id, token_hash))
        
        conn.commit()



def get_first_last_name_from_user_id(user_id):
    with get_db_connection() as conn:
        fetched_data = conn.execute("""
            SELECT first_name, last_name FROM user_accounts WHERE
            user_id = ?
        """, (user_id,)).fetchone()
        
    if fetched_data is not None:
        return (fetched_data['first_name'], fetched_data['last_name'])
    
    else:
        return ("john", "doe")



init_db()


INACTIVE_TOKEN_LIFESPAN = 86400 * 2
MAX_TOKEN_LIFESPAN = 86400 * 30
