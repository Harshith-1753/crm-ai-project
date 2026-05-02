import sqlite3

DB_NAME = "crm.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor TEXT,
        date TEXT,
        type TEXT,
        notes TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_interaction(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO interactions (doctor, date, type, notes)
    VALUES (?, ?, ?, ?)
    """, (
        data.get("doctor"),
        data.get("date"),
        data.get("type"),
        data.get("notes")
    ))

    conn.commit()
    conn.close()


def get_last_interaction():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT doctor, date, type, notes
    FROM interactions
    ORDER BY id DESC LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "doctor": row[0],
            "date": row[1],
            "type": row[2],
            "notes": row[3]
        }

    return {}