# auth.py
import sqlite3
import bcrypt
from flask import session
from database import get_db_connection

# Register a new user
def register_user(username, email, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                    (username, email, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Email or username already taken
    finally:
        conn.close()

# Log in an existing user
def login_user(email, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()

    if row and bcrypt.checkpw(password.encode('utf-8'), row[1]):
        session['user_id'] = row[0]
        return True
    return False

# Log the user out
def logout_user():
    session.pop('user_id', None)

# Check if the user is logged in
def is_logged_in():
    return 'user_id' in session

# Get the ID of the currently logged-in user
def get_current_user():
    return session.get('user_id')

# Get the email of the current user
def get_user_email(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None
