import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Float, Integer, Enum as SAEnum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db_base import Base


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(String(255), nullable=False, index=True)
    status = Column(
        SAEnum("running", "completed", "failed", name="workflow_status"),
        nullable=False,
        default="running",
    )
    start_time = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime(timezone=True), nullable=True)
    total_latency_ms = Column(Float, nullable=True)
    total_tokens = Column(Integer, nullable=True, default=0)
    avg_confidence = Column(Float, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)

    nodes = relationship("NodeRun", back_populates="workflow_run", cascade="all, delete-orphan")
    token_usages = relationship("TokenUsage", back_populates="workflow_run", cascade="all, delete-orphan")
