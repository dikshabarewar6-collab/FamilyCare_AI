"""
Database package for FamilyCare AI.
Provides models, connection lifecycle, and demo data seeding.
"""
import sys
from pathlib import Path

# Ensure project root is always on sys.path
_PKG_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _PKG_DIR.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

# Ensure this directory is recognized as a package
__path__ = [str(_PKG_DIR)]

# Expose submodules and core symbols directly on the database package
from . import connection
from . import models
from . import seed_data

from .connection import get_db, init_db, ENGINE, Base, SessionLocal
from .models import (
    Family, User, FamilyMember, CheckInRecord, MedicationReminder,
    MedicationLog, Appointment, CareTask, Notification
)
from .seed_data import seed_hackathon_demo_data, reset_database

__all__ = [
    "connection", "models", "seed_data",
    "get_db", "init_db", "ENGINE", "Base", "SessionLocal",
    "Family", "User", "FamilyMember", "CheckInRecord", "MedicationReminder",
    "MedicationLog", "Appointment", "CareTask", "Notification",
    "seed_hackathon_demo_data", "reset_database"
]
