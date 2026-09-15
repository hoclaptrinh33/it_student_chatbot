"""
Session Repository - Data Access Layer cho Chat Sessions & History
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

from sqlalchemy import func, select

from app.models.orm import Message, MessageFeedback, Session
from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)

_EXTRA_KEYS = {"latency_ms", "cached", "no_context", "feedback", "feedback_at", "feedback_comment"}


class SessionRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session, Session)

    async def create_session(
        self,
        user_id: str,
        name: str,
        parent_id: Optional[str] = None,
        branch_message_index: Optional[int] = None,
    ) -> dict:
        uid = self.parse_id(user_id)
        if not uid:
            raise ValueError("user_id must be a UUID")
        row = Session(
            user_id=uid,
            name=name,
            parent_id=self.parse_id(parent_id) if parent_id else None,
            branch_message_index=branch_message_index,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.session.add(row)
        await self.session.flush()
        return self.serialize_row(row)

    async def get_user_sessions(self, user_id: str, limit: int = 50, skip: int = 0) -> List[dict]:
        uid = self.parse_id(user_id)
        if not uid:
            return []
        result = await self.session.execute(
            select(Session)
            .where(Session.user_id == uid)
            .order_by(Session.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.serialize_rows(result.scalars().all())

    async def get_session(self, session_id: str) -> Optional[dict]:
        uid = self.parse_id(session_id)
        if not uid:
            return None
        row = await self.session.get(Session, uid)
        return self.serialize_row(row)

    async def update_session(self, session_id: str, update_data: dict) -> Optional[dict]:
        uid = self.parse_id(session_id)
        if not uid:
            return None
        row = await self.session.get(Session, uid)
        if not row:
            return None
        payload = dict(update_data)
        payload["updated_at"] = datetime.utcnow()
        if "parent_id" in payload and payload["parent_id"]:
            payload["parent_id"] = self.parse_id(payload["parent_id"])
        if "chatbot_id" in payload and payload["chatbot_id"]:
            payload["chatbot_id"] = self.parse_id(payload["chatbot_id"])
        if "user_id" in payload and payload["user_id"]:
            payload["user_id"] = self.parse_id(payload["user_id"])
        for key, value in payload.items():
            if hasattr(row, key):
                setattr(row, key, value)
        await self.session.flush()
        return self.serialize_row(row)

    async def delete_session(self, session_id: str) -> bool:
        uid = self.parse_id(session_id)
        if not uid:
            return False
        row = await self.session.get(Session, uid)
        if not row:
            return False
        await self.session.delete(row)
        await self.session.flush()
        return True

    def _serialize_message(self, row: Message, feedback: Optional[MessageFeedback] = None) -> dict:
        doc = self.serialize_row(row)
        if feedback:
            doc["feedback"] = feedback.rating
            doc["feedback_comment"] = feedback.comment
            doc["feedback_at"] = feedback.created_at
        return doc

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> dict:
        sid = self.parse_id(session_id)
        if not sid:
            raise ValueError("session_id must be a UUID")
        extra = {k: v for k, v in (extra or {}).items() if v is not None}
        sources = extra.pop("sources", None)
        extra_json = {k: v for k, v in extra.items() if k in _EXTRA_KEYS or k not in {"sources"}}
        row = Message(
            session_id=sid,
            role=role,
            content=content,
            sources=sources,
            extra=extra_json,
            created_at=datetime.utcnow(),
        )
        self.session.add(row)
        session_row = await self.session.get(Session, sid)
        if session_row:
            session_row.updated_at = datetime.utcnow()
        await self.session.flush()
        return self._serialize_message(row)

    async def get_messages(self, session_id: str, limit: int = 100) -> List[dict]:
        sid = self.parse_id(session_id)
        if not sid:
            return []
        result = await self.session.execute(
            select(Message)
            .where(Message.session_id == sid)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )
        messages = result.scalars().all()
        if not messages:
            return []
        ids = [m.id for m in messages]
        fb_result = await self.session.execute(
            select(MessageFeedback).where(MessageFeedback.message_id.in_(ids))
        )
        fb_by_msg = {}
        for fb in fb_result.scalars().all():
            fb_by_msg[fb.message_id] = fb
        return [self._serialize_message(m, fb_by_msg.get(m.id)) for m in messages]

    async def get_message(self, message_id: str) -> Optional[dict]:
        uid = self.parse_id(message_id)
        if not uid:
            return None
        row = await self.session.get(Message, uid)
        if not row:
            return None
        fb_result = await self.session.execute(
            select(MessageFeedback).where(MessageFeedback.message_id == uid)
        )
        return self._serialize_message(row, fb_result.scalars().first())

    async def set_message_feedback(
        self,
        message_id: str,
        rating: str,
        comment: Optional[str] = None,
    ) -> bool:
        uid = self.parse_id(message_id)
        if not uid:
            return False
        msg = await self.session.get(Message, uid)
        if not msg or msg.role != "assistant":
            return False
        result = await self.session.execute(
            select(MessageFeedback).where(MessageFeedback.message_id == uid)
        )
        existing = result.scalars().first()
        if existing:
            existing.rating = rating
            existing.comment = comment
            existing.session_id = msg.session_id
        else:
            self.session.add(
                MessageFeedback(
                    message_id=uid,
                    session_id=msg.session_id,
                    rating=rating,
                    comment=comment,
                    created_at=datetime.utcnow(),
                )
            )
        extra = dict(msg.extra or {})
        extra["feedback"] = rating
        extra["feedback_at"] = datetime.utcnow().isoformat()
        if comment is not None:
            extra["feedback_comment"] = comment
        msg.extra = extra
        await self.session.flush()
        return True

    async def get_recent_user_questions(self, user_id: str, limit: int = 8) -> List[str]:
        sessions = await self.get_user_sessions(user_id, limit=20)
        session_ids = [self.parse_id(s["id"]) for s in sessions]
        session_ids = [sid for sid in session_ids if sid]
        if not session_ids:
            return []
        result = await self.session.execute(
            select(Message.content)
            .where(Message.session_id.in_(session_ids), Message.role == "user")
            .order_by(Message.created_at.desc())
            .limit(40)
        )
        seen = set()
        questions = []
        for (text,) in result.all():
            text = (text or "").strip()
            key = text.lower()
            if len(text) < 8 or key in seen:
                continue
            seen.add(key)
            questions.append(text)
            if len(questions) >= limit:
                break
        return questions

    async def get_feedback_counts(self) -> Dict[str, int]:
        result = await self.session.execute(
            select(MessageFeedback.rating, func.count())
            .where(MessageFeedback.rating.in_(["up", "down"]))
            .group_by(MessageFeedback.rating)
        )
        counts = {"up": 0, "down": 0}
        for rating, count in result.all():
            if rating in counts:
                counts[rating] = int(count)
        return counts

    async def get_average_latency_ms(self, sample_limit: int = 200) -> Optional[float]:
        result = await self.session.execute(
            select(Message.extra)
            .where(Message.role == "assistant")
            .order_by(Message.created_at.desc())
            .limit(sample_limit)
        )
        values = []
        for (extra,) in result.all():
            if isinstance(extra, dict):
                latency = extra.get("latency_ms")
                if isinstance(latency, (int, float)) and latency > 0:
                    values.append(float(latency))
        if not values:
            return None
        return sum(values) / len(values)
