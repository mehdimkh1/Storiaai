"""Story generation and audio synthesis orchestration."""
from __future__ import annotations

import asyncio
import base64
import json
import logging
from dataclasses import dataclass
from typing import Dict, Optional

import httpx

try:  # pragma: no cover - depends on optional openai dependency
    from openai import RateLimitError as OpenAIRateLimitError
except Exception:  # pragma: no cover - used when openai not installed

    class OpenAIRateLimitError(Exception):
        """Fallback RateLimitError for environments without openai."""

        pass

from ..config import get_settings
from ..schemas import ControlSettings, StoryGenerationRequest, StoryPayload
from .providers import (
    get_elevenlabs_client,
    get_huggingface_client,
    get_llm_provider,
    get_murf_client,
    get_ollama_client,
    get_openai_client,
)

LOGGER = logging.getLogger(__name__)
SETTINGS = get_settings()

STUB_STORY = {
    "intro": "Ciao! Questa è una storia di esempio perché il servizio AI non è configurato.",
    "choice_1_prompt": "Vuoi seguire Pinocchio o la fata azzurra?",
    "choice_1_options": ["Pinocchio", "Fata"],
    "branch_1": "Pinocchio porta il bambino a scoprire un nuovo bosco pieno di lucciole.",
    "choice_2_prompt": "Preferisci ascoltare una canzone o raccontare un sogno?",
    "choice_2_options": ["Canzone", "Sogno"],
    "branch_2": "La fata azzurra insegna al bambino il valore della gentilezza condividendo piccoli gesti d'amore.",
    "resolution": "La serata termina con un abbraccio e un desiderio di sogni tranquilli.",
    "moral_summary": "La gentilezza rende la notte più luminosa.",
    "suggested_sequel_hook": "La prossima volta, esplorate il Carnevale di Venezia!",
}


@dataclass
class AudioRenderResult:
    """Container for audio synthesis output."""

    audio_url: Optional[str]
    voice: Optional[str]


def build_story_prompt(request: StoryGenerationRequest, previous_summary: Optional[str]) -> str:
    """Create the prompt text for OpenAI."""

    controls = request.controls
    mood_desc = request.child.mood
    interests_joined = ", ".join(request.child.interests) or "sogni dolci"
    control_lines = [
        "- Storia positiva, calma, adatta a bambini di età {}.".format(request.child.age),
        "- Linguaggio: {}.".format("italiano" if request.language == "it" else "inglese"),
        "- Durata obiettivo: {} minuti.".format(request.target_duration_minutes),
        "- Evita elementi spaventosi." if controls.no_scary else "- Elementi avventura ammessi, ma sempre rassicuranti.",
        "- Inserisci una lezione di gentilezza." if controls.kindness_lesson else "- Morale positiva generale.",
        "- Richiama folklore italiano (Pinocchio, fiabe regionali)." if controls.italian_focus else "- Inserisci elementi fantasy universali.",
        "- Aggiungi curiosità educative in modo leggero." if controls.educational else "",
    ]

    if previous_summary:
        control_lines.append("- Continua la storia riprendendo questi elementi: {}.".format(previous_summary))

    control_lines = [line for line in control_lines if line]

    prompt = (
        "Sei StoriaAI, narratore della buonanotte per bambini italiani. "
        "Genera una storia originale per {name} ({age} anni) interessato a {interests}. "
        "Il bambino questa sera si sente {mood}. "
        "Segui esattamente queste istruzioni:\n".format(
            name=request.child.name,
            age=request.child.age,
            interests=interests_joined,
            mood=mood_desc,
        )
        + "\n".join(control_lines)
        + "\nRestituisci la risposta in JSON con le chiavi intro, choice_1_prompt, choice_1_options (array), "
        "branch_1, choice_2_prompt, choice_2_options (array), branch_2, resolution, moral_summary, suggested_sequel_hook. "
        "Ogni valore deve essere una stringa senza caratteri di escape e priva di markdown."
    )
    return prompt


def _call_openai_story(prompt: str) -> StoryPayload:
    """Invoke OpenAI to generate the structured story."""

    client = get_openai_client()
    if client is None:
        LOGGER.warning("OpenAI client unavailable; returning stub story")
        return StoryPayload(**STUB_STORY)

    try:
        response = client.chat.completions.create(
            model=SETTINGS.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sei un narratore sicuro e gentile per bambini italiani. "
                        "Rispondi solo con JSON valido."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1200,
        )
    except OpenAIRateLimitError as err:
        LOGGER.warning("OpenAI rate limit reached for story generation: %s", err)
        return StoryPayload(**STUB_STORY)
    except Exception as err:  # pragma: no cover - unexpected provider errors
        LOGGER.error("OpenAI story request failed: %s", err)
        raise RuntimeError("Story generation failed") from err

    try:
        content = response.choices[0].message.content or ""
    except (AttributeError, IndexError, KeyError) as err:  # pragma: no cover
        LOGGER.error("Unexpected OpenAI response structure: %s", err)
        raise RuntimeError("Invalid OpenAI response") from err

    try:
        payload_dict = json.loads(content)
    except json.JSONDecodeError as err:  # pragma: no cover
        LOGGER.error("OpenAI returned invalid JSON: %s", err)
        raise RuntimeError("OpenAI returned invalid JSON") from err

    return StoryPayload(**payload_dict)


