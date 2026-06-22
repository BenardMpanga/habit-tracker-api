from enum import Enum
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

app = FastAPI(title="Habit Tracker API")

sqlite_file_name = "habits.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    skipped = "skipped"


class TaskBase(SQLModel):
    title: str = Field(min_length=1)
    status: TaskStatus = TaskStatus.pending


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1)
    status: Optional[TaskStatus] = None


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/tasks", response_model=List[Task])
def get_all_tasks(session: Session = Depends(get_session)):
    """Returns all tasks in the database."""
    return session.exec(select(Task)).all()


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    """Creates a new task and adds it to the database."""
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task:
        return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: TaskCreate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task:
        task.title = updated_task.title
        task.status = updated_task.status
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.patch("/tasks/{task_id}", response_model=Task)
def partially_update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session),
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if task:
        session.delete(task)
        session.commit()
        return
    raise HTTPException(status_code=404, detail="Task not found")

