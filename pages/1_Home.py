"""
FamilyCare AI - Landing Page & 3D Interactive Experience.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
try:
    from components.ui_helpers import apply_custom_css, render_disclaimer, render_ai_badge, render_html
except (ImportError, ModuleNotFoundError):
    from components.ui_helpers import apply_custom_css, render_disclaimer, render_ai_badge
    def render_html(html_str: str):
        lines = [line.strip() for line in html_str.strip().splitlines() if line.strip()]
        st.markdown("\n".join(lines), unsafe_allow_html=True)
from components.three_scene import render_3d_care_scene
import config

def render_home_page():
    apply_custom_css()

    # 1. Hero Section
    render_html(
        f"""
        <div class="fc-hero">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1.5rem;">
                <div style="max-width: 680px;">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.75rem;">
                        <span class="fc-badge completed">🏥 Healthcare Innovation Hackathon</span>
                        {render_ai_badge()}
                    </div>
                    <h1 style="font-size: 2.85rem; font-weight: 800; line-height: 1.15; margin: 0 0 1rem 0; color: #0F172A;">
                        Smart Elderly Care & <br/>
                        <span style="background: linear-gradient(135deg, #7052E6 0%, #0D9488 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                            Family Coordination
                        </span>
                    </h1>
                    <p style="font-size: 1.15rem; color: #475569; line-height: 1.6; margin-bottom: 1.5rem;">
                        Bridging geographic distances to care for elderly parents. Coordinate daily check-ins,
                        track medication reminders, synchronize doctor visits, and synthesize weekly care intelligence
                        powered by <strong>Google Gemini AI</strong>.
                    </p>
                </div>
            </div>
        </div>
        """
    )

    # 2. Interactive 3D Experience Section
    col_3d, col_info = st.columns([1.3, 0.9])

    with col_3d:
        render_html(
            """
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                <span style="font-weight:700; color:#334155; font-size:0.95rem;">
                    🌐 Interactive 3D Multi-City Care Coordination Scene
                </span>
                <span style="font-size:0.8rem; color:#64748B;">
                    Drag to rotate • Real-time WebGL
                </span>
            </div>
            """
        )
        render_3d_care_scene(height=410)

    with col_info:
        render_html(
            """
            <div class="fc-card" style="height: 410px; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <div style="font-size:0.8rem; font-weight:800; color:#7052E6; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.5rem;">
                        Live Multi-City Case Study
                    </div>
                    <h3 style="font-size:1.3rem; font-weight:700; margin:0 0 0.75rem 0; color:#0F172A;">
                        The Vance Family Scenario
                    </h3>
                    <p style="font-size:0.9rem; color:#475569; line-height:1.55; margin-bottom:0.85rem;">
                        <strong>Eleanor Vance (Age 78)</strong> lives independently in <strong>Chicago, IL</strong>.
                        Her daughter <strong>Sarah</strong> lives in <strong>New York</strong> (primary medical coordinator),
                        and son <strong>David</strong> lives in <strong>Seattle</strong> (household logistics coordinator).
                    </p>
                    <div style="display:flex; flex-direction:column; gap:0.5rem; font-size:0.85rem; color:#334155;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="color:#0D9488; font-weight:bold;">● Chicago:</span> Eleanor's 9:00 AM Daily "I'm Okay" Check-in
                        </div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="color:#0284C7; font-weight:bold;">● New York:</span> Sarah monitors Blood Pressure medication
                        </div>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="color:#7052E6; font-weight:bold;">● Seattle:</span> David tracks Dr. Ramirez cardiology appointments
                        </div>
                    </div>
                </div>

                <div style="background:#F8FAFC; border-radius:12px; padding:0.85rem; border:1px solid #E2E8F0; margin-top:0.75rem;">
                    <div style="font-size:0.78rem; color:#64748B; font-weight:600; text-transform:uppercase;">
                        Platform Status
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
                        <span style="font-size:0.88rem; font-weight:700; color:#10B981;">✓ All Nodes Synchronized</span>
                        <span class="fc-badge checked-in">Demo Active</span>
                    </div>
                </div>
            </div>
            """
        )

    # 3. Call-To-Action Quick Navigation
    st.markdown("---")
    cta_c1, cta_c2, cta_c3 = st.columns(3)
    with cta_c1:
        if st.button("📊 Open Family Dashboard", use_container_width=True, type="primary"):
            st.session_state["nav_target"] = "Dashboard"
            st.switch_page("pages/2_Family_Dashboard.py")
    with cta_c2:
        if st.button("✨ Ask AI Care Companion", use_container_width=True):
            st.session_state["nav_target"] = "AI Care Companion"
            st.switch_page("pages/8_AI_Care_Companion.py")
    with cta_c3:
        if st.button("📈 Explore 3D Analytics", use_container_width=True):
            st.session_state["nav_target"] = "Data Analytics"
            st.switch_page("pages/9_Data_Analytics.py")

    # 4. Problem & Solution
    render_html("<div style='height: 1.5rem;'></div>")
    render_html(
        """
        <div style="text-align:center; max-width:760px; margin: 0 auto 2rem auto;">
            <span class="fc-badge awaiting" style="margin-bottom:0.5rem;">The Challenge</span>
            <h2 style="font-size: 2rem; font-weight: 800; color:#0F172A; margin: 0.5rem 0;">
                The Distance Dilemma in Elderly Care
            </h2>
            <p style="color:#64748B; font-size:1rem; line-height:1.6;">
                Millions of adult children live in different cities from their aging parents.
                Schedules get fragmented, check-in calls are missed, medications slip through the cracks,
                and siblings constantly ask: <em>"Who checked on Mom today?"</em>
            </p>
        </div>
        """
    )

    ps_col1, ps_col2 = st.columns(2)
    with ps_col1:
        render_html(
            """
            <div class="fc-card" style="border-left: 4px solid #EF4444;">
                <h4 style="color:#B91C1C; margin:0 0 0.5rem 0;">❌ The Traditional Struggle</h4>
                <ul style="color:#475569; font-size:0.92rem; line-height:1.7; padding-left:1.2rem; margin:0;">
                    <li>Scattered WhatsApp chats and missed calls cause unnecessary anxiety.</li>
                    <li>No central source of truth for doctor visits or transport duties.</li>
                    <li>Uncertainty about daily medication compliance.</li>
                    <li>Caregiver burnout from lack of shared accountability between siblings.</li>
                </ul>
            </div>
            """
        )
    with ps_col2:
        render_html(
            """
            <div class="fc-card" style="border-left: 4px solid #10B981;">
                <h4 style="color:#047857; margin:0 0 0.5rem 0;">✨ The FamilyCare AI Solution</h4>
                <ul style="color:#475569; font-size:0.92rem; line-height:1.7; padding-left:1.2rem; margin:0;">
                    <li>One-tap morning "I'm Okay" check-in with configurable grace periods.</li>
                    <li>Transparent shared medication logs with reminder acknowledgement tracking.</li>
                    <li>Synchronized appointment scheduling with assigned family members.</li>
                    <li>Privacy-first AI intelligence distilling weekly caregiver summaries via Gemini.</li>
                </ul>
            </div>
            """
        )

    # 5. Core Platform Features
    render_html("<div style='height: 1.5rem;'></div>")
    render_html(
        """
        <div style="text-align:center; max-width:760px; margin: 0 auto 2rem auto;">
            <span class="fc-badge completed" style="margin-bottom:0.5rem;">Capabilities</span>
            <h2 style="font-size: 2rem; font-weight: 800; color:#0F172A; margin: 0.5rem 0;">
                Comprehensive Platform Features
            </h2>
        </div>
        """
    )

    f1, f2, f3 = st.columns(3)
    with f1:
        render_html(
            """
            <div class="fc-feature-card">
                <div class="fc-feature-icon">☀️</div>
                <div class="fc-feature-title">Daily "I'm Okay" Check-Ins</div>
                <div class="fc-feature-desc">
                    Configurable morning windows with smart grace periods. Transparent missed-check-in detection
                    triggers simulated caregiver alerts without panicking families.
                </div>
            </div>
            """
        )
    with f2:
        render_html(
            """
            <div class="fc-feature-card">
                <div class="fc-feature-icon">💊</div>
                <div class="fc-feature-title">Medication Reminders</div>
                <div class="fc-feature-desc">
                    Schedule recurrences, log acknowledgements, and distinguish recorded acknowledgements
                    from verified consumption with clear medical safeguards.
                </div>
            </div>
            """
        )
    with f3:
        render_html(
            """
            <div class="fc-feature-card">
                <div class="fc-feature-icon">🗓️</div>
                <div class="fc-feature-title">Appointments & Tasks</div>
                <div class="fc-feature-desc">
                    Coordinate clinic visits, specialists, household tasks, and grocery errands. Assign family members
                    with due dates and priority tracking.
                </div>
            </div>
            """
        )

    render_html("<div style='height: 1rem;'></div>")
    f4, f5, f6 = st.columns(3)
    with f4:
        render_html(
            """
            <div class="fc-feature-card">
                <div class="fc-feature-icon">✨</div>
                <div class="fc-feature-title">Google Gemini Care Companion</div>
                <div class="fc-feature-desc">
                    Generate privacy-conscious weekly care digests, extract action checklists, and receive
                    intelligent family coordination recommendations powered by Google Gen AI.
                </div>
            </div>
            """
        )
    with f5:
        render_html(
            """
            <div class="fc-feature-card">
                <div class="fc-feature-icon">📈</div>
                <div class="fc-feature-title">Plotly 3D Activity Analytics</div>
                <div class="fc-feature-desc">
                    Deep analytics powered by Pandas, NumPy, and Plotly. Interactive multi-dimensional 3D charts
                    surface check-in adherence and medication patterns over time.
                </div>
            </div>
            """
        )
    with f6:
        render_html(
            """
            <div class="fc-feature-card">
                <div class="fc-feature-icon">🧠</div>
                <div class="fc-feature-title">Experimental ML Pattern Analysis</div>
                <div class="fc-feature-desc">
                    Transparent rule-based activity baselines paired with Scikit-learn Isolation Forest anomaly
                    detection on numerical behavior metrics with clear medical disclaimers.
                </div>
            </div>
            """
        )

    # 6. How It Works Pipeline
    render_html("<div style='height: 2rem;'></div>")
    render_html(
        """
        <div style="text-align:center; max-width:760px; margin: 0 auto 1.5rem auto;">
            <span class="fc-badge awaiting">Process Flow</span>
            <h2 style="font-size: 2rem; font-weight: 800; color:#0F172A; margin: 0.5rem 0;">
                How FamilyCare AI Works
            </h2>
        </div>
        """
    )

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        render_html(
            """
            <div class="fc-step-card">
                <div class="fc-step-num">Step 1</div>
                <h4 style="margin:0 0 0.5rem 0;">Connect Family</h4>
                <p style="font-size:0.86rem; color:#64748B; margin:0;">
                    Register family members across cities and designate primary caregivers.
                </p>
            </div>
            """
        )
    with s2:
        render_html(
            """
            <div class="fc-step-card">
                <div class="fc-step-num">Step 2</div>
                <h4 style="margin:0 0 0.5rem 0;">Daily Routine</h4>
                <p style="font-size:0.86rem; color:#64748B; margin:0;">
                    Elderly parent taps "I'm Okay" each morning and logs medication acknowledgements.
                </p>
            </div>
            """
        )
    with s3:
        render_html(
            """
            <div class="fc-step-card">
                <div class="fc-step-num">Step 3</div>
                <h4 style="margin:0 0 0.5rem 0;">Coordinate</h4>
                <p style="font-size:0.86rem; color:#64748B; margin:0;">
                    Siblings claim tasks and appointments without stepping on each other's toes.
                </p>
            </div>
            """
        )
    with s4:
        render_html(
            """
            <div class="fc-step-card">
                <div class="fc-step-num">Step 4</div>
                <h4 style="margin:0 0 0.5rem 0;">AI Intelligence</h4>
                <p style="font-size:0.86rem; color:#64748B; margin:0;">
                    Gemini AI distills weekly progress and flags patterns requiring attention.
                </p>
            </div>
            """
        )

    # 7. Medical Disclaimer Banner
    render_disclaimer(
        "FamilyCare AI is designed solely for family coordination, wellness check-in tracking, "
        "and administrative scheduling. It is NOT a medical device, diagnostic system, or emergency service. "
        "A missed check-in must not automatically be treated as a medical emergency. "
        "Always call your local emergency services (e.g. 911) in urgent health situations."
    )

if __name__ == "__main__":
    render_home_page()
