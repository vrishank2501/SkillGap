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

4. In `.env`, set the following values from your Supabase project:

   ```dotenv
   SUPABASE_URL=https://YOUR_PROJECT.supabase.co
   SUPABASE_ANON_KEY=YOUR_PUBLIC_ANON_KEY
   SUPABASE_SERVICE_ROLE_KEY=YOUR_PRIVATE_SERVICE_ROLE_KEY
   ```

   The anon key is used by browser sign-in. The service-role key is backend-only; never put it in frontend code or share it publicly. Keep `SUPABASE_JWT_SECRET` and `DATABASE_URL` blank unless your deployment specifically needs them. The app's default Gemini/OpenAI server keys are optional because users can provide their own keys in the UI.

5. In Supabase, enable the Email provider under Authentication settings. Choose whether email confirmation is required.
6. In the Supabase SQL Editor, run these migrations in order:

   ```text
   supabase/migrations/001_initial.sql
   supabase/migrations/002_auth_profiles.sql
   ```

   The second migration creates profile rows for new signups and backfills existing Auth users. It is safe to rerun.

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

4. Open <http://localhost:8000>. Sign in or create an account. If Supabase email confirmation is enabled, confirm the address before signing in.
5. Add a Gemini or OpenAI API key in the top navigation when you want to use that provider. Demo mode can be selected from the app's provider fallback action and does not require an AI key.

Keep the server terminal running while using the app. Stop it with `Ctrl+C` when finished.

## Quick Checks

With the server running, these endpoints should respond:

```bash
curl -fsS http://127.0.0.1:8000/api/health
curl -fsS http://127.0.0.1:8000/api/auth/config
```

The health endpoint should report `healthy`. The auth config endpoint should return your Supabase URL and anon key; it does not return the service-role key. A protected route should reject requests without a signed-in session token.

Run the automated tests from the repository root:

```bash
python -m pytest tests/ -v
```

## Troubleshooting

- **Login says Supabase Auth is not configured:** verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`, then restart the server.
- **Sign-up succeeds but sign-in does not:** check the user's email confirmation and the Supabase Email provider settings.
- **Profile insert or data writes fail:** make sure both migrations ran successfully and `SUPABASE_SERVICE_ROLE_KEY` is set in the backend `.env`.
- **Port 8000 is already in use:** start with `uvicorn app.main:app --reload --host 0.0.0.0 --port 8001` and open <http://localhost:8001>.
- **Dependency imports fail:** activate `.venv` and run `python -m pip install -r requirements.txt` again.
