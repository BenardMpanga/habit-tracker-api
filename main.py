from contextlib import asynccontextmanager
from enum import Enum
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

sqlite_file_name = "habits.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


class HabitStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    skipped = "skipped"


class HabitBase(SQLModel):
    title: str = Field(min_length=1)
    status: HabitStatus = HabitStatus.pending


class Habit(HabitBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class HabitCreate(HabitBase):
    pass


class HabitUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1)
    status: Optional[HabitStatus] = None


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Habit Tracker API", lifespan=lifespan)


@app.get("/habits", response_model=List[Habit])
def get_all_habits(session: Session = Depends(get_session)):
    """Returns all habits in the database."""
    return session.exec(select(Habit)).all()


@app.post("/habits", response_model=Habit, status_code=201)
def create_habit(habit: HabitCreate, session: Session = Depends(get_session)):
    """Creates a new habit and adds it to the database."""
    db_habit = Habit.model_validate(habit)
    session.add(db_habit)
    session.commit()
    session.refresh(db_habit)
    return db_habit


@app.get("/habits/{habit_id}", response_model=Habit)
def get_habit(habit_id: int, session: Session = Depends(get_session)):
    habit = session.get(Habit, habit_id)
    if habit:
        return habit
    raise HTTPException(status_code=404, detail="Habit not found")


@app.put("/habits/{habit_id}", response_model=Habit)
def update_habit(
    habit_id: int,
    updated_habit: HabitCreate,
    session: Session = Depends(get_session),
):
    habit = session.get(Habit, habit_id)
    if habit:
        habit.title = updated_habit.title
        habit.status = updated_habit.status
        session.add(habit)
        session.commit()
        session.refresh(habit)
        return habit
    raise HTTPException(status_code=404, detail="Habit not found")


@app.patch("/habits/{habit_id}", response_model=Habit)
def partially_update_habit(
    habit_id: int,
    habit_update: HabitUpdate,
    session: Session = Depends(get_session),
):
    habit = session.get(Habit, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    update_data = habit_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(habit, key, value)

    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


@app.delete("/habits/{habit_id}", status_code=204)
def delete_habit(habit_id: int, session: Session = Depends(get_session)):
    habit = session.get(Habit, habit_id)
    if habit:
        session.delete(habit)
        session.commit()
        return
    raise HTTPException(status_code=404, detail="Habit not found")

