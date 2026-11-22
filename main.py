import os
import uvicorn
from fastapi import FastAPI, HTTPException, Query, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

import database as db
import ai_assistant
from models import (
    TaskCreate, TaskUpdate, TaskResponse,
    SubtaskCreate, SubtaskStatusUpdate, SubtaskResponse,
    AuthRequest, AuthResponse
)

app = FastAPI(
    title="TaskFlow API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    db.init_db(seed_if_empty=True)

class AIBreakdownRequest(BaseModel):
    project_title: str
    horizon: Optional[str] = "auto"
    custom_days: Optional[int] = None
    num_steps: Optional[int] = None

class BatchTasksRequest(BaseModel):
    tasks: List[TaskCreate]

# ----------------- AUTHENTICATION ENDPOINTS -----------------

@app.post("/api/auth/register", response_model=AuthResponse)
def register(req: AuthRequest):
    user = db.register_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=400, detail="Username already taken. Please choose another.")
    return {
        "id": user["id"],
        "username": user["username"],
        "token": f"token_{user['id']}_{user['username']}",
        "message": "Account created successfully!",
        "xp": user.get("xp", 150),
        "streak": user.get("streak", 1)
    }

@app.post("/api/auth/login", response_model=AuthResponse)
def login(req: AuthRequest):
    user = db.authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    return {
        "id": user["id"],
        "username": user["username"],
        "token": f"token_{user['id']}_{user['username']}",
        "message": f"Welcome back, {user['username']}!",
        "xp": user.get("xp", 150),
        "streak": user.get("streak", 1)
    }

@app.get("/api/auth/me")
def get_current_user(user_id: int = Query(1)):
    profile = db.get_user_profile(user_id)
    return profile

# ----------------- TASKS & SUBTASKS ENDPOINTS -----------------

@app.get("/api/tasks", response_model=List[TaskResponse])
def list_tasks(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    period: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None)
):
    return db.get_tasks(search=search, status=status, priority=priority, category=category, period=period, user_id=user_id)

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/api/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, user_id: int = Query(1)):
    created = db.create_task(task.model_dump(), user_id=user_id)
    return created

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate, user_id: int = Query(1)):
    updated = db.update_task(task_id, task.model_dump(exclude_unset=True), user_id=user_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_200_OK)
def delete_task(task_id: int):
    success = db.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task and all subtasks deleted successfully", "id": task_id}

# Subtask Operations
@app.post("/api/tasks/{task_id}/subtasks", response_model=SubtaskResponse, status_code=status.HTTP_201_CREATED)
def add_subtask(task_id: int, req: SubtaskCreate):
    sub = db.add_subtask(task_id, req.title)
    if not sub:
        raise HTTPException(status_code=400, detail="Could not create subtask")
    return sub

@app.put("/api/subtasks/{subtask_id}")
def update_subtask_status(subtask_id: int, req: SubtaskStatusUpdate, user_id: int = Query(1)):
    sub = db.update_subtask_status(subtask_id, req.status, user_id=user_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return sub

@app.delete("/api/subtasks/{subtask_id}")
def delete_subtask(subtask_id: int):
    success = db.delete_subtask(subtask_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subtask not found")
    return {"message": "Subtask deleted successfully", "id": subtask_id}

@app.post("/api/tasks/batch", status_code=status.HTTP_201_CREATED)
def create_tasks_batch(req: BatchTasksRequest, user_id: int = Query(1)):
    tasks_data = [t.model_dump() for t in req.tasks]
    created = db.create_tasks_batch(tasks_data, user_id=user_id)
    return {"message": f"{len(created)} tasks created successfully!", "tasks": created}

@app.get("/api/stats")
def get_statistics(user_id: int = Query(1)):
    return db.get_stats(user_id=user_id)

@app.post("/api/reset-demo")
def reset_demo_data():
    db.seed_demo_data()
    return {"message": "Demo data reset successfully"}

# ----------------- AI ASSISTANT ENDPOINT -----------------

@app.post("/api/ai/breakdown")
def ai_breakdown(req: AIBreakdownRequest):
    if not req.project_title.strip():
        raise HTTPException(status_code=400, detail="Please enter a project title or goal")
    
    generated = ai_assistant.generate_project_tasks(
        project_title=req.project_title,
        horizon=req.horizon or "auto",
        custom_days=req.custom_days,
        num_steps=req.num_steps
    )
    return {
        "project": req.project_title,
        "horizon": req.horizon,
        "custom_days": req.custom_days,
        "num_steps": req.num_steps,
        "tasks": generated
    }

@app.get("/health")
def health():
    return {"status": "ok"}

# ----------------- STATIC ASSETS & FRONTEND -----------------

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")
if not os.path.exists(PUBLIC_DIR):
    os.makedirs(PUBLIC_DIR, exist_ok=True)

app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host=host, port=port)
