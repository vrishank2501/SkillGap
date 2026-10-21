# SkillBridge AI

> **A BYO-AI (Bring Your Own API Key) personalized skill-gap learning platform.**  
> Upload your study materials, chat with an AI tutor grounded in your own content, take adaptive quizzes, and track your progress — all powered by your own Gemini or OpenAI account.

---

## ✨ Features

| Feature | Status |
|---|---|
| PDF/document upload & parsing | ✅ Done |
| Full-text document search (PostgreSQL FTS) | ✅ Done |
| BYO-AI: Gemini + OpenAI key support | ✅ Done |
| Skill-based AI commands (`/quiz`, `/explain`, `/summarize`, `/answer`) | ✅ Done |
| Progress tracking (Supabase) | ✅ Done |
| Demo mode (no key required) | ✅ Done |
| Dark-mode single-page UI (Tailwind, no framework) | ✅ Done |
| Quiz renderer with interactive MCQ UI | ✅ Done |

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11+, FastAPI, Uvicorn |
| **AI Providers** | Google Gemini (`google-genai` v2), OpenAI (`openai` v1) |
| **Database** | Supabase (PostgreSQL + Row Level Security) |
| **Document Parsing** | PyMuPDF (PDF text extraction + chunking) |
| **Search** | PostgreSQL Full-Text Search (`tsvector`) |
| **Frontend** | Single HTML file, Tailwind CSS (CDN), Vanilla JS |
| **Auth** | Supabase Auth (JWT, Row Level Security) |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/skillbridge-ai.git
cd skillbridge-ai
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 3. Set Up Database

Run the migration in your Supabase SQL editor:

```
supabase/migrations/001_initial.sql
```

### 4. Run the App

```bash
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000** in your browser.

---

## 🔑 BYO-AI Setup

You do **not** need a pre-configured server API key. Instead:

1. Go to [aistudio.google.com](https://aistudio.google.com) → **Get API Key** (free)  
   _or_ [platform.openai.com](https://platform.openai.com) → **API Keys** (requires prepaid credits)
2. Paste your key into the **top navigation bar** of the app
3. Click **⚡** to test the connection
4. Start chatting!

> **Working Gemini models** (as of Oct 2026): `gemini-3.5-flash` (fastest), `gemini-flash-latest`, `gemini-3.8-flash`  
> **Note:** `gemini-1.5-flash`, `gemini-2.0-flash` and `gemini-2.5-flash` are no longer available to new API keys.

---

## 💬 Slash Commands

| Command | Description |
|---|---|
| `/explain [topic]` | Explain a topic grounded in your uploaded documents |
| `/quiz [topic]` | Generate an interactive MCQ quiz |
| `/summarize [topic]` | Summarize content from your materials |
| `/answer [question]` | Get a direct answer from your documents |
| `/progress` | View your learning progress stats |
| `/recommend` | Get a personalized next-lesson recommendation |

---

## 📁 Project Structure

```
skill_GAP/
├── app/
│   ├── api/            # FastAPI route handlers
│   │   ├── chat.py         # Main chat endpoint + command routing
│   │   ├── documents.py    # File upload & management
│   │   ├── progress.py     # Progress REST API
│   │   └── providers.py    # BYO-AI key validation endpoint
│   ├── core/           # Config & Supabase client
│   ├── documents/      # PDF parser + FTS search
│   ├── harness/        # Skill loader, command router, prompt builder
│   ├── progress/       # Supabase progress tracking logic
│   ├── providers/      # AI provider wrappers (Gemini, OpenAI, Demo)
│   └── ui/             # index.html (single-page frontend)
├── skills/             # SKILL.md definition files (prompt instructions)
│   ├── answer_question/
│   ├── explain_concept/
│   ├── generate_quiz/
│   ├── get_learning_progress/
│   ├── recommend_next_lesson/
│   └── summarize_content/
├── supabase/
│   └── migrations/     # SQL schema
├── data/documents/     # Local document storage (gitignored)
├── tests/              # Pytest test suite
├── .env.example        # Environment variable template
├── requirements.txt
└── README.md
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## ⚙️ Environment Variables

See [`.env.example`](.env.example) for all variables. Key ones:

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (backend only) |
| `SUPABASE_ANON_KEY` | Supabase anon key |
| `DATABASE_URL` | Direct PostgreSQL connection string |
| `DEFAULT_GEMINI_API_KEY` | Optional fallback key (leave empty for BYO-only) |
| `DEFAULT_OPENAI_API_KEY` | Optional fallback key (leave empty for BYO-only) |

---

## 📄 License

MIT

