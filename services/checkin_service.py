"""
Service layer for Daily Check-In routine, grace period calculation,
and overdue/missed check-in detection.
"""
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any, Optional, Tuple
from database.connection import get_db
from database.models import CheckInRecord, FamilyMember, Notification

def get_today_checkin_status(member_id: int) -> Tuple[str, Optional[CheckInRecord]]:
    """
    Evaluate today's check-in status for a given family member.
    Returns (status, record):
      - 'Checked In': Member completed check-in today
      - 'Awaiting Check-In': Within schedule or still within grace period
      - 'Missed Check-In': Past scheduled time + grace period without check-in
    """
    today = date.today()
    now = datetime.now()

    with get_db() as db:
        member = db.query(FamilyMember).filter(FamilyMember.id == member_id).first()
        if not member:
            return ("Unknown", None)

        record = db.query(CheckInRecord).filter(
            CheckInRecord.member_id == member_id,
            CheckInRecord.checkin_date == today
        ).first()

        if record and record.status == "Checked In":
            return ("Checked In", record)

        # Parse member's scheduled target time
        target_str = member.morning_checkin_time or "09:00"
        try:
            parts = [int(p) for p in target_str.split(":")]
            target_time = time(parts[0], parts[1])
        except Exception:
            target_time = time(9, 0)

        grace_mins = member.grace_period_minutes or 60
        target_dt = datetime.combine(today, target_time)
        deadline_dt = target_dt + timedelta(minutes=grace_mins)

        if now > deadline_dt:
            # Overdue / Missed Check-in
            if not record:
                # Create a missed record
                record = CheckInRecord(
                    member_id=member_id,
                    checkin_date=today,
                    scheduled_time=target_str,
                    status="Missed Check-In",
                    notes="Check-in window and grace period expired without response."
                )
                db.add(record)
                db.flush()
            elif record.status != "Missed Check-In":
                record.status = "Missed Check-In"
                db.flush()
            return ("Missed Check-In", record)
        else:
            # Still within window
            if not record:
                record = CheckInRecord(
                    member_id=member_id,
                    checkin_date=today,
                    scheduled_time=target_str,
                    status="Awaiting Check-In"
                )
                db.add(record)
                db.flush()
            return ("Awaiting Check-In", record)

def record_checkin(member_id: int, mood: str = "Good", notes: str = "", is_simulated: bool = False) -> CheckInRecord:
    """Record an 'I'm Okay' check-in for today."""
    today = date.today()
    now = datetime.now()

    with get_db() as db:
        member = db.query(FamilyMember).filter(FamilyMember.id == member_id).first()
        if not member:
            raise ValueError(f"Family member #{member_id} not found.")

        record = db.query(CheckInRecord).filter(
            CheckInRecord.member_id == member_id,
            CheckInRecord.checkin_date == today
        ).first()

        target_str = member.morning_checkin_time or "09:00"

        if record:
            record.status = "Checked In"
            record.actual_checkin_time = now
            record.mood = mood
            record.notes = notes
            record.is_simulated = is_simulated
            db.flush()
        else:
            record = CheckInRecord(
                member_id=member_id,
                checkin_date=today,
                scheduled_time=target_str,
                actual_checkin_time=now,
                status="Checked In",
                mood=mood,
                notes=notes,
                is_simulated=is_simulated
            )
            db.add(record)
            db.flush()

        # Create confirmation notification for family
        notif = Notification(
            family_id=member.family_id,
            member_id=member_id,
            title=f"✓ {member.full_name} Checked In ('I'm Okay')",
            message=f"{member.full_name} checked in at {now.strftime('%I:%M %p')}. Mood: {mood}. {f'Note: {notes}' if notes else ''}",
            category="Check-In",
            priority="Info",
            is_simulated=is_simulated
        )
        db.add(notif)
        db.refresh(record)
        return record

def simulate_missed_checkin(member_id: int) -> CheckInRecord:
    """
    Judge/Demo Simulator: Triggers a simulated missed check-in workflow.
    Generates simulated alerts for primary caregiver.
    """
    today = date.today()
    with get_db() as db:
        member = db.query(FamilyMember).filter(FamilyMember.id == member_id).first()
        if not member:
            raise ValueError("Member not found.")

        record = db.query(CheckInRecord).filter(
            CheckInRecord.member_id == member_id,
            CheckInRecord.checkin_date == today
        ).first()

        target_str = member.morning_checkin_time or "09:00"
        if not record:
            record = CheckInRecord(
                member_id=member_id,
                checkin_date=today,
                scheduled_time=target_str,
                status="Missed Check-In",
                notes="[SIMULATED DEMO] Overdue morning check-in window.",
                is_simulated=True
            )
            db.add(record)
        else:
            record.status = "Missed Check-In"
            record.notes = "[SIMULATED DEMO] Overdue morning check-in window."
            record.is_simulated = True
        db.flush()

        # Simulated alert notification
        cg_text = f"Primary Caregiver ({member.assigned_caregiver.full_name if member.assigned_caregiver else 'Family'}) alerted."
        notif = Notification(
            family_id=member.family_id,
            member_id=member_id,
            title=f"⚠️ [SIMULATION] Missed Check-In: {member.full_name}",
            message=(
                f"[DEMO SIMULATION] {member.full_name} did not check in by {target_str} + "
                f"{member.grace_period_minutes}m grace period. {cg_text} "
                "Note: A missed check-in is not automatically an emergency."
            ),
            category="Check-In",
            priority="Warning",
            is_simulated=True
        )
        db.add(notif)
        db.refresh(record)
        return record

def get_checkin_history(member_id: Optional[int] = None, limit: int = 30) -> List[CheckInRecord]:
    """Retrieve historical check-in records."""
    with get_db() as db:
        query = db.query(CheckInRecord)
        if member_id:
            query = query.filter(CheckInRecord.member_id == member_id)
        return query.order_by(CheckInRecord.checkin_date.desc()).limit(limit).all()
