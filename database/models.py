"""
SQLAlchemy ORM Data Models for FamilyCare AI.
"""
from datetime import datetime, date, time
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Time, Text, ForeignKey, Float
)
from sqlalchemy.orm import relationship
from database.connection import Base

class Family(Base):
    __tablename__ = "families"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    primary_city = Column(String(100), default="Chicago, IL")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    members = relationship("FamilyMember", back_populates="family", cascade="all, delete-orphan", foreign_keys="FamilyMember.family_id")
    tasks = relationship("CareTask", back_populates="family", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="family", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), default="Caregiver")
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    full_name = Column(String(100), nullable=False)
    relationship_type = Column(String(50), nullable=False)  # Elderly Parent, Primary Caregiver, Daughter, Son, Nurse, etc.
    city = Column(String(80), nullable=False)
    state = Column(String(40), nullable=False)
    phone = Column(String(30), nullable=True)
    email = Column(String(120), nullable=True)
    is_elderly = Column(Boolean, default=False)
    age = Column(Integer, nullable=True)
    
    # Care Preferences & Schedule
    morning_checkin_time = Column(String(10), default="09:00")  # HH:MM format
    grace_period_minutes = Column(Integer, default=60)
    preferred_hospital = Column(String(120), nullable=True)
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(30), nullable=True)
    care_notes = Column(Text, nullable=True)

    # Assigned caregiver among family members
    assigned_caregiver_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    family = relationship("Family", back_populates="members", foreign_keys=[family_id])
    assigned_caregiver = relationship("FamilyMember", remote_side=[id], foreign_keys=[assigned_caregiver_id])
    checkins = relationship("CheckInRecord", back_populates="member", cascade="all, delete-orphan", foreign_keys="[CheckInRecord.member_id]")
    medications = relationship("MedicationReminder", back_populates="member", cascade="all, delete-orphan", foreign_keys="[MedicationReminder.member_id]")
    appointments = relationship("Appointment", back_populates="member", cascade="all, delete-orphan", foreign_keys="[Appointment.member_id]")

class CheckInRecord(Base):
    __tablename__ = "checkin_records"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("family_members.id"), nullable=False)
    checkin_date = Column(Date, nullable=False, default=date.today)
    scheduled_time = Column(String(10), nullable=False, default="09:00")
    actual_checkin_time = Column(DateTime, nullable=True)
    status = Column(String(30), default="Awaiting Check-In")  # Checked In, Awaiting Check-In, Missed Check-In
    mood = Column(String(30), nullable=True)  # Good, Energetic, Tired, Low Energy
    notes = Column(Text, nullable=True)
    is_simulated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    member = relationship("FamilyMember", back_populates="checkins")

class MedicationReminder(Base):
    __tablename__ = "medication_reminders"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("family_members.id"), nullable=False)
    medication_name = Column(String(100), nullable=False)
    dosage_label = Column(String(80), nullable=True)  # e.g. "1 Tablet", "10mg", "With breakfast"
    schedule_time = Column(String(10), nullable=False, default="08:00")  # HH:MM
    frequency = Column(String(40), default="Daily")  # Daily, Twice Daily, Weekly
    instructions = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    member = relationship("FamilyMember", back_populates="medications")
    logs = relationship("MedicationLog", back_populates="reminder", cascade="all, delete-orphan")

class MedicationLog(Base):
    __tablename__ = "medication_logs"

    id = Column(Integer, primary_key=True, index=True)
    reminder_id = Column(Integer, ForeignKey("medication_reminders.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("family_members.id"), nullable=False)
    scheduled_time = Column(String(10), nullable=False)
    log_date = Column(Date, nullable=False, default=date.today)
    logged_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(30), default="Taken")  # Taken, Skipped, Pending
    acknowledgement_note = Column(Text, nullable=True)
    is_simulated = Column(Boolean, default=False)

    # Relationships
    reminder = relationship("MedicationReminder", back_populates="logs")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("family_members.id"), nullable=False)
    title = Column(String(120), nullable=False)
    doctor_name = Column(String(100), nullable=False)
    specialty = Column(String(80), nullable=True)
    clinic_name = Column(String(120), nullable=True)
    location_address = Column(String(200), nullable=True)
    appointment_datetime = Column(DateTime, nullable=False)
    assigned_caregiver_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)
    status = Column(String(30), default="Upcoming")  # Upcoming, Completed, Rescheduled, Cancelled
    transport_notes = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    member = relationship("FamilyMember", back_populates="appointments", foreign_keys=[member_id])
    assigned_caregiver = relationship("FamilyMember", foreign_keys=[assigned_caregiver_id])

class CareTask(Base):
    __tablename__ = "care_tasks"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), default="Household")  # Groceries, Household, Prescription, Administrative, Wellness
    due_date = Column(Date, nullable=False)
    priority = Column(String(20), default="Medium")  # High, Medium, Low
    status = Column(String(30), default="Pending")  # Pending, In Progress, Completed
    assigned_member_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    family = relationship("Family", back_populates="tasks")
    assigned_member = relationship("FamilyMember", foreign_keys=[assigned_member_id])

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    member_id = Column(Integer, ForeignKey("family_members.id"), nullable=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(40), default="System")  # Check-In, Medication, Appointment, Task, System
    priority = Column(String(20), default="Info")  # Info, Warning, Urgent
    is_read = Column(Boolean, default=False)
    is_simulated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    family = relationship("Family", back_populates="notifications")
    member = relationship("FamilyMember", foreign_keys=[member_id])
