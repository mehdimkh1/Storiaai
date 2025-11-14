"""Authentication utilities and endpoints."""
from __future__ import annotations

import datetime as dt
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import User

SETTINGS = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = APIRouter()


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[dt.timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = dt.datetime.now(dt.timezone.utc) + expires_delta
    else:
        expire = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SETTINGS.jwt_secret_key, algorithm=SETTINGS.jwt_algorithm)
    return encoded_jwt


def get_user(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    user = get_user(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: Session = Depends(get_db),
) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SETTINGS.jwt_secret_key, algorithms=[SETTINGS.jwt_algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


@security.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)) -> Token:
    """Register a new user."""
    db_user = get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=dt.timedelta(hours=SETTINGS.jwt_expiration_hours)
    )
    return Token(access_token=access_token, token_type="bearer")


@security.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)) -> Token:
    """Login a user."""
    db_user = authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=dt.timedelta(hours=SETTINGS.jwt_expiration_hours)
    )
    return Token(access_token=access_token, token_type="bearer")
