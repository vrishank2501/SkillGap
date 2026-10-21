# Workspace Setup

Use this guide when you first open the SkillBridge AI workspace and whenever you return to it.

## First-Time Setup

1. Open a terminal at the repository root (`/workspaces/SkillGap`).
2. Create the local Python environment and install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

3. Create `.env` from the template if it does not already exist:

   ```bash
   cp .env.example .env
   ```

   Keep `.env` local. It is gitignored and must not be committed.

4. Supabase is optional. To enable Supabase-backed document search and progress storage, set the following values in `.env`:

   ```dotenv
   SUPABASE_URL=https://YOUR_PROJECT.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=YOUR_PRIVATE_SERVICE_ROLE_KEY
   ```

   The service-role key is backend-only; never put it in frontend code or share it publicly. You can instead set `SUPABASE_ANON_KEY` if you do not use a service-role key. Keep `DATABASE_URL` blank unless your deployment specifically needs it. The app's default Gemini/OpenAI server keys are optional because users can provide their own keys in the UI.

5. In the Supabase SQL Editor, run the initial schema migration:

   ```text
   supabase/migrations/001_initial.sql
   ```

## Each Time You Reopen

1. Open the repository folder and a terminal at its root.
2. Activate the existing environment. If `.venv` is missing, repeat First-Time Setup steps 2-3.

   ```bash
   source .venv/bin/activate
   ```

3. Start the development server:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Open <http://localhost:8000>; the workspace loads directly without sign-in.
5. Add a Gemini or OpenAI API key in the top navigation when you want to use that provider. Demo mode can be selected from the app's provider fallback action and does not require an AI key.

Keep the server terminal running while using the app. Stop it with `Ctrl+C` when finished.
The app has no user authentication or per-visitor data isolation. Keep it local or restrict network access rather than exposing it as a public multi-user service.

## Quick Checks

With the server running, these endpoints should respond:

```bash
curl -fsS http://127.0.0.1:8000/api/health
```

The health endpoint should report `healthy`. API routes are available without an authentication token.

Run the automated tests from the repository root:

```bash
python -m pytest tests/ -v
```

## Troubleshooting

- **Supabase-backed data writes fail:** verify `SUPABASE_URL` and the backend Supabase key are set, then check that the initial migration ran successfully.
- **Port 8000 is already in use:** start with `uvicorn app.main:app --reload --host 0.0.0.0 --port 8001` and open <http://localhost:8001>.
- **Dependency imports fail:** activate `.venv` and run `python -m pip install -r requirements.txt` again.
