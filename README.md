# Task API

A simple CRUD (Create, Read, Update, Delete) API for managing a to-do list, built with **Python** and **FastAPI**. Now secured with real user authentication via Supabase Auth.

This project was completed as part of my **Backend AI Engineer internship at FlyRank**.

- **Week 2 (A1):** Built the initial CRUD API with in-memory storage.
- **Week 3 (A2):** Migrated storage to a SQLite database — same endpoints, now persistent.
- **Week 1 (A3):** Containerized the whole stack with Docker — the API and a real PostgreSQL database now run together with one command.
- **Week 2 (A4):** Added authentication with Supabase Auth — signup, login, logout, and protected routes guarded by JWT verification.

## Tech stack

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Database:** PostgreSQL 16 (containerized)
- **Authentication:** Supabase Auth (JWT-based)
- **Containerization:** Docker + Docker Compose
- **Docs:** Swagger UI with Bearer auth support (built in at `/docs`)

## How to run (one command)

```bash
git clone https://github.com/Developer-AHM/flyrank-w2-crud-api.git
cd flyrank-w2-crud-api
cp .env.example .env
docker compose up
```

Then edit `.env` and fill in your own Supabase project URL and anon key (see below).

The API is available at `http://localhost:8000`.
Interactive API docs (Swagger UI): `http://localhost:8000/docs`

## Environment variables

Copy `.env.example` to `.env` and fill in your own values:

```
DATABASE_URL=postgres://postgres:yourpassword@localhost:5432/tasks
POSTGRES_PASSWORD=yourpassword
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
PORT=8000
```

To get your own Supabase values: create a free project at [supabase.com](https://supabase.com), then go to **Project Settings → API** and copy your **Project URL** and **anon public key**. Never use the `service_role` key here.

`.env` is git-ignored — never commit real credentials. `.env.example` shows the required keys with placeholder values only.

## Why Supabase Auth

Rolling your own authentication — password hashing, token signing, session management — is a common source of real security vulnerabilities. Supabase acts as a trusted Identity Provider: it stores accounts, hashes passwords, and issues signed JWTs. This API never touches a raw password; it only forwards credentials to Supabase and verifies the tokens Supabase issues.

## Endpoints

| Method | Path                   | Description                          | Auth required |
|--------|------------------------|---------------------------------------|----------------|
| GET    | `/`                    | API info                              | No |
| GET    | `/health`              | Health check                          | No |
| GET    | `/tasks`               | List all tasks (optional `?search=`)  | No |
| GET    | `/tasks/{id}`          | Get a single task by id               | No |
| POST   | `/tasks`               | Create a new task                     | No |
| PUT    | `/tasks/{id}`          | Update a task                         | No |
| DELETE | `/tasks/{id}`          | Delete a task                         | No |
| POST   | `/auth/signup`         | Create a new user account             | No |
| POST   | `/auth/login`          | Authenticate, returns a JWT           | No |
| POST   | `/auth/logout`         | End the current session               | Yes (Bearer token) |
| GET    | `/public/info`         | Public, open info                     | No |
| GET    | `/protected/profile`   | Current user's profile                | Yes (Bearer token) |
| GET    | `/protected/dashboard` | Example second protected route        | Yes (Bearer token) |

## Example auth flow (curl)

**Sign up:**
```bash
curl -i -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" -d '{"email":"you@example.com","password":"yourpassword"}'
```

**Log in:**
```bash
curl -i -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"you@example.com","password":"yourpassword"}'
```
Response includes an `access_token` — use it as a Bearer token for protected routes:

```bash
curl -i http://localhost:8000/protected/profile -H "Authorization: Bearer <your_access_token>"
```

A tampered or expired token correctly returns `401 Unauthorized`.

## Swagger UI with Bearer auth

Protected routes show a padlock icon in `/docs`. Click **"Authorize"**, paste an access token (no `Bearer ` prefix needed — Swagger adds it automatically), and every protected route's "Try it out" will use it.

![Swagger UI with Bearer auth](swagger-auth-screenshot.png)

## Persistence

Tasks are stored in a named Docker volume (`taskdata`), separate from the containers themselves, surviving a full stack teardown:

```bash
docker compose down   # containers removed
docker compose up     # fresh containers, same data — the volume kept it
```

## Exploring with SQLite (Week 3)

Before moving to Postgres, the database was explored directly using SQLite's command-line tool:

```sql
UPDATE tasks SET done = 1;
```

Calling `GET /tasks` through the API immediately reflected the change, with no restart needed.

![SQLite terminal session](sqlite-terminal.png)

## Viewing the database directly (Postgres)

```bash
docker exec -it $(docker compose ps -q db) psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```

![Postgres data](postgres-screenshot.png)

## Project structure

```
task-api/
├── main.py                       # All API code
├── Dockerfile                     # Builds the API's container image
├── compose.yaml                    # Defines the api + db services
├── requirements.txt               # Python dependencies
├── .env.example                    # Template for required environment variables
├── .gitignore                       # Excludes venv/, .env, tasks.db, cache files
├── Swagger UI.png                  # Swagger UI screenshot (Week 2)
├── sqlite-terminal.png             # SQLite CLI exploration screenshot (Week 3)
├── postgres-screenshot.png         # Postgres data screenshot (Week 1/A3)
├── swagger-auth-screenshot.png     # Swagger Bearer auth screenshot (this week)
└── README.md
```