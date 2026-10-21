# SkillBridge AI — What's Done ✅

> Last updated: 21 October 2026  
> Status: **MVP functional** — core chat, BYO-AI, quiz, progress tracking all working.

---

## 1. Backend — FastAPI Application

### `app/main.py`
- FastAPI app with CORS middleware
- Static file serving for the single-page UI at `/`
- All routers registered: `chat`, `documents`, `progress`, `providers`, `health`

### `app/core/config.py`
- `pydantic-settings` config object loading from `.env`
- Exposes: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SKILLS_DIR`, `DOCUMENT_STORAGE_DIR`, `DEFAULT_GEMINI_API_KEY`, `DEFAULT_OPENAI_API_KEY`

### `app/core/supabase.py`
- Lazy Supabase client factory (`get_supabase_client()`)
- Gracefully returns `None` if credentials not configured (app still works locally)

---

## 2. AI Provider System (BYO-AI)

### `app/providers/base.py`
- `BaseAIProvider` abstract class with `generate_text()`, `generate_structured()`, `validate_connection()`

### `app/providers/gemini_provider.py`
- `GeminiProvider` using `google-genai` v2.32.0 SDK
- Supports `google-genai` (new) and `google-generativeai` (legacy) SDKs
- Confirmed working models: `gemini-3.5-flash` (default, ~6.7s), `gemini-flash-latest`, `gemini-3.8-flash`
- `_map_gemini_error()` helper: maps raw SDK errors → user-friendly messages (404, 429, 403, API_KEY_INVALID)
- `validate_connection()` uses a real 1-token generation call (not `models.get()` which 404s on v1beta)

### `app/providers/openai_provider.py`
- `OpenAIProvider` using `openai` v1 SDK
- Supports `gpt-4o-mini` (default), `gpt-4o`, `gpt-3.5-turbo`
- Friendly error messages for quota exhaustion and invalid keys
- Advises users to add billing credits at `platform.openai.com`

### `app/providers/demo_provider.py`
- `DemoProvider` — no API key required
- Returns skill-harness-based static responses for testing all commands without a real LLM

### `app/providers/__init__.py`
- `get_provider(provider_name, api_key, model)` factory function

---

## 3. API Endpoints

### `POST /api/chat/`
- Accepts: `message`, `provider`, `api_key`, `model`, `session_id`, `user_id`
- Resolves API key (BYO > `.env` default > error)
- Routes to Command Router → selects skill → builds prompt → calls LLM
- Handles `/progress` and `/recommend` commands without LLM calls
- Falls back to text if JSON generation fails (quiz command)
- Persists messages to Supabase if session active

### `POST /api/providers/validate`
- Validates a BYO key in real time
- Returns `{ valid, latency_ms, model }` or `{ valid: false, error: "..." }`

### `GET /api/providers/models`
- Returns current list of supported models per provider

### `POST /api/documents/upload`
- Accepts PDF/text files up to 25MB
- Parses with PyMuPDF, chunks text, stores to Supabase `document_chunks`

### `GET /api/documents/`
- Lists user's uploaded documents

### `DELETE /api/documents/{id}`
- Deletes document + chunks from Supabase

### `GET /api/progress/{user_id}`
- Returns progress summary from Supabase

### `GET /api/health`
- Health check endpoint

---

## 4. Skill Harness

### `app/harness/skill_loader.py`
- Loads `SKILL.md` files from `skills/` directory
- Parses YAML frontmatter (name, command, version, description)
- Caches skills in memory; hot-reloadable

### `app/harness/command_router.py`
- Detects slash commands (`/quiz`, `/explain`, `/summarize`, `/answer`, `/progress`, `/recommend`)
- Extracts parameters (topic, difficulty, question_count)
- Falls back to natural-language routing if no command matched

### `app/harness/prompt_builder.py`
- `build_system_instruction()` — wraps skill instructions into system prompt
- `build_user_prompt()` — injects document excerpts as grounded context

---

## 5. Skills Defined (`skills/`)

| Skill | Command | Description |
|---|---|---|
| `answer_question` | `/answer` | Direct Q&A from documents |
| `explain_concept` | `/explain` | Detailed concept explanation |
| `generate_quiz` | `/quiz` | MCQ quiz generator (structured JSON output) |
| `get_learning_progress` | `/progress` | Progress summary |
| `recommend_next_lesson` | `/recommend` | Next-lesson recommendation |
| `summarize_content` | `/summarize` | Content summarization |

---

## 6. Document Pipeline

### `app/documents/parser.py`
- PyMuPDF-based PDF parser
- Chunks text at ~500 characters with 50-character overlap
- Preserves page numbers per chunk

### `app/documents/search.py`
- PostgreSQL Full-Text Search using `tsvector` + `plainto_tsquery`
- Returns top-K ranked chunks with page number and score
- Falls back to local file scan if Supabase unavailable

---

## 7. Database Schema (`supabase/migrations/001_initial.sql`)

| Table | Purpose |
|---|---|
| `profiles` | User profile, preferred provider, skill goal |
| `documents` | Uploaded file metadata |
| `document_chunks` | Parsed text chunks with `tsvector` for FTS |
| `sessions` | Chat session grouping |
| `messages` | Chat history (user + assistant turns) |
| `user_progress` | Topic-level progress (status, best score) |
| `quiz_attempts` | Per-quiz attempt records with auto-computed `percentage` |
| `daily_activity` | Streak tracking (one row per user per day) |

All tables have **Row Level Security (RLS)** enabled with per-user access policies.

---

## 8. Frontend (`app/ui/index.html`)

Single-file dark-mode UI (~900 lines, Tailwind CSS via CDN, Vanilla JS):

- **BYO-AI key inputs**: Gemini key, OpenAI key, model selectors, test-connection (⚡) buttons, visibility toggles
- **Chat interface**: Markdown rendering, loading states, error banners
- **Quiz renderer**: Interactive MCQ cards rendered from structured JSON
- **Document upload panel**: Drag-drop or file picker, upload progress
- **Progress display**: Inline stats via `/progress` command response
- **Provider toggle**: Switch between Gemini / OpenAI / Demo Mode
- **Key persistence**: `localStorage` saves entered keys across sessions

---

## 9. Tests (`tests/`)

| File | Tests |
|---|---|
| `test_providers.py` | Provider factory, validation flow |
| `test_harness.py` | Skill loading, command routing, prompt building |
| `test_parser.py` | PDF chunk extraction |
| `test_progress.py` | Progress summary and recommendation logic |

