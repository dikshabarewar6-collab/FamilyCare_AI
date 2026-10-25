"""
About and Privacy Page for FamilyCare AI.
System architecture, privacy notice, medical disclaimers, and hackathon presentation summary.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from components.ui_helpers import (
    apply_custom_css, render_page_header, render_disclaimer, render_ai_badge
)
from ml.activity_pattern import run_experimental_ml_analysis

def render_about_page():
    apply_custom_css()
    render_page_header(
        title="About & Privacy Governance",
        subtitle="Platform architecture, privacy notice, ethical AI principles, and healthcare disclaimers.",
        icon="🛡️"
    )

    tab_about, tab_privacy, tab_ml, tab_arch = st.tabs([
        "🌸 About FamilyCare AI",
        "🔒 Privacy & Data Policy",
        "🧠 Experimental ML Architecture",
        "📐 System Architecture"
    ])

    with tab_about:
        st.markdown(
            f"""
            <div class="fc-hero" style="padding: 1.75rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h2 style="margin:0 0 0.5rem 0; font-size:1.8rem; color:#0F172A;">
                            FamilyCare AI: Care Across Distance
                        </h2>
                        <p style="margin:0; font-size:1rem; color:#475569; max-width:700px; line-height:1.6;">
                            Designed for modern distributed families where adult children live hundreds or thousands of miles
                            away from their aging parents. FamilyCare AI provides peace of mind through structured routines,
                            transparent accountability, and Google Gemini AI care intelligence.
                        </p>
                    </div>
                    {render_ai_badge()}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 🏆 Hackathon Value Proposition")
        v1, v2, v3 = st.columns(3)
        with v1:
            st.markdown(
                """
                <div class="fc-card">
                    <h4>🌍 Real-World Impact</h4>
                    <p style="font-size:0.88rem; color:#64748B; line-height:1.6;">
                        Over 40 million Americans care for aging family members. Over 20% do so from a distance,
                        enduring emotional stress and logistical friction. FamilyCare AI centralizes accountability.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with v2:
            st.markdown(
                """
                <div class="fc-card">
                    <h4>✨ Google Gemini Integration</h4>
                    <p style="font-size:0.88rem; color:#64748B; line-height:1.6;">
                        Rather than raw LLM generation, FamilyCare AI pre-processes SQLite data via Pandas,
                        strips personal identifiers, and queries Gemini for structured weekly caregiver syntheses.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with v3:
            st.markdown(
                """
                <div class="fc-card">
                    <h4>🌐 3D Visual Experience</h4>
                    <p style="font-size:0.88rem; color:#64748B; line-height:1.6;">
                        Embedded Three.js WebGL multi-city care orbit + interactive Plotly 3D scatter landscapes
                        for visualizing circadian rhythm stability without leaving Python.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    with tab_privacy:
        st.markdown("### 🔒 Privacy-by-Design & Legal Disclaimers")
        st.markdown(
            """
            FamilyCare AI is built strictly according to **Data Minimization** and **Privacy-by-Design** principles:
            
            1. **Minimal Contact Information Only**:
               We only collect basic names, cities, phone numbers, and check-in times. No Social Security Numbers,
               banking details, insurance policy IDs, or electronic health record (EHR) files are stored or requested.
            
            2. **Anonymized AI Pre-Processing**:
               Before any summary request reaches the Google Gemini API, a Pandas data pipeline aggregates records
               into numerical percentages and general category counts. Specific home addresses, contact numbers,
               and personal identifying information (PII) are NEVER transmitted to external LLM endpoints.

            3. **Secure Secret Management**:
               All API credentials and keys reside in backend environment variables (`.env`) or secure Streamlit secrets.
               Keys are never logged, exposed in client-side HTML, or checked into Git version control.

            4. **No Commercial Data Resale**:
               Your family records remain entirely in your private SQLite database.
            """
        )

        st.markdown("---")
        render_disclaimer(
            "FamilyCare AI is NOT a certified medical device, emergency medical dispatch system, or diagnostic tool. "
            "It is an administrative family coordination and communication utility. "
            "A missed morning check-in does NOT constitute a clinical diagnosis of distress or medical emergency. "
            "If an elderly parent or family member is experiencing a medical emergency, call 911 or your local emergency services immediately.",
            title="CRITICAL MEDICAL & EMERGENCY DISCLAIMER"
        )

    with tab_ml:
        st.markdown("### 🧠 Experimental Machine Learning Module")
        st.markdown(
            """
            To complement reliable rule-based check-in monitoring, FamilyCare AI includes an optional,
            experimental activity-pattern analysis engine powered by **Scikit-Learn**:
            """
        )

        # Run live ML check to display real status
        ml_res = run_experimental_ml_analysis(family_id=1)

        c_ml1, c_ml2 = st.columns([1.5, 1])
        with c_ml1:
            st.markdown(
                f"""
                <div class="fc-card">
                    <h4>Model Specification: Isolation Forest</h4>
                    <ul style="font-size:0.88rem; color:#475569; line-height:1.7;">
                        <li><strong>Algorithm:</strong> <code>sklearn.ensemble.IsolationForest</code></li>
                        <li><strong>Parameters:</strong> <code>n_estimators=100</code>, <code>contamination=0.08</code></li>
                        <li><strong>Input Features:</strong>
                            <ol>
                                <li><code>checkin_hour</code>: Floating-point hour of morning check-in</li>
                                <li><code>delay_mins</code>: Minutes variance from scheduled 9:00 AM target</li>
                                <li><code>day_of_week</code>: Day index (0=Monday, 6=Sunday)</li>
                            </ol>
                        </li>
                        <li><strong>Imputation:</strong> Median behavioral imputation for missing check-in timestamps</li>
                        <li><strong>Status:</strong> <span class="fc-badge completed">{ml_res['status']} ({ml_res.get('sample_size', 0)} samples)</span></li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c_ml2:
            st.markdown(
                f"""
                <div class="fc-card">
                    <h4>Rule-Based vs ML Separation</h4>
                    <p style="font-size:0.86rem; color:#64748B; line-height:1.55;">
                        <strong>1. Primary Safety (Rule-Based):</strong><br/>
                        Direct comparison of current clock vs <code>scheduled_time + grace_period</code>. 100% deterministic and transparent.
                    </p>
                    <p style="font-size:0.86rem; color:#64748B; line-height:1.55;">
                        <strong>2. Secondary Discovery (ML):</strong><br/>
                        Detects statistical shifts (e.g. checking in 45 minutes earlier or later than usual on specific weekdays).
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("#### 🔍 Active Model Evaluation & Detected Pattern Anomalies")
        anomalies = ml_res.get("anomalous_events", [])
        if anomalies:
            st.dataframe(anomalies, use_container_width=True)
            st.caption("Statistical anomalies flagged by Isolation Forest. Notes indicate real-world context (e.g. church attendance).")
        else:
            st.info("No statistical pattern anomalies detected in current sample.")

        st.warning(
            "⚠️ **Model Limitations**:\n"
            "- The Isolation Forest flags statistical outliers in timing, NOT medical crises or health decline.\n"
            "- Small sample sizes may produce false positives when routines naturally change (vacations, daylight savings).\n"
            "- Never rely on experimental ML outputs for healthcare decisions."
        )

    with tab_arch:
        st.markdown("### 📐 Modular Technical Architecture")
        st.markdown(
            """
            ```
            familycare-ai/
            │
            ├── app.py                      # Multi-page router & navigation layout (st.navigation)
            ├── config.py                   # Central theme tokens, environment loader, defaults
            ├── git_ops.py                  # Portable Git operations & commit history (Dulwich)
            │
            ├── database/
            │   ├── connection.py           # SQLite connection & SQLAlchemy scoped sessions
            │   ├── models.py               # 9 Relational SQLAlchemy entities (Users, Families, Members, etc.)
            │   └── seed_data.py            # Fictional multi-city demo scenario generator (Eleanor Vance)
            │
            ├── services/
            │   ├── member_service.py       # Member CRUD, caregiver roles, care preferences
            │   ├── checkin_service.py      # Grace periods, 'I'm Okay' logger, missed check-in detection
            │   ├── medication_service.py   # Medication schedules, acknowledge logs, adherence tracking
            │   ├── appointment_service.py  # Doctor visits, clinic details, companion escorts
            │   ├── task_service.py         # Shared family tasks, grocery runs, prescription refills
            │   ├── notification_service.py # In-app notification center & simulation alerts
            │   └── gemini_service.py       # Google Gen AI Python SDK, Pandas privacy pre-processing
            │
            ├── analytics/
            │   ├── data_processor.py       # Pandas/NumPy aggregations & completion metrics
            │   └── visualizations.py       # Plotly 2D charts & 3D activity landscapes
            │
            ├── ml/
            │   └── activity_pattern.py     # Rule baseline + Scikit-Learn Isolation Forest
            │
            ├── components/
            │   ├── ui_helpers.py           # Healthcare glassmorphism cards, badges, and banners
            │   └── three_scene.py          # Interactive Three.js WebGL 3D care scene with SVG fallback
            │
            ├── pages/                      # 10 Dedicated Streamlit pages
            ├── assets/custom.css           # Premium glassmorphic styling, animations, colors
            └── tests/test_services.py      # Automated unit test suite
            ```
            """
        )

if __name__ == "__main__":
    render_about_page()
