"""Story summarisation using configurable LLM providers."""
from __future__ import annotations

import json
import logging
import re
from typing import Optional

import httpx

from ..config import get_settings
from ..schemas import StorySummaryRequest, StorySummaryResponse
from .providers import (
    get_huggingface_client,
    get_llm_provider,
    get_ollama_client,
    get_openai_client,
)

LOGGER = logging.getLogger(__name__)
SETTINGS = get_settings()

STUB_SUMMARY = StorySummaryResponse(
    summary="La storia di prova celebra l'amicizia e la gentilezza.",
    characters=["Bambino", "Fatina"],
    moral="La gentilezza illumina la notte",
    unresolved_threads=["Visitare il Carnevale di Venezia"],
)


try:  # pragma: no cover - depends on optional openai dependency
    from openai import RateLimitError as OpenAIRateLimitError
except Exception:  # pragma: no cover - used when openai not installed

    class OpenAIRateLimitError(Exception):
        """Fallback RateLimitError for environments without openai."""

        pass


_FALLBACK_SUMMARY_MAX_CHARS = 260


def _fallback_summary(story_text: str) -> StorySummaryResponse:
    """Generate a lightweight summary when OpenAI is unavailable."""

    cleaned = story_text.strip()
    if not cleaned:
        return STUB_SUMMARY

    sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", cleaned) if segment.strip()]
    summary_text = " ".join(sentences[:2]) if sentences else cleaned
    summary_text = summary_text[:_FALLBACK_SUMMARY_MAX_CHARS].rstrip()

    name_candidates = {
        match.strip("'\"")
        for match in re.findall(r"\b[A-Z][A-Za-zÀ-ÖØ-öø-ÿ']{2,}\b", cleaned)
    }
    characters = sorted(name_candidates)[:4] or STUB_SUMMARY.characters

    return StorySummaryResponse(
        summary=summary_text,
        characters=characters,
        moral=STUB_SUMMARY.moral,
        unresolved_threads=[],
    )

def _summarize_with_openai(request: StorySummaryRequest) -> StorySummaryResponse:
    client = get_openai_client()
    if client is None:
        LOGGER.warning("OpenAI client unavailable; returning stub summary")
        return STUB_SUMMARY

    system_prompt = (
        "Sei un assistente editor per storie della buonanotte. Riassumi brevemente e trova personaggi e morali."  # noqa: E501
    )
    try:
        response = client.chat.completions.create(
            model=SETTINGS.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Analizza il seguente testo e restituisci JSON con summary (<=120 parole), "
                        "characters (lista), moral (stringa facoltativa), unresolved_threads (lista):\n"
                        f"{request.story_text}"
                    ),
                },
            ],
            temperature=0.1,
            max_tokens=400,
        )
    except OpenAIRateLimitError as err:
        LOGGER.warning("OpenAI rate limit reached for summary generation: %s", err)
        return _fallback_summary(request.story_text)
    except Exception as err:  # pragma: no cover - unexpected provider errors
        LOGGER.error("OpenAI summary request failed: %s", err)
        raise RuntimeError("Summary generation failed") from err

    try:
        content = response.choices[0].message.content or ""
        payload = json.loads(content)
    except (AttributeError, IndexError, KeyError, json.JSONDecodeError) as err:
        LOGGER.error("Failed to parse summary response: %s", err)
        raise RuntimeError("Invalid summary response") from err

    return StorySummaryResponse(**payload)


def _summarize_with_ollama(request: StorySummaryRequest) -> StorySummaryResponse:
    client = get_ollama_client()
    if client is None:
        LOGGER.warning("Ollama client unavailable; returning stub summary")
        return _fallback_summary(request.story_text)

    prompt = (
        "You are a bedtime story editor. Return compact JSON with keys summary, characters (list), "
        "moral (string or null), unresolved_threads (list).\n"
        f"STORY:\n{request.story_text}"
    )
    payload = {
        "model": SETTINGS.ollama_summary_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }

    try:
        response = client.post("/api/generate", json=payload)
        response.raise_for_status()
    except httpx.HTTPError as err:  # pragma: no cover - network issues
        LOGGER.error("Ollama summary request failed: %s", err)
        return _fallback_summary(request.story_text)

    response_json = response.json()
    content = response_json.get("response", "").strip()
    if not content:
        LOGGER.warning("Ollama summary response empty; using fallback summary")
        return _fallback_summary(request.story_text)

    if "{" not in content:
        json_start = content.find("{")
        if json_start == -1:
            LOGGER.warning("Ollama summary missing JSON; using fallback summary")
            return _fallback_summary(request.story_text)
        content = content[json_start:]

    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        LOGGER.warning("Ollama summary not JSON; using fallback summary")
        return _fallback_summary(request.story_text)

    try:
        return StorySummaryResponse(**payload)
    except Exception:
        LOGGER.warning("Ollama summary payload invalid; using fallback summary")
        return _fallback_summary(request.story_text)


def _summarize_with_huggingface(request: StorySummaryRequest) -> StorySummaryResponse:
    client = get_huggingface_client()
    if client is None:
        LOGGER.warning("Hugging Face client unavailable; returning fallback summary")
        return _fallback_summary(request.story_text)

    prompt = (
        "You are a bedtime story editor. Return valid JSON with keys summary, characters (array), "
        "moral (string or null), unresolved_threads (array).\n"
        f"STORY:\n{request.story_text}"
    )
    payload = {
        "inputs": prompt,
        "parameters": {
            "temperature": 0.1,
            "max_new_tokens": 400,
            "return_full_text": False,
        },
        "options": {"wait_for_model": True},
    }

    model = SETTINGS.huggingface_summary_model

    try:
        response = client.post(f"/models/{model}", json=payload)
        response.raise_for_status()
    except httpx.HTTPError as err:  # pragma: no cover - network issues
        LOGGER.error("Hugging Face summary request failed: %s", err)
        return _fallback_summary(request.story_text)

    try:
        response_json = response.json()
    except json.JSONDecodeError:
        LOGGER.warning("Hugging Face summary response not JSON; using fallback summary")
        return _fallback_summary(request.story_text)

    if isinstance(response_json, list) and response_json:
        content = response_json[0].get("generated_text", "").strip()
    elif isinstance(response_json, dict):
        content = response_json.get("generated_text", "").strip()
    else:
        content = ""

    if not content:
        LOGGER.warning("Hugging Face summary response empty; using fallback summary")
        return _fallback_summary(request.story_text)

    if "{" not in content:
        json_start = content.find("{")
        if json_start == -1:
            LOGGER.warning("Hugging Face summary missing JSON; using fallback summary")
            return _fallback_summary(request.story_text)
        content = content[json_start:]

    try:
        payload_dict = json.loads(content)
    except json.JSONDecodeError:
        LOGGER.warning("Hugging Face summary not valid JSON; using fallback summary")
        return _fallback_summary(request.story_text)

    try:
        return StorySummaryResponse(**payload_dict)
    except Exception:
        LOGGER.warning("Hugging Face summary payload invalid; using fallback summary")
        return _fallback_summary(request.story_text)


def summarize_story(request: StorySummaryRequest) -> StorySummaryResponse:
    """Summarize story text using the configured LLM provider."""

    provider = get_llm_provider()
    if provider == "ollama":
        return _summarize_with_ollama(request)
    if provider == "huggingface":
        return _summarize_with_huggingface(request)
    return _summarize_with_openai(request)
