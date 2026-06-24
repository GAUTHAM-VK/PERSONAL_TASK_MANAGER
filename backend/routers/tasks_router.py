from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

import database
import auth
from schemas import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse, TaskSummary

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _row_to_task_response(row) -> TaskResponse:
    return TaskResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        priority=row["priority"],
        status=row["status"],
        due_date=row["due_date"],
        owner_email=row["owner_email"],
    )


def _get_owned_task_or_error(task_id: int, current_user: str):
    """
    Shared helper: fetch a task by id and enforce ownership.
    - 404 if the task does not exist at all
    - 403 if it exists but belongs to someone else
    """
    task = database.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    if task["owner_email"] != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your task.")
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, current_user: str = Depends(auth.get_current_user)):
    row = database.create_task(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        status="pending",
        due_date=payload.due_date,
        owner_email=current_user,
    )
    return _row_to_task_response(row)


@router.get("/summary", response_model=TaskSummary)
def task_summary(current_user: str = Depends(auth.get_current_user)):
    return database.get_task_summary(current_user)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: str = Depends(auth.get_current_user),
):
    rows = database.get_tasks_for_user(current_user, status=status_filter, priority=priority)
    return [_row_to_task_response(r) for r in rows]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, current_user: str = Depends(auth.get_current_user)):
    task = _get_owned_task_or_error(task_id, current_user)
    return _row_to_task_response(task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, payload: TaskUpdate, current_user: str = Depends(auth.get_current_user)
):
    _get_owned_task_or_error(task_id, current_user)  # ownership check first
    updated = database.update_task(
        task_id=task_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date,
    )
    return _row_to_task_response(updated)


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_status(
    task_id: int, payload: TaskStatusUpdate, current_user: str = Depends(auth.get_current_user)
):
    _get_owned_task_or_error(task_id, current_user)
    updated = database.update_task_status(task_id, payload.status)
    return _row_to_task_response(updated)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user: str = Depends(auth.get_current_user)):
    _get_owned_task_or_error(task_id, current_user)
    database.delete_task(task_id)
    return None
