

from datetime import datetime, date, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship

try:
    from .connection import Base
except (ImportError, ValueError):
    from database.connection import Base


# --------------------------------------------------
# Utility Function
# --------------------------------------------------

def utc_now():
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


# --------------------------------------------------
# Family Model
# --------------------------------------------------

class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    primary_city = Column(String(100), default="Chicago, IL")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    members = relationship(
        "FamilyMember",
        back_populates="family",
        cascade="all, delete-orphan",
        foreign_keys="FamilyMember.family_id",
    )

    tasks = relationship(
        "CareTask",
        back_populates="family",
        cascade="all, delete-orphan",
    )

    notifications = relationship(
        "Notification",
        back_populates="family",
        cascade="all, delete-orphan",
    )


# --------------------------------------------------
# User Model
# --------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), default="Caregiver")
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utc_now)


# --------------------------------------------------
# Family Member Model
# --------------------------------------------------

class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)

    family_id = Column(
        Integer,
        ForeignKey("families.id"),
        nullable=False,
    )

    full_name = Column(String(100), nullable=False)
    relationship_type = Column(String(50), nullable=False)
    city = Column(String(80), nullable=False)
    state = Column(String(40), nullable=False)

    phone = Column(String(30), nullable=True)
    email = Column(String(120), nullable=True)

    is_elderly = Column(Boolean, default=False)
    age = Column(Integer, nullable=True)

    # Care preferences and schedule
    morning_checkin_time = Column(String(10), default="09:00")
    grace_period_minutes = Column(Integer, default=60)

    preferred_hospital = Column(String(120), nullable=True)
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(30), nullable=True)
    care_notes = Column(Text, nullable=True)

    # Self-referencing caregiver relationship
    assigned_caregiver_id = Column(
        Integer,
        ForeignKey("family_members.id"),
        nullable=True,
    )

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
    )

    # Family relationship
    family = relationship(
        "Family",
        back_populates="members",
        foreign_keys=[family_id],
    )

    # Caregiver assigned to this family member
    assigned_caregiver = relationship(
        "FamilyMember",
        remote_side=[id],
        foreign_keys=[assigned_caregiver_id],
        uselist=False,
    )

    # Check-in records
    checkins = relationship(
        "CheckInRecord",
        back_populates="member",
        cascade="all, delete-orphan",
        foreign_keys="CheckInRecord.member_id",
    )

    # Medication reminders
    medications = relationship(
        "MedicationReminder",
        back_populates="member",
        cascade="all, delete-orphan",
        foreign_keys="MedicationReminder.member_id",
    )

    # Appointments belonging to this member
    appointments = relationship(
        "Appointment",
        back_populates="member",
        cascade="all, delete-orphan",
        foreign_keys="Appointment.member_id",
    )


# --------------------------------------------------
# Check-In Record Model
# --------------------------------------------------

class CheckInRecord(Base):
    __tablename__ = "checkin_records"

    id = Column(Integer, primary_key=True, index=True)

    member_id = Column(
        Integer,
        ForeignKey("family_members.id"),
        nullable=False,
    )

    checkin_date = Column(Date, nullable=False, default=date.today)
    scheduled_time = Column(String(10), nullable=False, default="09:00")

    actual_checkin_time = Column(DateTime, nullable=True)

    status = Column(
        String(30),
        default="Awaiting Check-In",
    )

    mood = Column(String(30), nullable=True)
    notes = Column(Text, nullable=True)

    is_simulated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    # Relationships
    member = relationship(
        "FamilyMember",
        back_populates="checkins",
        foreign_keys=[member_id],
    )


# --------------------------------------------------
# Medication Reminder Model
# --------------------------------------------------

