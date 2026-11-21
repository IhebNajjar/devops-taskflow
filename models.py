from pydantic import BaseModel, Field
from typing import Optional, List, Any

class SubtaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    due_date: Optional[str] = Field(None, description="Optional deadline (YYYY-MM-DD)")

class SubtaskCreate(SubtaskBase):
    pass

class SubtaskStatusUpdate(BaseModel):
    status: str

class SubtaskResponse(SubtaskBase):
    id: int
    task_id: int
    status: str
    created_at: str

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150, description="Task or Project title")
    description: Optional[str] = Field("", max_length=1000, description="Detailed description")
    category: str = Field(default="Development", description="Category (Development, Studies, Personal, Work)")
    priority: str = Field(default="Medium", description="Priority (Low, Medium, High)")
    status: str = Field(default="To Do", description="Status (To Do, In Progress, Completed)")
    due_date: Optional[str] = Field(None, description="Due date (YYYY-MM-DD)")

class TaskCreate(TaskBase):
    subtasks: Optional[List[Any]] = Field(default=[], description="List of subtask titles or objects")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    user_id: Optional[int] = 1
    created_at: str
    subtasks: Optional[List[SubtaskResponse]] = []
    subtasks_total: Optional[int] = 0
    subtasks_completed: Optional[int] = 0
    subtasks_progress: Optional[float] = 0.0

    class Config:
        from_attributes = True

class AuthRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=3, max_length=100)

class AuthResponse(BaseModel):
    id: int
    username: str
    token: str
    message: str
    xp: Optional[int] = 150
    streak: Optional[int] = 1

class AIAdviseRequest(BaseModel):
    question: Optional[str] = None
