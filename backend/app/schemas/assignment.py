from pydantic import BaseModel
from datetime import datetime

from app.models.assignment import AssignmentStatus


class AssignmentCreate(BaseModel):
    child_id: int
    title: str
    description: str = ""
    remind_at: datetime


class AssignmentUpdate(BaseModel):
    child_id: int | None = None
    title: str | None = None
    description: str | None = None
    remind_at: datetime | None = None
    status: AssignmentStatus | None = None


class AssignmentResponse(BaseModel):
    id: int
    parent_id: int
    child_id: int
    title: str
    description: str
    remind_at: datetime
    status: AssignmentStatus
    created_at: datetime
    child_name: str | None = None

    model_config = {"from_attributes": True}
