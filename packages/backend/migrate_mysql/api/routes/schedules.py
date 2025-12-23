"""Schedule routes."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..auth import get_current_active_user
from ..database import get_db
from ..models import Schedule, User
from ..schemas import ScheduleCreate, ScheduleResponse

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


@router.get("", response_model=list[ScheduleResponse])
async def get_schedules(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all schedules for current user."""
    schedules = db.query(Schedule).filter(
        Schedule.user_id == current_user.id
    ).order_by(Schedule.created_at.desc()).all()

    return schedules


@router.post("", response_model=ScheduleResponse)
async def create_schedule(
    request: ScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new schedule."""
    schedule = Schedule(
        user_id=current_user.id,
        name=request.name,
        cron_expression=request.cron_expression,
        config=request.config,
        is_active=True,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a schedule."""
    schedule = db.query(Schedule).filter(
        Schedule.id == schedule_id,
        Schedule.user_id == current_user.id,
    ).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    db.delete(schedule)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
