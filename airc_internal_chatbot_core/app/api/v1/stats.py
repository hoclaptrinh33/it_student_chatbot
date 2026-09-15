"""
Statistics API endpoints
Provides dashboard statistics and system metrics
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
import logging
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.orm import Chatbot, Dataset, Session as ChatSession
from app.services.cache_service import semantic_cache_service
from app.models.auth import User, Permission
from app.api.dependencies import require_permission, get_session_repo

logger = logging.getLogger(__name__)

router = APIRouter()


class DashboardStats(BaseModel):
    """Dashboard statistics response"""
    chatbot_count: int = 0
    dataset_count: int = 0
    conversation_count: int = 0
    user_count: int = 0
    
    # RAG Performance
    avg_response_time: float = 0.0  # seconds
    accuracy_rate: float = 0.0  # percentage
    cache_hit_rate: float = 0.0  # percentage
    total_chunks_indexed: int = 0
    
    # Recent activity
    conversations_today: int = 0
    datasets_processing: int = 0


class RecentActivity(BaseModel):
    """Recent activity item"""
    type: str  # chatbot, dataset, conversation
    title: str
    description: str
    timestamp: datetime


async def _count(session: AsyncSession, stmt) -> int:
    result = await session.execute(stmt)
    return int(result.scalar_one() or 0)


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(require_permission(Permission.ANALYTICS_VIEW)),
    session_repo=Depends(get_session_repo),
    session: AsyncSession = Depends(get_session),
):
    """
    Get dashboard statistics for admin/teacher view
    """
    try:
        chatbot_count = await _count(session, select(func.count()).select_from(Chatbot))
        dataset_count = await _count(session, select(func.count()).select_from(Dataset))
        conversation_count = await _count(session, select(func.count()).select_from(ChatSession))
        user_count = await _count(
            session, select(func.count(func.distinct(ChatSession.user_id)))
        )

        total_chunks_result = await session.execute(select(func.coalesce(func.sum(Dataset.total_chunks), 0)))
        total_chunks = int(total_chunks_result.scalar_one() or 0)

        datasets_processing = await _count(
            session,
            select(func.count()).select_from(Dataset).where(Dataset.status.in_(["processing", "pending"])),
        )

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        conversations_today = await _count(
            session,
            select(func.count()).select_from(ChatSession).where(ChatSession.created_at >= today_start),
        )

        cache_stats = semantic_cache_service.get_stats()
        cache_hit_rate = 0.0
        if cache_stats.get("hits", 0) + cache_stats.get("misses", 0) > 0:
            cache_hit_rate = (cache_stats.get("hits", 0) /
                           (cache_stats.get("hits", 0) + cache_stats.get("misses", 0))) * 100

        avg_latency_ms = await session_repo.get_average_latency_ms()
        avg_response_time = round((avg_latency_ms or 0) / 1000.0, 2)

        feedback_counts = await session_repo.get_feedback_counts()
        rated = feedback_counts.get("up", 0) + feedback_counts.get("down", 0)
        accuracy_rate = (
            round((feedback_counts.get("up", 0) / rated) * 100, 1) if rated else 0.0
        )

        return DashboardStats(
            chatbot_count=chatbot_count,
            dataset_count=dataset_count,
            conversation_count=conversation_count,
            user_count=user_count,
            avg_response_time=avg_response_time,
            accuracy_rate=accuracy_rate,
            cache_hit_rate=round(cache_hit_rate, 1),
            total_chunks_indexed=total_chunks,
            conversations_today=conversations_today,
            datasets_processing=datasets_processing
        )

    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-activity", response_model=List[RecentActivity])
async def get_recent_activity(
    limit: int = 5,
    current_user: User = Depends(require_permission(Permission.ANALYTICS_VIEW)),
    session: AsyncSession = Depends(get_session),
):
    """
    Get recent system activities for dashboard
    """
    try:
        activities = []

        chatbot_result = await session.execute(
            select(Chatbot).order_by(Chatbot.updated_at.desc().nullslast()).limit(2)
        )
        for bot in chatbot_result.scalars().all():
            activities.append(RecentActivity(
                type="chatbot",
                title=f'Chatbot "{bot.name or "Unknown"}"',
                description="được cập nhật",
                timestamp=bot.updated_at or bot.created_at or datetime.utcnow()
            ))

        dataset_result = await session.execute(
            select(Dataset)
            .where(Dataset.status.in_(["completed", "ready"]))
            .order_by(Dataset.updated_at.desc().nullslast())
            .limit(2)
        )
        for ds in dataset_result.scalars().all():
            activities.append(RecentActivity(
                type="dataset",
                title=f'Dataset "{ds.name or "Unknown"}"',
                description="xử lý hoàn tất",
                timestamp=ds.updated_at or ds.created_at or datetime.utcnow()
            ))

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        conv_today = await _count(
            session,
            select(func.count()).select_from(ChatSession).where(ChatSession.created_at >= today_start),
        )
        if conv_today > 0:
            activities.append(RecentActivity(
                type="conversation",
                title=f"{conv_today} cuộc hội thoại mới",
                description="trong hôm nay",
                timestamp=datetime.utcnow()
            ))

        activities.sort(key=lambda x: x.timestamp, reverse=True)
        return activities[:limit]

    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))
