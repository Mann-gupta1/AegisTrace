import uuid

from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class LLMCall(Base):
    __tablename__ = "llm_calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_run_id = Column(UUID(as_uuid=True), ForeignKey("node_runs.id"), nullable=False, index=True)
    model_name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False, default="gemini")
    prompt_text = Column(Text, nullable=True)
    response_text = Column(Text, nullable=True)
    prompt_tokens = Column(Integer, nullable=True, default=0)
    completion_tokens = Column(Integer, nullable=True, default=0)
    total_tokens = Column(Integer, nullable=True, default=0)
    latency_ms = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    prompt_version_id = Column(UUID(as_uuid=True), ForeignKey("prompt_versions.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    node_run = relationship("NodeRun", back_populates="llm_calls")
    prompt_version = relationship("PromptVersion", back_populates="llm_calls")
