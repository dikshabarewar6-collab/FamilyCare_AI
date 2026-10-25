"""
Service layer for Medication Reminders, Acknowledged vs Taken logs,
and adherence tracking.

Relationships are eagerly loaded where needed to prevent
SQLAlchemy DetachedInstanceError after the database session closes.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import joinedload

from database.connection import get_db
from database.models import (
    MedicationReminder,
    MedicationLog,
    FamilyMember,
    Notification,
)


def _clean(value: Any) -> str:
    """Safely convert optional text values to strings."""
    return str(value or "").strip()


def create_medication_reminder(
    data: Dict[str, Any],
) -> MedicationReminder:
    """Create a medication reminder and its notification."""

    with get_db() as db:
        member = (
            db.query(FamilyMember)
            .filter(FamilyMember.id == data["member_id"])
            .first()
        )

        if member is None:
            raise ValueError(
                f"Family member #{data['member_id']} not found."
            )

        reminder = MedicationReminder(
            member_id=data["member_id"],
            medication_name=_clean(data["medication_name"]),
            dosage_label=_clean(data.get("dosage_label")),
            schedule_time=_clean(
                data.get("schedule_time") or "08:00"
            ),
            frequency=data.get("frequency") or "Daily",
            instructions=_clean(data.get("instructions")),
            is_active=True,
        )

        db.add(reminder)
        db.flush()

        notification = Notification(
            family_id=member.family_id,
            member_id=reminder.member_id,
            title="New Medication Reminder Added",
            message=(
                f"Reminder set for {member.full_name}: "
                f"{reminder.medication_name} "
                f"({reminder.dosage_label or 'As directed'}) "
                f"at {reminder.schedule_time}."
            ),
            category="Medication",
            priority="Info",
        )

        db.add(notification)
        db.flush()

        reminder_id = reminder.id

        # Reload the reminder and member relationship before
        # the database session closes.
        result = (
            db.query(MedicationReminder)
            .options(
                joinedload(MedicationReminder.member)
            )
            .filter(MedicationReminder.id == reminder_id)
            .first()
        )

        return result


def record_medication_acknowledgement(
    reminder_id: int,
    status: str = "Taken",
    note: str = "",
    is_simulated: bool = False,
) -> MedicationLog:
    """
    Record a user's medication acknowledgement.

    A recorded acknowledgement does not verify clinical consumption.
    """

    allowed_statuses = {"Taken", "Skipped", "Pending"}

    if status not in allowed_statuses:
        raise ValueError(
            f"Invalid medication status: {status}. "
            f"Allowed statuses: {', '.join(sorted(allowed_statuses))}"
        )

    today = date.today()
    now = datetime.now()

    with get_db() as db:
        reminder = (
            db.query(MedicationReminder)
            .filter(MedicationReminder.id == reminder_id)
            .first()
        )

        if reminder is None:
            raise ValueError(
                f"Medication reminder #{reminder_id} not found."
            )

        # Find today's existing log for this reminder.
        log = (
            db.query(MedicationLog)
            .filter(
                MedicationLog.reminder_id == reminder_id,
                MedicationLog.log_date == today,
            )
            .first()
        )

        if log is not None:
            log.status = status
            log.logged_at = now
            log.acknowledgement_note = note
            log.is_simulated = is_simulated

        else:
            log = MedicationLog(
                reminder_id=reminder.id,
                member_id=reminder.member_id,
                scheduled_time=reminder.schedule_time,
                log_date=today,
                logged_at=now,
                status=status,
                acknowledgement_note=note,
                is_simulated=is_simulated,
            )

            db.add(log)
            db.flush()

        member = (
            db.query(FamilyMember)
            .filter(FamilyMember.id == reminder.member_id)
            .first()
        )

        member_name = (
            member.full_name if member else "Family Member"
        )

        notification = Notification(
            family_id=member.family_id if member else 1,
            member_id=reminder.member_id,
            title=(
                f"Medication Acknowledged: "
                f"{reminder.medication_name}"
            ),
            message=(
                f"{member_name} recorded "
                f"{reminder.medication_name} as '{status}' "
                f"at {now.strftime('%I:%M %p')}."
            ),
            category="Medication",
            priority="Info",
            is_simulated=is_simulated,
        )

        db.add(notification)
        db.flush()

        log_id = log.id

        # Load both relationships before the session closes.
        result = (
            db.query(MedicationLog)
            .options(
                joinedload(MedicationLog.reminder)
                .joinedload(MedicationReminder.member)
            )
            .filter(MedicationLog.id == log_id)
            .first()
        )

        return result


def get_medication_reminders(
    member_id: Optional[int] = None,
) -> List[MedicationReminder]:
    """Retrieve active medication reminders with member details."""

    with get_db() as db:
        query = (
            db.query(MedicationReminder)
            .options(
                joinedload(MedicationReminder.member)
            )
            .filter(MedicationReminder.is_active.is_(True))
        )

        if member_id is not None:
            query = query.filter(
                MedicationReminder.member_id == member_id
            )

        return query.order_by(
            MedicationReminder.schedule_time.asc()
        ).all()


def get_today_medication_status(
    member_id: int,
) -> List[Dict[str, Any]]:
    """Retrieve today's medication reminders and acknowledgement status."""

    today = date.today()

    with get_db() as db:
        reminders = (
            db.query(MedicationReminder)
            .options(
                joinedload(MedicationReminder.member)
            )
            .filter(
                MedicationReminder.member_id == member_id,
                MedicationReminder.is_active.is_(True),
            )
            .order_by(
                MedicationReminder.schedule_time.asc()
            )
            .all()
        )

        if not reminders:
            return []

        reminder_ids = [reminder.id for reminder in reminders]

        logs = (
            db.query(MedicationLog)
            .filter(
                MedicationLog.reminder_id.in_(reminder_ids),
                MedicationLog.log_date == today,
            )
            .all()
        )

        # Each reminder normally has one log per day.
        logs_by_reminder_id = {
            log.reminder_id: log
            for log in logs
        }

        results = []

        for reminder in reminders:
            log = logs_by_reminder_id.get(reminder.id)

            results.append(
                {
                    "reminder": reminder,
                    "status": log.status if log else "Pending",
                    "logged_at": log.logged_at if log else None,
                    "note": (
                        log.acknowledgement_note
                        if log
                        else ""
                    ),
                }
            )

        return results


def get_medication_logs(
    limit: int = 40,
) -> List[MedicationLog]:
    """
    Retrieve medication history with reminder and family member
    relationships eagerly loaded.
    """

    with get_db() as db:
        logs = (
            db.query(MedicationLog)
            .options(
                joinedload(MedicationLog.reminder)
                .joinedload(MedicationReminder.member)
            )
            .order_by(
                MedicationLog.log_date.desc(),
                MedicationLog.logged_at.desc(),
                MedicationLog.id.desc(),
            )
            .limit(max(1, limit))
            .all()
        )

        return logs