# StoriaAI - Complete Technical Overview

## 📋 Table of Contents
1. [Project Architecture](#project-architecture)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Backend Deep Dive](#backend-deep-dive)
5. [Frontend Deep Dive](#frontend-deep-dive)
6. [Data Flow](#data-flow)
7. [API Reference](#api-reference)

---

## 🏗️ Project Architecture

StoriaAI is a **full-stack web application** that generates personalized bedtime stories for children with multi-language support and audio narration.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  HTML5 + CSS3 + Vanilla JavaScript                   │   │
│  │  - 3D Animated UI (Vanta.js particles)               │   │
│  │  - Form handling & validation                        │   │
│  │  - Audio player                                      │   │
│  │  - Multi-language support (5 languages)              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI)                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Layer (FastAPI + Uvicorn)                       │   │
│  │  - REST endpoints                                    │   │
│  │  - CORS middleware                                   │   │
│  │  - Request validation (Pydantic)                     │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Services Layer                                      │   │
│  │  - Story Engine (generation + sanitization)         │   │
│  │  - Audio Synthesis (Edge TTS + gTTS)                │   │
│  │  - Provider Management (OpenAI/Ollama/HF)           │   │
│  │  - Quota Management                                  │   │
│  │  - Continuity/Sequels                                │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Database Layer (SQLAlchemy + SQLite)                │   │
│  │  - Parents, Children, Stories                        │   │
│  │  - Story State (for sequels)                        │   │
│  │  - Usage Metrics & Quotas                           │   │
│  │  - Consent Logs                                      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                  EXTERNAL SERVICES (Optional)                │
│  - OpenAI API (GPT-4)                                       │
│  - Hugging Face Inference API                               │
│  - Ollama (Local LLM)                                       │
│  - Microsoft Edge TTS                                       │
│  - Google TTS (gTTS - Always Available)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.111.0
- **Web Server**: Uvicorn 0.30.1 (ASGI)
- **Database**: SQLAlchemy + SQLite
- **Data Validation**: Pydantic v2
- **Text-to-Speech**:
  - gTTS 2.5.1 (free, always available)
  - edge-tts 6.1.13 (free, requires network)
- **LLM Integration**:
  - OpenAI API (optional)
  - Hugging Face Transformers 4.36.2 (optional)
  - Ollama (optional, local)
- **HTTP Client**: httpx
- **Testing**: pytest 8.2.1

### Frontend
- **Core**: HTML5, CSS3, Vanilla JavaScript
- **3D Graphics**: Vanta.js (particle effects)
- **Dependencies**: Three.js (required by Vanta.js)
- **No Build Process**: Static files only

### Infrastructure
- **Python**: 3.12.6
- **Virtual Environment**: `.venv/`
- **Database**: SQLite (`storiaai.db`)
- **Configuration**: `.env` file

---

## 📂 Project Structure

```
vscode output/
│
├── backend/                          # FastAPI backend application
│   ├── app/                          # Main application package
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app + API endpoints
│   │   ├── config.py                 # Settings & environment config
│   │   ├── database.py               # SQLAlchemy setup
│   │   ├── models.py                 # Database models (ORM)
│   │   ├── schemas.py                # Pydantic schemas (validation)
│   │   │
│   │   └── services/                 # Business logic layer
│   │       ├── __init__.py
│   │       ├── story_engine.py       # Story generation + audio
│   │       ├── summaries.py          # Story summarization
│   │       ├── providers.py          # External API clients
│   │       ├── quota.py              # Usage limits management
│   │       ├── continuity.py         # Sequel/continuation logic
│   │       └── crypto.py             # Hashing utilities
│   │
│   ├── tests/                        # Test suite
│   │   ├── conftest.py               # Pytest fixtures
│   │   └── test_generate_story.py    # Integration tests
│   │
│   ├── .env                          # Environment variables (secrets)
│   ├── .env.example                  # Example configuration
│   ├── requirements.txt              # Python dependencies
│   ├── storiaai.db                   # SQLite database (runtime)
│   └── README.md                     # Backend documentation
│
├── frontend/                         # Static web interface
│   ├── index.html                    # Main HTML page
│   ├── styles.css                    # CSS (3D animations)
│   └── app.js                        # JavaScript (app logic)
│
├── docs/                             # Documentation
│   └── architecture.md
│
├── .venv/                            # Python virtual environment
├── START_APP.bat                     # Windows launcher script
├── test_story.ps1                    # PowerShell test script
├── README_WORKING.md                 # User documentation
└── TECHNICAL_OVERVIEW.md             # This file
```

---

## 🔧 Backend Deep Dive

### 1. Application Entry Point: `main.py`

**Purpose**: FastAPI application initialization and HTTP endpoint definitions.

**Key Components**:

#### a) Application Lifecycle
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()  # Creates tables if not exist
    LOGGER.info("Database initialised")
    yield  # Application runs
    # Cleanup code would go here
```

#### b) FastAPI App Instance
```python
app = FastAPI(
    title="StoriaAI Backend",
    version="0.1.0",
    lifespan=lifespan
)
```

#### c) CORS Middleware
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allow all origins (for development)
    allow_credentials=False,
    allow_methods=["*"],      # Allow all HTTP methods
    allow_headers=["*"],      # Allow all headers
)
```

#### d) API Endpoints

**`GET /health`** - Health check
- Returns: `{"status": "ok", "timestamp": "..."}`
- Use: Monitor server availability

**`POST /generate_story`** - Main story generation
- Input: `StoryGenerationRequest` (Pydantic schema)
- Process:
  1. Get or create parent record
  2. Check quota (3 stories/day for free users)
  3. Hash child alias for privacy
  4. Upsert child record
  5. Retrieve previous summary if sequel requested
  6. Generate story using AI/stub
  7. Synthesize audio (Edge TTS → gTTS fallback)
  8. Store story in database
  9. Generate summary for sequel support
  10. Log usage metrics
- Output: `StoryResponse` with story, audio_url, voice

**`POST /summarize_story`** - Summarize story text
- Input: `StorySummaryRequest`
- Output: `StorySummaryResponse` (summary, characters, moral)

**`POST /validate_story`** - Safety validation
- Input: Story text
- Output: Safe/unsafe + list of banned words found

**`POST /consent`** - Log parental consent
- Input: Parent email, consent version, IP
- Output: `{"status": "recorded"}`

**`POST /delete_user_data`** - GDPR compliance
- Input: Parent email
- Output: Deletes all related data

**`POST /metrics`** - Analytics events
- Input: Event type + payload
- Output: `{"status": "accepted"}`

---

### 2. Configuration: `config.py`

**Purpose**: Centralized settings management using Pydantic.

**Settings Class**:
```python
class Settings(BaseSettings):
    # LLM Provider Selection
    llm_provider: Literal["openai", "ollama", "huggingface"]
    
    # OpenAI
    openai_api_key: Optional[str]
    openai_model: str = "gpt-4.1-mini"
    
    # Ollama (Local)
    ollama_base_url: str = "http://localhost:11434"
    ollama_story_model: str = "mistral"
    ollama_summary_model: str = "mistral"
    
    # Hugging Face
    huggingface_api_key: Optional[str]
    huggingface_base_url: str = "https://api-inference.huggingface.co"
    huggingface_story_model: str = "mistralai/Mixtral-8x7B-Instruct"
    huggingface_tts_model: Optional[str] = "suno/bark-small"
    
    # Premium TTS
    elevenlabs_api_key: Optional[str]
    murf_api_key: Optional[str]
    
    # Free TTS
    use_gtts: bool = True
    edge_tts_enabled: bool = True
    edge_tts_rate: str = "+0%"
    edge_tts_pitch: str = "+0Hz"
    edge_tts_voice_map: Dict[str, str]  # Language → voice mapping
    
    # Database
    database_url: str = "sqlite:///./storiaai.db"
    
    # Quota
    max_free_stories_per_day: int = 3
    
    # Safety
    banned_words: tuple[str, ...]
    allowed_languages: tuple[str, ...] = ("ar", "en", "es", "fr", "it")
    
    # Mode
    offline_mode: bool = False
```

**Singleton Pattern**:
```python
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings instance"""
    return Settings()
```

---

### 3. Database Models: `models.py`

**Purpose**: SQLAlchemy ORM models for data persistence.

**Entity Relationship Diagram**:
```
Parent (1) ──┬── (N) Child (1) ──┬── (N) Story (1) ── (1) StoryState
             │                     │
             │                     └── (N) UsageMetric
             │
             ├── (N) StoryQuota
             └── (N) ConsentLog
```

**Models**:

#### `Parent`
- `id`: UUID primary key
- `email_hash`: Hashed email (privacy)
- `is_premium`: Boolean flag
- `created_at`: Timestamp

#### `Child`
- `id`: UUID primary key
- `parent_id`: Foreign key to Parent
- `alias_hash`: Hashed name (privacy)
- `age`: Integer (2-12)
- `language`: String (ar/en/es/fr/it)
- `interests`: JSON array
- `controls`: JSON object (preferences)

#### `Story`
- `id`: UUID primary key
- `child_id`: Foreign key to Child
- `language`: Story language
- `duration_minutes`: Target duration
- `request_payload`: JSON (original request)
- `story_json`: JSON (generated story)
- `audio_url`: Base64 MP3 data
- `moral_summary`: Text summary
- `created_at`: Timestamp

#### `StoryState`
- `story_id`: Primary key (FK to Story)
- `summary`: Text for continuity
- `characters`: JSON array
- `moral`: String
- `unresolved_threads`: JSON array
- `sequel_hook`: Text

#### `StoryQuota`
- `parent_id`: Composite PK
- `quota_date`: Composite PK
- `story_count`: Integer counter

#### `UsageMetric`
- `id`: UUID primary key
- `parent_id`: Optional FK
- `story_id`: Optional FK
- `event_type`: String
- `payload`: JSON
- `created_at`: Timestamp

#### `ConsentLog`
- `id`: UUID primary key
- `parent_id`: FK to Parent
- `consent_version`: String
- `ip_address`: Optional string
- `created_at`: Timestamp

---

### 4. Pydantic Schemas: `schemas.py`

**Purpose**: Request/response validation and serialization.

**Key Schemas**:

#### `ChildProfile`
```python
class ChildProfile(BaseModel):
    name: str  # 1-40 chars, stripped
    age: int   # 2-12
    mood: str  # 1-60 chars
    interests: List[str]  # Normalized, deduplicated
```

#### `ControlSettings`
```python
class ControlSettings(BaseModel):
    no_scary: bool = True
    kindness_lesson: bool = True
    italian_focus: bool = True
    educational: bool = False
```

#### `StoryGenerationRequest`
```python
class StoryGenerationRequest(BaseModel):
    parent_email: str
    child: ChildProfile
    controls: ControlSettings
    language: str  # Validated against allowed_languages
    target_duration_minutes: int  # 5-10
    sequel: bool = False
    previous_story_id: Optional[str] = None
    voice: Optional[str] = None  # Edge TTS voice name
```

#### `StoryPayload`
```python
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
    suggested_sequel_hook: Optional[str]
```

#### `StoryResponse`
```python
class StoryResponse(BaseModel):
    story_id: str
    audio_url: Optional[str]  # Base64 MP3
    language: str
    duration_minutes: int
    story: StoryPayload
    created_at: datetime
    voice: Optional[str]  # Voice used for audio
```

---

### 5. Story Engine: `services/story_engine.py`

**Purpose**: Core story generation and audio synthesis logic.

#### **Story Generation Flow**

**1. Prompt Construction** - `build_story_prompt()`
```python
def build_story_prompt(
    request: StoryGenerationRequest,
    previous_summary: Optional[str]
) -> str:
    """Build AI prompt from user request"""
    
    # Components:
    # - Child profile (name, age, mood, interests)
    # - Control settings (no_scary, kindness, etc.)
    # - Language preference
    # - Duration target
    # - Previous story summary (if sequel)
    
    # Output: Detailed instructions for LLM
```

**2. LLM Provider Selection** - `generate_story()`
```python
def generate_story(
    request: StoryGenerationRequest,
    previous_summary: Optional[str]
) -> StoryPayload:
    """Orchestrate story generation"""
    
    prompt = build_story_prompt(request, previous_summary)
    provider = get_llm_provider()
    
    if provider == "ollama":
        story = _call_ollama_story(prompt)
    elif provider == "huggingface":
        story = _call_huggingface_story(prompt)
    else:
        story = _call_openai_story(prompt)
    
    return sanitize_story_text(story, request.controls)
```

**3. Provider Implementations**

**OpenAI** - `_call_openai_story()`
```python
def _call_openai_story(prompt: str) -> StoryPayload:
    """Call OpenAI GPT-4"""
    
    client = get_openai_client()
    if not client:
        return StoryPayload(**STUB_STORY)
    
    response = client.chat.completions.create(
        model=SETTINGS.openai_model,
        messages=[
            {"role": "system", "content": "You are a bedtime storyteller..."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1200
    )
    
    content = response.choices[0].message.content
    payload_dict = json.loads(content)
    return StoryPayload(**payload_dict)
```

**Ollama** - `_call_ollama_story()`
```python
def _call_ollama_story(prompt: str) -> StoryPayload:
    """Call local Ollama model"""
    
    client = get_ollama_client()
    response = client.post("/api/generate", json={
        "model": SETTINGS.ollama_story_model,
        "prompt": f"You are StoriaAI...\n{prompt}",
        "stream": False,
        "options": {"temperature": 0.7}
    })
    
    # Extract JSON from response
    # Parse and return StoryPayload
```

**Hugging Face** - `_call_huggingface_story()`
```python
def _call_huggingface_story(prompt: str) -> StoryPayload:
    """Call Hugging Face Inference API"""
    
    client = get_huggingface_client()
    response = client.post(f"/models/{model}", json={
        "inputs": prompt,
        "parameters": {
            "temperature": 0.7,
            "max_new_tokens": 800
        },
        "options": {"wait_for_model": True}
    })
    
    # Extract and parse JSON
```

**4. Story Sanitization** - `sanitize_story_text()`
```python
def sanitize_story_text(
    story: StoryPayload,
    controls: ControlSettings
) -> StoryPayload:
    """Remove banned words and apply controls"""
    
    if controls.no_scary:
        # Replace scary words with safe alternatives
        # "paura" → "serenità"
        # "morte" → "riposo"
```

#### **Audio Synthesis Flow**

**1. Main Audio Function** - `render_audio_for_story()`
```python
def render_audio_for_story(
    story: StoryPayload,
    language: str,
    voice: Optional[str] = None
) -> AudioRenderResult:
    """Join story sections and synthesize audio"""
    
    full_text = "\n".join([
        story.intro,
        story.branch_1,
        story.branch_2,
        story.resolution,
        story.moral_summary
    ])
    
    return synthesize_audio(full_text, language, voice)
```

**2. Audio Provider Cascade** - `synthesize_audio()`
```python
def synthesize_audio(
    text: str,
    language: str,
    voice: Optional[str]
) -> AudioRenderResult:
    """Try providers in order until success"""
    
    # Priority 1: User-requested voice (Edge TTS)
    if voice:
        edge_result = _synthesize_audio_edge_tts(text, language, voice)
        if edge_result.audio_url:
            return edge_result
    
    # Priority 2: gTTS (free, always works)
    if SETTINGS.use_gtts:
        audio_url = _synthesize_audio_gtts(text, language)
        if audio_url:
            return AudioRenderResult(audio_url, "gtts")
    
    # Priority 3: Edge TTS with default voice
    edge_result = _synthesize_audio_edge_tts(text, language, None)
    if edge_result.audio_url:
        return edge_result
    
    # Priority 4: Premium providers (Murf, ElevenLabs)
    # ...
    
    # No audio generated
    return AudioRenderResult(None, None)
```

**3. Edge TTS Implementation** - `_synthesize_audio_edge_tts()`
```python
def _synthesize_audio_edge_tts(
    text: str,
    language: str,
    requested_voice: Optional[str]
) -> AudioRenderResult:
    """Generate audio via Microsoft Edge TTS"""
    
    # Resolve voice name from language or request
    voice_name = _resolve_edge_voice(language, requested_voice)
    
    # Async audio generation
    async def _generate() -> Optional[bytes]:
        communicator = edge_tts.Communicate(
            text=text,
            voice=voice_name,
            rate=SETTINGS.edge_tts_rate,
            pitch=SETTINGS.edge_tts_pitch
        )
        
        audio_chunks = bytearray()
        async for chunk in communicator.stream():
            if chunk["type"] == "audio":
                audio_chunks.extend(chunk["data"])
        
        return bytes(audio_chunks) if audio_chunks else None
    
    # Run async code in sync context
    audio_bytes = asyncio.run(_generate())
    
    # Encode as base64 MP3
    encoded = base64.b64encode(audio_bytes).decode("ascii")
    return AudioRenderResult(
        f"data:audio/mp3;base64,{encoded}",
        voice_name
    )
```

**4. gTTS Implementation** - `_synthesize_audio_gtts()`
```python
def _synthesize_audio_gtts(text: str, language: str) -> Optional[str]:
    """Generate audio via Google TTS (free)"""
    
    # Create temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
        tmp_path = tmp.name
    
    # Generate audio
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(tmp_path)
    
    # Read and encode
    with open(tmp_path, 'rb') as audio_file:
        audio_data = audio_file.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
    
    # Cleanup
    os.unlink(tmp_path)
    
    return f"data:audio/mp3;base64,{audio_base64}"
```

---

### 6. Provider Clients: `services/providers.py`

**Purpose**: Initialize and cache external API clients.

**Functions**:

```python
def get_llm_provider() -> str:
    """Return active LLM provider name"""
    return settings.llm_provider.lower()

def get_openai_client() -> Optional[OpenAI]:
    """Return OpenAI client if configured"""
    if get_llm_provider() != "openai":
        return None
    if settings.use_stub_providers or not settings.openai_api_key:
        return None
    return OpenAI(api_key=settings.openai_api_key)

def get_ollama_client() -> Optional[httpx.Client]:
    """Return HTTP client for Ollama"""
    if get_llm_provider() != "ollama":
        return None
    
    # Singleton pattern with headers for ngrok bypass
    global _OLLAMA_CLIENT
    if _OLLAMA_CLIENT is None:
        headers = {
            "ngrok-skip-browser-warning": "true",
            "User-Agent": "Mozilla/5.0..."
        }
        _OLLAMA_CLIENT = httpx.Client(
            base_url=settings.ollama_base_url,
            timeout=60,
            headers=headers
        )
    return _OLLAMA_CLIENT

def get_huggingface_client() -> Optional[httpx.Client]:
    """Return HTTP client for Hugging Face"""
    if get_llm_provider() != "huggingface":
        return None
    
    if not settings.huggingface_api_key:
        return None
    
    global _HUGGINGFACE_CLIENT
    if _HUGGINGFACE_CLIENT is None:
        headers = {
            "Authorization": f"Bearer {settings.huggingface_api_key}",
            "Accept": "application/json"
        }
        _HUGGINGFACE_CLIENT = httpx.Client(
            base_url=settings.huggingface_base_url,
            headers=headers,
            timeout=90
        )
    return _HUGGINGFACE_CLIENT
```

---

### 7. Quota Management: `services/quota.py`

**Purpose**: Enforce free tier limits (3 stories/day).

**Functions**:

```python
def get_or_create_parent(db: Session, email: str) -> Parent:
    """Get parent by hashed email or create new"""
    email_hash = hash_alias(email)
    parent = db.query(Parent).filter_by(email_hash=email_hash).first()
    
    if parent is None:
        parent = Parent(email_hash=email_hash, is_premium=False)
        db.add(parent)
        db.commit()
        db.refresh(parent)
    
    return parent

def check_and_increment_quota(db: Session, parent_id: str) -> bool:
    """Check quota and increment if allowed"""
    today = dt.date.today()
    
    quota = db.query(StoryQuota).filter_by(
        parent_id=parent_id,
        quota_date=today
    ).first()
    
    if quota is None:
        # First story today
        quota = StoryQuota(
            parent_id=parent_id,
            quota_date=today,
            story_count=1
        )
        db.add(quota)
        db.commit()
        return True
    
    if quota.story_count >= SETTINGS.max_free_stories_per_day:
        # Quota exceeded
        return False
    
    # Increment counter
    quota.story_count += 1
    db.commit()
    return True
```

---

### 8. Continuity: `services/continuity.py`

**Purpose**: Support story sequels using previous story state.

**Functions**:

```python
def upsert_child(
    db: Session,
    parent_id: str,
    alias_hash: str,
    language: str,
    age: int,
    interests: List[str],
    controls: dict
) -> Child:
    """Create or update child record"""
    child = db.query(Child).filter_by(
        parent_id=parent_id,
        alias_hash=alias_hash
    ).first()
    
    if child is None:
        child = Child(
            parent_id=parent_id,
            alias_hash=alias_hash,
            age=age,
            language=language,
            interests=interests,
            controls=controls
        )
        db.add(child)
    else:
        # Update existing
        child.age = age
        child.language = language
        child.interests = interests
        child.controls = controls
    
    db.commit()
    db.refresh(child)
    return child

def get_previous_story_summary(
    db: Session,
    child_id: str
) -> Optional[str]:
    """Retrieve most recent story summary for sequel"""
    
    # Get latest story with state
    story = db.query(Story).filter_by(child_id=child_id) \
        .order_by(Story.created_at.desc()) \
        .first()
    
    if not story or not story.state:
        return None
    
    # Build summary from state
    summary = story.state.summary
    if story.state.unresolved_threads:
        summary += "\nThreads: " + ", ".join(story.state.unresolved_threads)
    
    return summary
```

---

### 9. Summaries: `services/summaries.py`

**Purpose**: Generate story summaries for sequel continuity.

**Function**:

```python
def summarize_story(request: StorySummaryRequest) -> StorySummaryResponse:
    """Summarize story using OpenAI or fallback"""
    
    client = get_openai_client()
    if not client:
        # Fallback: Basic extraction
        return StorySummaryResponse(
            summary="Story continuation available",
            characters=["child"],
            moral="Be kind",
            unresolved_threads=[]
        )
    
    # Call OpenAI for smart summarization
    response = client.chat.completions.create(
        model=SETTINGS.openai_model,
        messages=[
            {
                "role": "system",
                "content": "Extract: summary, characters, moral, open threads"
            },
            {"role": "user", "content": request.story_text}
        ],
        temperature=0.3,
        max_tokens=300
    )
    
    # Parse JSON response
    content = response.choices[0].message.content
    data = json.loads(content)
    return StorySummaryResponse(**data)
```

---

### 10. Crypto: `services/crypto.py`

**Purpose**: Hash sensitive data for privacy.

```python
import hashlib

def hash_alias(text: str) -> str:
    """SHA-256 hash for email/name privacy"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()
```

---

### 11. Database: `database.py`

**Purpose**: SQLAlchemy engine and session management.

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import get_settings

SETTINGS = get_settings()

# Create engine
engine = create_engine(
    SETTINGS.database_url,
    echo=SETTINGS.database_echo,
    connect_args={"check_same_thread": False}  # SQLite only
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

def init_db() -> None:
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency injection for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 🌐 Frontend Deep Dive

### File: `frontend/index.html`

**Structure**:
```html
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>StoriaAI - Storie della Buonanotte</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- Background 3D effects (Vanta.js) -->
    <div id="vanta-background"></div>
    
    <!-- Main container -->
    <div class="container">
        <header>
            <h1>✨ StoriaAI</h1>
            <p>Storie Magiche della Buonanotte</p>
        </header>
        
        <!-- Story Generation Form -->
        <form id="story-form">
            <div class="form-group">
                <label>Email Genitore</label>
                <input type="email" name="parent_email" required>
            </div>
            
            <div class="form-group">
                <label>Nome Bambino</label>
                <input type="text" name="child_name" required>
            </div>
            
            <div class="form-group">
                <label>Età</label>
                <input type="number" name="age" min="2" max="12" required>
            </div>
            
            <div class="form-group">
                <label>Umore</label>
                <input type="text" name="mood" placeholder="curioso, stanco, felice...">
            </div>
            
            <div class="form-group">
                <label>Interessi</label>
                <input type="text" name="interests" placeholder="draghi, calcio, principesse...">
            </div>
            
            <div class="form-group">
                <label>Lingua</label>
                <select name="language">
                    <option value="it">🇮🇹 Italiano</option>
                    <option value="en">🇬🇧 English</option>
                    <option value="es">🇪🇸 Español</option>
                    <option value="fr">🇫🇷 Français</option>
                    <option value="ar">🇸🇦 العربية</option>
                </select>
            </div>
            
            <div class="checkbox-group">
                <label><input type="checkbox" name="no_scary" checked> Niente paura</label>
                <label><input type="checkbox" name="kindness_lesson" checked> Lezione di gentilezza</label>
                <label><input type="checkbox" name="italian_focus"> Focus italiano</label>
                <label><input type="checkbox" name="educational"> Educativo</label>
            </div>
            
            <button type="submit" class="btn-generate">✨ Crea Storia Magica</button>
        </form>
        
        <!-- Loading Animation -->
        <div id="loading" style="display: none;">
            <div class="book-animation">📖</div>
            <p>Creazione storia in corso...</p>
        </div>
        
        <!-- Story Display -->
        <div id="story-container" style="display: none;">
            <h2>La Tua Storia</h2>
            <div id="story-content"></div>
            
            <!-- Audio Player -->
            <audio id="audio-player" controls>
                <source id="audio-source" type="audio/mp3">
            </audio>
            
            <button id="download-story">📥 Scarica Storia</button>
        </div>
    </div>
    
    <!-- JavaScript Libraries -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.waves.min.js"></script>
    <script src="app.js"></script>
</body>
</html>
```

---

### File: `frontend/styles.css`

**Key Features**:

1. **3D Background Effects**
```css
#vanta-background {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
}
```

2. **Glass Morphism**
```css
.container {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
```

3. **Animations**
```css
@keyframes bookFlip {
    0%, 100% { transform: rotateY(0deg); }
    50% { transform: rotateY(180deg); }
}

.book-animation {
    animation: bookFlip 2s infinite;
}
```

4. **Responsive Design**
```css
@media (max-width: 768px) {
    .container {
        padding: 20px;
        margin: 10px;
    }
}
```

---

### File: `frontend/app.js`

**Main Functions**:

#### 1. Initialize 3D Background
```javascript
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Vanta.js waves effect
    VANTA.WAVES({
        el: "#vanta-background",
        mouseControls: true,
        touchControls: true,
        gyroControls: false,
        minHeight: 200.00,
        minWidth: 200.00,
        scale: 1.00,
        scaleMobile: 1.00,
        color: 0x23153c,
        shininess: 30.00,
        waveHeight: 15.00,
        waveSpeed: 0.75,
        zoom: 0.65
    });
});
```

#### 2. Form Submission Handler
```javascript
document.getElementById('story-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('story-container').style.display = 'none';
    
    // Collect form data
    const formData = new FormData(e.target);
    const request = {
        parent_email: formData.get('parent_email'),
        child: {
            name: formData.get('child_name'),
            age: parseInt(formData.get('age')),
            mood: formData.get('mood'),
            interests: formData.get('interests').split(',').map(s => s.trim())
        },
        controls: {
            no_scary: formData.get('no_scary') === 'on',
            kindness_lesson: formData.get('kindness_lesson') === 'on',
            italian_focus: formData.get('italian_focus') === 'on',
            educational: formData.get('educational') === 'on'
        },
        language: formData.get('language'),
        target_duration_minutes: 7,
        sequel: false
    };
    
    try {
        // Call API
        const response = await fetch('http://localhost:8000/generate_story', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // Display story
        displayStory(data);
        
    } catch (error) {
        console.error('Error:', error);
        alert('Errore nella generazione della storia. Riprova.');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
});
```

#### 3. Story Display
```javascript
function displayStory(data) {
    const container = document.getElementById('story-content');
    const story = data.story;
    
    // Build story HTML
    let html = `
        <div class="story-section">
            <h3>Inizio</h3>
            <p>${story.intro}</p>
        </div>
        
        <div class="story-section">
            <h3>${story.choice_1_prompt}</h3>
            <ul>
                ${story.choice_1_options.map(opt => `<li>${opt}</li>`).join('')}
            </ul>
            <p>${story.branch_1}</p>
        </div>
        
        <div class="story-section">
            <h3>${story.choice_2_prompt}</h3>
            <ul>
                ${story.choice_2_options.map(opt => `<li>${opt}</li>`).join('')}
            </ul>
            <p>${story.branch_2}</p>
        </div>
        
        <div class="story-section">
            <h3>Fine</h3>
            <p>${story.resolution}</p>
        </div>
        
        <div class="story-moral">
            <strong>Morale:</strong> ${story.moral_summary}
        </div>
    `;
    
    if (story.suggested_sequel_hook) {
        html += `
            <div class="sequel-hook">
                <em>Prossima avventura: ${story.suggested_sequel_hook}</em>
            </div>
        `;
    }
    
    container.innerHTML = html;
    
    // Set audio source
    if (data.audio_url) {
        document.getElementById('audio-source').src = data.audio_url;
        document.getElementById('audio-player').load();
    }
    
    // Show story container
    document.getElementById('story-container').style.display = 'block';
    
    // Scroll to story
    container.scrollIntoView({ behavior: 'smooth' });
}
```

#### 4. Download Story
```javascript
document.getElementById('download-story').addEventListener('click', () => {
    const content = document.getElementById('story-content').innerText;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'storia.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});
```

---

## 🔄 Data Flow Diagram

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ 1. POST /generate_story
       │    {parent_email, child, controls, language}
       ↓
┌──────────────────────────────────────────────────────┐
│                    FastAPI (main.py)                  │
│  ┌────────────────────────────────────────────────┐  │
│  │  generate_story_endpoint()                     │  │
│  │  - Validate request (Pydantic)                 │  │
│  │  - Get/create parent (quota.py)                │  │
│  │  - Check quota                                  │  │
│  │  - Hash child alias (crypto.py)                │  │
│  │  - Upsert child record                         │  │
│  └────────────────────────────────────────────────┘  │
└───────────────────┬──────────────────────────────────┘
                    │ 2. Generate story
                    ↓
┌──────────────────────────────────────────────────────┐
│              Story Engine (story_engine.py)           │
│  ┌────────────────────────────────────────────────┐  │
│  │  generate_story()                              │  │
│  │  - Build prompt                                │  │
│  │  - Select provider (openai/ollama/hf)         │  │
│  │  - Call LLM API or return STUB                 │  │
│  │  - Parse JSON response                         │  │
│  │  - Sanitize content                            │  │
│  └────────────────────────────────────────────────┘  │
└───────────────────┬──────────────────────────────────┘
                    │ 3. Generate audio
                    ↓
┌──────────────────────────────────────────────────────┐
│              Audio Synthesis (story_engine.py)        │
│  ┌────────────────────────────────────────────────┐  │
│  │  render_audio_for_story()                      │  │
│  │  - Join story sections                         │  │
│  │  - Try Edge TTS (requested voice)              │  │
│  │  - Fallback to gTTS                            │  │
│  │  - Encode as base64 MP3                        │  │
│  │  - Return AudioRenderResult                    │  │
│  └────────────────────────────────────────────────┘  │
└───────────────────┬──────────────────────────────────┘
                    │ 4. Save to database
                    ↓
┌──────────────────────────────────────────────────────┐
│                 Database (models.py)                  │
│  - Create Story record                                │
│  - Store request, story_json, audio_url, voice        │
│  - Generate summary (summaries.py)                    │
│  - Create StoryState (for sequels)                    │
│  - Log UsageMetric                                    │
└───────────────────┬──────────────────────────────────┘
                    │ 5. Return response
                    ↓
┌──────────────────────────────────────────────────────┐
│                    Response JSON                      │
│  {                                                    │
│    story_id: "uuid",                                  │
│    audio_url: "data:audio/mp3;base64,...",            │
│    language: "it",                                    │
│    duration_minutes: 7,                               │
│    voice: "gtts",                                     │
│    story: {                                           │
│      intro: "...",                                    │
│      choice_1_prompt: "...",                          │
│      ...                                              │
│    },                                                 │
│    created_at: "2025-11-13T12:14:33.748706"          │
│  }                                                    │
└───────────────────┬──────────────────────────────────┘
                    │ 6. Render in browser
                    ↓
┌──────────────────────────────────────────────────────┐
│                  Frontend (app.js)                    │
│  - Parse JSON response                                │
│  - Display story sections                             │
│  - Load audio in <audio> element                      │
│  - Enable download button                             │
└──────────────────────────────────────────────────────┘
```

---

## 📡 API Reference

### `POST /generate_story`

**Request Body**:
```json
{
  "parent_email": "parent@example.com",
  "child": {
    "name": "Luca",
    "age": 6,
    "mood": "curioso",
    "interests": ["draghi", "calcio"]
  },
  "controls": {
    "no_scary": true,
    "kindness_lesson": true,
    "italian_focus": true,
    "educational": false
  },
  "language": "it",
  "target_duration_minutes": 7,
  "sequel": false,
  "voice": "it-IT-IsabellaNeural"
}
```

**Response** (200 OK):
```json
{
  "story_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "audio_url": "data:audio/mp3;base64,//uQx...",
  "language": "it",
  "duration_minutes": 7,
  "voice": "gtts",
  "story": {
    "intro": "Ciao Luca! Questa è una storia magica...",
    "choice_1_prompt": "Vuoi seguire il drago o il cavaliere?",
    "choice_1_options": ["Drago", "Cavaliere"],
    "branch_1": "Il drago ti porta in un regno di nuvole...",
    "choice_2_prompt": "Preferisci giocare a calcio o esplorare?",
    "choice_2_options": ["Calcio", "Esplorare"],
    "branch_2": "Nel campo magico, il pallone brilla...",
    "resolution": "La notte finisce con un sorriso e sogni felici.",
    "moral_summary": "La curiosità rende ogni avventura speciale.",
    "suggested_sequel_hook": "Domani il drago tornerà per un'altra avventura!"
  },
  "created_at": "2025-11-13T12:14:33.748706"
}
```

**Error Responses**:
- `402 Payment Required`: Quota exceeded
- `422 Unprocessable Entity`: Invalid request data
- `500 Internal Server Error`: Story generation failed

---

### Other Endpoints

**`GET /health`**
- Response: `{"status": "ok", "timestamp": "..."}`

**`POST /summarize_story`**
- Input: `{"story_text": "..."}`
- Output: `{"summary": "...", "characters": [...], "moral": "...", "unresolved_threads": [...]}`

**`POST /validate_story`**
- Input: `{"story_text": "..."}`
- Output: `{"safe": true, "issues": []}`

**`POST /consent`**
- Input: `{"parent_email": "...", "consent_version": "1.0", "ip_address": "..."}`
- Output: `{"status": "recorded"}`

**`POST /delete_user_data`**
- Input: `{"parent_email": "..."}`
- Output: `{"status": "deleted"}`

**`POST /metrics`**
- Input: `{"event_type": "...", "payload": {...}}`
- Output: `{"status": "accepted"}`

---

## 🔍 Key Design Decisions

### 1. **Stub Mode for Demo**
- Allows testing without API keys
- STUB_STORY provides consistent demo content
- Production-ready architecture underneath

### 2. **Audio Fallback Chain**
- User-requested voice → gTTS → Edge TTS default → Premium
- Ensures audio always generates (gTTS never fails)
- Graceful degradation

### 3. **Privacy by Design**
- Email and names are hashed (SHA-256)
- No plaintext PII in database
- GDPR-compliant data deletion

### 4. **Multi-Provider Architecture**
- Abstract provider interface
- Easy to add new LLM/TTS providers
- Failover support

### 5. **Quota System**
- Daily limits per parent
- Premium flag for unlimited access
- Date-based partitioning

### 6. **Sequel Support**
- StoryState preserves context
- Characters, plot threads, moral continuity
- Optional feature

### 7. **Static Frontend**
- No build process required
- Works offline (after first load)
- Easy deployment (S3, Netlify, GitHub Pages)

### 8. **Base64 Audio Embedding**
- No file storage needed
- Self-contained responses
- Works with CORS restrictions

---

## 🚀 Running the Application

### Development Mode

**Terminal 1 - Backend**:
```bash
cd backend
source ../.venv/Scripts/activate  # Windows
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend**:
```bash
# Open frontend/index.html in browser
# OR use a simple HTTP server:
cd frontend
python -m http.server 3000
```

### Production Mode

**Option 1: Windows Launcher**
```bash
START_APP.bat
```

**Option 2: Manual Start**
```bash
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Then open `frontend/index.html` or deploy to web server.

---

## 🧪 Testing

**Run Test Suite**:
```bash
.venv\Scripts\python.exe -m pytest backend/tests -v
```

**Test Coverage**:
- Health endpoint
- Story generation (stub mode)
- Quota enforcement
- Rate limit handling
- OpenAI fallback behavior

**Manual API Testing**:
```powershell
# PowerShell
$body = @{
    parent_email = "test@example.com"
    child = @{
        name = "Luca"
        age = 6
        mood = "curioso"
        interests = @("draghi")
    }
    language = "it"
    target_duration_minutes = 7
    sequel = $false
}

Invoke-RestMethod -Uri "http://localhost:8000/generate_story" `
    -Method Post `
    -Body ($body | ConvertTo-Json -Depth 5) `
    -ContentType "application/json"
```

---

## 📦 Dependencies Summary

### Backend Core
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation
- **sqlalchemy**: ORM
- **httpx**: HTTP client

### AI/ML
- **transformers**: Hugging Face models
- **openai**: OpenAI SDK (optional)

### Audio
- **gtts**: Google TTS (free)
- **edge-tts**: Microsoft Edge TTS (free)

### Testing
- **pytest**: Test framework
- **pytest-asyncio**: Async test support

### Frontend
- **three.js**: 3D graphics library
- **vanta.js**: Background effects

---

## 🔐 Environment Variables

```env
# LLM Provider
LLM_PROVIDER=huggingface  # openai | ollama | huggingface
OFFLINE_MODE=true          # Use stub stories

# OpenAI (Optional)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini

# Ollama (Optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_STORY_MODEL=mistral

# Hugging Face (Optional)
HUGGINGFACE_API_KEY=hf_...
HUGGINGFACE_STORY_MODEL=mistralai/Mixtral-8x7B-Instruct

# TTS
USE_GTTS=true
EDGE_TTS_ENABLED=true

# Database
DATABASE_URL=sqlite:///./storiaai.db

# Quota
MAX_FREE_STORIES_PER_DAY=3
```

---

## 📈 Performance Considerations

### Response Times
- **Stub mode**: ~500ms (database + gTTS)
- **OpenAI**: ~3-5s (API call + audio)
- **Ollama**: ~10-30s (local inference + audio)
- **Hugging Face**: ~5-10s (API + model loading + audio)

### Bottlenecks
1. **LLM API calls**: Longest part (3-30s)
2. **Audio synthesis**: 1-3s for gTTS, 2-5s for Edge TTS
3. **Base64 encoding**: <100ms
4. **Database writes**: <50ms

### Optimizations
- Audio caching (future)
- Background processing (Celery)
- CDN for audio files
- Database connection pooling
- Async audio generation

---

## 🐛 Common Issues & Solutions

### Issue: Edge TTS returns 403
**Cause**: No valid TrustedClient token
**Solution**: Falls back to gTTS automatically, or disable Edge TTS in config

### Issue: Quota exceeded
**Cause**: Parent has generated 3 stories today
**Solution**: Set `is_premium=True` or wait until tomorrow

### Issue: Story generation slow
**Cause**: Using Ollama with large model
**Solution**: Use smaller model or switch to OpenAI/Hugging Face

### Issue: Audio not playing
**Cause**: Browser doesn't support base64 audio
**Solution**: Save audio to file and serve via URL

### Issue: CORS error
**Cause**: Frontend and backend on different origins
**Solution**: CORS is configured for `*`, check browser console

---

## 🎯 Next Steps

This overview covers the complete architecture. In the next step, we'll dive deeper into:

1. **Backend Function-by-Function Analysis**
   - Line-by-line code explanation
   - Parameter details
   - Return value analysis
   - Edge case handling

2. **Database Schema Deep Dive**
   - Relationships and cascades
   - Indexing strategy
   - Migration considerations

3. **Frontend Component Breakdown**
   - Event handling details
   - State management
   - Error handling

4. **Integration Patterns**
   - Request/response flow
   - Error propagation
   - Retry logic

5. **Deployment Guide**
   - Production configuration
   - Scaling strategies
   - Monitoring setup

---

**Ready to proceed with the detailed backend function analysis?**
