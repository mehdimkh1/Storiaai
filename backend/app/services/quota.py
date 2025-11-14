"""Quota management for freemium usage."""
from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Parent, StoryQuota
from .crypto import hash_email

SETTINGS = get_settings()


def get_or_create_parent(db: Session, email: str) -> Parent:
    """Return parent record for hashed email, creating if needed."""

    email_hash = hash_email(email)
    parent = db.execute(select(Parent).where(Parent.email_hash == email_hash)).scalar_one_or_none()
    if parent is None:
        parent = Parent(email_hash=email_hash)
        db.add(parent)
        db.flush()
    return parent


def get_parent(db: Session, email: str) -> Parent | None:
    """Return parent if exists without creating a new record."""

    email_hash = hash_email(email)
    return db.execute(select(Parent).where(Parent.email_hash == email_hash)).scalar_one_or_none()


def check_and_increment_quota(db: Session, parent_id: str) -> bool:
    """Return True if quota allows another story; increments when allowed."""

    today = dt.date.today()
    quota = db.get(StoryQuota, {"parent_id": parent_id, "quota_date": today})
    if quota is None:
        quota = StoryQuota(parent_id=parent_id, quota_date=today, story_count=1)
        db.add(quota)
        return True

    if quota.story_count >= SETTINGS.max_free_stories_per_day:
        return False

    quota.story_count += 1
    return True
