# StoriaAI Backend

FastAPI backend powering the StoriaAI bedtime storytelling MVP.

## Features
- Configurable LLM provider (OpenAI, Hugging Face Inference, or local Ollama) for Italian bedtime storytelling.
- ElevenLabs integration for Italian voice narration (configurable).
- SQLite persistence for parents, children, stories, continuity state, and quotas.
- Freemium quota enforcement (3 stories/day per parent email by default).
- GDPR-friendly endpoints for consent logging and data deletion.
- Basic safety validation heuristics and banned-word filtering.

## Getting Started
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add provider configuration:
   ```env
   LLM_PROVIDER=openai       # set to "huggingface" or "ollama" if you prefer those
   OPENAI_API_KEY=sk-...     # required when LLM_PROVIDER=openai
   HUGGINGFACE_API_KEY=hf_... # required when LLM_PROVIDER=huggingface
   HUGGINGFACE_TTS_MODEL=suno/bark-small
   ELEVENLABS_API_KEY=...
   ELEVENLABS_VOICE_ID=bella
   MURF_API_KEY=...
   MURF_VOICE_ID=...
   ```
   When keys are missing, the app operates in stub mode (static stories, no audio). For Ollama, install [Ollama](https://ollama.com/) and run `ollama run mistral` to download the default model, then keep the Ollama server running. For Hugging Face, create a token at https://huggingface.co/settings/tokens (read access) and ensure the chosen models are available via the Inference API (e.g., `tiiuae/falcon-7b-instruct` for text and `suno/bark-small` for audio). For Murf, generate an API key at https://murf.ai/api/api-keys and set an available voice ID from their catalog.
4. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Open `http://127.0.0.1:8000/docs` for interactive Swagger UI.

## Running Tests
```bash
pytest
```

## Environment Variables
See `app/config.py` for tunable settings. Key ones include:
- `LLM_PROVIDER` (`openai`, `huggingface`, or `ollama`)
- `OPENAI_API_KEY` / `OPENAI_MODEL`
- `HUGGINGFACE_API_KEY` / `HUGGINGFACE_*`
- `OLLAMA_BASE_URL` / `OLLAMA_STORY_MODEL` / `OLLAMA_SUMMARY_MODEL`
- `ELEVENLABS_API_KEY` / `ELEVENLABS_VOICE_ID`
- `DATABASE_URL`
- `MAX_FREE_STORIES_PER_DAY`
- `OFFLINE_MODE` (forces stub providers when set to true)

## Deployment Notes
- Designed for Replit or Vercel serverless (may require adjusting database connection).
- For production, replace SQLite with PostgreSQL and configure persistent storage for audio files (e.g., Supabase Storage or S3).
- Ensure environment variables are set securely and HTTPS is enforced.
