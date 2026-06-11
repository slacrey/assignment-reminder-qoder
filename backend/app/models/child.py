from datetime import datetime

from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Child(Base):
    __tablename__ = "children"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    qq_number: Mapped[str] = mapped_column(String(20), default="", nullable=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    parent: Mapped["Parent"] = relationship("Parent", back_populates="children")
    assignments: Mapped[list["Assignment"]] = relationship("Assignment", back_populates="child", cascade="all, delete-orphan")
