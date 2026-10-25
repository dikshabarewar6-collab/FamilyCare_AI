"""
Service layer for In-App Notifications and Alerts.
"""
from typing import List, Optional
from database.connection import get_db
from database.models import Notification

def get_recent_notifications(family_id: int = 1, limit: int = 15) -> List[Notification]:
    """Retrieve recent notifications ordered by timestamp."""
    with get_db() as db:
        return (
            db.query(Notification)
            .filter(Notification.family_id == family_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

def get_unread_count(family_id: int = 1) -> int:
    """Return count of unread notifications."""
    with get_db() as db:
        return (
            db.query(Notification)
            .filter(Notification.family_id == family_id, Notification.is_read == False)
            .count()
        )

def mark_all_notifications_as_read(family_id: int = 1):
    """Mark all notifications as read for a family."""
    with get_db() as db:
        db.query(Notification).filter(
            Notification.family_id == family_id,
            Notification.is_read == False
        ).update({Notification.is_read: True})

def create_notification(
    family_id: int,
    title: str,
    message: str,
    category: str = "System",
    priority: str = "Info",
    member_id: Optional[int] = None,
    is_simulated: bool = False
) -> Notification:
    """Create a new in-app notification."""
    with get_db() as db:
        notif = Notification(
            family_id=family_id,
            member_id=member_id,
            title=title,
            message=message,
            category=category,
            priority=priority,
            is_read=False,
            is_simulated=is_simulated
        )
        db.add(notif)
        db.flush()
        db.refresh(notif)
        return notif
