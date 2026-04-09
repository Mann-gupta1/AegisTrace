import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_name = Column(String(255), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    template_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    metadata_ = Column("metadata", JSONB, nullable=True)

    llm_calls = relationship("LLMCall", back_populates="prompt_version")
