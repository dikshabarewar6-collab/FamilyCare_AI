"""
Daily Check-Ins Page.
Configurable schedules, 'I'm Okay' check-in button, grace period logic,
and simulated missed check-in detection.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from datetime import datetime, date
import streamlit as st
from components.ui_helpers import (
    apply_custom_css, render_page_header, render_status_badge, render_disclaimer
)
from services.member_service import get_elderly_members, get_family_members
from services.checkin_service import (
    get_today_checkin_status, record_checkin, simulate_missed_checkin, get_checkin_history
)

def render_checkins_page():
    apply_custom_css()
    render_page_header(
        title="Daily Check-Ins",
        subtitle="Morning wellness routines, 'I'm Okay' check-in button, and overdue alerts.",
        icon="☀️"
    )

    elderly_members = get_elderly_members(family_id=1)
    if not elderly_members:
        # Fallback to all members if none marked elderly
        elderly_members = get_family_members(family_id=1)

    if not elderly_members:
        st.info("No family members found. Please add a member in 'Family Members' or load demo data from the Dashboard.")
        return

    # Select member to check-in for
    member_names = {m.id: f"{m.full_name} ({m.city}, {m.state})" for m in elderly_members}
    selected_member_id = st.selectbox(
        "Select Family Member to View/Record Check-In",
        options=list(member_names.keys()),
        format_func=lambda x: member_names[x]
    )

    selected_member = next(m for m in elderly_members if m.id == selected_member_id)

    # Today's Status Banner
    status, record = get_today_checkin_status(selected_member_id)
    today_str = date.today().strftime("%A, %B %d, %Y")

    col_status, col_action = st.columns([1.1, 1.4])

    with col_status:
        st.markdown(
            f"""
            <div class="fc-card" style="text-align:center; padding: 2rem 1.5rem;">
                <div style="font-size:0.85rem; color:#64748B; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">
                    Today's Status • {today_str}
                </div>
                <div style="margin: 1rem 0;">
                    {render_status_badge(status)}
                </div>
                <div style="font-size:0.92rem; color:#334155;">
                    Scheduled: <strong>{selected_member.morning_checkin_time or '09:00'}</strong> 
                    <br/><span style="color:#64748B; font-size:0.84rem;">Grace Period: {selected_member.grace_period_minutes} minutes</span>
                </div>
                {f"<div style='margin-top:0.75rem; font-size:0.85rem; color:#10B981;'>Checked in at: {record.actual_checkin_time.strftime('%I:%M %p') if record and record.actual_checkin_time else ''}</div>" if status == 'Checked In' else ''}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_action:
        st.markdown(
            """
            <div class="fc-card">
                <h3 style="margin:0 0 0.5rem 0; font-size:1.2rem; color:#0F172A;">
                    🌸 Morning Check-In Routine
                </h3>
                <p style="font-size:0.88rem; color:#64748B; margin-bottom:1rem;">
                    Let your family know you are awake, well, and starting your day.
                </p>
            """,
            unsafe_allow_html=True
        )

        with st.form("checkin_form"):
            mood = st.selectbox(
                "How are you feeling today?",
                ["Good & Peaceful 😊", "Energetic & Ready 🏃", "A Bit Tired 😴", "Resting Today 🍵", "Would Love a Call 📞"]
            )
            note = st.text_input("Optional Note to Family", placeholder="e.g. Slept well! Going for a walk in Lincoln Park.")
            
            btn_col1, btn_col2 = st.columns([1.5, 1])
            with btn_col1:
                submit_checkin = st.form_submit_button("💚 I'm Okay! (Tap to Check In)", type="primary", use_container_width=True)

        if submit_checkin:
            record_checkin(selected_member_id, mood=mood, notes=note)
            st.success(f"✓ Check-in recorded for {selected_member.full_name}! Family members notified.")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # Hackathon Demo / Simulation Tools Box
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    with st.expander("🧪 Hackathon Judge Simulation: Test Overdue / Missed Check-In Alert"):
        st.markdown(
            """
            **How Missed Check-In Detection Works:**
            FamilyCare AI calculates: `deadline = scheduled_time + grace_period_minutes`.
            If current time surpasses this deadline without an "I'm Okay" event, the system transitions to 
            **Missed Check-In** and simulates a priority alert to the primary caregiver.
            """
        )
        sim_col1, sim_col2 = st.columns([1.5, 2])
        with sim_col1:
            if st.button("⚠️ Trigger Simulated Overdue Check-In", type="secondary", use_container_width=True):
                simulate_missed_checkin(selected_member_id)
                st.warning(f"Simulated alert triggered for {selected_member.full_name}! View Notification Center.")
                st.rerun()
        with sim_col2:
            st.caption(
                "💡 Safe Simulation: This demonstrates automated escalation workflows without generating real medical alarms."
            )

    # Check-In History
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 📜 30-Day Check-In History")
    history = get_checkin_history(member_id=selected_member_id, limit=30)
    if history:
        table_rows = []
        for h in history:
            time_str = h.actual_checkin_time.strftime("%I:%M %p") if h.actual_checkin_time else "—"
            sim_badge = " [SIM]" if h.is_simulated else ""
            table_rows.append({
                "Date": h.checkin_date.strftime("%Y-%m-%d"),
                "Scheduled": h.scheduled_time,
                "Actual Check-In": time_str,
                "Status": f"{h.status}{sim_badge}",
                "Mood": h.mood or "—",
                "Notes": h.notes or "—"
            })
        st.dataframe(table_rows, use_container_width=True)
    else:
        st.info("No check-in history yet for this member.")

    # Medical Disclaimer
    render_disclaimer(
        "A missed check-in must not automatically be treated as a medical emergency. "
        "Network disconnects, phone battery drain, or delayed morning routines may cause a delay. "
        "Caregivers should attempt regular telephone contact before taking further steps."
    )

if __name__ == "__main__":
    render_checkins_page()