def _call_ollama_story(prompt: str) -> StoryPayload:
    """Invoke an Ollama local model to generate the structured story."""

    client = get_ollama_client()
    if client is None:
        LOGGER.warning("Ollama client unavailable; returning stub story")
        return StoryPayload(**STUB_STORY)

    payload = {
        "model": SETTINGS.ollama_story_model,
        "prompt": (
            "You are StoriaAI, an Italian bedtime storyteller. "
            "Respond only with strict JSON matching the requested schema.\n"
            f"PROMPT:\n{prompt}"
        ),
        "stream": False,
        "options": {"temperature": 0.7},
    }

    try:
        response = client.post("/api/generate", json=payload)
        response.raise_for_status()
    except httpx.HTTPError as err:  # pragma: no cover - network issues
        LOGGER.error("Ollama story request failed: %s", err)
        return StoryPayload(**STUB_STORY)

    response_json = response.json()
    content = response_json.get("response", "").strip()
    if not content:
        LOGGER.warning("Ollama returned empty response; using stub story")
        return StoryPayload(**STUB_STORY)

    if "{" not in content:
        json_start = content.find("{")
        if json_start == -1:
            LOGGER.warning("Ollama response missing JSON payload; using stub story")
            return StoryPayload(**STUB_STORY)
        content = content[json_start:]

    try:
        payload_dict = json.loads(content)
    except json.JSONDecodeError:
        LOGGER.warning("Ollama returned non-JSON output; using stub story")
        return StoryPayload(**STUB_STORY)

    return StoryPayload(**payload_dict)


def _call_huggingface_story(prompt: str) -> StoryPayload:
    """Invoke Hugging Face Inference API to generate the structured story."""

    client = get_huggingface_client()
    if client is None:
        LOGGER.warning("Hugging Face client unavailable; returning stub story")
        return StoryPayload(**STUB_STORY)

    instruction = (
        "You are StoriaAI, an Italian bedtime storyteller. Respond only with strict JSON "
        "matching the requested schema."
    )
    inputs = f"{instruction}\nPROMPT:\n{prompt}"

    payload = {
        "inputs": inputs,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 800,
            "return_full_text": False,
        },
        "options": {"wait_for_model": True},
    }

    model = SETTINGS.huggingface_story_model

    try:
        response = client.post(f"/models/{model}", json=payload)
        response.raise_for_status()
    except httpx.HTTPError as err:  # pragma: no cover - network issues
        LOGGER.error("Hugging Face story request failed: %s", err)
        return StoryPayload(**STUB_STORY)

    try:
        response_json = response.json()
    except json.JSONDecodeError:
        LOGGER.warning("Hugging Face story response not JSON; using stub story")
        return StoryPayload(**STUB_STORY)

    if isinstance(response_json, list) and response_json:
        content = response_json[0].get("generated_text", "").strip()
    elif isinstance(response_json, dict):
        content = response_json.get("generated_text", "").strip()
    else:
        content = ""

    if not content:
        LOGGER.warning("Hugging Face story response empty; using stub story")
        return StoryPayload(**STUB_STORY)

    if "{" not in content:
        json_start = content.find("{")
        if json_start == -1:
            LOGGER.warning("Hugging Face story missing JSON; using stub story")
            return StoryPayload(**STUB_STORY)
        content = content[json_start:]

    try:
        payload_dict = json.loads(content)
    except json.JSONDecodeError:
        LOGGER.warning("Hugging Face story not valid JSON; using stub story")
        return StoryPayload(**STUB_STORY)

    try:
        return StoryPayload(**payload_dict)
    except Exception:
        LOGGER.warning("Hugging Face story payload invalid; using stub story")
        return StoryPayload(**STUB_STORY)


