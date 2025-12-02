"""History routes."""

import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..auth import get_current_active_user
from ..database import get_db
from ..models import MigrationHistory, User
from ..schemas import MigrationHistoryResponse, PaginatedResponse

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=PaginatedResponse)
async def get_history_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get paginated migration history."""
    query = db.query(MigrationHistory).filter(
        MigrationHistory.user_id == current_user.id
    )

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    items = (
        query.order_by(MigrationHistory.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedResponse(
        items=[MigrationHistoryResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{history_id}", response_model=MigrationHistoryResponse)
async def get_history_detail(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get migration history detail."""
    history = db.query(MigrationHistory).filter(
        MigrationHistory.id == history_id,
        MigrationHistory.user_id == current_user.id,
    ).first()

    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History not found",
        )

    return history
