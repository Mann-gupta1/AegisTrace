import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Float, Integer, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db_base import Base


class NodeRun(Base):
    __tablename__ = "node_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_run_id = Column(UUID(as_uuid=True), ForeignKey("workflow_runs.id"), nullable=False, index=True)
    node_id = Column(String(255), nullable=False)
    node_type = Column(
        SAEnum("retrieval", "tool", "llm", "postprocessing", name="node_type"),
        nullable=False,
    )
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime(timezone=True), nullable=True)
    latency_ms = Column(Float, nullable=True)
    status = Column(
        SAEnum("running", "completed", "failed", name="node_status"),
        nullable=False,
        default="running",
    )
    order_index = Column(Integer, nullable=False, default=0)

    workflow_run = relationship("WorkflowRun", back_populates="nodes")
    llm_calls = relationship("LLMCall", back_populates="node_run", cascade="all, delete-orphan")
    retrieval_events = relationship("RetrievalEvent", back_populates="node_run", cascade="all, delete-orphan")
    tool_calls = relationship("ToolCall", back_populates="node_run", cascade="all, delete-orphan")
    token_usages = relationship("TokenUsage", back_populates="node_run", cascade="all, delete-orphan")
