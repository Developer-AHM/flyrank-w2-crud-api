# Task API

A simple CRUD (Create, Read, Update, Delete) API for managing a to-do list, built with **Python** and **FastAPI**.

This project was completed as **Week 2, Assignment 1** of my **Backend AI Engineer internship at FlyRank**. The goal was to build a working backend from scratch, understand HTTP methods and status codes, and publish it properly with Git and GitHub.

The API stores tasks **in memory** — there is no database yet. This means all data resets whenever the server restarts. That's expected for this stage of the assignment (databases are introduced in Week 3).

## Tech stack

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Server:** Uvicorn
- **Docs:** Swagger UI (built in at `/docs`)

## How to install and run

Clone the repo, then run:

```bash
git clone https://github.com/Developer-AHM/flyrank-w2-crud-api.git
cd flyrank-w2-crud-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`.

Interactive API docs (Swagger UI) are available at `http://localhost:8000/docs`.

## Endpoints

| Method | Path            | Description                          | Success | Error |
|--------|-----------------|---------------------------------------|---------|-------|
| GET    | `/`             | API info (name, version, endpoints)   | 200     | —     |
| GET    | `/health`       | Health check                          | 200     | —     |
| GET    | `/tasks`        | List all tasks                        | 200     | —     |
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

Creating a new task:

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
```

Response:

```
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI

Every endpoint is documented and testable interactively at `/docs`. Screenshot of the full CRUD cycle being tested via "Try it out":

![Swagger UI](Swagger%20UI.png)

## Notes on in-memory storage

Since the task list lives only in a Python variable, restarting the server (`Ctrl+C` then re-running `uvicorn`) wipes all tasks back to the original 3 example tasks. This is intentional at this stage — persistent storage (a real database) is the focus of Week 3.

## Project structure

```
task-api/
├── main.py            # All API code
├── requirements.txt   # Python dependencies
├── .gitignore          # Excludes venv/ and cache files from git
├── Swagger UI.png      # Screenshot for this README
└── README.md
```