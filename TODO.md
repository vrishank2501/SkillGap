# SkillBridge AI — What Needs To Be Done 🛠️

> Last updated: 21 October 2026  
> Priority: 🔴 High · 🟡 Medium · 🟢 Nice-to-have

---

## 🔴 P1 — Core UX / Blockers

### 1. Real Supabase Auth (User Login)
**Current state:** All requests use `user_id = "dev-user-01"` hardcoded. No actual login.  
**What to build:**
- Supabase Auth email/password sign-up and login flow
- JWT token sent with every API request via `Authorization: Bearer <token>` header
- Backend reads user ID from token instead of hardcoded value
- `profiles` table auto-populated on first login (Supabase trigger or `/onboarding` endpoint)

**Files to change:** `app/ui/index.html` (login screen), `app/api/chat.py` (auth middleware), `app/core/supabase.py`

---

### 2. Document Upload Working End-to-End
**Current state:** Upload API exists; Supabase insert may fail silently if RLS blocks `dev-user-01` UUID.  
**What to build:**
- Confirm `document_chunks` insert works with real UUID from auth
- Add upload progress bar in UI (currently placeholder)
- Show uploaded document list in sidebar with delete button
- Handle duplicate file names gracefully

**Files to change:** `app/api/documents.py`, `app/ui/index.html`

---

### 3. Document-Grounded Search Reliability
**Current state:** `document_search.search()` hits Supabase FTS. Falls back to local file if Supabase unavailable.  
**What to build:**
- Verify FTS returns relevant chunks (test with real uploaded PDFs)
- Add minimum relevance threshold (discard chunks with score < 0.1)
- Handle case where user has no documents uploaded (show helpful "upload a document first" message instead of hallucinated response)

**Files to change:** `app/documents/search.py`, `app/api/chat.py`

---

### 4. Quiz Interaction — Answer Submission & Scoring
**Current state:** Quiz cards render in UI. Answer selection and score calculation not yet wired to backend.  
**What to build:**
- "Submit Answers" button collects selected options → `POST /api/quiz/submit`
- Backend compares against `correct_answer` field, calculates `score`
- Inserts row into `quiz_attempts` table
- Updates `user_progress` table (`quizzes_taken++`, `best_score`)
- Returns per-question feedback (correct/incorrect + explanation)
- UI shows results overlay with score badge

**New files needed:** `app/api/quiz.py`  
**Files to change:** `app/ui/index.html`, `app/progress/supabase_progress.py`

---

## 🟡 P2 — Important Features

### 5. Onboarding Flow
**What to build:**
- First-login screen: "What do you want to learn?" → saves to `profiles.target_skill_goal`
- "What's your learning style?" (visual / practical / conceptual) → `profiles.learning_style`
- This data feeds into the system prompt (personalizes all responses)

**Files to change:** `app/ui/index.html`, new `app/api/onboarding.py`

---

### 6. Progress Dashboard Screen
**Current state:** `/progress` command shows a markdown text summary in chat.  
**What to build:**
- Dedicated dashboard panel (or modal) with:
  - Topics studied list with status badges
  - Quiz accuracy bar chart (per topic)
  - Study streak counter with flame emoji 🔥
  - "Recommended next" card
- Fetch from `GET /api/progress/{user_id}`

**Files to change:** `app/ui/index.html`, `app/api/progress.py`

---

### 7. Chat History / Session Persistence
**Current state:** Messages saved to Supabase `messages` table if `session_id` present. UI doesn't load previous sessions.  
**What to build:**
- Sidebar "Recent Sessions" list from `GET /api/sessions/`
- Click session → loads message history into chat pane
- New session button creates fresh `session_id`
- Session title auto-generated from first message (LLM summary)

**New files needed:** `app/api/sessions.py`  
**Files to change:** `app/ui/index.html`

---

### 8. Skill Gap Detection (Core Product Feature)
**What to build:**
- "Analyse my skill gap" button or `/skillgap` command
- Compares user's uploaded materials against their stated `target_skill_goal`
- LLM generates a structured skill gap report: `{ known: [], gaps: [], priority: [] }`
- Displayed as a visual card with topic status chips
- Saves gap report to `user_progress` table as initial seed data

**New files needed:** `skills/skill_gap_analysis/SKILL.md`  
**Files to change:** `app/harness/command_router.py`, `app/ui/index.html`

---

### 9. Multi-Document Support Per User
**Current state:** Search queries all chunks for `user_id`. Works but no way to select/filter documents.  
**What to build:**
- Document selector in UI sidebar (toggle which docs to include in search)
- Passes `document_ids[]` filter to search endpoint
- Useful when user has e.g. a syllabus + a textbook and wants to chat about only one

**Files to change:** `app/documents/search.py`, `app/api/chat.py`, `app/ui/index.html`

---

### 10. Streaming Chat Responses
**Current state:** Full response returned as single JSON blob. For long answers this causes UI lag.  
**What to build:**
- Backend: `StreamingResponse` using `generate_content_stream()` (both Gemini and OpenAI support this)
- Frontend: `EventSource` or `fetch` with `ReadableStream` to render tokens as they arrive
- Shows typing indicator during stream

**Files to change:** `app/providers/gemini_provider.py`, `app/providers/openai_provider.py`, `app/api/chat.py`, `app/ui/index.html`

---

## 🟢 P3 — Polish & Nice-to-Have

### 11. Responsive / Mobile UI
**Current state:** UI designed for desktop.  
**What to build:**
- Collapsible sidebar for mobile
- Touch-friendly quiz card interaction
- Responsive grid for progress cards

---

### 12. PDF Viewer Panel
**What to build:**
- When a citation appears in a response, clicking it opens the relevant PDF page inline
- Use `pdf.js` (CDN) to render the PDF page in a side panel
- Highlights the cited passage

---

### 13. Export Progress Report
**What to build:**
- "Download PDF report" button
- Generates a PDF summary of: topics studied, quiz scores, skill gap analysis, recommended next steps
- Use `reportlab` or `fpdf2` Python library server-side

---

### 14. Add More AI Providers
**Current state:** Gemini and OpenAI only.  
**Options to add:**
- **Anthropic Claude** (`anthropic` SDK) — popular alternative
- **Groq** (OpenAI-compatible API, very fast free tier)
- Both just need a new provider class inheriting `BaseAIProvider`

---

### 15. Admin Dashboard
**What to build:**
- Simple read-only view of aggregate stats (total users, documents uploaded, quizzes taken)
- Only accessible with service-role Supabase credentials
- Could be a separate `/admin` FastAPI route with basic auth

---

## 📋 Priority Order for Next Sprint

```
1. Supabase Auth login (P1 #1)          → unblocks all user data isolation
2. Quiz submit + scoring (P1 #4)        → makes core product loop complete
3. Document upload E2E fix (P1 #2)      → needed for grounded responses
4. Skill Gap Detection (P2 #8)          → the actual "skill gap" feature
5. Onboarding flow (P2 #5)             → personalizes all prompts
6. Progress dashboard (P2 #6)          → shows users their improvement
7. Chat history (P2 #7)               → retention / returning users
8. Streaming responses (P2 #10)        → UX polish
```

