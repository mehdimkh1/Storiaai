"""External provider clients."""
from __future__ import annotations

import logging
from typing import Any, Optional, TYPE_CHECKING

import httpx

from ..config import get_settings

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore


if TYPE_CHECKING:
    OpenAIClient = Any


LOGGER = logging.getLogger(__name__)
settings = get_settings()
_OLLAMA_CLIENT: Optional[httpx.Client] = None
_HUGGINGFACE_CLIENT: Optional[httpx.Client] = None
_MURF_CLIENT: Optional[httpx.Client] = None


def get_llm_provider() -> str:
    """Return the configured LLM provider in lowercase."""

    return settings.llm_provider.lower()


def get_openai_client() -> Optional["OpenAIClient"]:
    """Return an OpenAI client when keys are available."""

    if get_llm_provider() != "openai":
        return None
    if settings.use_stub_providers or OpenAI is None:
        return None
    return OpenAI(api_key=settings.openai_api_key)


def get_ollama_client() -> Optional[httpx.Client]:
    """Return an HTTP client configured for Ollama."""

    if get_llm_provider() != "ollama":
        return None

    base_url = settings.ollama_base_url.rstrip("/")
    if not base_url:
        LOGGER.warning("OLLAMA_BASE_URL not configured; falling back to stubs")
        return None

    global _OLLAMA_CLIENT
    if _OLLAMA_CLIENT is None:
        # Add headers to bypass ngrok browser warning and look like a browser
        headers = {
            "ngrok-skip-browser-warning": "true",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        _OLLAMA_CLIENT = httpx.Client(base_url=base_url, timeout=60, headers=headers)
    return _OLLAMA_CLIENT


def get_huggingface_client() -> Optional[httpx.Client]:
    """Return an HTTP client configured for Hugging Face Inference API."""

    if get_llm_provider() != "huggingface":
        return None

    api_key = settings.huggingface_api_key or ""
    if not api_key:
        LOGGER.warning("Hugging Face API key missing; falling back to stubs")
        return None

    base_url = settings.huggingface_base_url.rstrip("/") or "https://api-inference.huggingface.co"

    global _HUGGINGFACE_CLIENT
    if _HUGGINGFACE_CLIENT is None:
        headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
        _HUGGINGFACE_CLIENT = httpx.Client(base_url=base_url, headers=headers, timeout=90)
    return _HUGGINGFACE_CLIENT


def get_elevenlabs_client() -> Optional[httpx.Client]:
    """Return an HTTP client configured for ElevenLabs."""

    api_key = settings.elevenlabs_api_key or ""
    if not api_key:
        return None
    headers = {"xi-api-key": api_key}
    client = httpx.Client(base_url="https://api.elevenlabs.io", headers=headers, timeout=30)
    return client


def get_murf_client() -> Optional[httpx.Client]:
    """Return an HTTP client configured for Murf API."""

    api_key = settings.murf_api_key or ""
    if not api_key:
        return None

    global _MURF_CLIENT
    if _MURF_CLIENT is None:
        headers = {
            "apikey": api_key,
            "Content-Type": "application/json",
        }
        _MURF_CLIENT = httpx.Client(base_url="https://api.murf.ai/v1", headers=headers, timeout=90)
    return _MURF_CLIENT
