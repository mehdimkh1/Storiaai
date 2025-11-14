"""Database models."""
from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from .database import Base


def _generate_uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    children = relationship("Child", back_populates="user", cascade="all, delete-orphan")


class Parent(Base):
    __tablename__ = "parents"

    id = Column(String, primary_key=True, default=_generate_uuid)
    email_hash = Column(String, unique=True, index=True, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    children = relationship("Child", back_populates="parent", cascade="all, delete-orphan")


class Child(Base):
    __tablename__ = "children"

    id = Column(String, primary_key=True, default=_generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    alias_hash = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    language = Column(String, default="it", nullable=False)
    interests = Column(JSON, default=list)
    controls = Column(JSON, default=dict)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    user = relationship("User", back_populates="children")
    stories = relationship("Story", back_populates="child", cascade="all, delete-orphan")


class Story(Base):
    __tablename__ = "stories"

    id = Column(String, primary_key=True, default=_generate_uuid)
    child_id = Column(String, ForeignKey("children.id"), nullable=False, index=True)
    language = Column(String, default="it", nullable=False)
    duration_minutes = Column(Integer, nullable=False, default=7)
    request_payload = Column(JSON, default=dict)
    story_json = Column(JSON, default=dict)
    audio_url = Column(String, nullable=True)
    moral_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)

    child = relationship("Child", back_populates="stories")
    state = relationship("StoryState", back_populates="story", uselist=False, cascade="all, delete-orphan")


class StoryState(Base):
    __tablename__ = "story_state"

    story_id = Column(String, ForeignKey("stories.id"), primary_key=True)
    summary = Column(Text, nullable=True)
    characters = Column(JSON, default=list)
    moral = Column(String, nullable=True)
    unresolved_threads = Column(JSON, default=list)
    sequel_hook = Column(Text, nullable=True)

    story = relationship("Story", back_populates="state", uselist=False)


class UsageMetric(Base):
    __tablename__ = "usage_metrics"

    id = Column(String, primary_key=True, default=_generate_uuid)
    parent_id = Column(String, ForeignKey("parents.id"), nullable=True)
    story_id = Column(String, ForeignKey("stories.id"), nullable=True)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, default=dict)
    created_at = Column(DateTime, default=_utcnow, nullable=False, index=True)


class StoryQuota(Base):
    __tablename__ = "story_quota"

    parent_id = Column(String, ForeignKey("parents.id"), primary_key=True)
    quota_date = Column(Date, primary_key=True)
    story_count = Column(Integer, default=0, nullable=False)


class ConsentLog(Base):
    __tablename__ = "consent_log"

    id = Column(String, primary_key=True, default=_generate_uuid)
    parent_id = Column(String, ForeignKey("parents.id"), nullable=False)
    consent_version = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
