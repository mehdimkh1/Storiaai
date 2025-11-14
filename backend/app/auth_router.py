"""
API Router for handling user authentication, including registration and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import auth, schemas, database
from .services import quota

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=schemas.Parent)
def register_parent(parent_create: schemas.ParentCreate, db: Session = Depends(database.get_db)):
    """
    Handles new parent registration.
    Hashes the password and creates a new Parent record.
    """
    db_parent = quota.get_parent_by_email(db, email=parent_create.email)
    if db_parent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    hashed_password = auth.get_password_hash(parent_create.password)
    return quota.create_parent(db=db, email=parent_create.email, hashed_password=hashed_password)


@router.post("/login", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """
    Handles parent login.
    Verifies credentials and returns a JWT access token.
    """
    parent = quota.get_parent_by_email(db, email=form_data.username)
    if not parent or not auth.verify_password(form_data.password, parent.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": str(parent.id)}
    )
    return {"access_token": access_token, "token_type": "bearer"}
