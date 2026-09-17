from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sqlite3

app = FastAPI()


def get_db():
    return sqlite3.connect("tasks.db")


def setup_database():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute(
            "INSERT INTO tasks (id, title, done) VALUES (?, ?, ?)",
            (1, "Learn FastAPI", False)
        )
        cursor.execute(
            "INSERT INTO tasks (id, title, done) VALUES (?, ?, ?)",
            (2, "Build CRUD API", False)
        )
        cursor.execute(
            "INSERT INTO tasks (id, title, done) VALUES (?, ?, ?)",
            (3, "Publish on GitHub", False)
        )

    conn.commit()
    conn.close()


setup_database()


@app.get("/", summary="API information")
def home():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Check API health")
def health():
    return {"status": "ok"}


@app.get("/tasks", summary="Get all tasks")
def get_tasks():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "done": bool(row[2])
        }
        for row in rows
    ]


@app.get("/tasks/{id}", summary="Get a task by ID")
def get_task(id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (id,)
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "title": row[1],
            "done": bool(row[2])
        }

    return JSONResponse(
        status_code=404,
        content={"error": "Task not found"}
    )


@app.post("/tasks", summary="Create a new task", status_code=201)
def create_task(data: dict):
    title = data.get("title")

    if not title or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(id) FROM tasks")
    max_id = cursor.fetchone()[0]
    new_id = 1 if max_id is None else max_id + 1

    cursor.execute(
        "INSERT INTO tasks (id, title, done) VALUES (?, ?, ?)",
        (new_id, title, False)
    )

    conn.commit()
    conn.close()

    return {
        "id": new_id,
        "title": title,
        "done": False
    }


@app.put("/tasks/{id}", summary="Update a task")
def update_task(id: int, data: dict):
    if not data:
        return JSONResponse(
            status_code=400,
            content={"error": "Update data is required"}
        )

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (id,)
    )

    row = cursor.fetchone()

    if not row:
        conn.close()
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    title = row[1]
    done = bool(row[2])

    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            conn.close()
            return JSONResponse(
                status_code=400,
                content={"error": "Title cannot be empty"}
            )
        title = data["title"]

    if "done" in data:
        if not isinstance(data["done"], bool):
            conn.close()
            return JSONResponse(
                status_code=400,
                content={"error": "Done must be true or false"}
            )
        done = data["done"]

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (title, done, id)
    )

    conn.commit()
    conn.close()

    return {
        "id": id,
        "title": title,
        "done": done
    }


@app.delete("/tasks/{id}", summary="Delete a task", status_code=204)
def delete_task(id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM tasks WHERE id = ?",
        (id,)
    )

    row = cursor.fetchone()

    if not row:
        conn.close()
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()