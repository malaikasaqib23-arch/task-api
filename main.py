from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Publish on GitHub", "done": False}
]

@app.get("/")
def home():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )

@app.post("/tasks", status_code=201)
def create_task(data: dict):
    title = data.get("title")

    if not title or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )

    new_id = max(task["id"] for task in tasks) + 1

    new_task = {
        "id": new_id,
        "title": title,
        "done": False
    }

    tasks.append(new_task)

    return new_task
@app.put("/tasks/{id}")
def update_task(id: int, data: dict):
    for task in tasks:
        if task["id"] == id:

            if not data:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Update data is required"}
                )

            if "title" in data:
                if not isinstance(data["title"], str) or not data["title"].strip():
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Title cannot be empty"}
                    )
                task["title"] = data["title"]

            if "done" in data:
                if not isinstance(data["done"], bool):
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Done must be true or false"}
                    )
                task["done"] = data["done"]

            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )


@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):
    for task in tasks:
        if task["id"] == id:
            tasks.remove(task)
            return

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {id} not found"}
    )