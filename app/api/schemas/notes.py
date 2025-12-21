# app/api/schemas/notes.py

"""
Notes Schemas
Pydantic models for notes API requests and responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    """Base note fields."""
    text: str = Field(
        ..., 
        min_length=1, 
        max_length=5000, 
        description="Note text content",
        examples=["This occupation requires strong communication skills"]
    )


class NoteCreate(NoteBase):
    """Schema for creating a new note."""
    pass





class NoteResponse(BaseModel):
    """Schema for note response."""
    occupation_uri: str = Field(
        ..., 
        alias="occupationUri",
        examples=["http://data.europa.eu/esco/occupation/114e1eff-215e-47df-8e10-45a5b72f8197"]
    )
    note_id: str = Field(
        ..., 
        alias="noteId",
        examples=["note-001"]
    )
    text: str = Field(
        examples=["This occupation requires strong communication skills"]
    )
    created_at: Optional[datetime] = Field(
        None, 
        alias="createdAt"
    )
    updated_at: Optional[datetime] = Field(
        None, 
        alias="updatedAt"
    )

    class Config:
        populate_by_name = True
        from_attributes = True


class NoteSearchResponse(BaseModel):
    """Schema for note search results."""
    total: int = Field(
        description="Total number of notes matching the search criteria",
        examples=[42]
    )
    notes: list[NoteResponse] = Field(
        description="List of notes"
    )


class NoteDeleteResponse(BaseModel):
    """Schema for note deletion response."""
    message: str = Field(
        examples=["Note deleted successfully"]
    )
    occupation_uri: str = Field(
        ..., 
        alias="occupationUri",
        examples=["http://data.europa.eu/esco/occupation/114e1eff-215e-47df-8e10-45a5b72f8197"]
    )
    note_id: str = Field(
        ..., 
        alias="noteId",
        examples=["note-001"]
    )

    class Config:
        populate_by_name = True
