from flask_login import UserMixin
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "flowtrace.db")
)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class User(UserMixin):
    def __init__(self, id, name, email, username):
        self.id = str(id)
        self.name = name
        self.email = email
        self.username = username

    @staticmethod
    def get(user_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, name, email, username FROM users WHERE id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return User(id=row[0], name=row[1], email=row[2], username=row[3])
        return None

    @staticmethod
    def find_by_username(username):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, name, email, username, password_hash FROM users WHERE username = ?', (username,))
        row = c.fetchone()
        conn.close()
        if row:
            user = User(id=row[0], name=row[1], email=row[2], username=row[3])
            user.password_hash = row[4]
            return user
        return None

    @staticmethod
    def create(name, email, username, password):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        password_hash = generate_password_hash(password)
        try:
            c.execute('INSERT INTO users (name, email, username, password_hash) VALUES (?, ?, ?, ?)',
                      (name, email, username, password_hash))
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            success = False
        conn.close()
        return success

    @staticmethod
    def update(user_id, name, email, new_password_hash=None):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            if new_password_hash:
                c.execute('UPDATE users SET name=?, email=?, password_hash=? WHERE id=?', (name, email, new_password_hash, user_id))
            else:
                c.execute('UPDATE users SET name=?, email=? WHERE id=?', (name, email, user_id))
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            success = False
        conn.close()
        return success

    def check_password(self, password):
        return check_password_hash(getattr(self, 'password_hash', ''), password)
