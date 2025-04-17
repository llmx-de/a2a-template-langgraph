from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.sql import func
from a2a_service.database import Base

class TaskModel(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    state = Column(String, nullable=False)
    message = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class ArtifactModel(Base):
    __tablename__ = "artifacts"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False, index=True)
    index = Column(Integer, nullable=False)
    append = Column(Boolean, default=False, nullable=False)
    parts = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False) 