class MedicationReminder(Base):
    __tablename__ = "medication_reminders"

    id = Column(Integer, primary_key=True, index=True)

    member_id = Column(
        Integer,
        ForeignKey("family_members.id"),
        nullable=False,
    )

    medication_name = Column(String(100), nullable=False)
    dosage_label = Column(String(80), nullable=True)

    schedule_time = Column(String(10), nullable=False, default="08:00")
    frequency = Column(String(40), default="Daily")

    instructions = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=utc_now)

    # Relationships
    member = relationship(
        "FamilyMember",
        back_populates="medications",
        foreign_keys=[member_id],
    )

    logs = relationship(
        "MedicationLog",
        back_populates="reminder",
        cascade="all, delete-orphan",
    )


# --------------------------------------------------
# Medication Log Model
# --------------------------------------------------

class MedicationLog(Base):
    __tablename__ = "medication_logs"

    id = Column(Integer, primary_key=True, index=True)

    reminder_id = Column(
        Integer,
        ForeignKey("medication_reminders.id"),
        nullable=False,
    )

    member_id = Column(
        Integer,
        ForeignKey("family_members.id"),
        nullable=False,
    )

    scheduled_time = Column(String(10), nullable=False)
    log_date = Column(Date, nullable=False, default=date.today)

    logged_at = Column(DateTime, default=datetime.utcnow)

    status = Column(String(30), default="Taken")
    acknowledgement_note = Column(Text, nullable=True)

    is_simulated = Column(Boolean, default=False)

    # Relationships
    reminder = relationship(
        "MedicationReminder",
        back_populates="logs",
        foreign_keys=[reminder_id],
    )

    member = relationship(
        "FamilyMember",
        foreign_keys=[member_id],
    )


# --------------------------------------------------
# Appointment Model
# --------------------------------------------------

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    member_id = Column(
        Integer,
        ForeignKey("family_members.id"),
        nullable=False,
    )

    title = Column(String(120), nullable=False)
    doctor_name = Column(String(100), nullable=False)

    specialty = Column(String(80), nullable=True)
    clinic_name = Column(String(120), nullable=True)
    location_address = Column(String(200), nullable=True)

    appointment_datetime = Column(DateTime, nullable=False)

    assigned_caregiver_id = Column(
        Integer,
        ForeignKey("family_members.id"),
        nullable=True,
    )

    status = Column(String(30), default="Upcoming")

    transport_notes = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utc_now)

    # Family member who has the appointment
    member = relationship(
        "FamilyMember",
        back_populates="appointments",
        foreign_keys=[member_id],
        uselist=False,
    )

    # Caregiver assigned to the appointment
    assigned_caregiver = relationship(
        "FamilyMember",
        foreign_keys=[assigned_caregiver_id],
        uselist=False,
    )


# --------------------------------------------------
# Care Task Model
# --------------------------------------------------

class CareTask(Base):
    __tablename__ = "care_tasks"

    id = Column(Integer, primary_key=True, index=True)

    family_id = Column(
        Integer,
        ForeignKey("families.id"),
        nullable=False,
    )

    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)

    category = Column(String(50), default="Household")
    due_date = Column(Date, nullable=False)

    priority = Column(String(20), default="Medium")
    status = Column(String(30), default="Pending")

    assigned_member_id = Column(
        Integer,
        ForeignKey("family_members.id"),
        nullable=True,
    )

    created_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    family = relationship(
        "Family",
        back_populates="tasks",
    )

    assigned_member = relationship(
        "FamilyMember",
        foreign_keys=[assigned_member_id],
        uselist=False,
    )


# --------------------------------------------------
# Notification Model
# --------------------------------------------------

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    family_id = Column(
        Integer,
        ForeignKey("families.id"),
        nullable=False,
    )

    member_id = Column(
        Integer,
        ForeignKey("family_members.id"),
        nullable=True,
    )

    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)

    category = Column(String(40), default="System")
    priority = Column(String(20), default="Info")

    is_read = Column(Boolean, default=False)
    is_simulated = Column(Boolean, default=False)

    created_at = Column(DateTime, default=utc_now)

    # Relationships
    family = relationship(
        "Family",
        back_populates="notifications",
        foreign_keys=[family_id],
    )

    member = relationship(
        "FamilyMember",
        foreign_keys=[member_id],
        uselist=False,
    )