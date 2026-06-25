from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, field_validator


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def username_not_blank(cls, v):
        if not v.strip():
            raise ValueError("Username cannot be empty")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    username: str


PriorityType = Literal["low", "medium", "high"]
StatusType = Literal["pending", "in-progress", "done"]


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: PriorityType = "medium"
    due_date: Optional[str] = None  # ISO date string, e.g. "2026-07-01"

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v


class TaskUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: PriorityType = "medium"
    due_date: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v


class TaskStatusUpdate(BaseModel):
    status: StatusType


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: str
    status: str
    due_date: Optional[str] = None
    owner_email: str


class TaskSummary(BaseModel):
    total: int
    pending: int
    in_progress: int
    done: int