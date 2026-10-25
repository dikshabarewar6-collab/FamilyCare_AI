
"""
Service layer for Family Member management,
validation, and caregiver assignment.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy.orm import joinedload

from database.connection import get_db
from database.models import FamilyMember, Family, Notification


RELATIONSHIP_TYPES = [
    "Elderly Parent",
    "Primary Caregiver",
    "Daughter",
    "Son",
    "Grandchild",
    "Sibling",
    "Professional Nurse",
    "Family Friend",
    "Other Relative",
]


def validate_member_data(data: Dict[str, Any]) -> List[str]:
    """Validate member form inputs and return a list of errors."""

    errors = []

    full_name = data.get("full_name", "").strip()

    if not full_name:
        errors.append("Full name is required.")
    elif len(full_name) < 2:
        errors.append("Full name must be at least 2 characters.")

    city = data.get("city", "").strip()
    state = data.get("state", "").strip()

    if not city or not state:
        errors.append(
            "City and State are required for multi-city coordination."
        )

    relationship_type = data.get("relationship_type", "").strip()

    if not relationship_type:
        errors.append("Relationship type is required.")

    # Validate check-in time.
    checkin_time = data.get("morning_checkin_time", "09:00")

    if checkin_time:
        parts = checkin_time.split(":")

        if (
            len(parts) != 2
            or not (parts[0].isdigit() and parts[1].isdigit())
        ):
            errors.append(
                "Check-in time must be formatted as HH:MM."
            )
        else:
            h, m = int(parts[0]), int(parts[1])

            if not (0 <= h <= 23 and 0 <= m <= 59):
                errors.append(
                    "Check-in time must be between 00:00 and 23:59."
                )

    # Validate grace period.
    grace = data.get("grace_period_minutes", 60)

    try:
        grace_val = int(grace)

        if grace_val < 5 or grace_val > 360:
            errors.append(
                "Grace period must be between 5 and 360 minutes."
            )

    except (ValueError, TypeError):
        errors.append(
            "Grace period must be a valid integer."
        )

    return errors


def create_family_member(data: Dict[str, Any]) -> FamilyMember:
    """Create and persist a new family member."""

    errors = validate_member_data(data)

    if errors:
        raise ValueError("; ".join(errors))

    with get_db() as db:

        family_id = data.get("family_id", 1)

        family = (
            db.query(Family)
            .filter(Family.id == family_id)
            .first()
        )

        if not family:
            family = Family(
                id=1,
                name="Vance Family Coordination",
                primary_city="Chicago, IL",
            )

            db.add(family)
            db.flush()

        member = FamilyMember(
            family_id=family.id,
            full_name=data["full_name"].strip(),
            relationship_type=data["relationship_type"],
            city=data["city"].strip(),
            state=data["state"].strip(),
            phone=data.get("phone", "").strip(),
            email=data.get("email", "").strip(),
            is_elderly=bool(data.get("is_elderly", False)),
            age=int(data["age"]) if data.get("age") else None,
            morning_checkin_time=data.get(
                "morning_checkin_time", "09:00"
            ),
            grace_period_minutes=int(
                data.get("grace_period_minutes", 60)
            ),
            preferred_hospital=data.get(
                "preferred_hospital", ""
            ).strip(),
            emergency_contact_name=data.get(
                "emergency_contact_name", ""
            ).strip(),
            emergency_contact_phone=data.get(
                "emergency_contact_phone", ""
            ).strip(),
            care_notes=data.get("care_notes", "").strip(),
            assigned_caregiver_id=data.get(
                "assigned_caregiver_id"
            ),
        )

        db.add(member)
        db.flush()

        notif = Notification(
            family_id=family.id,
            member_id=member.id,
            title="New Family Member Added",
            message=(
                f"{member.full_name} ({member.relationship_type}) "
                f"was registered in {member.city}, {member.state}."
            ),
            category="System",
            priority="Info",
        )

        db.add(notif)

        db.flush()

        # Load caregiver relationship while the session is active.
        member = (
            db.query(FamilyMember)
            .options(
                joinedload(FamilyMember.assigned_caregiver)
            )
            .filter(FamilyMember.id == member.id)
            .one()
        )

        # Return a detached object with its loaded attributes preserved.
        db.expunge(member)

        return member


def update_family_member(
    member_id: int,
    data: Dict[str, Any],
) -> Optional[FamilyMember]:
    """Update details of an existing family member."""

    errors = validate_member_data(data)

    if errors:
        raise ValueError("; ".join(errors))

    with get_db() as db:

        member = (
            db.query(FamilyMember)
            .options(
                joinedload(FamilyMember.assigned_caregiver)
            )
            .filter(FamilyMember.id == member_id)
            .first()
        )

        if not member:
            return None

        member.full_name = data["full_name"].strip()
        member.relationship_type = data["relationship_type"]
        member.city = data["city"].strip()
        member.state = data["state"].strip()
        member.phone = data.get("phone", "").strip()
        member.email = data.get("email", "").strip()
        member.is_elderly = bool(data.get("is_elderly", False))
        member.age = int(data["age"]) if data.get("age") else None

        member.morning_checkin_time = data.get(
            "morning_checkin_time", "09:00"
        )

        member.grace_period_minutes = int(
            data.get("grace_period_minutes", 60)
        )

        member.preferred_hospital = data.get(
            "preferred_hospital", ""
        ).strip()

        member.emergency_contact_name = data.get(
            "emergency_contact_name", ""
        ).strip()

        member.emergency_contact_phone = data.get(
            "emergency_contact_phone", ""
        ).strip()

        member.care_notes = data.get("care_notes", "").strip()

        member.assigned_caregiver_id = data.get(
            "assigned_caregiver_id"
        )

        member.updated_at = datetime.utcnow()

        db.flush()

        # Reload updated record and its caregiver relationship.
        updated_member = (
            db.query(FamilyMember)
            .options(
                joinedload(FamilyMember.assigned_caregiver)
            )
            .filter(FamilyMember.id == member_id)
            .one()
        )

        db.expunge(updated_member)

        return updated_member


def get_family_members(
    family_id: int = 1,
) -> List[FamilyMember]:
    """Retrieve family members with caregivers eagerly loaded."""

    with get_db() as db:

        members = (
            db.query(FamilyMember)
            .options(
                joinedload(FamilyMember.assigned_caregiver)
            )
            .filter(FamilyMember.family_id == family_id)
            .all()
        )

        # Detach only after the relationship has been loaded.
        for member in members:
            db.expunge(member)

        return members


def get_elderly_members(
    family_id: int = 1,
) -> List[FamilyMember]:
    """Retrieve elderly members with caregivers eagerly loaded."""

    with get_db() as db:

        members = (
            db.query(FamilyMember)
            .options(
                joinedload(FamilyMember.assigned_caregiver)
            )
            .filter(
                FamilyMember.family_id == family_id,
                FamilyMember.is_elderly.is_(True),
            )
            .all()
        )

        for member in members:
            db.expunge(member)

        return members


def get_member_by_id(
    member_id: int,
) -> Optional[FamilyMember]:
    """Retrieve a member and load their caregiver relationship."""

    with get_db() as db:

        member = (
            db.query(FamilyMember)
            .options(
                joinedload(FamilyMember.assigned_caregiver)
            )
            .filter(FamilyMember.id == member_id)
            .first()
        )

        if member is not None:
            db.expunge(member)

        return member


def delete_family_member(member_id: int) -> bool:
    """Delete a family member."""

    with get_db() as db:

        member = (
            db.query(FamilyMember)
            .filter(FamilyMember.id == member_id)
            .first()
        )

        if not member:
            return False

        db.delete(member)

        return True
