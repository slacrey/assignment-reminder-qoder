from pydantic import BaseModel
from datetime import datetime

from app.models.reminder_log import ReminderStatus


class ReminderLogResponse(BaseModel):
    id: int
    assignment_id: int
    channel: str
    status: ReminderStatus
    sent_at: datetime
    error_message: str | None = None
    assignment_title: str | None = None
    child_name: str | None = None

    model_config = {"from_attributes": True}
