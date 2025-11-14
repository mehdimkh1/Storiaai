"""Continuity helpers for StoriaAI."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from ..models import Child, Story, StoryState


def get_previous_story_summary(db: Session, child_id: str) -> Optional[str]:
    """Return the summary of the most recent story for a child."""

    story = (
        db.query(Story)
        .filter(Story.child_id == child_id)
        .order_by(Story.created_at.desc())
        .join(StoryState, isouter=True)
        .first()
    )
    if story and story.state and story.state.summary:
        return story.state.summary
    return None


def upsert_child(
    db: Session,
    user_id: str,
    alias_hash: str,
    language: str,
    age: int,
    interests: list[str],
    controls: dict,
) -> Child:
    """Create or update a child profile."""

    child = (
        db.query(Child)
        .filter(Child.user_id == user_id, Child.alias_hash == alias_hash)
        .first()
    )
    if child is None:
        child = Child(
            user_id=user_id,
            alias_hash=alias_hash,
            language=language,
            age=age,
            interests=interests,
            controls=controls,
        )
        db.add(child)
    else:
        child.language = language
        child.age = age
        child.interests = interests
        child.controls = controls
    return child
