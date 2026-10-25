"""
Doctor & Specialist Appointments Page.
Schedule medical visits, assign caregiver escorts, and coordinate transport logistics.
"""
from datetime import datetime, date, time
import streamlit as st
from components.ui_helpers import (
    apply_custom_css, render_page_header, render_status_badge, render_disclaimer
)
from services.member_service import get_family_members
from services.appointment_service import (
    create_appointment, get_upcoming_appointments, get_all_appointments, update_appointment_status
)

def render_appointments_page():
    apply_custom_css()
    render_page_header(
        title="Doctor & Clinic Appointments",
        subtitle="Coordinate healthcare visits, specialists, transport, and assigned family companions.",
        icon="🗓️"
    )

    members = get_family_members(family_id=1)
    if not members:
        st.info("Please register family members first.")
        return

    tab_list, tab_add = st.tabs(["📋 Scheduled Appointments", "➕ Book New Appointment"])

    with tab_add:
        st.markdown("### Schedule a Doctor Visit")
        with st.form("add_appointment_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Appointment Title *", placeholder="e.g. Cardiology Follow-Up")
                doctor_name = st.text_input("Physician / Specialist *", placeholder="e.g. Dr. Robert Ramirez")
                specialty = st.text_input("Specialty", placeholder="e.g. Cardiology")
                clinic_name = st.text_input("Clinic / Hospital", placeholder="e.g. Northwestern Medical Center")
                location_address = st.text_input("Address / Location", placeholder="e.g. 251 E Huron St, Chicago, IL")

            with c2:
                # Member who has the appointment
                m_dict = {m.id: f"{m.full_name} ({m.city})" for m in members}
                member_id = st.selectbox("Family Member Attending", options=list(m_dict.keys()), format_func=lambda x: m_dict[x])

                app_date = st.date_input("Appointment Date", value=date.today())
                app_time = st.time_input("Appointment Time", value=time(10, 30))

                # Assigned caregiver escort/driver
                cg_dict = {None: "None / Independent"}
                for m in members:
                    cg_dict[m.id] = f"{m.full_name} ({m.relationship_type})"
                assigned_cg_id = st.selectbox("Assigned Caregiver Escort / Transport", options=list(cg_dict.keys()), format_func=lambda x: cg_dict[x])

                transport_notes = st.text_input("Transport / Escort Notes", placeholder="e.g. Sarah driving from airport or Uber voucher")

            notes = st.text_area("Appointment Goals & Questions for Doctor", height=70)

            if st.form_submit_button("Schedule Appointment", type="primary"):
                if not title or not doctor_name:
                    st.error("Title and Doctor Name are required.")
                else:
                    app_dt = datetime.combine(app_date, app_time)
                    create_appointment({
                        "member_id": member_id,
                        "title": title,
                        "doctor_name": doctor_name,
                        "specialty": specialty,
                        "clinic_name": clinic_name,
                        "location_address": location_address,
                        "appointment_datetime": app_dt,
                        "assigned_caregiver_id": assigned_cg_id,
                        "transport_notes": transport_notes,
                        "notes": notes
                    })
                    st.success(f"✓ Appointment '{title}' scheduled!")
                    st.rerun()

    with tab_list:
        appointments = get_all_appointments(family_id=1)
        if not appointments:
            st.info("No appointments currently scheduled. Add one using the 'Book New Appointment' tab.")
        else:
            for app in appointments:
                is_upcoming = app.appointment_datetime >= datetime.now()
                with st.container():
                    col_info, col_cg, col_status = st.columns([2, 1.4, 0.9])
                    with col_info:
                        dt_str = app.appointment_datetime.strftime("%A, %b %d, %Y at %I:%M %p")
                        st.markdown(
                            f"""
                            <div style="margin-bottom:2px;">
                                <strong style="font-size:1.15rem; color:#0F172A;">{app.title}</strong>
                                <span style="font-size:0.85rem; color:#7052E6; margin-left:8px; font-weight:600;">{app.specialty or ''}</span>
                            </div>
                            <div style="font-size:0.88rem; color:#334155;">
                                👨‍⚕️ <strong>{app.doctor_name}</strong> • 🏥 {app.clinic_name or 'Clinic'}
                            </div>
                            <div style="font-size:0.84rem; color:#64748B;">
                                📅 <strong>{dt_str}</strong>
                            </div>
                            {f'<div style="font-size:0.82rem; color:#64748B;">📍 {app.location_address}</div>' if app.location_address else ''}
                            {f'<div style="font-size:0.82rem; color:#0284C7; margin-top:2px;">🚗 Transport: {app.transport_notes}</div>' if app.transport_notes else ''}
                            """,
                            unsafe_allow_html=True
                        )

                    with col_cg:
                        attendee_name = app.member.full_name if app.member else "Family Member"
                        cg_name = app.assigned_caregiver.full_name if app.assigned_caregiver else "Unassigned"
                        st.markdown(
                            f"""
                            <div style="background:#F8FAFC; border-radius:10px; padding:0.6rem 0.85rem; font-size:0.84rem; border:1px solid #E2E8F0;">
                                <div><strong>Patient:</strong> {attendee_name}</div>
                                <div><strong>Assigned Companion:</strong> {cg_name}</div>
                                {f'<div style="color:#64748B; font-style:italic; margin-top:3px;">"{app.notes}"</div>' if app.notes else ''}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    with col_status:
                        st.markdown(render_status_badge(app.status), unsafe_allow_html=True)
                        if app.status == "Upcoming":
                            if st.button("Mark Completed", key=f"comp_app_{app.id}", use_container_width=True):
                                update_appointment_status(app.id, "Completed")
                                st.success("Marked as Completed!")
                                st.rerun()

                    st.markdown("<hr style='margin:0.75rem 0; opacity:0.3;'>", unsafe_allow_html=True)

    render_disclaimer(
        "FamilyCare AI organizes personal calendars and family transport. Always confirm appointment times directly with "
        "the physician's clinic or healthcare facility."
    )

if __name__ == "__main__":
    render_appointments_page()
