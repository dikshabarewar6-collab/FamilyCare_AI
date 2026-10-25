"""
Family Members Page for FamilyCare AI.
Manage family members, caregiver assignments, and care preferences.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from sqlalchemy.orm import joinedload

from database.connection import get_db
from database.models import Family, FamilyMember
from components.ui_helpers import (
    apply_custom_css,
    render_page_header,
    render_disclaimer,
)


FAMILY_ID = 1

RELATIONSHIP_TYPES = [
    "Elderly Parent",
    "Primary Caregiver",
    "Daughter",
    "Son",
    "Spouse",
    "Sibling",
    "Nurse",
    "Other",
]


def load_members():
    """Load family members and caregiver relationships before closing the session."""

    with get_db() as db:
        members = (
            db.query(FamilyMember)
            .options(joinedload(FamilyMember.assigned_caregiver))
            .filter(FamilyMember.family_id == FAMILY_ID)
            .order_by(FamilyMember.full_name.asc())
            .all()
        )

        # Convert ORM objects to dictionaries while the session is open.
        result = []

        for member in members:
            caregiver = member.assigned_caregiver

            result.append({
                "id": member.id,
                "full_name": member.full_name,
                "relationship_type": member.relationship_type,
                "city": member.city,
                "state": member.state,
                "phone": member.phone or "",
                "email": member.email or "",
                "is_elderly": bool(member.is_elderly),
                "age": member.age,
                "morning_checkin_time": member.morning_checkin_time or "09:00",
                "grace_period_minutes": member.grace_period_minutes or 60,
                "preferred_hospital": member.preferred_hospital or "",
                "emergency_contact_name": member.emergency_contact_name or "",
                "emergency_contact_phone": member.emergency_contact_phone or "",
                "care_notes": member.care_notes or "",
                "assigned_caregiver_id": member.assigned_caregiver_id,
                "caregiver_name": caregiver.full_name if caregiver else "",
                "caregiver_city": caregiver.city if caregiver else "",
            })

        return result


def add_member(data):
    """Create a family member."""

    with get_db() as db:
        family = db.query(Family).filter(Family.id == FAMILY_ID).first()

        if not family:
            st.error(
                f"Family ID {FAMILY_ID} does not exist. "
                "Create the family record before adding members."
            )
            return False

        member = FamilyMember(
            family_id=FAMILY_ID,
            full_name=data["full_name"],
            relationship_type=data["relationship_type"],
            city=data["city"],
            state=data["state"],
            phone=data["phone"] or None,
            email=data["email"] or None,
            is_elderly=data["is_elderly"],
            age=data["age"],
            morning_checkin_time=data["morning_checkin_time"],
            grace_period_minutes=data["grace_period_minutes"],
            preferred_hospital=data["preferred_hospital"] or None,
            emergency_contact_name=data["emergency_contact_name"] or None,
            emergency_contact_phone=data["emergency_contact_phone"] or None,
            care_notes=data["care_notes"] or None,
            assigned_caregiver_id=data["assigned_caregiver_id"],
        )

        db.add(member)
        db.flush()

    return True


def update_member(member_id, data):
    """Update an existing family member."""

    with get_db() as db:
        member = (
            db.query(FamilyMember)
            .filter(
                FamilyMember.id == member_id,
                FamilyMember.family_id == FAMILY_ID,
            )
            .first()
        )

        if not member:
            return False

        member.full_name = data["full_name"]
        member.relationship_type = data["relationship_type"]
        member.city = data["city"]
        member.state = data["state"]
        member.phone = data["phone"] or None
        member.email = data["email"] or None
        member.is_elderly = data["is_elderly"]
        member.age = data["age"]
        member.morning_checkin_time = data["morning_checkin_time"]
        member.grace_period_minutes = data["grace_period_minutes"]
        member.preferred_hospital = data["preferred_hospital"] or None
        member.emergency_contact_name = data["emergency_contact_name"] or None
        member.emergency_contact_phone = data["emergency_contact_phone"] or None
        member.care_notes = data["care_notes"] or None
        member.assigned_caregiver_id = data["assigned_caregiver_id"]

        db.flush()

    return True


def render_member_form(member=None, available_members=None):
    """Display add/edit form."""

    member = member or {}
    available_members = available_members or []

    member_id = member.get("id")

    caregiver_options = {
        None: "Self / Unassigned"
    }

    for person in available_members:
        if person["id"] != member_id:
            caregiver_options[person["id"]] = person["full_name"]

    current_caregiver_id = member.get("assigned_caregiver_id")

    if current_caregiver_id not in caregiver_options:
        current_caregiver_id = None

    relationship_type = member.get("relationship_type", RELATIONSHIP_TYPES[0])

    if relationship_type not in RELATIONSHIP_TYPES:
        relationship_type = "Other"

    with st.form(f"member_form_{member_id or 'new'}"):
        st.subheader(
            "Edit Family Member" if member_id else "Add Family Member"
        )

        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input(
                "Full Name *",
                value=member.get("full_name", ""),
            )

            relationship_type = st.selectbox(
                "Relationship / Role",
                RELATIONSHIP_TYPES,
                index=RELATIONSHIP_TYPES.index(relationship_type),
            )

            city = st.text_input(
                "City *",
                value=member.get("city", ""),
            )

            state = st.text_input(
                "State *",
                value=member.get("state", ""),
            )

            phone = st.text_input(
                "Phone",
                value=member.get("phone", ""),
            )

            email = st.text_input(
                "Email",
                value=member.get("email", ""),
            )

        with col2:
            is_elderly = st.checkbox(
                "Monitored Elderly Member",
                value=member.get("is_elderly", False),
            )

            age_value = member.get("age")
            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=int(age_value) if age_value is not None else 0,
            )

            caregiver_id = st.selectbox(
                "Assigned Caregiver",
                options=list(caregiver_options.keys()),
                format_func=lambda x: caregiver_options[x],
                index=list(caregiver_options.keys()).index(
                    current_caregiver_id
                ),
            )

            morning_time = st.text_input(
                "Morning Check-In Time (HH:MM)",
                value=member.get("morning_checkin_time", "09:00"),
            )

            grace_period = st.number_input(
                "Grace Period (minutes)",
                min_value=0,
                max_value=240,
                value=int(member.get("grace_period_minutes", 60)),
            )

            hospital = st.text_input(
                "Preferred Hospital",
                value=member.get("preferred_hospital", ""),
            )

        st.markdown("#### Emergency Contact")

        col3, col4 = st.columns(2)

        with col3:
            emergency_name = st.text_input(
                "Emergency Contact Name",
                value=member.get("emergency_contact_name", ""),
            )

        with col4:
            emergency_phone = st.text_input(
                "Emergency Contact Phone",
                value=member.get("emergency_contact_phone", ""),
            )

        care_notes = st.text_area(
            "Care Notes / Preferences",
            value=member.get("care_notes", ""),
        )

        submitted = st.form_submit_button(
            "Save Changes" if member_id else "Add Member",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not full_name.strip():
                st.error("Full name is required.")
                return

            if not city.strip() or not state.strip():
                st.error("City and state are required.")
                return

            if morning_time.strip():
                try:
                    from datetime import datetime
                    datetime.strptime(morning_time.strip(), "%H:%M")
                except ValueError:
                    st.error("Enter the check-in time in HH:MM format.")
                    return
            else:
                st.error("Check-in time is required.")
                return

            data = {
                "full_name": full_name.strip(),
                "relationship_type": relationship_type,
                "city": city.strip(),
                "state": state.strip(),
                "phone": phone.strip(),
                "email": email.strip(),
                "is_elderly": is_elderly,
                "age": int(age) if age > 0 else None,
                "assigned_caregiver_id": caregiver_id,
                "morning_checkin_time": morning_time.strip(),
                "grace_period_minutes": int(grace_period),
                "preferred_hospital": hospital.strip(),
                "emergency_contact_name": emergency_name.strip(),
                "emergency_contact_phone": emergency_phone.strip(),
                "care_notes": care_notes.strip(),
            }

            try:
                if member_id:
                    success = update_member(member_id, data)
                else:
                    success = add_member(data)

                if success:
                    st.success("Family member saved successfully.")
                    st.rerun()

            except Exception as exc:
                st.error(f"Unable to save family member: {exc}")


def render_family_members_page():
    apply_custom_css()

    render_page_header(
        title="Family Members",
        subtitle=(
            "Manage distributed family members, assign primary caregivers, "
            "and set care preferences."
        ),
        icon="👨‍👩‍👧‍👦",
    )

    members = load_members()

    tab_directory, tab_add = st.tabs([
        "📋 Family Directory",
        "➕ Add Member",
    ])

    with tab_directory:
        st.subheader(f"{len(members)} Registered Members Across Cities")

        if not members:
            st.info("No family members registered yet.")
        else:
            for member in members:
                with st.container(border=True):
                    col_info, col_details, col_actions = st.columns(
                        [1.1, 1.5, 0.5]
                    )

                    with col_info:
                        st.markdown(f"### {member['full_name']}")
                        st.caption(
                            f"{'👵 Monitored Parent' if member['is_elderly'] else '👤 ' + member['relationship_type']}"
                        )

                        st.write(
                            f"📍 {member['city']}, {member['state']}"
                        )

                        if member["age"]:
                            st.write(f"Age: {member['age']} years")

                        if member["phone"]:
                            st.write(f"📞 {member['phone']}")

                        if member["email"]:
                            st.write(f"✉️ {member['email']}")

                    with col_details:
                        caregiver = (
                            f"{member['caregiver_name']} "
                            f"({member['caregiver_city']})"
                            if member["caregiver_name"]
                            else "Self / Unassigned"
                        )

                        st.write(f"**Assigned Caregiver:** {caregiver}")

                        st.write(
                            f"**Check-In Window:** "
                            f"{member['morning_checkin_time']} "
                            f"(Grace: {member['grace_period_minutes']}m)"
                        )

                        if member["preferred_hospital"]:
                            st.write(
                                f"**Hospital:** {member['preferred_hospital']}"
                            )

                        if member["care_notes"]:
                            st.caption(member["care_notes"])

                    with col_actions:
                        if st.button(
                            "✏️ Edit",
                            key=f"edit_member_{member['id']}",
                            use_container_width=True,
                        ):
                            st.session_state["editing_member_id"] = member["id"]

                    if st.session_state.get("editing_member_id") == member["id"]:
                        with st.expander("Edit Member Details", expanded=True):
                            render_member_form(member, members)

    with tab_add:
        render_member_form(available_members=members)

    render_disclaimer(
        "FamilyCare AI supports family coordination and care reminders. "
        "It does not replace professional medical advice.",
        title="Care Coordination Disclaimer",
    )


if __name__ == "__main__":
    render_family_members_page()