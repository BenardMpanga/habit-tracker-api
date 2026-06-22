# Habit Tracker API

A small FastAPI project for tracking tasks or habits. The app exposes a simple REST API that lets you list, create, read, update, and delete task records.

Right now the data is stored in an in-memory mock database inside `main.py`, so any changes made through the API are lost when the server restarts.

## What Is In The Project

- `main.py` - the FastAPI application and all API routes.
- `.gitignore` - ignores the local `venv/` virtual environment.
- `venv/` - local Python environment, not meant to be committed.

## Data Model

Each task has this shape:

```json
{
  "id": 1,
  "title": "Learn REST Fundamentals",
  "status": "completed"
}
```

Fields:

- `id` - integer identifier for the task.
- `title` - task or habit name.
- `status` - task state, defaults to `"pending"` if not provided.

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/tasks` | Get all tasks |
| `POST` | `/tasks` | Create a new task |
| `GET` | `/tasks/{task_id}` | Get one task by ID |
| `PUT` | `/tasks/{task_id}` | Replace an existing task |
| `DELETE` | `/tasks/{task_id}` | Delete a task |

## Getting Started

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install fastapi uvicorn
```

Run the API:

```powershell
uvicorn main:app --reload
```

Then open the interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Example Requests

Create a new task:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/tasks `
  -ContentType "application/json" `
  -Body '{"id":3,"title":"Drink water","status":"pending"}'
```

Get all tasks:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/tasks
```

Delete a task:

```powershell
Invoke-RestMethod -Method Delete http://127.0.0.1:8000/tasks/3
```

## Notes

This is a prototype API. A good next step would be replacing the mock list with a real database so tasks persist after restarting the app.
