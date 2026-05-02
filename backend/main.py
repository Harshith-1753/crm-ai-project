from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import agent_logic
from db import init_db
import sqlite3
from collections import Counter
import csv
from fastapi.responses import StreamingResponse
from io import StringIO

app = FastAPI()
init_db()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELS
# =========================
class Interaction(BaseModel):
    doctor: str
    date: str
    type: str
    notes: str


class ChatRequest(BaseModel):
    message: str


# =========================
# HOME
# =========================
@app.get("/")
def home():
    return {"message": "Backend is running successfully"}


# =========================
# CREATE
# =========================
@app.post("/log-interaction")
def log_interaction(data: Interaction):
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO interactions (doctor, date, type, notes)
        VALUES (?, ?, ?, ?)
    """, (data.doctor, data.date, data.type, data.notes))

    conn.commit()
    conn.close()

    return {"message": "Interaction saved successfully"}


# =========================
# UPDATE
# =========================
@app.put("/update/{id}")
def update_interaction(id: int, data: Interaction):
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE interactions
        SET doctor=?, date=?, type=?, notes=?
        WHERE id=?
    """, (data.doctor, data.date, data.type, data.notes, id))

    conn.commit()
    conn.close()

    return {"message": "Interaction updated successfully"}


# =========================
# DELETE
# =========================
@app.delete("/delete/{id}")
def delete_interaction(id: int):
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM interactions WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return {"message": "Deleted successfully"}


# =========================
# HISTORY
# =========================
@app.get("/history")
def get_history():
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, doctor, date, type, notes
        FROM interactions
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "doctor": r[1],
            "date": r[2],
            "type": r[3],
            "notes": r[4]
        }
        for r in rows
    ]


# =========================
# CHAT
# =========================
@app.post("/chat")
def chat(req: ChatRequest):
    response = agent_logic(req.message)

    if isinstance(response, dict):
        return {"type": "form", "data": response}

    return {"type": "text", "data": response}


# =========================
# DASHBOARD
# =========================
@app.get("/dashboard")
def get_dashboard():
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()

    cursor.execute("SELECT type FROM interactions")
    types = [row[0] for row in cursor.fetchall()]

    cursor.execute("""
        SELECT id, doctor, date, type, notes
        FROM interactions
        ORDER BY id DESC LIMIT 5
    """)
    recent_rows = cursor.fetchall()

    conn.close()

    return {
        "total": len(types),
        "by_type": dict(Counter(types)),
        "recent": [
            {
                "id": r[0],
                "doctor": r[1],
                "date": r[2],
                "type": r[3],
                "notes": r[4]
            }
            for r in recent_rows
        ]
    }


# =========================
# EXPORT CSV ✅ FIXED
# @app.get("/export")
def export_csv():
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["doctor","date","type","notes"])
    writer.writeheader()

    # 🔥 FETCH FROM DATABASE
    conn = sqlite3.connect("crm.db")
    cursor = conn.cursor()

    cursor.execute("SELECT doctor, date, type, notes FROM interactions")
    rows = cursor.fetchall()

    for r in rows:
        writer.writerow({
            "doctor": r[0],
            "date": r[1],
            "type": r[2],
            "notes": r[3]
        })

    conn.close()

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=interactions.csv"}
    )