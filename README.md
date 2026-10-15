# Smart Job Application Tracker

An end-to-end software engineering portfolio project built with **React, TypeScript, FastAPI, SQLAlchemy, PostgreSQL and Docker**.

> **Status: MVP under development.** Authentication, application CRUD, search/filtering, dashboard statistics, automated tests and container setup are the initial milestones. Don't present future roadmap items as completed work.

## Features (MVP)
- Account registration and bearer-token login
- Private, per-user job application records
- Create/edit/delete applications; track Wishlist, Applied, Interview, Offer and Rejected stages
- Company/role search, status filtering, application deadlines, interview dates, notes and links
- Dashboard totals
- Local Docker Compose stack (PostgreSQL + FastAPI + Vite/React)
- Unit/integration testing and automated CI checks

## Deploy online

See [production MVP deployment steps](docs/deployment.md) for hosted PostgreSQL, Render backend, Vercel frontend and secrets setup. **No public app URL has been verified yet.**

## Start with Docker
```sh
cp .env.example .env
# Change SECRET_KEY in .env, then:
docker compose up --build
```
Open http://localhost:5173 for the app and http://localhost:8000/docs for REST API documentation.

## Local development
Backend:
```sh
cd backend
python -m venv .venv
# Activate .venv first
pip install -r requirements.txt
uvicorn app.main:app --reload
```
With no DATABASE_URL set, SQLite `tracker.db` is used for local development.

Frontend:
```sh
cd frontend
npm install
npm run dev
```
Default frontend expects API at `http://localhost:8000`.

## Tests
```sh
cd backend && python -m pytest -q
cd ../frontend && npm install && npm run build
```

## Security notes
Passwords are salted and stretched with PBKDF2-HMAC-SHA256; API tokens are signed with an environment-configured secret and expire. Each application query is restricted to its authenticated owner. Never commit the .env file. This demo does **not** replace production-ready practices such as HTTPS, refresh-token rotation, rate limiting, CSRF-safe HttpOnly cookie sessions, and database migrations.

## Roadmap
- [x] MVP backend, frontend and CI verified
- [x] Browser end-to-end tests with PostgreSQL and Playwright
- [ ] Production deployment with managed PostgreSQL
- [ ] Automated email reminders, advanced interview calendar and analytics

Created as a practical, testable full-stack project for software development internship applications.

## Browser end-to-end integration tests

The [browser integration workflow](.github/workflows/browser-e2e.yml) starts PostgreSQL 16, launches the FastAPI service and React development server, and runs Playwright Chromium tests. Its test journey covers registration, creating an application with deadline and interview date, searching, editing status, page reload persistence, sign-out and separation of records between accounts.

The workflow must pass before browser integration is considered verified; a successful frontend build alone is not proof of browser functionality. To run locally after starting the backend, frontend and PostgreSQL:

```sh
cd frontend
npm install
npx playwright install chromium
npm run test:e2e
```

For local schema changes made after initializing an existing database, recreate the development database or use migrations; the MVP uses `create_all` and does not automatically alter existing tables.
