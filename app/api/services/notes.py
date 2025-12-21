# app/api/services/notes.py

"""
Notes Service
Business logic for notes management.
"""

import logging
from typing import Optional

from fastapi import HTTPException, status

from app.api.repos.notes import NotesRepo
from app.api.schemas.notes import (
    NoteCreate,
    NoteResponse,
    NoteSearchResponse,
    NoteDeleteResponse
)

logger = logging.getLogger(__name__)


class NotesService:
    """Service for notes operations."""

    def __init__(self, notes_repo: NotesRepo):
        self.notes_repo = notes_repo

    def search_notes(
        self,
        occupation_uri: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> NoteSearchResponse:
        """
        Search notes with optional filtering.

        Args:
            occupation_uri: Optional occupation URI filter
            limit: Maximum results
            skip: Pagination offset

        Returns:
            Search results with notes
            
        Raises:
            HTTPException 500: If search fails
        """
        try:
            result = self.notes_repo.search_notes(
                occupation_uri=occupation_uri,
                limit=limit,
                skip=skip
            )
            
            notes = [NoteResponse(**note) for note in result["notes"]]
            
            logger.info(f"Found {result['total']} notes (returning {len(notes)})")
            
            return NoteSearchResponse(
                total=result["total"],
                notes=notes
            )
        except Exception as e:
            logger.error(f"Failed to search notes: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to search notes: {str(e)}"
            )

    def create_or_update_note(
        self,
        occupation_uri: str,
        note_id: str,
        note_data: NoteCreate
    ) -> NoteResponse:
        """
        Create or update a note.

        Args:
            occupation_uri: Occupation URI
            note_id: Note identifier
            note_data: Note content

        Returns:
            Created/updated note

        Raises:
            HTTPException 400: If validation fails
            HTTPException 404: If occupation not found
            HTTPException 500: If operation fails
        """
        # Validate text is not empty or whitespace only
        if not note_data.text or not note_data.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Note text cannot be empty or whitespace only"
            )
        
        try:
            result = self.notes_repo.upsert_note(
                occupation_uri=occupation_uri,
                note_id=note_id,
                text=note_data.text.strip()
            )
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Occupation not found: {occupation_uri}"
                )
            
            logger.info(f"Upserted note {note_id} for occupation {occupation_uri}")
            
            return NoteResponse(**result)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to upsert note: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create/update note: {str(e)}"
            )



    def delete_note(
        self,
        occupation_uri: str,
        note_id: str
    ) -> NoteDeleteResponse:
        """
        Delete a note.

        Args:
            occupation_uri: Occupation URI
            note_id: Note identifier

        Returns:
            Deletion confirmation

        Raises:
            HTTPException 404: If note not found
            HTTPException 500: If deletion fails
        """
        try:
            deleted = self.notes_repo.delete_note(
                occupation_uri=occupation_uri,
                note_id=note_id
            )
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Note not found: {note_id} for occupation {occupation_uri}"
                )
            
            logger.info(f"Deleted note {note_id} from occupation {occupation_uri}")
            
            return NoteDeleteResponse(
                message="Note deleted successfully",
                occupationUri=occupation_uri,
                noteId=note_id
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete note: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete note: {str(e)}"
            )