def sanitize_story_text(story: StoryPayload, controls: ControlSettings) -> StoryPayload:
    """Ensure story text is safe according to controls."""

    banned = SETTINGS.banned_words
    updated_fields: Dict[str, str] = {}

    for field_name, value in story.model_dump().items():
        if isinstance(value, str):
            lowered = value.lower()
            if controls.no_scary and any(bad in lowered for bad in banned):
                updated_fields[field_name] = value.replace("paura", "serenità").replace("morte", "riposo")
        elif isinstance(value, list):
            sanitized = []
            for option in value:
                option_lower = option.lower()
                if controls.no_scary and any(bad in option_lower for bad in banned):
                    sanitized.append("Un'opzione tranquilla")
                else:
                    sanitized.append(option)
            updated_fields[field_name] = sanitized  # type: ignore[assignment]

    if not updated_fields:
        return story

    merged = story.model_dump()
    merged.update(updated_fields)
    return StoryPayload(**merged)


def synthesize_audio(text: str, language: str, voice: Optional[str]) -> AudioRenderResult:
    """Generate audio narration using available providers."""

    requested_voice = voice.strip() if voice else None

    if requested_voice and requested_voice.lower().startswith("gtts"):
        if SETTINGS.use_gtts:
            audio_url = _synthesize_audio_gtts(text, language)
            if audio_url:
                return AudioRenderResult(audio_url, "gtts")
        requested_voice = None

    if requested_voice:
        edge_result = _synthesize_audio_edge_tts(text, language, requested_voice)
        if edge_result.audio_url:
            return edge_result

    if SETTINGS.use_gtts:
        audio_url = _synthesize_audio_gtts(text, language)
        if audio_url:
            return AudioRenderResult(audio_url, "gtts")

    edge_result = _synthesize_audio_edge_tts(text, language, None)
    if edge_result.audio_url:
        return edge_result

    murf_client = get_murf_client()
    if murf_client is not None:
        audio_url = _synthesize_audio_murf(murf_client, text, language)
        if audio_url:
            return AudioRenderResult(audio_url, SETTINGS.murf_voice_id)

    if get_llm_provider() == "huggingface":
        audio_url = _synthesize_audio_huggingface(text)
        if audio_url:
            return AudioRenderResult(audio_url, SETTINGS.huggingface_tts_model)

    client = get_elevenlabs_client()
    if client is None:
        LOGGER.warning("No TTS provider configured; skipping audio")
        return AudioRenderResult(None, None)

    voice_id = SETTINGS.elevenlabs_voice_id or ("bella" if language == "it" else "rachel")
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.4, "style": 0.4},
    }
    try:
        response = client.post(f"/v1/text-to-speech/{voice_id}", json=payload)
        response.raise_for_status()
    except httpx.HTTPError as err:  # pragma: no cover
        LOGGER.error("Failed to generate audio: %s", err)
        return AudioRenderResult(None, None)

    return AudioRenderResult(f"data:audio/mpeg;base64,{response.text}", voice_id)


def _synthesize_audio_huggingface(text: str) -> Optional[str]:
    """Generate audio narration using Hugging Face Inference API."""

    api_key = SETTINGS.huggingface_api_key
    model = SETTINGS.huggingface_tts_model
    if not api_key or not model:
        LOGGER.warning("Hugging Face TTS not configured; skipping audio")
        return None

    base_url = SETTINGS.huggingface_base_url.rstrip("/")
    url = f"{base_url}/models/{model}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "audio/wav",
    }
    payload = {
        "inputs": text,
        "parameters": {"return_full_text": False},
        "options": {"wait_for_model": True},
    }

    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
    except httpx.HTTPError as err:  # pragma: no cover - dependent on external service
        LOGGER.error("Hugging Face TTS request failed: %s", err)
        return None

    audio_bytes = response.content
    if not audio_bytes:
        LOGGER.warning("Hugging Face TTS returned empty audio")
        return None

    encoded = base64.b64encode(audio_bytes).decode("ascii")
    return f"data:audio/wav;base64,{encoded}"


def _synthesize_audio_murf(client: httpx.Client, text: str, language: str) -> Optional[str]:
    """Generate audio narration using the Murf.ai API."""

    voice_id = SETTINGS.murf_voice_id
    if not voice_id:
        LOGGER.warning("Murf voice ID missing; skipping Murf TTS")
        return None

    payload = {
        "voiceId": voice_id,
        "text": text,
        "rate": 0,
        "pitch": 0,
        "sampleRate": 48000,
        "format": "MP3",
        "channelType": "STEREO",
        "pronunciationDictionary": {},
        "encodeAsBase64": True,
    }

    try:
        response = client.post("/text-to-speech", json=payload)
        response.raise_for_status()
    except httpx.HTTPError as err:  # pragma: no cover - external dependency
        LOGGER.error("Murf TTS request failed: %s", err)
        return None

    try:
        data = response.json()
    except json.JSONDecodeError:  # pragma: no cover
        LOGGER.error("Murf TTS response was not JSON")
        return None

    audio_base64 = data.get("audioFile")
    if not audio_base64:
        LOGGER.warning("Murf TTS response missing audioFile payload")
        return None

    return f"data:audio/mp3;base64,{audio_base64}"


