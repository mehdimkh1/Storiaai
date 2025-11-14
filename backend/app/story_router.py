"""
API Router for handling story-related operations.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import auth, schemas, database, models
from .services import continuity

router = APIRouter(
    prefix="/stories",
    tags=["Stories"],
    dependencies=[Depends(auth.oauth2_scheme)] # All routes in this router require authentication
)

@router.get("/me", response_model=List[schemas.StoryResponse])
def get_my_stories(db: Session = Depends(database.get_db), token: str = Depends(auth.oauth2_scheme)):
    """
    Fetches all stories created by the currently authenticated parent.
    """
    token_data = auth.decode_access_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    stories = continuity.get_stories_by_parent(db, parent_id=token_data.parent_id)
    return stories
