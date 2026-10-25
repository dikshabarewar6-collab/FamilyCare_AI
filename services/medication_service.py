"""
Service layer for Medication Reminders, Acknowledged vs Taken logs,
and adherence tracking.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Tuple
from database.connection import get_db
from database.models import MedicationReminder, MedicationLog, FamilyMember, Notification

def create_medication_reminder(data: Dict[str, Any]) -> MedicationReminder:
    """Create a new medication reminder schedule."""
    with get_db() as db:
        reminder = MedicationReminder(
            member_id=data["member_id"],
            medication_name=data["medication_name"].strip(),
            dosage_label=data.get("dosage_label", "").strip(),
            schedule_time=data.get("schedule_time", "08:00").strip(),
            frequency=data.get("frequency", "Daily"),
            instructions=data.get("instructions", "").strip(),
            is_active=True
        )
        db.add(reminder)
        db.flush()

        member = db.query(FamilyMember).filter(FamilyMember.id == reminder.member_id).first()
        mem_name = member.full_name if member else "Family Member"

        notif = Notification(
            family_id=member.family_id if member else 1,
            member_id=reminder.member_id,
            title="New Medication Reminder Added",
            message=f"Reminder set for {mem_name}: {reminder.medication_name} ({reminder.dosage_label}) at {reminder.schedule_time}.",
            category="Medication",
            priority="Info"
        )
        db.add(notif)
        db.refresh(reminder)
        return reminder

def record_medication_acknowledgement(
    reminder_id: int,
    status: str = "Taken",
    note: str = "",
    is_simulated: bool = False
) -> MedicationLog:
    """
    Record that a medication reminder was acknowledged or taken.
    NOTE: Distinguishes recorded acknowledgement from verified clinical consumption.
    """
    today = date.today()
    now = datetime.now()

    with get_db() as db:
        reminder = db.query(MedicationReminder).filter(MedicationReminder.id == reminder_id).first()
        if not reminder:
            raise ValueError(f"Reminder #{reminder_id} not found.")

        # Check if already logged for today
        log = db.query(MedicationLog).filter(
            MedicationLog.reminder_id == reminder_id,
            MedicationLog.log_date == today
        ).first()

        if log:
            log.status = status
            log.logged_at = now
            log.acknowledgement_note = note
            log.is_simulated = is_simulated
        else:
            log = MedicationLog(
                reminder_id=reminder_id,
                member_id=reminder.member_id,
                scheduled_time=reminder.schedule_time,
                log_date=today,
                logged_at=now,
                status=status,
                acknowledgement_note=note,
                is_simulated=is_simulated
            )
            db.add(log)
            db.flush()

        member = db.query(FamilyMember).filter(FamilyMember.id == reminder.member_id).first()
        mem_name = member.full_name if member else "Family Member"

        notif = Notification(
            family_id=member.family_id if member else 1,
            member_id=reminder.member_id,
            title=f"Medication Acknowledged: {reminder.medication_name}",
            message=f"{mem_name} recorded {reminder.medication_name} as '{status}' at {now.strftime('%I:%M %p')}.",
            category="Medication",
            priority="Info",
            is_simulated=is_simulated
        )
        db.add(notif)
        db.refresh(log)
        return log

def get_medication_reminders(member_id: Optional[int] = None) -> List[MedicationReminder]:
    """Retrieve all active medication reminders."""
    with get_db() as db:
        q = db.query(MedicationReminder).filter(MedicationReminder.is_active == True)
        if member_id:
            q = q.filter(MedicationReminder.member_id == member_id)
        return q.all()

def get_today_medication_status(member_id: int) -> List[Dict[str, Any]]:
    """Retrieve today's reminders and whether they have been acknowledged."""
    today = date.today()
    results = []
    with get_db() as db:
        reminders = db.query(MedicationReminder).filter(
            MedicationReminder.member_id == member_id,
            MedicationReminder.is_active == True
        ).all()

        for r in reminders:
            log = db.query(MedicationLog).filter(
                MedicationLog.reminder_id == r.id,
                MedicationLog.log_date == today
            ).first()

            results.append({
                "reminder": r,
                "status": log.status if log else "Pending",
                "logged_at": log.logged_at if log else None,
                "note": log.acknowledgement_note if log else ""
            })
    return results

def get_medication_logs(limit: int = 40) -> List[MedicationLog]:
    """Retrieve medication log history."""
    with get_db() as db:
        return db.query(MedicationLog).order_by(MedicationLog.log_date.desc(), MedicationLog.logged_at.desc()).limit(limit).all()
