# app/api/routes/notes.py

"""
Notes API Routes
Endpoints for managing occupation notes.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status

from app.core.deps import Neo4jDep
from app.api.repos.notes import NotesRepo
from app.api.services.notes import NotesService
from app.api.schemas.notes import (
    NoteCreate,
    NoteResponse,
    NoteSearchResponse,
    NoteDeleteResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notes", tags=["Notes"])


def get_notes_service(neo4j_client: Neo4jDep) -> NotesService:
    """
    Dependency injection for notes service.
    
    Args:
        neo4j_client: Neo4j client instance (injected)
    
    Returns:
        NotesService instance
    """
    notes_repo = NotesRepo(neo4j_client)
    return NotesService(notes_repo)


@router.get(
    "",
    response_model=NoteSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search notes",
    description="""
    Search and filter occupation notes with pagination support.
    
    **Query Parameters:**
    - `occupation_uri`: Optional filter by occupation URI (URL-encoded)
    - `limit`: Maximum number of results (1-1000, default: 100)
    - `skip`: Number of results to skip for pagination (default: 0)
    
    **Returns:**
    - List of notes with total count
    - Notes ordered by most recently updated first
    """
)
async def search_notes(
    occupation_uri: Optional[str] = Query(None, description="Filter by occupation URI"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    service: NotesService = Depends(get_notes_service)
) -> NoteSearchResponse:
    """
    Search notes with optional filtering.
    
    Args:
        occupation_uri: Optional occupation URI to filter by
        limit: Maximum number of results
        skip: Pagination offset
        service: Notes service (injected)
    
    Returns:
        Search results with total count and notes list
    
    Raises:
        HTTPException 500: If search fails
    """
    try:
        return service.search_notes(
            occupation_uri=occupation_uri,
            limit=limit,
            skip=skip
        )
    except Exception as e:
        logger.error(f"Failed to search notes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search notes: {str(e)}"
        )


@router.put(
    "/admin/occupations/{occupation_uri:path}/notes/{note_id}",
    response_model=NoteResponse,
    status_code=status.HTTP_200_OK,
    summary="Create or update note",
    description="""
    Create a new note or update existing one (upsert operation).
    
    **Path Parameters:**
    - `occupation_uri`: Full occupation URI (URL-encoded)
    - `note_id`: Unique note identifier
    
    **Request Body:**
    - `text`: Note content (1-5000 characters)
    
    **Behavior:**
    - Creates new note if it doesn't exist
    - Updates existing note if it already exists
    - Returns 404 if occupation doesn't exist
    """
)
async def upsert_note(
    occupation_uri: str = Path(..., description="Occupation URI (URL-encoded)"),
    note_id: str = Path(..., description="Note identifier"),
    note_data: NoteCreate = ...,
    service: NotesService = Depends(get_notes_service)
) -> NoteResponse:
    """
    Create or update a note for an occupation.
    
    Args:
        occupation_uri: Occupation URI
        note_id: Note identifier
        note_data: Note content
        service: Notes service (injected)
    
    Returns:
        Created or updated note
    
    Raises:
        HTTPException 404: If occupation not found
        HTTPException 400: If validation fails
        HTTPException 500: If operation fails
    """
    return service.create_or_update_note(
        occupation_uri=occupation_uri,
        note_id=note_id,
        note_data=note_data
    )





@router.delete(
    "/admin/occupations/{occupation_uri:path}/notes/{note_id}",
    response_model=NoteDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete note",
    description="""
    Delete a note from an occupation.
    
    **Path Parameters:**
    - `occupation_uri`: Full occupation URI (URL-encoded)
    - `note_id`: Unique note identifier
    
    **Behavior:**
    - Deletes the HAS_NOTE relationship
    - If no other occupations reference the note, deletes the Note node as well
    - Returns 404 if note or relationship doesn't exist
    """
)
async def delete_note(
    occupation_uri: str = Path(..., description="Occupation URI (URL-encoded)"),
    note_id: str = Path(..., description="Note identifier"),
    service: NotesService = Depends(get_notes_service)
) -> NoteDeleteResponse:
    """
    Delete a note from an occupation.
    
    Args:
        occupation_uri: Occupation URI
        note_id: Note identifier
        service: Notes service (injected)
    
    Returns:
        Deletion confirmation message
    
    Raises:
        HTTPException 404: If note not found
        HTTPException 500: If deletion fails
    """
    return service.delete_note(
        occupation_uri=occupation_uri,
        note_id=note_id
    )
