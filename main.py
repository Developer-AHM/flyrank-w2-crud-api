from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client
import os
import psycopg

app = FastAPI()

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

conn = psycopg.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT,
    done BOOLEAN
    )
""")

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": False},
    {"id": 3, "title": "Learn FastAPI", "done": True},
]

cursor.execute("SELECT COUNT(*) FROM tasks")
count = cursor.fetchone()[0]

if count == 0:
    cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Buy milk", False))
    cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Walk the dog", False))
    cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Learn FastAPI", True))

conn.commit()

@app.get("/", summary="API Information")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", summary="Health Check")
def health():
    return {"status": "ok"}

@app.get("/tasks", summary="List all tasks")
def get_tasks(search: str = None):
    if search is not None:
        cursor.execute("SELECT * FROM tasks WHERE title LIKE %s", ("%" + search + "%",))
    else:
        cursor.execute("SELECT * FROM tasks")

    rows = cursor.fetchall()

    result = []
    for row in rows:
        task = {"id": row[0], "title": row[1], "done": bool(row[2])}
        result.append(task)

    return result

@app.get("/tasks/{task_id}", summary="Get a single task by id")
def get_task(task_id: int):
    cursor.execute("SELECT * FROM tasks WHERE id= %s", (task_id,))
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    return {"id": row[0], "title":row[1], "done": bool(row[2])}

class TaskCreate(BaseModel):
    title: str = " "

@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(new_task: TaskCreate):
    if not new_task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    cursor.execute("INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id", (new_task.title, False))
    new_id = cursor.fetchone()[0]
    conn.commit()
    task = {"id": new_id, "title": new_task.title, "done": False}
    return task

class TaskUpdate(BaseModel):
    title: str = None
    done: bool = None

@app.put("/tasks/{task_id}", summary="Update an existing task")
def update_task(task_id: int, updated: TaskUpdate):
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    new_title = updated.title if updated.title is not None else row[1]
    new_done = updated.done if updated.done is not None else bool(row[2])

    if updated.title is not None and not updated.title.strip():
        raise HTTPException(status_code=400, detail="Title cannont be empty")

    cursor.execute("UPDATE tasks SET title = %s, done = %s WHERE id = %s", (new_title, new_done, task_id))
    conn.commit()

    return {"id": task_id, "title": new_title, "done": new_done}


            
@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    cursor.execute("SELECT * FROM tasks WHERE id = %s ", (task_id,))
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    return