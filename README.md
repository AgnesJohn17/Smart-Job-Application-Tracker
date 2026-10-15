# Smart Job Application Tracker

An end-to-end software engineering portfolio project built with **React, TypeScript, FastAPI, SQLAlchemy, PostgreSQL and Docker**.

> **Status: MVP under development.** Authentication, application CRUD, search/filtering, dashboard statistics, automated tests and container setup are the initial milestones. Don't present future roadmap items as completed work.

## Features (MVP)
- Account registration and bearer-token login
- Private, per-user job application records
- Create/edit/delete applications; track Wishlist, Applied, Interview, Offer and Rejected stages
- Company/role search, status filtering, deadlines, notes and links
- Dashboard totals
- Local Docker Compose stack (PostgreSQL + FastAPI + Vite/React)
- Unit/integration testing and automated CI checks

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
cd backend && pytest -q
cd ../frontend && npm ci && npm run build
```

## Security notes
Passwords are salted and stretched with PBKDF2-HMAC-SHA256; API tokens are signed with an environment-configured secret and expire. Each application query is restricted to its authenticated owner. Never commit the .env file. This demo does **not** replace production-ready practices such as HTTPS, refresh-token rotation, rate limiting, CSRF-safe HttpOnly cookie sessions, and database migrations.

## Roadmap
- [ ] MVP backend, frontend and CI verified
- [ ] Browser end-to-end tests
- [ ] Production deployment with managed PostgreSQL
- [ ] Automated email reminders, advanced interview calendar and analytics

Created as a practical, testable full-stack project for software development internship applications.
