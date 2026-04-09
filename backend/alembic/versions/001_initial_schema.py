"""Initial schema

Revision ID: 001
Revises: None
Create Date: 2026-04-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "prompt_versions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("prompt_name", sa.String(255), nullable=False, index=True),
        sa.Column("version", sa.Integer(), nullable=False, default=1),
        sa.Column("template_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
    )

    # create_type=False: table DDL must not emit CREATE TYPE (types may exist from a failed run).
    workflow_status = postgresql.ENUM(
        "running", "completed", "failed", name="workflow_status", create_type=False
    )
    workflow_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "workflow_runs",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("workflow_id", sa.String(255), nullable=False, index=True),
        sa.Column("status", workflow_status, nullable=False, server_default="running"),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_latency_ms", sa.Float(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True, default=0),
        sa.Column("avg_confidence", sa.Float(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
    )

    node_type = postgresql.ENUM(
        "retrieval", "tool", "llm", "postprocessing", name="node_type", create_type=False
    )
    node_type.create(op.get_bind(), checkfirst=True)

    node_status = postgresql.ENUM(
        "running", "completed", "failed", name="node_status", create_type=False
    )
    node_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "node_runs",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("workflow_run_id", sa.UUID(), sa.ForeignKey("workflow_runs.id"), nullable=False, index=True),
        sa.Column("node_id", sa.String(255), nullable=False),
        sa.Column("node_type", node_type, nullable=False),
        sa.Column("input_data", postgresql.JSONB(), nullable=True),
        sa.Column("output_data", postgresql.JSONB(), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("status", node_status, nullable=False, server_default="running"),
        sa.Column("order_index", sa.Integer(), nullable=False, default=0),
    )

    op.create_table(
        "llm_calls",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("node_run_id", sa.UUID(), sa.ForeignKey("node_runs.id"), nullable=False, index=True),
        sa.Column("model_name", sa.String(255), nullable=False),
        sa.Column("provider", sa.String(100), nullable=False, server_default="gemini"),
        sa.Column("prompt_text", sa.Text(), nullable=True),
        sa.Column("response_text", sa.Text(), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True, default=0),
        sa.Column("completion_tokens", sa.Integer(), nullable=True, default=0),
        sa.Column("total_tokens", sa.Integer(), nullable=True, default=0),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("prompt_version_id", sa.UUID(), sa.ForeignKey("prompt_versions.id"), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "retrieval_events",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("node_run_id", sa.UUID(), sa.ForeignKey("node_runs.id"), nullable=False, index=True),
        sa.Column("query_text", sa.Text(), nullable=True),
        sa.Column("query_embedding", Vector(384), nullable=True),
        sa.Column("num_docs_retrieved", sa.Integer(), nullable=True, default=0),
        sa.Column("doc_texts", postgresql.JSONB(), nullable=True),
        sa.Column("similarity_scores", postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column("coverage_score", sa.Float(), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
    )

    op.create_table(
        "tool_calls",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("node_run_id", sa.UUID(), sa.ForeignKey("node_runs.id"), nullable=False, index=True),
        sa.Column("tool_name", sa.String(255), nullable=False),
        sa.Column("tool_input", postgresql.JSONB(), nullable=True),
        sa.Column("tool_output", postgresql.JSONB(), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("error_message", sa.Text(), nullable=True),
    )

    op.create_table(
        "token_usage",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("workflow_run_id", sa.UUID(), sa.ForeignKey("workflow_runs.id"), nullable=False, index=True),
        sa.Column("node_run_id", sa.UUID(), sa.ForeignKey("node_runs.id"), nullable=True),
        sa.Column("model_name", sa.String(255), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("total_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("estimated_cost_usd", sa.Float(), nullable=True, default=0.0),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("token_usage")
    op.drop_table("tool_calls")
    op.drop_table("retrieval_events")
    op.drop_table("llm_calls")
    op.drop_table("node_runs")
    op.drop_table("workflow_runs")
    op.drop_table("prompt_versions")

    op.execute("DROP TYPE IF EXISTS workflow_status")
    op.execute("DROP TYPE IF EXISTS node_type")
    op.execute("DROP TYPE IF EXISTS node_status")
    op.execute("DROP EXTENSION IF EXISTS vector")
