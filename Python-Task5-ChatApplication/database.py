import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

ROOT = Path(__file__).resolve().parent
DB_DIR = ROOT / "database"
DB_PATH = DB_DIR / "relaychat.db"

def connect():
    DB_DIR.mkdir(exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS room_members (
            user_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            joined_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(user_id, room_id),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_messages_room_id ON messages(room_id, id);
        """)
        db.executemany("INSERT OR IGNORE INTO rooms(name, description) VALUES (?, ?)", [
            ("general", "A place for everyday conversations"),
            ("technology", "Coding, tools and new ideas"),
            ("random", "Anything that does not fit elsewhere")
        ])

def username_exists(username):
    with connect() as db:
        return db.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone() is not None

def create_user(username, password):
    try:
        with connect() as db:
            cur = db.execute("INSERT INTO users(username, password_hash) VALUES (?, ?)",
                             (username, generate_password_hash(password)))
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None

def authenticate_user(username, password):
    with connect() as db:
        user = db.execute("SELECT id, username, password_hash FROM users WHERE username=?", (username,)).fetchone()
    if user and check_password_hash(user["password_hash"], password):
        return {"id": user["id"], "username": user["username"]}
    return None

def add_user_to_default_rooms(user_id):
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO room_members(user_id, room_id) SELECT ?, id FROM rooms", (user_id,))

def get_rooms():
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT id, name, description FROM rooms ORDER BY id").fetchall()]

def get_user_room_ids(user_id):
    with connect() as db:
        rows = db.execute("SELECT room_id FROM room_members WHERE user_id=?", (user_id,)).fetchall()
    return {row["room_id"] for row in rows}

def get_messages(room_id, limit=100):
    with connect() as db:
        rows = db.execute("""
            SELECT m.id, m.content, m.sent_at, u.username
            FROM messages m JOIN users u ON u.id=m.user_id
            WHERE m.room_id=? ORDER BY m.id DESC LIMIT ?
        """, (room_id, limit)).fetchall()
    return [dict(row) for row in reversed(rows)]

def save_message(user_id, room_id, content):
    with connect() as db:
        cur = db.execute("INSERT INTO messages(user_id, room_id, content) VALUES (?, ?, ?)",
                         (user_id, room_id, content))
        row = db.execute("""
            SELECT m.id, m.content, m.sent_at, u.username
            FROM messages m JOIN users u ON u.id=m.user_id WHERE m.id=?
        """, (cur.lastrowid,)).fetchone()
    return dict(row)
