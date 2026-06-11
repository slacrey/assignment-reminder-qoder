from datetime import datetime
import enum

from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReminderStatus(str, enum.Enum):
    success = "success"
    failed = "failed"


class ReminderLog(Base):
    __tablename__ = "reminder_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    assignment_id: Mapped[int] = mapped_column(Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), default="email", nullable=False)
    status: Mapped[ReminderStatus] = mapped_column(Enum(ReminderStatus), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    assignment: Mapped["Assignment"] = relationship("Assignment", back_populates="reminder_logs")
