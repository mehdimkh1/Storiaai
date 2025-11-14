"""Integration tests for story generation endpoint."""
from __future__ import annotations

import datetime as dt

from fastapi.testclient import TestClient

from app.schemas import StoryGenerationRequest, StorySummaryRequest
from app.services import story_engine, summaries


def test_healthcheck(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    dt.datetime.fromisoformat(payload["timestamp"])


def test_generate_story_stub(client: TestClient) -> None:
    request_payload = {
        "parent_email": "test@example.com",
        "child": {
            "name": "Luca",
            "age": 6,
            "mood": "curioso",
            "interests": ["draghi"],
        },
        "controls": {
            "no_scary": True,
            "kindness_lesson": True,
            "italian_focus": True,
            "educational": False,
        },
        "language": "it",
        "target_duration_minutes": 7,
        "sequel": False,
    }

    response = client.post("/generate_story", json=request_payload)
    assert response.status_code == 200
    payload = response.json()
    assert payload["language"] == "it"
    assert payload["story"]["intro"].startswith("Ciao")


def test_quota_enforcement(client: TestClient) -> None:
    request_payload = {
        "parent_email": "quota@example.com",
        "child": {
            "name": "Luca",
            "age": 6,
            "mood": "curioso",
            "interests": ["draghi"],
        },
    }

    for _ in range(3):
        assert client.post("/generate_story", json=request_payload).status_code == 200

    response = client.post("/generate_story", json=request_payload)
    assert response.status_code == 402


def test_summarize_story_rate_limit_fallback(monkeypatch) -> None:
    class _LocalRateLimitError(Exception):
        pass

    monkeypatch.setattr(summaries, "OpenAIRateLimitError", _LocalRateLimitError, raising=False)

    class _DummyCompletions:
        @staticmethod
        def create(*_, **__):
            raise summaries.OpenAIRateLimitError("quota exceeded")

    class _DummyChat:
        def __init__(self) -> None:
            self.completions = _DummyCompletions()

    class _DummyClient:
        def __init__(self) -> None:
            self.chat = _DummyChat()

    monkeypatch.setattr(summaries, "get_openai_client", lambda: _DummyClient())

    request = StorySummaryRequest(story_text="Luca incontra Anna al parco.")
    response = summaries.summarize_story(request)

    assert response.summary
    assert response.characters


def test_generate_story_rate_limit_fallback(monkeypatch) -> None:
    class _LocalRateLimitError(Exception):
        pass

    monkeypatch.setattr(story_engine, "OpenAIRateLimitError", _LocalRateLimitError, raising=False)

    class _DummyCompletions:
        @staticmethod
        def create(*_, **__):
            raise story_engine.OpenAIRateLimitError("quota exceeded")

    class _DummyChat:
        def __init__(self) -> None:
            self.completions = _DummyCompletions()

    class _DummyClient:
        def __init__(self) -> None:
            self.chat = _DummyChat()

    monkeypatch.setattr(story_engine, "get_openai_client", lambda: _DummyClient())

    request = StoryGenerationRequest(
        parent_email="rate-limit@example.com",
        child={
            "name": "Luca",
            "age": 6,
            "mood": "curioso",
            "interests": ["draghi"],
        },
        language="it",
        target_duration_minutes=7,
        sequel=False,
    )

    story = story_engine.generate_story(request, previous_summary=None)

    assert story.intro.startswith("Ciao")