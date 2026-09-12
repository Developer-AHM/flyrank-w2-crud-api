# Task API

A simple CRUD (Create, Read, Update, Delete) API for managing a to-do list, built with **Python** and **FastAPI**.

This project was completed as part of my **Backend AI Engineer internship at FlyRank**.

- **Week 2 (A1):** Built the initial CRUD API with in-memory storage.
- **Week 3 (A2):** Migrated storage to a SQLite database — same endpoints, now persistent.
- **Week 1 (A3):** Containerized the whole stack with Docker — the API and a real PostgreSQL database now run together with one command.

## Tech stack

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Database:** PostgreSQL 16 (containerized)
- **Containerization:** Docker + Docker Compose
- **Docs:** Swagger UI (built in at `/docs`)

## How to run (one command)

```bash
git clone https://github.com/Developer-AHM/flyrank-w2-crud-api.git
cd flyrank-w2-crud-api
cp .env.example .env
docker compose up
```

That's it — this single command builds the API image, starts a PostgreSQL container, connects them together, and creates + seeds the `tasks` table automatically on first run.

The API is available at `http://localhost:8000`.
Interactive API docs (Swagger UI): `http://localhost:8000/docs`

To stop everything:
```bash
docker compose down
```
(Your data stays safe in a Docker volume even after this — see "Persistence" below.)

## Environment variables

Copy `.env.example` to `.env` and adjust if needed:

```
DATABASE_URL=postgres://postgres:yourpassword@localhost:5432/tasks
POSTGRES_PASSWORD=yourpassword
```

`.env` is git-ignored — never commit real credentials. `.env.example` shows the required keys with placeholder values.

## Why Docker + Postgres

SQLite (Week 3) was a single file — simple, but not how most real backends store data. PostgreSQL is a full database *server*, the same kind of engine powering most production applications. Running it in Docker means no manual installation or version conflicts — Postgres runs identically on any machine with Docker installed. Docker Compose then ties the API and database together, so the entire stack starts with one command instead of two separate manual steps.

## Endpoints

| Method | Path            | Description                          | Success | Error |
|--------|-----------------|---------------------------------------|---------|-------|
| GET    | `/`             | API info (name, version, endpoints)   | 200     | —     |
| GET    | `/health`       | Health check                          | 200     | —     |
| GET    | `/tasks`        | List all tasks (optional `?search=`)  | 200     | —     |
| GET    | `/tasks/{id}`   | Get a single task by id               | 200     | 404 if not found |
| POST   | `/tasks`        | Create a new task                     | 201     | 400 if title is missing/empty |
| PUT    | `/tasks/{id}`   | Update a task's title and/or done     | 200     | 404 if not found, 400 if title invalid |
| DELETE | `/tasks/{id}`   | Delete a task                         | 204     | 404 if not found |

### Example task object

```json
{
  "id": 1,
  "title": "Buy milk",
  "done": false
}
```

## Example request (curl)

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
```

Response:

```
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Persistence

Tasks are stored in a named Docker volume (`taskdata`), separate from the containers themselves. This means data survives even a full stack teardown:

```bash
docker compose down   # containers removed
docker compose up     # fresh containers, same data — the volume kept it
```

## Viewing the database directly

```bash
docker exec -it $(docker compose ps -q db) psql -U postgres -d tasks -c "SELECT * FROM tasks;"
```

Screenshot of this:

![Postgres data](postgres-screenshot.png)

## Swagger UI

Every endpoint is documented and testable interactively at `/docs`.

![Swagger UI](Swagger%20UI.png)

## Project structure

```
task-api/
├── main.py                  # All API code
├── Dockerfile                # Builds the API's container image
├── compose.yaml               # Defines the api + db services
├── requirements.txt          # Python dependencies
├── .env.example               # Template for required environment variables
├── .gitignore                  # Excludes venv/, .env, tasks.db, cache files
├── Swagger UI.png             # Swagger UI screenshot
├── sqlite-terminal.png        # SQLite CLI exploration screenshot (Week 3)
├── postgres-screenshot.png    # Postgres data screenshot (this week)
└── README.md
```