def generate_story(request: StoryGenerationRequest, previous_summary: Optional[str]) -> StoryPayload:
    """High-level orchestration to build and sanitize a story payload."""

    prompt = build_story_prompt(request, previous_summary)
    provider = get_llm_provider()
    if provider == "ollama":
        story = _call_ollama_story(prompt)
    elif provider == "huggingface":
        story = _call_huggingface_story(prompt)
    else:
        story = _call_openai_story(prompt)
    sanitized_story = sanitize_story_text(story, request.controls)
    return sanitized_story


def render_audio_for_story(
    story: StoryPayload,
    language: str,
    voice: Optional[str] = None,
) -> AudioRenderResult:
    """Join story sections and delegate to the audio synthesiser."""

    full_text = "\n".join(
        [
            story.intro,
            story.branch_1,
            story.branch_2,
            story.resolution,
            story.moral_summary,
        ]
    )
    return synthesize_audio(full_text, language, voice)


def _resolve_edge_voice(language: str, requested_voice: Optional[str]) -> Optional[str]:
    """Return an Edge TTS voice name for the requested language."""

    if requested_voice:
        candidate = requested_voice.strip()
        if not candidate:
            return None
        if candidate.lower().startswith("edge:"):
            candidate = candidate.split(":", 1)[1].strip()
        return candidate or None

    voice_map = SETTINGS.edge_tts_voice_map or {}
    if not isinstance(voice_map, dict):  # defensive: allow JSON string env overrides
        LOGGER.warning("EDGE_TTS_VOICE_MAP must be a JSON object; received %s", type(voice_map))
        return None

    return voice_map.get(language) or voice_map.get("default")


def _synthesize_audio_edge_tts(
    text: str,
    language: str,
    requested_voice: Optional[str],
) -> AudioRenderResult:
    """Generate audio narration via Microsoft Edge TTS."""

    if not SETTINGS.edge_tts_enabled:
        return AudioRenderResult(None, None)

    try:
        import edge_tts  # type: ignore
    except ImportError:  # pragma: no cover - optional dependency
        LOGGER.warning("edge-tts package missing; skipping Edge TTS synthesis")
        return AudioRenderResult(None, None)

    voice_name = _resolve_edge_voice(language, requested_voice)
    if not voice_name:
        return AudioRenderResult(None, None)

    async def _generate() -> Optional[bytes]:
        communicator = edge_tts.Communicate(
            text=text,
            voice=voice_name,
            rate=SETTINGS.edge_tts_rate,
            pitch=SETTINGS.edge_tts_pitch,
        )

        audio_chunks = bytearray()
        try:
            async for chunk in communicator.stream():
                chunk_type = chunk.get("type")
                if chunk_type == "audio":
                    audio_chunks.extend(chunk["data"])
        except Exception as exc:  # pragma: no cover - network/runtime issues
            LOGGER.error("Edge TTS stream failed for voice %s: %s", voice_name, exc)
            return None

        return bytes(audio_chunks) if audio_chunks else None

    try:
        audio_bytes = asyncio.run(_generate())
    except RuntimeError as err:
        if "asyncio.run()" in str(err) and "running event loop" in str(err):
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                audio_bytes = loop.run_until_complete(_generate())
            finally:
                asyncio.set_event_loop(None)
                loop.close()
        else:
            LOGGER.error("Edge TTS runtime error: %s", err)
            return AudioRenderResult(None, None)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.error("Edge TTS synthesis failed: %s", exc)
        return AudioRenderResult(None, None)

    if not audio_bytes:
        LOGGER.warning("Edge TTS produced empty audio for voice %s", voice_name)
        return AudioRenderResult(None, None)

    encoded = base64.b64encode(audio_bytes).decode("ascii")
    return AudioRenderResult(f"data:audio/mp3;base64,{encoded}", voice_name)


def _synthesize_audio_gtts(text: str, language: str) -> Optional[str]:
    """Generate audio using free Google TTS (gTTS)."""
    try:
        from gtts import gTTS
        import os
        import tempfile
        
        LOGGER.info(f"Generating audio with gTTS for language: {language}")
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tmp_path = tmp_file.name
        
        # Generate audio
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(tmp_path)
        
        # Read and encode as base64
        with open(tmp_path, 'rb') as audio_file:
            audio_data = audio_file.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Clean up
        os.unlink(tmp_path)
        
        return f"data:audio/mp3;base64,{audio_base64}"
    
    except Exception as e:
        LOGGER.error(f"gTTS failed: {e}")
        return None

