from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Task Tracker API")

# 1. Pydantic Model: Defines what a "Task" looks like
class Task(BaseModel):
    id: int
    title: str
    status: str = "pending" # Defaults to pending if not provided

# 2. Our Mock Database
mock_db: List[Task] = [
    Task(id=1, title="Learn REST Fundamentals", status="completed"),
    Task(id=2, title="Build FastAPI Prototype", status="pending")
]
# 3. API Endpoint: Get all tasks
@app.get("/tasks", response_model=List[Task])
def get_all_tasks():
    """Returns all tasks in the database."""
    return mock_db
# 4. API Endpoint: Create a new task
@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: Task):
    """Creates a new task and adds it to the database."""
    # Check if a task with this ID already exists
    for existing_task in mock_db:
        if existing_task.id == task.id:
            raise HTTPException(status_code=400, detail="Task with this ID already exists")
    
    mock_db.append(task)
    return task

# Get a single task
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    for task in mock_db:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

# Update a task
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    for index, task in enumerate(mock_db):
        if task.id == task_id:
            mock_db[index] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Task not found")

# Delete a task
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    for index, task in enumerate(mock_db):
        if task.id == task_id:
            mock_db.pop(index)
            return
    raise HTTPException(status_code=404, detail="Task not found")

