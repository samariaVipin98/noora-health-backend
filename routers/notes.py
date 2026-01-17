import sqlite3
from typing import List
from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, HTTPException
from config.db import get_db_connection
from models.models import DeleteNoteRequest, NoteResponse, SaveNoteRequest


router = APIRouter(prefix="/note", tags=["note"])


@router.post("/save", response_model=NoteResponse)
async def save_note(payload: SaveNoteRequest):
    note_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO notes (_id, character_id, note, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (note_id, payload.character_id, payload.note, created_at),
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"DB Insert Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save note")

    return NoteResponse(
        id=note_id,
        character_id=payload.character_id,
        note=payload.note,
        created_at=datetime.fromisoformat(created_at),
    )

@router.get("", response_model=List[NoteResponse])
async def get_note(character_id: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT _id, character_id, note, created_at
            FROM notes
            WHERE character_id = ?
            ORDER BY created_at ASC
            """,
            (character_id,),
        )
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"DB Select Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch notes")

    notes: List[NoteResponse] = []
    for _id, char_id, note, created_at in rows:
        try:
            created_dt = datetime.fromisoformat(created_at)
        except ValueError:
            created_dt = datetime.now(timezone.utc)
        notes.append(
            NoteResponse(
                id=_id,
                character_id=char_id,
                note=note,
                created_at=created_dt,
            )
        )

    return notes

@router.post("/delete")
async def delete_note(payload: DeleteNoteRequest):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM notes
            WHERE _id = ?
            """,
            (payload.note_id,),
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Note not found")
    except sqlite3.Error as e:
        print(f"DB Delete Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete note")

    return {"deleted": True}