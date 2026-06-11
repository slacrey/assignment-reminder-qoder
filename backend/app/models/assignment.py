from datetime import datetime
import enum

from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AssignmentStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    child_id: Mapped[int] = mapped_column(Integer, ForeignKey("children.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=True)
    remind_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus), default=AssignmentStatus.pending, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    parent: Mapped["Parent"] = relationship("Parent", back_populates="assignments")
    child: Mapped["Child"] = relationship("Child", back_populates="assignments")
    reminder_logs: Mapped[list["ReminderLog"]] = relationship("ReminderLog", back_populates="assignment", cascade="all, delete-orphan")
