from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

conn = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    title TEXT,
    done INTEGER
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
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Buy milk", 0))
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Walk the dog", 0))
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Learn FastAPI", 1))

conn.commit()

@app.get("/", summary="API Information")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", summary="Health Check")
def health():
    return {"status": "ok"}

@app.get("/tasks", summary="List all tasks")
def get_tasks():
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    result = []
    for row in rows:
        task = {"id": row[0], "title": row[1], "done": bool(row[2])}
        result.append(task)

    return result

@app.get("/tasks/{task_id}", summary="Get a single task by id")
def get_task(task_id: int):
    cursor.execute("SELECT * FROM tasks WHERE id= ?", (task_id,))
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

    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (new_task.title, 0))
    conn.commit()
    new_id = cursor.lastrowid
    task = {"id": new_id, "title": new_task.title, "done": False}
    return task

class TaskUpdate(BaseModel):
    title: str = None
    done: bool = None

@app.put("/tasks/{task_id}", summary="Update an existing task")
def update_task(task_id: int, updated: TaskUpdate):
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    new_title = updated.title if updated.title is not None else row[1]
    new_done = updated.done if updated.done is not None else bool(row[2])

    if updated.title is not None and not updated.title.strip():
        raise HTTPException(status_code=400, detail="Title cannont be empty")

    cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (new_title, int(new_done), task_id))
    conn.commit()

    return {"id": task_id, "title": new_title, "done": new_done}


            
@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    cursor.execute("SELECT * FROM tasks WHERE id = ? ", (task_id,))
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    return