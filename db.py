import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "app.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'admin')),
                bio TEXT DEFAULT ''
            );
            """
        )


def seed_default_admin(username: str, password_hash: str) -> bool:
    """Ensure a default admin account exists and has admin role.

    Returns True when a new admin account is inserted, otherwise False.
    """
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if not existing:
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
                (username, password_hash),
            )
            return True

        if existing["role"] != "admin":
            conn.execute(
                "UPDATE users SET role = 'admin' WHERE id = ?",
                (existing["id"],),
            )

    return False


def create_user(username: str, password_hash: str, role: str = "user") -> bool:
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_username(username: str):
    with get_connection() as conn:
        # return conn.execute(
        #     "SELECT id, username, password_hash, role, bio FROM users WHERE username = ?",
        #     (username,),
        # ).fetchone()
        query = f"SELECT id, username, password_hash, role, bio FROM users WHERE username = '{username}'"
        return conn.execute(query).fetchone()


def get_user_by_id(user_id: int):
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, username, role, bio FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()


def get_all_users():
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, username, role, bio FROM users ORDER BY id ASC"
        ).fetchall()


def update_bio(user_id: int, bio: str) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE users SET bio = ? WHERE id = ?", (bio, user_id))
