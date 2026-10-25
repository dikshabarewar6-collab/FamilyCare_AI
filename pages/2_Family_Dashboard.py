"""
Family Dashboard Page.
Real-time care metrics read from SQLite, quick action shortcuts,
recent notifications feed, and judge demo controls.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from datetime import date, datetime
import streamlit as st
from components.ui_helpers import (
    apply_custom_css, render_page_header, render_metric_card,
    render_status_badge, render_disclaimer, render_ai_badge
)
from services.member_service import get_family_members, get_elderly_members
from services.checkin_service import get_today_checkin_status, simulate_missed_checkin
from services.medication_service import get_medication_reminders, get_today_medication_status
from services.appointment_service import get_upcoming_appointments
from services.task_service import get_care_tasks, get_pending_tasks_count
from services.notification_service import get_recent_notifications
try:
    from database.seed_data import seed_hackathon_demo_data, reset_database
except (ImportError, ModuleNotFoundError):
    from database import seed_hackathon_demo_data, reset_database

def render_dashboard_page():
    apply_custom_css()
    render_page_header(
        title="Family Coordination Dashboard",
        subtitle="Real-time status across distributed family members and daily elderly care routines.",
        icon="📊",
        badge="Live SQLite"
    )

    # 1. Top Control Bar: Demo Controls for Hackathon Judges
    with st.expander("🛠️ Hackathon Judge Control Center (Demo Mode & Simulation)"):
        col_d1, col_d2, col_d3 = st.columns([1.5, 1.5, 2])
        with col_d1:
            if st.button("🔄 Reload Demo Data (Vance Family)", use_container_width=True, type="primary"):
                seed_hackathon_demo_data()
                st.success("✓ Demo data loaded: Eleanor Vance in Chicago, Sarah in NYC, David in Seattle.")
                st.rerun()
        with col_d2:
            if st.button("🗑️ Reset Database to Empty", use_container_width=True):
                reset_database()
                st.warning("Database reset to empty state.")
                st.rerun()
        with col_d3:
            st.caption(
                "💡 Judge Tip: Reload demo data anytime to inspect 30 days of realistic check-in patterns, "
                "medication logs, appointments, and test the real Google Gemini AI summary."
            )

    # 2. Query Live Metrics from SQLite
    members = get_family_members(family_id=1)
    elderly_list = get_elderly_members(family_id=1)
    monitored_member = elderly_list[0] if elderly_list else (members[0] if members else None)

    # Today's check-in
    checked_in_count = 0
    total_elderly = len(elderly_list)
    today_status_label = "No Members"
    if monitored_member:
        status, _ = get_today_checkin_status(monitored_member.id)
        today_status_label = status
        if status == "Checked In":
            checked_in_count += 1

    # Medications
    med_reminders = get_medication_reminders(monitored_member.id if monitored_member else None)
    today_meds = get_today_medication_status(monitored_member.id) if monitored_member else []
    pending_meds = sum(1 for m in today_meds if m["status"] == "Pending")

    # Upcoming Appointments
    upcoming_apps = get_upcoming_appointments(family_id=1, limit=5)

    # Pending Tasks
    pending_tasks = get_pending_tasks_count(family_id=1)

    # 3. KPI Metric Cards (2x2 or 1x5 layout)
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(
            render_metric_card(
                label="Family Members",
                value=str(len(members)),
                icon="👨‍👩‍👧‍👦",
                color_class="purple",
                sublabel=f"{total_elderly} monitored"
            ),
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            render_metric_card(
                label="Today's Check-In",
                value=f"{checked_in_count}/{total_elderly or 1}",
                icon="☀️",
                color_class="teal" if checked_in_count > 0 else "amber",
                sublabel=today_status_label
            ),
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            render_metric_card(
                label="Medication Reminders",
                value=str(len(med_reminders)),
                icon="💊",
                color_class="blue",
                sublabel=f"{pending_meds} pending today"
            ),
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            render_metric_card(
                label="Upcoming Visits",
                value=str(len(upcoming_apps)),
                icon="🗓️",
                color_class="green",
                sublabel="Doctor appointments"
            ),
            unsafe_allow_html=True
        )
    with m5:
        st.markdown(
            render_metric_card(
                label="Pending Tasks",
                value=str(pending_tasks),
                icon="✅",
                color_class="amber",
                sublabel="Care coordination"
            ),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # 4. Main Dashboard Two-Column Layout
    col_left, col_right = st.columns([1.6, 1.2])

    with col_left:
        # Monitored Parent Live Card
        if monitored_member:
            st.markdown(
                f"""
                <div class="fc-card" style="border-left: 5px solid #7052E6;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-size:0.8rem; font-weight:700; color:#7052E6; text-transform:uppercase; letter-spacing:0.05em;">
                                Primary Monitored Parent
                            </span>
                            <h3 style="margin:0.25rem 0 0.5rem 0; font-size:1.4rem; color:#0F172A;">
                                {monitored_member.full_name} ({monitored_member.age} yrs)
                            </h3>
                            <div style="font-size:0.88rem; color:#64748B;">
                                📍 <strong>{monitored_member.city}, {monitored_member.state}</strong> • Check-In Target: <strong>{monitored_member.morning_checkin_time}</strong> (Grace: {monitored_member.grace_period_minutes}m)
                            </div>
                        </div>
                        <div>
                            {render_status_badge(today_status_label)}
                        </div>
                    </div>
                    <div style="margin-top:1rem; padding-top:0.75rem; border-top:1px solid #F1F5F9; display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:0.85rem; color:#475569;">
                            🏥 Hospital: <strong>{monitored_member.preferred_hospital or 'Not specified'}</strong>
                        </span>
                        <span style="font-size:0.85rem; color:#475569;">
                            🛡️ Primary Caregiver: <strong>{monitored_member.assigned_caregiver.full_name if monitored_member.assigned_caregiver else 'Unassigned'}</strong>
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Quick Actions Row
        st.markdown("### ⚡ Quick Caregiver Actions")
        q1, q2, q3, q4 = st.columns(4)
        with q1:
            if st.button("☀️ Record Check-In", use_container_width=True):
                st.switch_page("pages/4_Daily_CheckIns.py")
        with q2:
            if st.button("💊 Medication Log", use_container_width=True):
                st.switch_page("pages/5_Medication_Reminders.py")
        with q3:
            if st.button("🗓️ Appointments", use_container_width=True):
                st.switch_page("pages/6_Appointments.py")
        with q4:
            if st.button("✨ Gemini Summary", use_container_width=True, type="primary"):
                st.switch_page("pages/8_AI_Care_Companion.py")

        # Upcoming Appointments & Next Care Tasks
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("### 🗓️ Next Upcoming Doctor Appointments")
        if upcoming_apps:
            for app in upcoming_apps[:3]:
                dt_str = app.appointment_datetime.strftime("%a, %b %d • %I:%M %p")
                cg_name = app.assigned_caregiver.full_name if app.assigned_caregiver else "Unassigned"
                st.markdown(
                    f"""
                    <div style="background:white; border-radius:12px; padding:0.85rem 1rem; border:1px solid #E2E8F0; margin-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong style="color:#0F172A; font-size:0.95rem;">{app.title}</strong>
                            <div style="font-size:0.82rem; color:#64748B;">
                                👨‍⚕️ {app.doctor_name} ({app.specialty}) • 📍 {app.clinic_name}
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <span class="fc-badge completed" style="font-size:0.75rem;">{dt_str}</span>
                            <div style="font-size:0.75rem; color:#64748B; margin-top:2px;">Escort: {cg_name}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No upcoming appointments scheduled.")

    with col_right:
        # Cross-City Family Nodes Presence
        st.markdown("### 🌐 Distributed Care Network")
        if members:
            for m in members:
                role_color = "#7052E6" if m.is_elderly else "#0D9488"
                st.markdown(
                    f"""
                    <div style="background:white; border-radius:12px; padding:0.75rem 1rem; border:1px solid #E2E8F0; margin-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <div style="width:10px; height:10px; border-radius:50%; background:{role_color};"></div>
                            <div>
                                <strong style="font-size:0.92rem; color:#0F172A;">{m.full_name}</strong>
                                <div style="font-size:0.78rem; color:#64748B;">{m.relationship_type}</div>
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:0.82rem; font-weight:700; color:#334155;">{m.city}, {m.state}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Recent In-App Notifications Feed
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown("### 🔔 Recent Care Activity Feed")
        notifications = get_recent_notifications(family_id=1, limit=5)
        if notifications:
            for notif in notifications:
                sim_tag = ' <span style="font-size:0.68rem; background:#FEF3C7; color:#B45309; padding:1px 6px; border-radius:6px;">SIM</span>' if notif.is_simulated else ""
                st.markdown(
                    f"""
                    <div style="background:white; border-radius:12px; padding:0.75rem 1rem; border-left:3px solid #0D9488; border-top:1px solid #E2E8F0; border-right:1px solid #E2E8F0; border-bottom:1px solid #E2E8F0; margin-bottom:0.5rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong style="font-size:0.86rem; color:#0F172A;">{notif.title}</strong>
                            <span style="font-size:0.75rem; color:#94A3B8;">{notif.created_at.strftime('%I:%M %p')}{sim_tag}</span>
                        </div>
                        <div style="font-size:0.8rem; color:#64748B; margin-top:2px; line-height:1.4;">
                            {notif.message}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No notifications in log.")

    # Medical Disclaimer
    render_disclaimer(
        "FamilyCare AI is designed for family coordination, check-in reminders, and scheduling. "
        "It does not provide emergency medical detection, diagnoses, or prescriptions."
    )

if __name__ == "__main__":
    render_dashboard_page()
