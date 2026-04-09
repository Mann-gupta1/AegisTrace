import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class TokenUsage(Base):
    __tablename__ = "token_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id"), nullable=False, index=True)
    node_run_id = Column(UUID(as_uuid=True), ForeignKey("node_runs.id"), nullable=True)
    model_name = Column(String(255), nullable=False)
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    estimated_cost_usd = Column(Float, nullable=True, default=0.0)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    workflow_run = relationship("WorkflowRun", back_populates="token_usages")
    node_run = relationship("NodeRun", back_populates="token_usages")
