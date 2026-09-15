"""SQLAlchemy 2.0 mappings for Core RAG tables. Schema source of truth is init_db.sql."""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_id: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="private")
    shared_with: Mapped[list] = mapped_column(ARRAY(Text), nullable=False, default=list)
    file_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_chunks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ready")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class File(Base):
    __tablename__ = "files"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Ready")
    owner_id: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class DatasetFile(Base):
    __tablename__ = "dataset_files"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    dataset_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    file_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="Pending")
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    dataset_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    dataset_file_id: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("dataset_files.id", ondelete="CASCADE"), nullable=True)
    file_id: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qdrant_point_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    embedding_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    context_enriched_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    heading_path: Mapped[list] = mapped_column(ARRAY(Text), nullable=False, default=list)
    is_parent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    parent_chunk_id: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("chunks.id", ondelete="SET NULL"), nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default="vi")
    section_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    chunk_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="standalone")
    is_table: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    table_caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    table_header: Mapped[list] = mapped_column(ARRAY(Text), nullable=False, default=list)
    quality_flags: Mapped[list] = mapped_column(ARRAY(Text), nullable=False, default=list)
    page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)


class Chatbot(Base):
    __tablename__ = "chatbots"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    owner_id: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    visibility: Mapped[str] = mapped_column(String(20), nullable=False, default="public")
    allowed_roles: Mapped[list] = mapped_column(ARRAY(Text), nullable=False, default=list)
    allowed_user_ids: Mapped[list] = mapped_column(ARRAY(PG_UUID(as_uuid=True)), nullable=False, default=list)
    allowed_departments: Mapped[list] = mapped_column(ARRAY(Text), nullable=False, default=list)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class ChatbotDataset(Base):
    __tablename__ = "chatbot_datasets"

    chatbot_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("chatbots.id", ondelete="CASCADE"), primary_key=True
    )
    dataset_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), primary_key=True
    )


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chatbot_id: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("chatbots.id", ondelete="SET NULL"), nullable=True)
    parent_id: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    branch_message_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    conversation_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    extra: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class MessageFeedback(Base):
    __tablename__ = "message_feedback"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    message_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True)
    user_id: Mapped[Optional[UUID]] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rating: Mapped[str] = mapped_column(String(10), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, default="singleton")
    config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
