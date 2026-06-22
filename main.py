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