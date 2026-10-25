"""
Service layer for Family Care Tasks and Household Coordination.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from database.connection import get_db
from database.models import CareTask, FamilyMember, Notification

TASK_CATEGORIES = ["Groceries", "Household", "Prescription", "Administrative", "Wellness"]
TASK_PRIORITIES = ["High", "Medium", "Low"]
TASK_STATUSES = ["Pending", "In Progress", "Completed"]

def create_care_task(data: Dict[str, Any]) -> CareTask:
    """Create a new family care task."""
    with get_db() as db:
        due = data["due_date"]
        if isinstance(due, str):
            due = datetime.strptime(due, "%Y-%m-%d").date()

        task = CareTask(
            family_id=data.get("family_id", 1),
            title=data["title"].strip(),
            description=data.get("description", "").strip(),
            category=data.get("category", "Household"),
            due_date=due,
            priority=data.get("priority", "Medium"),
            status="Pending",
            assigned_member_id=data.get("assigned_member_id")
        )
        db.add(task)
        db.flush()

        assigned_str = ""
        if task.assigned_member_id:
            assigned = db.query(FamilyMember).filter(FamilyMember.id == task.assigned_member_id).first()
            if assigned:
                assigned_str = f" Assigned to {assigned.full_name}."

        notif = Notification(
            family_id=task.family_id,
            member_id=task.assigned_member_id,
            title=f"New Care Task: {task.title}",
            message=f"Due on {task.due_date.strftime('%b %d, %Y')}. Priority: {task.priority}.{assigned_str}",
            category="Task",
            priority="Info" if task.priority != "High" else "Warning"
        )
        db.add(notif)
        db.refresh(task)
        return task

def update_task_status(task_id: int, new_status: str) -> Optional[CareTask]:
    """Update task status (Pending, In Progress, Completed)."""
    with get_db() as db:
        task = db.query(CareTask).filter(CareTask.id == task_id).first()
        if not task:
            return None
        task.status = new_status
        if new_status == "Completed":
            task.completed_at = datetime.utcnow()
        db.flush()
        db.refresh(task)
        return task

def get_care_tasks(family_id: int = 1, status: Optional[str] = None) -> List[CareTask]:
    """Retrieve family care tasks, optionally filtered by status."""
    with get_db() as db:
        q = db.query(CareTask).filter(CareTask.family_id == family_id)
        if status:
            q = q.filter(CareTask.status == status)
        return q.order_by(CareTask.due_date.asc(), CareTask.id.desc()).all()

def get_pending_tasks_count(family_id: int = 1) -> int:
    """Return count of active/pending tasks."""
    with get_db() as db:
        return db.query(CareTask).filter(
            CareTask.family_id == family_id,
            CareTask.status.in_(["Pending", "In Progress"])
        ).count()
