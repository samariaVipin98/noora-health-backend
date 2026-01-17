from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class Character(BaseModel):
    id: int
    name: str
    species: str
    status: str


class GenerateRequest(BaseModel):
    character: Character


class SearchRequest(BaseModel):
    query: str

class AgentPayload(BaseModel):
    status: Optional[str] = None
    species: Optional[str] = None
    episode_code: Optional[str] = None
    location_name: Optional[str] = None


class SaveNoteRequest(BaseModel):
    character_id: str
    note: str


class DeleteNoteRequest(BaseModel):
    note_id: str


class NoteResponse(BaseModel):
    id: str = Field(alias="_id")
    character_id: str
    note: str
    created_at: datetime
    model_config = ConfigDict(populate_by_name=True)