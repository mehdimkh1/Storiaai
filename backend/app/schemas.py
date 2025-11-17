"""Pydantic schemas for the API."""
from __future__ import annotations

import datetime as dt
from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic import StringConstraints, ConfigDict

from .config import get_settings


settings = get_settings()


class ControlSettings(BaseModel):
    no_scary: bool = Field(default=True)
    kindness_lesson: bool = Field(default=True)
    italian_focus: bool = Field(default=True)
    educational: bool = Field(default=False)


class ChildProfile(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=40, strip_whitespace=True)]
    age: Annotated[int, Field(ge=2, le=12)]
    mood: Annotated[str, StringConstraints(min_length=1, max_length=60, strip_whitespace=True)]
    interests: List[str] = Field(default_factory=list)

    @field_validator("interests", mode="before")
    @classmethod
    def _normalize_interests(cls, value: List[str]) -> List[str]:  # noqa: D401
        if not value:
            return []
        cleaned = []
        seen = set()
        for item in value:
            normalized = (item or "").strip()
            if not normalized:
                continue
            normalized = normalized[:60]
            key = normalized.lower()
            if key not in seen:
                seen.add(key)
                cleaned.append(normalized)
        return cleaned


class StoryGenerationRequest(BaseModel):
    parent_email: Annotated[str, StringConstraints(min_length=3, max_length=120, strip_whitespace=True)]
    child: ChildProfile
    controls: ControlSettings = Field(default_factory=ControlSettings)
    language: str = Field(default="it")
    target_duration_minutes: Annotated[int, Field(ge=5, le=10)] = 7
    sequel: bool = Field(default=False)
    previous_story_id: Optional[str] = None
    voice: Optional[str] = Field(default=None, max_length=80)
    # New optional stylistic controls
    style: Optional[str] = Field(
        default=None,
        description="Narrative style e.g. 'fiaba classica', 'avventura', 'fantascienza', 'umoristica'",
        max_length=40,
    )
    tone: Optional[str] = Field(
        default=None,
        description="Desired emotional tone e.g. 'calmo', 'gioioso', 'riflessivo'",
        max_length=30,
    )
    educational_topic: Optional[str] = Field(
        default=None,
        description="Specific educational topic to weave lightly (e.g. 'sistema solare')",
        max_length=60,
    )
    generate_panels: bool = Field(
        default=False,
        description="If true, backend will derive structured panel prompts for illustration",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "parent_email": "parent@example.com",
                "child": {
                    "name": "Luca",
                    "age": 6,
                    "mood": "curioso",
                    "interests": ["draghi", "calcio"],
                },
                "controls": {
                    "no_scary": True,
                    "kindness_lesson": True,
                    "italian_focus": True,
                    "educational": False,
                },
                "language": "it",
                "voice": "it-IT-IsabellaNeural",
                "target_duration_minutes": 7,
                "sequel": False,
            }
        }
    )

    @field_validator("language")
    @classmethod
    def _validate_language(cls, value: str) -> str:  # noqa: D401
        sanitized = value.strip().lower()
        if sanitized not in settings.allowed_languages:
            raise ValueError("Unsupported language")
        return sanitized

    @field_validator("voice")
    @classmethod
    def _sanitize_voice(cls, value: Optional[str]) -> Optional[str]:  # noqa: D401
        if value is None:
            return None
        sanitized = value.strip()
        if not sanitized:
            return None
        return sanitized[:80]


class StoryBranch(BaseModel):
    label: str
    text: str


class StoryPayload(BaseModel):
    intro: str
    choice_1_prompt: str
    choice_1_options: List[str]
    branch_1: str
    choice_2_prompt: str
    choice_2_options: List[str]
    branch_2: str
    resolution: str
    moral_summary: str
    suggested_sequel_hook: Optional[str] = None
    # Optional illustration panel prompts (simple textual guidance)
    panel_prompts: List[str] = Field(default_factory=list)


class MemorySnapshot(BaseModel):
    characters: List[str] = Field(default_factory=list)
    moral: Optional[str] = None
    unresolved_threads: List[str] = Field(default_factory=list)
    sequel_hook: Optional[str] = None


class StoryResponse(BaseModel):
    story_id: str
    audio_url: Optional[str]
    language: str
    duration_minutes: int
    story: StoryPayload
    created_at: dt.datetime
    voice: Optional[str] = None
    memory_snapshot: Optional[MemorySnapshot] = None


class StorySummaryRequest(BaseModel):
    story_text: str


class StorySummaryResponse(BaseModel):
    summary: str
    characters: List[str]
    moral: Optional[str]
    unresolved_threads: List[str] = Field(default_factory=list)


class StoryValidationResponse(BaseModel):
    safe: bool
    issues: List[str] = Field(default_factory=list)


class ConsentRequest(BaseModel):
    parent_email: str
    consent_version: str
    ip_address: Optional[str] = None


class DeleteUserDataRequest(BaseModel):
    parent_email: str


class UsageMetricRequest(BaseModel):
    event_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
