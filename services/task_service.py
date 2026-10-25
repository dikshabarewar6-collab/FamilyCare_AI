"""
Service layer for Family Care Tasks and Household Coordination.
Handles task creation, retrieval, and status updates.
Eagerly loads relationships to prevent DetachedInstanceError.
"""

from datetime import datetime, date, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import joinedload

from database.connection import get_db
from database.models import CareTask, FamilyMember, Notification


TASK_CATEGORIES = [
    "Groceries",
    "Household",
    "Prescription",
    "Administrative",
    "Wellness",
]

TASK_PRIORITIES = [
    "High",
    "Medium",
    "Low",
]

TASK_STATUSES = [
    "Pending",
    "In Progress",
    "Completed",
]


def _load_task_with_relationships(db, task_id: int) -> Optional[CareTask]:
    """
    Retrieve a task with assigned_member already loaded.
    The relationship remains accessible after the session closes.
    """
    return (
        db.query(CareTask)
        .options(joinedload(CareTask.assigned_member))
        .filter(CareTask.id == task_id)
        .first()
    )


def create_care_task(data: Dict[str, Any]) -> CareTask:
    """Create a new family care task and its notification."""

    with get_db() as db:

        due = data["due_date"]

        if isinstance(due, str):
            due = datetime.strptime(due, "%Y-%m-%d").date()

        elif isinstance(due, datetime):
            due = due.date()

        task = CareTask(
            family_id=data.get("family_id", 1),
            title=data["title"].strip(),
            description=(data.get("description") or "").strip(),
            category=data.get("category", "Household"),
            due_date=due,
            priority=data.get("priority", "Medium"),
            status="Pending",
            assigned_member_id=data.get("assigned_member_id"),
        )

        db.add(task)
        db.flush()

        # Prepare the assigned member's name for the notification.
        assigned_str = ""

        if task.assigned_member_id:
            assigned = (
                db.query(FamilyMember)
                .filter(
                    FamilyMember.id == task.assigned_member_id,
                    FamilyMember.family_id == task.family_id,
                )
                .first()
            )

            if assigned:
                assigned_str = f" Assigned to {assigned.full_name}."

        notification = Notification(
            family_id=task.family_id,
            member_id=task.assigned_member_id,
            title=f"New Care Task: {task.title}",
            message=(
                f"Due on {task.due_date.strftime('%b %d, %Y')}. "
                f"Priority: {task.priority}."
                f"{assigned_str}"
            ),
            category="Task",
            priority=(
                "Warning"
                if task.priority == "High"
                else "Info"
            ),
        )

        db.add(notification)
        db.flush()

        # Reload the task while the database session is open.
        task_id = task.id

        result = _load_task_with_relationships(db, task_id)

        return result


def update_task_status(
    task_id: int,
    new_status: str,
) -> Optional[CareTask]:
    """Update task status and return the task with relationships loaded."""

    if new_status not in TASK_STATUSES:
        raise ValueError(
            f"Invalid task status: {new_status}. "
            f"Allowed statuses: {', '.join(TASK_STATUSES)}"
        )

    with get_db() as db:

        task = (
            db.query(CareTask)
            .filter(CareTask.id == task_id)
            .first()
        )

        if task is None:
            return None

        task.status = new_status

        if new_status == "Completed":
            task.completed_at = datetime.now(timezone.utc)
        else:
            task.completed_at = None

        db.flush()

        # Reload assigned_member before the session closes.
        result = _load_task_with_relationships(db, task_id)

        return result


def get_care_tasks(
    family_id: int = 1,
    status: Optional[str] = None,
) -> List[CareTask]:
    """Retrieve family care tasks with assigned members eagerly loaded."""

    with get_db() as db:

        query = (
            db.query(CareTask)
            .options(joinedload(CareTask.assigned_member))
            .filter(CareTask.family_id == family_id)
        )

        if status:
            query = query.filter(CareTask.status == status)

        tasks = query.order_by(
            CareTask.due_date.asc(),
            CareTask.id.desc(),
        ).all()

        return tasks


def get_pending_tasks_count(family_id: int = 1) -> int:
    """Return the number of pending and in-progress tasks."""

    with get_db() as db:

        return (
            db.query(CareTask)
            .filter(
                CareTask.family_id == family_id,
                CareTask.status.in_(
                    ["Pending", "In Progress"]
                ),
            )
            .count()
        )