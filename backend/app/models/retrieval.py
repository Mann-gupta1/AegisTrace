import uuid

from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.db_base import Base


class RetrievalEvent(Base):
    __tablename__ = "retrieval_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_run_id = Column(UUID(as_uuid=True), ForeignKey("node_runs.id"), nullable=False, index=True)
    query_text = Column(Text, nullable=True)
    query_embedding = Column(Vector(384), nullable=True)
    num_docs_retrieved = Column(Integer, nullable=True, default=0)
    doc_texts = Column(JSONB, nullable=True)
    similarity_scores = Column(ARRAY(Float), nullable=True)
    coverage_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)

    node_run = relationship("NodeRun", back_populates="retrieval_events")
