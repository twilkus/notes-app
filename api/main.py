import os
import sqlite3
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Where the database lives. Locally this is ./data; in Docker we'll point it at a volume.
DATA_DIR = os.environ.get("DATA_DIR", "./data")
DB_PATH = os.path.join(DATA_DIR, "notes.db")
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


with get_db() as db:
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


class NoteIn(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/notes")
def list_notes():
    with get_db() as db:
        rows = db.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


@app.post("/api/notes", status_code=201)
def create_note(note: NoteIn):
    with get_db() as db:
        cur = db.execute("INSERT INTO notes (text) VALUES (?)", (note.text,))
        row = db.execute("SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)).fetchone()
        return dict(row)


@app.delete("/api/notes/{note_id}")
def delete_note(note_id: int):
    with get_db() as db:
        cur = db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"deleted": note_id}