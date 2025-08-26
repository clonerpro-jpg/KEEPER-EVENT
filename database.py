import sqlite3
from datetime import datetime

DB_PATH = "database.db"

def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER,
        guild_id INTEGER,
        coins INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0,
        reg_date TEXT,
        join_date TEXT,
        PRIMARY KEY (user_id, guild_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shop_items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        type TEXT,
        role_id INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS xp_channels (
        guild_id INTEGER,
        channel_id INTEGER,
        PRIMARY KEY (guild_id, channel_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS guilds (
        guild_id INTEGER PRIMARY KEY,
        xp_multiplier REAL DEFAULT 1
    )
    """)

    conn.commit()
    conn.close()


def register_user(user_id: int, guild_id: int, join_date: str):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM users WHERE user_id=? AND guild_id=?", (user_id, guild_id))
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO users (user_id, guild_id, coins, xp, reg_date, join_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            guild_id,
            100,  # стартовые монеты
            0,
            str(datetime.utcnow().date()),
            join_date
        ))
    conn.commit()
    conn.close()