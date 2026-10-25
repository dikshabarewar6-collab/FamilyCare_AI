"""
FamilyCare AI - Smart Elderly Care & Family Coordination Platform
Main Streamlit Application Entrypoint & Modern Multi-Page Navigation.
"""
import sys
from pathlib import Path

# Ensure project root directory is ALWAYS at the beginning of sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from database.connection import init_db
from database.seed_data import seed_hackathon_demo_data
from services.member_service import get_family_members

# Initialize Page Configuration
st.set_page_config(
    page_title="FamilyCare AI • Smart Elderly Care",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database schema on startup
init_db()

# Auto-seed initial demo data if database is empty on first boot
if "initialized_db" not in st.session_state:
    st.session_state["initialized_db"] = True
    members = get_family_members(1)
    if not members:
        seed_hackathon_demo_data()

# Navigation setup using modern Streamlit 1.36+ st.navigation
pages = {
    "Overview": [
        st.Page("pages/1_Home.py", title="Home", icon="🏠", default=True),
        st.Page("pages/2_Family_Dashboard.py", title="Family Dashboard", icon="📊"),
    ],
    "Daily Care Routine": [
        st.Page("pages/3_Family_Members.py", title="Family Members", icon="👨‍👩‍👧‍👦"),
        st.Page("pages/4_Daily_CheckIns.py", title="Daily Check-Ins", icon="☀️"),
        st.Page("pages/5_Medication_Reminders.py", title="Medications", icon="💊"),
    ],
    "Care Coordination": [
        st.Page("pages/6_Appointments.py", title="Appointments", icon="🗓️"),
        st.Page("pages/7_Care_Tasks.py", title="Care Tasks", icon="✅"),
    ],
    "Intelligence & Analytics": [
        st.Page("pages/8_AI_Care_Companion.py", title="AI Care Companion", icon="✨"),
        st.Page("pages/9_Data_Analytics.py", title="Data Analytics & 3D", icon="📈"),
    ],
    "About": [
        st.Page("pages/10_About_and_Privacy.py", title="About & Privacy", icon="🛡️"),
    ]
}

# Sidebar Custom Branding & Demo Status
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid rgba(155, 134, 238, 0.2); margin-bottom: 1rem;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size: 1.8rem;">🌸</span>
                <div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #0F172A; line-height: 1.1;">FamilyCare AI</div>
                    <div style="font-size: 0.75rem; color: #7052E6; font-weight: 600;">Cross-City Elderly Care</div>
                </div>
            </div>
            <div style="margin-top: 0.6rem; display:flex; align-items:center; gap:6px;">
                <span class="fc-badge checked-in" style="font-size:0.7rem; padding:2px 8px;">Demo Active</span>
                <span style="font-size:0.75rem; color:#64748B;">Vance Family • CHI/NYC/SEA</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

nav = st.navigation(pages)
nav.run()
