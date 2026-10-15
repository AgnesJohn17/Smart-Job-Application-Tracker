# Deployment guide (production MVP)

The demo is **not deployed yet**. Backend and frontend are independent services and need a persistent PostgreSQL database.

## 1. Persistent PostgreSQL

Create a hosted PostgreSQL instance (Render PostgreSQL or Neon). Copy the private connection string into the backend environment as `DATABASE_URL`. The backend accepts both `postgresql://` and `postgres://` strings and uses psycopg v3. Never place the database password in frontend settings or GitHub.

## 2. Backend web service (Render)

Connect `AgnesJohn17/Smart-Job-Application-Tracker` to a new **Web Service**. Choose Python and set:
- **Root directory:** `backend`
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment:** `APP_ENV=production`, `DATABASE_URL=<private-db-url>`, `SECRET_KEY=<random-32-plus-character-secret>`, `CORS_ORIGINS=https://<your-frontend-domain>`
- Use the production service hostname with HTTPS.
- **Health endpoint:** `/api/health`

Generate a signing key locally using `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Do not save secrets in repository files.

On initial startup, the MVP creates database tables. For future schema changes use migrations. Free hosting tiers may sleep or have limited database storage; choose based on your needs.

## 3. Frontend (Vercel)

Connect the same GitHub repository to a Vercel project:
- **Root directory:** `frontend`
- **Framework:** Vite
- **Build:** `npm run build`
- **Output directory:** `dist`
- **Environment:** `VITE_API_URL=https://<your-backend-host>`

Redeploy frontend when changing `VITE_API_URL` (Vite compiles environment variables into the JavaScript bundle). Update backend `CORS_ORIGINS` to your exact Vercel public HTTPS origin, without a trailing slash.

## 4. Verification checklist

- Visit the Vercel frontend URL.
- Register with a non-sensitive test email and a unique test password.
- Add an application with a deadline and interview date.
- Edit the status, search, and refresh the page to verify PostgreSQL persistence.
- Sign out and register another test account; verify records remain separate.
- Check browser developer console and network for errors.
- Remove test users from the database before showcasing the app if needed.

## Caveats

This is a student demonstration, **not yet production security hardened**. It uses browser sessionStorage bearer tokens and lacks rate limiting, password resets, email verification, application auditing, and formal database migrations. Use non-sensitive demo data only; do not invite public users to provide personal information until security and privacy issues are addressed.

## CI evidence

The [full-stack CI](../.github/workflows/ci.yml) validates Python tests and TypeScript/Vite builds. The [browser integration workflow](../.github/workflows/browser-e2e.yml) runs a real Chromium browser against PostgreSQL 16, FastAPI, and the React frontend.
