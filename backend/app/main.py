"""FastAPI application entrypoint for StoriaAI."""
from __future__ import annotations

import datetime as dt
import logging
from contextlib import asynccontextmanager
from typing import Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .auth import security
from .config import get_settings
from .database import get_db, init_db
from .models import ConsentLog, Story, StoryState, UsageMetric, ChildMemory
from .schemas import (
    ConsentRequest,
    DeleteUserDataRequest,
    MemorySnapshot,
    StoryGenerationRequest,
    StoryResponse,
    StorySummaryRequest,
    StorySummaryResponse,
    StoryValidationResponse,
    UsageMetricRequest,
)
from .services.continuity import get_previous_story_summary, upsert_child
from .services.crypto import hash_alias
from .services.quota import check_and_increment_quota, get_or_create_parent, get_parent
from .services.story_engine import generate_story, render_audio_for_story
from .services.summaries import summarize_story

LOGGER = logging.getLogger(__name__)
SETTINGS = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover - FastAPI manages lifecycle
    init_db()
    LOGGER.info("Database initialised")
    yield


app = FastAPI(title="StoriaAI Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(security, prefix="/auth", tags=["auth"])
@app.get("/health")
def healthcheck() -> Dict[str, str]:
    """Simple health check endpoint."""

    return {
        "status": "ok",
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


@app.post("/generate_story", response_model=StoryResponse)
def generate_story_endpoint(
    request: StoryGenerationRequest,
    db: Session = Depends(get_db),
) -> StoryResponse:
    """Generate a personalized bedtime story."""

    # For now, use a dummy user_id until auth is implemented
    user_id = "dummy_user_id"  # TODO: Replace with actual user ID from auth

    # Identify parent from email for metrics/quota (hashed internally)
    parent = get_or_create_parent(db, request.parent_email)

    # Check quota (simplified for now)
    allowed = True  # TODO: Implement proper quota check with user
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Quota exceeded. Upgrade to premium for unlimited stories.",
        )

    alias_hash = hash_alias(request.child.name)
    child = upsert_child(
        db=db,
        user_id=user_id,
        alias_hash=alias_hash,
        language=request.language,
        age=request.child.age,
        interests=request.child.interests,
        controls=request.controls.model_dump(),
    )

    previous_summary = get_previous_story_summary(db, child.id) if request.sequel else None
    story_payload = generate_story(request, previous_summary)
    audio_result = render_audio_for_story(story_payload, request.language, request.voice)
    audio_url = audio_result.audio_url

    story_obj = Story(
        child=child,
        language=request.language,
        duration_minutes=request.target_duration_minutes,
        request_payload=request.model_dump(),
        story_json=story_payload.model_dump(),
        audio_url=audio_url,
        moral_summary=story_payload.moral_summary,
    )
    db.add(story_obj)
    db.flush()

    summary_response: Optional[StorySummaryResponse] = None
    try:
        story_segments = []
        for value in story_payload.model_dump().values():
            if isinstance(value, str):
                story_segments.append(value)
            elif isinstance(value, list):
                story_segments.extend(str(item) for item in value)
        summary_response = summarize_story(
            StorySummaryRequest(story_text="\n".join(story_segments))
        )
    except Exception as exc:  # pragma: no cover - summariser is optional
        LOGGER.warning("Summary generation failed: %s", exc)

    memory_snapshot: Optional[MemorySnapshot] = None
    if summary_response:
        story_state = StoryState(
            story=story_obj,
            summary=summary_response.summary,
            characters=summary_response.characters,
            moral=summary_response.moral,
            unresolved_threads=summary_response.unresolved_threads,
        )
        db.add(story_state)

        # Upsert child memory
        existing_memory: Optional[ChildMemory] = db.query(ChildMemory).filter(ChildMemory.child_id == child.id).one_or_none()
        if existing_memory is None:
            existing_memory = ChildMemory(
                child_id=child.id,
                characters=summary_response.characters,
                last_moral=summary_response.moral,
                unresolved_threads=summary_response.unresolved_threads,
                sequel_hook=story_payload.suggested_sequel_hook,
            )
            db.add(existing_memory)
        else:
            # Merge characters uniquely
            all_chars = set(existing_memory.characters or []) | set(summary_response.characters)
            existing_memory.characters = sorted(all_chars)
            existing_memory.last_moral = summary_response.moral
            existing_memory.unresolved_threads = summary_response.unresolved_threads
            existing_memory.sequel_hook = story_payload.suggested_sequel_hook

        memory_snapshot = MemorySnapshot(
            characters=existing_memory.characters or [],
            moral=existing_memory.last_moral,
            unresolved_threads=existing_memory.unresolved_threads or [],
            sequel_hook=existing_memory.sequel_hook,
        )

    db.add(
        UsageMetric(
            parent_id=parent.id,
            story_id=story_obj.id,
            event_type="story_generated",
            payload={
                "language": request.language,
                "sequel": request.sequel,
                "voice": audio_result.voice,
            },
        )
    )

    db.commit()
    db.refresh(story_obj)

    return StoryResponse(
        story_id=story_obj.id,
        audio_url=story_obj.audio_url,
        language=story_obj.language,
        duration_minutes=story_obj.duration_minutes,
        story=story_payload,
        created_at=story_obj.created_at,
        voice=audio_result.voice,
        memory_snapshot=memory_snapshot,
    )


@app.post("/summarize_story", response_model=StorySummaryResponse)
def summarize_story_endpoint(request: StorySummaryRequest) -> StorySummaryResponse:
    """Summarize a story text payload."""

    return summarize_story(request)


@app.post("/validate_story", response_model=StoryValidationResponse)
def validate_story_endpoint(request: StorySummaryRequest) -> StoryValidationResponse:
    """Simple heuristic validation for safety."""

    lowered = request.story_text.lower()
    issues = [word for word in SETTINGS.banned_words if word in lowered]
    return StoryValidationResponse(safe=not issues, issues=issues)


@app.post("/consent", status_code=status.HTTP_201_CREATED)
def log_consent(request: ConsentRequest, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Record parental consent event."""

    parent = get_or_create_parent(db, request.parent_email)
    log_entry = ConsentLog(
        parent_id=parent.id,
        consent_version=request.consent_version,
        ip_address=request.ip_address,
    )
    db.add(log_entry)
    db.commit()
    return {"status": "recorded"}


@app.post("/delete_user_data")
def delete_user_data(request: DeleteUserDataRequest, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Delete user data associated with the parent email."""

    parent = get_parent(db, request.parent_email)
    if parent is None:
        return {"status": "not_found"}

    db.delete(parent)
    db.commit()
    return {"status": "deleted"}


@app.post("/metrics", status_code=status.HTTP_202_ACCEPTED)
def capture_metric(request: UsageMetricRequest, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Capture lightweight analytics events."""

    event = UsageMetric(event_type=request.event_type, payload=request.payload)
    db.add(event)
    db.commit()
    return {"status": "accepted"}


@app.middleware("http")
async def add_security_headers(request: Request, call_next):  # type: ignore[override]
    """Add basic security headers for compliance."""

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response
