"""
Medication Reminders & Adherence Tracking Page.
Track daily medication schedules and distinguish recorded acknowledgements from verified clinical consumption.
"""
from datetime import date
import streamlit as st
from components.ui_helpers import (
    apply_custom_css, render_page_header, render_status_badge, render_disclaimer
)
from services.member_service import get_elderly_members, get_family_members
from services.medication_service import (
    get_today_medication_status, record_medication_acknowledgement,
    create_medication_reminder, get_medication_logs
)

def render_medication_page():
    apply_custom_css()
    render_page_header(
        title="Medication Reminders",
        subtitle="Manage daily medication schedules, record acknowledgements, and review family adherence.",
        icon="💊"
    )

    members = get_elderly_members(family_id=1) or get_family_members(family_id=1)
    if not members:
        st.info("Please register family members first.")
        return

    m_dict = {m.id: f"{m.full_name} ({m.city})" for m in members}
    sel_id = st.selectbox("Family Member", options=list(m_dict.keys()), format_func=lambda x: m_dict[x])
    member = next(m for m in members if m.id == sel_id)

    tab_today, tab_add, tab_logs = st.tabs(["📋 Today's Medication Routine", "➕ Add Reminder Schedule", "📜 Historical Logs"])

    with tab_today:
        st.markdown(f"### Today's Schedule for {member.full_name}")
        items = get_today_medication_status(member_id=sel_id)

        if not items:
            st.info(f"No active medication reminders configured for {member.full_name}. Add one using the 'Add Reminder Schedule' tab.")
        else:
            for item in items:
                rem = item["reminder"]
                cur_status = item["status"]
                logged_at = item["logged_at"]

                with st.container():
                    c_main, c_act = st.columns([2, 1.2])
                    with c_main:
                        status_html = render_status_badge(cur_status)
                        st.markdown(
                            f"""
                            <div style="margin-bottom:0.25rem;">
                                <strong style="font-size:1.15rem; color:#0F172A;">{rem.medication_name}</strong>
                                <span style="margin-left:8px;">{status_html}</span>
                            </div>
                            <div style="font-size:0.88rem; color:#475569;">
                                ⏰ <strong>{rem.schedule_time}</strong> • {rem.frequency} • Dosage Note: <em>{rem.dosage_label or 'As directed by physician'}</em>
                            </div>
                            {f'<div style="font-size:0.82rem; color:#64748B; margin-top:3px;">Instructions: {rem.instructions}</div>' if rem.instructions else ''}
                            {f'<div style="font-size:0.8rem; color:#10B981; margin-top:4px;">Recorded at: {logged_at.strftime("%I:%M %p")}</div>' if logged_at else ''}
                            """,
                            unsafe_allow_html=True
                        )

                    with c_act:
                        if cur_status != "Taken":
                            b1, b2 = st.columns(2)
                            with b1:
                                if st.button("✓ Taken", key=f"take_{rem.id}", type="primary", use_container_width=True):
                                    record_medication_acknowledgement(rem.id, status="Taken", note="Acknowledged via app.")
                                    st.success(f"Recorded {rem.medication_name} as taken.")
                                    st.rerun()
                            with b2:
                                if st.button("Skip", key=f"skip_{rem.id}", use_container_width=True):
                                    record_medication_acknowledgement(rem.id, status="Skipped", note="Skipped by user.")
                                    st.warning(f"Recorded {rem.medication_name} as skipped.")
                                    st.rerun()
                        else:
                            st.success("✓ Acknowledged for Today")

                    st.markdown("<hr style='margin:0.75rem 0; opacity:0.3;'>", unsafe_allow_html=True)

    with tab_add:
        st.markdown("### Add New Medication Reminder")
        st.caption("Coordinate medication times. FamilyCare AI does not prescribe or verify dosages.")
        with st.form("add_med_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                med_name = st.text_input("Medication Name *", placeholder="e.g. Lisinopril")
                sched_time = st.text_input("Scheduled Time (HH:MM) *", value="08:00")
            with col2:
                frequency = st.selectbox("Frequency", ["Daily", "Twice Daily (Morning/Evening)", "Weekly", "As Needed"])
                dosage_label = st.text_input("Physician's Label / Packaging Note", placeholder="e.g. 1 tablet with water")
            
            instructions = st.text_area("Physician's Instructions (take with meal, avoid grapefruit, etc.)", height=60)

            if st.form_submit_button("Add Medication Reminder", type="primary"):
                if not med_name:
                    st.error("Medication name is required.")
                else:
                    create_medication_reminder({
                        "member_id": sel_id,
                        "medication_name": med_name,
                        "dosage_label": dosage_label,
                        "schedule_time": sched_time,
                        "frequency": frequency,
                        "instructions": instructions
                    })
                    st.success(f"✓ Added reminder for {med_name}!")
                    st.rerun()

    with tab_logs:
        st.markdown("### 📜 Medication Acknowledgement Log")
        st.caption("Historical log of user-recorded acknowledgements.")
        logs = get_medication_logs(limit=40)
        if logs:
            df_rows = []
            for l in logs:
                med_name = l.reminder.medication_name if l.reminder else "Medication"
                mem_name = l.reminder.member.full_name if l.reminder and l.reminder.member else "Family Member"
                df_rows.append({
                    "Date": l.log_date.strftime("%Y-%m-%d"),
                    "Time": l.logged_at.strftime("%I:%M %p") if l.logged_at else "—",
                    "Member": mem_name,
                    "Medication": med_name,
                    "Status": l.status,
                    "Note": l.acknowledgement_note or "—"
                })
            st.dataframe(df_rows, use_container_width=True)
        else:
            st.info("No medication logs recorded yet.")

    render_disclaimer(
        "FamilyCare AI does NOT provide medical advice, prescription management, or clinical dosage recommendations. "
        "A recorded acknowledgement indicates that a user interacted with the reminder; it does NOT constitute clinical "
        "verification of medication ingestion or biological efficacy. Consult your doctor or pharmacist for medical guidance.",
        title="Medication & Clinical Disclaimer"
    )

if __name__ == "__main__":
    render_medication_page()
