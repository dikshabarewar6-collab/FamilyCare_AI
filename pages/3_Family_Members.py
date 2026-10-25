"""
Family Members Management Page.
Add, edit, view, and assign caregivers across distributed cities.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from components.ui_helpers import (
    apply_custom_css, render_page_header, render_status_badge, render_disclaimer
)
from services.member_service import (
    get_family_members, create_family_member, update_family_member,
    delete_family_member, RELATIONSHIP_TYPES
)

def render_family_members_page():
    apply_custom_css()
    render_page_header(
        title="Family Members & Caregivers",
        subtitle="Manage distributed family members, assign primary caregivers, and set care preferences.",
        icon="👨‍👩‍👧‍👦"
    )

    members = get_family_members(family_id=1)

    # Top Action Tabs: Directory vs Add New Member
    tab_dir, tab_add = st.tabs(["📋 Family Directory", "➕ Add New Family Member"])

    with tab_add:
        st.markdown("### Register a Family Member")
        st.caption("Coordinate elderly parents and family caregivers across different cities.")

        with st.form("add_member_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                full_name = st.text_input("Full Name *", placeholder="e.g. Eleanor Vance")
                relationship = st.selectbox("Relationship / Role *", RELATIONSHIP_TYPES)
                city = st.text_input("City *", placeholder="e.g. Chicago")
                state = st.text_input("State / Province *", placeholder="e.g. IL")
                phone = st.text_input("Phone Number", placeholder="e.g. +1 (312) 555-0143")
                email = st.text_input("Email Address", placeholder="e.g. eleanor.vance@example.com")

            with c2:
                is_elderly = st.checkbox("Requires Daily Care Monitoring / Elderly Parent", value=False)
                age = st.number_input("Age (optional)", min_value=0, max_value=120, value=75 if is_elderly else 40)
                
                st.markdown("**Care & Check-In Preferences**")
                checkin_time = st.text_input("Daily Check-In Target Time (HH:MM)", value="09:00")
                grace_mins = st.slider("Grace Period (Minutes)", min_value=15, max_value=180, value=60, step=15)
                preferred_hospital = st.text_input("Preferred Hospital / Medical Center", placeholder="e.g. Northwestern Memorial")
                em_name = st.text_input("Emergency Contact Name", placeholder="e.g. Sarah Vance")
                em_phone = st.text_input("Emergency Contact Phone", placeholder="e.g. +1 (212) 555-0199")

            care_notes = st.text_area("Care Preferences & Household Notes (dietary, mobility, transport)", height=70)

            # Caregiver assignment dropdown
            caregiver_options = {None: "None / Self"}
            for m in members:
                caregiver_options[m.id] = f"{m.full_name} ({m.relationship_type} - {m.city})"
            assigned_cg = st.selectbox("Assign Primary Caregiver", options=list(caregiver_options.keys()), format_func=lambda x: caregiver_options[x])

            submitted = st.form_submit_button("Register Member", type="primary")
            if submitted:
                payload = {
                    "full_name": full_name,
                    "relationship_type": relationship,
                    "city": city,
                    "state": state,
                    "phone": phone,
                    "email": email,
                    "is_elderly": is_elderly,
                    "age": age if age > 0 else None,
                    "morning_checkin_time": checkin_time,
                    "grace_period_minutes": grace_mins,
                    "preferred_hospital": preferred_hospital,
                    "emergency_contact_name": em_name,
                    "emergency_contact_phone": em_phone,
                    "care_notes": care_notes,
                    "assigned_caregiver_id": assigned_cg
                }
                try:
                    create_family_member(payload)
                    st.success(f"✓ Successfully registered {full_name}!")
                    st.rerun()
                except ValueError as err:
                    st.error(f"Validation Error: {err}")

    with tab_dir:
        if not members:
            st.info("No family members registered yet. Use the 'Add New Family Member' tab or load Demo Data from the Family Dashboard.")
            return

        st.markdown(f"**{len(members)} Registered Members Across Cities**")

        # Caregiver & Member Cards
        for m in members:
            with st.container():
                c_info, c_details, c_actions = st.columns([1.5, 2, 0.8])
                with c_info:
                    elderly_tag = '<span class="fc-badge completed" style="font-size:0.75rem;">👴 Monitored Parent</span>' if m.is_elderly else '<span class="fc-badge pending" style="font-size:0.75rem;">🛡️ Caregiver</span>'
                    st.markdown(
                        f"""
                        <div style="margin-bottom:0.25rem;">
                            <span style="font-size:1.15rem; font-weight:700; color:#0F172A;">{m.full_name}</span>
                            <span style="margin-left:6px;">{elderly_tag}</span>
                        </div>
                        <div style="font-size:0.85rem; color:#64748B;">
                            📍 <strong>{m.city}, {m.state}</strong> • {m.relationship_type} {f'({m.age} yrs)' if m.age else ''}
                        </div>
                        <div style="font-size:0.82rem; color:#64748B; margin-top:2px;">
                            📞 {m.phone or 'No phone'} • ✉️ {m.email or 'No email'}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c_details:
                    # Caregiver assignment info
                    cg_name = "Self / Unassigned"
                    if m.assigned_caregiver:
                        cg_name = f"{m.assigned_caregiver.full_name} ({m.assigned_caregiver.city})"
                    
                    st.markdown(
                        f"""
                        <div style="background:#F8FAFC; border-radius:10px; padding:0.6rem 0.85rem; font-size:0.84rem; border:1px solid #E2E8F0;">
                            <div><strong>Assigned Caregiver:</strong> {cg_name}</div>
                            <div><strong>Check-In Window:</strong> {m.morning_checkin_time} (Grace: {m.grace_period_minutes}m)</div>
                            {f'<div><strong>Hospital:</strong> {m.preferred_hospital}</div>' if m.preferred_hospital else ''}
                            {f'<div style="color:#64748B; font-style:italic; margin-top:2px;">"{m.care_notes}"</div>' if m.care_notes else ''}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with c_actions:
                    with st.expander("⚙️ Edit"):
                        with st.form(f"edit_member_{m.id}"):
                            new_name = st.text_input("Name", value=m.full_name)
                            new_rel = st.selectbox("Role", RELATIONSHIP_TYPES, index=RELATIONSHIP_TYPES.index(m.relationship_type) if m.relationship_type in RELATIONSHIP_TYPES else 0)
                            new_city = st.text_input("City", value=m.city)
                            new_state = st.text_input("State", value=m.state)
                            new_phone = st.text_input("Phone", value=m.phone or "")
                            new_email = st.text_input("Email", value=m.email or "")
                            new_checkin = st.text_input("Check-In Time", value=m.morning_checkin_time or "09:00")
                            new_grace = st.number_input("Grace Mins", value=m.grace_period_minutes or 60, min_value=15, max_value=360)
                            new_notes = st.text_area("Notes", value=m.care_notes or "")

                            # Assign caregiver
                            other_members = {None: "None"}
                            for om in members:
                                if om.id != m.id:
                                    other_members[om.id] = f"{om.full_name} ({om.city})"
                            cur_cg_idx = list(other_members.keys()).index(m.assigned_caregiver_id) if m.assigned_caregiver_id in other_members else 0
                            new_cg = st.selectbox("Caregiver", options=list(other_members.keys()), index=cur_cg_idx, format_func=lambda x: other_members[x])

                            if st.form_submit_button("Save Changes"):
                                update_payload = {
                                    "full_name": new_name,
                                    "relationship_type": new_rel,
                                    "city": new_city,
                                    "state": new_state,
                                    "phone": new_phone,
                                    "email": new_email,
                                    "is_elderly": m.is_elderly,
                                    "age": m.age,
                                    "morning_checkin_time": new_checkin,
                                    "grace_period_minutes": new_grace,
                                    "preferred_hospital": m.preferred_hospital,
                                    "emergency_contact_name": m.emergency_contact_name,
                                    "emergency_contact_phone": m.emergency_contact_phone,
                                    "care_notes": new_notes,
                                    "assigned_caregiver_id": new_cg
                                }
                                try:
                                    update_family_member(m.id, update_payload)
                                    st.success("Updated!")
                                    st.rerun()
                                except ValueError as err:
                                    st.error(f"Error: {err}")

                        if st.button("🗑️ Delete", key=f"del_{m.id}", type="secondary"):
                            delete_family_member(m.id)
                            st.warning(f"Deleted {m.full_name}.")
                            st.rerun()

                st.markdown("<hr style='margin:0.5rem 0; opacity:0.3;'>", unsafe_allow_html=True)

    render_disclaimer(
        "FamilyCare AI adheres to strict data minimization principles. Only essential contact and "
        "scheduling details are stored. No sensitive health insurance, payment, or diagnostic data is collected."
    )

if __name__ == "__main__":
    render_family_members_page()
