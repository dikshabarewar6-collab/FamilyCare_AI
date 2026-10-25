"""
Service layer for Doctor & Specialist Appointments.
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from database.connection import get_db
from database.models import Appointment, FamilyMember, Notification

def create_appointment(data: Dict[str, Any]) -> Appointment:
    """Create a new doctor or specialist appointment."""
    with get_db() as db:
        app_dt = data["appointment_datetime"]
        if isinstance(app_dt, str):
            app_dt = datetime.fromisoformat(app_dt)

        appointment = Appointment(
            member_id=data["member_id"],
            title=data["title"].strip(),
            doctor_name=data["doctor_name"].strip(),
            specialty=data.get("specialty", "").strip(),
            clinic_name=data.get("clinic_name", "").strip(),
            location_address=data.get("location_address", "").strip(),
            appointment_datetime=app_dt,
            assigned_caregiver_id=data.get("assigned_caregiver_id"),
            status="Upcoming",
            transport_notes=data.get("transport_notes", "").strip(),
            notes=data.get("notes", "").strip()
        )
        db.add(appointment)
        db.flush()

        member = db.query(FamilyMember).filter(FamilyMember.id == appointment.member_id).first()
        mem_name = member.full_name if member else "Family Member"

        notif = Notification(
            family_id=member.family_id if member else 1,
            member_id=appointment.member_id,
            title=f"New Appointment: {appointment.title}",
            message=f"{mem_name} has an appointment with {appointment.doctor_name} ({appointment.specialty}) on {appointment.appointment_datetime.strftime('%b %d at %I:%M %p')}.",
            category="Appointment",
            priority="Info"
        )
        db.add(notif)
        db.refresh(appointment)
        return appointment

def get_upcoming_appointments(family_id: int = 1, limit: int = 10) -> List[Appointment]:
    """Retrieve upcoming appointments starting from today."""
    today_start = datetime.combine(date.today(), datetime.min.time())
    with get_db() as db:
        return (
            db.query(Appointment)
            .join(FamilyMember, Appointment.member_id == FamilyMember.id)
            .filter(FamilyMember.family_id == family_id)
            .filter(Appointment.appointment_datetime >= today_start)
            .order_by(Appointment.appointment_datetime.asc())
            .limit(limit)
            .all()
        )

def get_all_appointments(family_id: int = 1) -> List[Appointment]:
    """Retrieve all appointments ordered by datetime."""
    with get_db() as db:
        return (
            db.query(Appointment)
            .join(FamilyMember, Appointment.member_id == FamilyMember.id)
            .filter(FamilyMember.family_id == family_id)
            .order_by(Appointment.appointment_datetime.desc())
            .all()
        )

def update_appointment_status(appointment_id: int, status: str) -> Optional[Appointment]:
    """Update appointment status (e.g. Completed, Rescheduled, Cancelled)."""
    with get_db() as db:
        app = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not app:
            return None
        app.status = status
        db.flush()
        db.refresh(app)
        return app
