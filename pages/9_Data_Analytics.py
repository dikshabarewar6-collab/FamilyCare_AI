"""
Data Analytics & 3D Visual Experience Page.
Pandas-powered metrics, Plotly interactive 2D charts, and multi-dimensional 3D activity pattern analysis.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from components.ui_helpers import (
    apply_custom_css, render_page_header, render_metric_card, render_disclaimer
)
from analytics.data_processor import (
    get_checkin_metrics, get_medication_metrics, get_task_metrics, get_3d_activity_landscape_data
)
from analytics.visualizations import (
    create_checkin_trend_chart, create_medication_adherence_chart,
    create_task_donut_chart, create_3d_activity_scatter
)

def render_analytics_page():
    apply_custom_css()
    render_page_header(
        title="Care Activity Analytics & 3D Trends",
        subtitle="Data-driven insights into elderly morning check-in regularity, medication adherence, and task velocity.",
        icon="📈",
        badge="Pandas & Plotly"
    )

    # Fetch processed metrics
    c_metrics = get_checkin_metrics(family_id=1)
    m_metrics = get_medication_metrics(family_id=1)
    t_metrics = get_task_metrics(family_id=1)
    df_3d = get_3d_activity_landscape_data(family_id=1)

    # 1. Top KPI Row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            render_metric_card(
                label="Check-In Rate",
                value=f"{c_metrics['completion_rate']}%",
                icon="☀️",
                color_class="teal" if c_metrics['completion_rate'] >= 85 else "amber",
                sublabel=f"{c_metrics['checked_in_count']} completed / {c_metrics['missed_count']} missed"
            ),
            unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            render_metric_card(
                label="Medication Adherence",
                value=f"{m_metrics['adherence_rate']}%",
                icon="💊",
                color_class="blue" if m_metrics['adherence_rate'] >= 85 else "amber",
                sublabel=f"{m_metrics['taken_count']} taken / {m_metrics['skipped_count']} skipped"
            ),
            unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            render_metric_card(
                label="Task Velocity",
                value=f"{t_metrics['completion_rate']}%",
                icon="✅",
                color_class="purple",
                sublabel=f"{t_metrics['completed']} done / {t_metrics['pending']} pending"
            ),
            unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            render_metric_card(
                label="Overdue Tasks",
                value=str(t_metrics['overdue']),
                icon="⚠️",
                color_class="red" if t_metrics['overdue'] > 0 else "green",
                sublabel="Action required" if t_metrics['overdue'] > 0 else "All on track"
            ),
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # 2. Interactive 3D Visual Activity Landscape Section
    st.markdown(
        """
        <div class="fc-card" style="margin-bottom: 1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h3 style="margin:0 0 0.25rem 0; font-size:1.3rem; color:#0F172A;">
                        🌐 Interactive 3D Morning Routine Landscape
                    </h3>
                    <p style="margin:0; font-size:0.88rem; color:#64748B;">
                        Multi-dimensional activity topography: <strong>Day of Week (X)</strong> vs <strong>Check-In Hour (Y)</strong> vs <strong>Variance / Delay from Target (Z)</strong>.
                        Rotate, zoom, and tilt the 3D surface to inspect circadian stability.
                    </p>
                </div>
                <span class="fc-badge completed">Plotly 3D WebGL</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    fig_3d = create_3d_activity_scatter(df_3d)
    st.plotly_chart(fig_3d, use_container_width=True)

    # 3. Two-Column Analytics: Check-In Trends vs Medication Adherence
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.markdown("### ☀️ Daily Check-In Trends (Last 30 Days)")
        st.caption("Tracking daily 'I'm Okay' check-in confirmations and missed check-in events.")
        fig_trend = create_checkin_trend_chart(c_metrics["daily_df"])
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_c2:
        st.markdown("### 💊 Medication Acknowledgement Rates")
        st.caption("Adherence percentages by medication schedule. Note: Recorded logs != verified clinical ingestion.")
        fig_med = create_medication_adherence_chart(m_metrics["med_breakdown_df"])
        st.plotly_chart(fig_med, use_container_width=True)

    # 4. Care Task Breakdown
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 Care Tasks Coordination Breakdown")
    tc1, tc2 = st.columns([1.2, 1.8])
    with tc1:
        st.caption("Distribution by Task Category")
        fig_donut = create_task_donut_chart(t_metrics["category_df"])
        st.plotly_chart(fig_donut, use_container_width=True)

    with tc2:
        st.caption("Task Status & Assignee Accountability")
        if not t_metrics["raw_df"].empty:
            summary_table = t_metrics["raw_df"][["title", "category", "priority", "status", "assignee", "due_date"]]
            st.dataframe(summary_table, use_container_width=True, height=260)
        else:
            st.info("No task records available.")

    # Medical & Data Disclaimer
    render_disclaimer(
        "Adherence analytics are computed from user-submitted acknowledgements in SQLite. "
        "They illustrate behavioral engagement patterns rather than pharmacokinetic drug levels. "
        "Synthetic demonstration data is utilized when demo mode is active.",
        title="Analytics & Adherence Safeguards"
    )

if __name__ == "__main__":
    render_analytics_page()
