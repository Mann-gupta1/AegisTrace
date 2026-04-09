import uuid

from sqlalchemy import Column, String, Text, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db_base import Base


class ToolCall(Base):
    __tablename__ = "tool_calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_run_id = Column(UUID(as_uuid=True), ForeignKey("node_runs.id"), nullable=False, index=True)
    tool_name = Column(String(255), nullable=False)
    tool_input = Column(JSONB, nullable=True)
    tool_output = Column(JSONB, nullable=True)
    latency_ms = Column(Float, nullable=True)
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)

    node_run = relationship("NodeRun", back_populates="tool_calls")
