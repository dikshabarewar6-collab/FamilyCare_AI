"""
Family Care Tasks & Household Coordination Page.
Distribute care duties, track prescription refills, grocery orders, and household safety.
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
    apply_custom_css, render_page_header, render_status_badge, render_disclaimer
)
from services.member_service import get_family_members
from services.task_service import (
    create_care_task, get_care_tasks, update_task_status,
    TASK_CATEGORIES, TASK_PRIORITIES
)

def render_tasks_page():
    apply_custom_css()
    render_page_header(
        title="Family Care Tasks",
        subtitle="Shared to-do list for siblings and caregivers: grocery delivery, prescription refills, and home maintenance.",
        icon="✅"
    )

    members = get_family_members(family_id=1)
    if not members:
        st.info("Please register family members first.")
        return

    tab_board, tab_add = st.tabs(["📋 Task Board", "➕ Create New Care Task"])

    with tab_add:
        st.markdown("### Create Care Task")
        with st.form("add_task_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Task Title *", placeholder="e.g. Order blood pressure monitor refills")
                category = st.selectbox("Category", TASK_CATEGORIES)
                priority = st.selectbox("Priority Level", TASK_PRIORITIES, index=1)

            with col2:
                due_date = st.date_input("Due Date", value=date.today())
                
                # Assignee
                m_options = {None: "Unassigned / Open to All"}
                for m in members:
                    m_options[m.id] = f"{m.full_name} ({m.city})"
                assigned_id = st.selectbox("Assign To", options=list(m_options.keys()), format_func=lambda x: m_options[x])

            description = st.text_area("Task Description & Details", placeholder="e.g. Delivery via Walgreens to Eleanor's address.", height=70)

            if st.form_submit_button("Add Task", type="primary"):
                if not title:
                    st.error("Task title is required.")
                else:
                    create_care_task({
                        "family_id": 1,
                        "title": title,
                        "description": description,
                        "category": category,
                        "due_date": due_date,
                        "priority": priority,
                        "assigned_member_id": assigned_id
                    })
                    st.success(f"✓ Task '{title}' created!")
                    st.rerun()

    with tab_board:
        # Filter controls
        f_col1, f_col2 = st.columns([1, 1])
        with f_col1:
            status_filter = st.selectbox("Filter Status", ["All Tasks", "Pending", "In Progress", "Completed"])
        with f_col2:
            st.caption("Tasks help siblings across cities share the load without confusion.")

        selected_status = None if status_filter == "All Tasks" else status_filter
        tasks = get_care_tasks(family_id=1, status=selected_status)

        if not tasks:
            st.info("No care tasks match the selected filter.")
        else:
            for t in tasks:
                with st.container():
                    c_info, c_assign, c_act = st.columns([2, 1.2, 1])
                    with c_info:
                        pri_badge = render_status_badge(t.priority)
                        stat_badge = render_status_badge(t.status)
                        is_overdue = t.status != "Completed" and t.due_date < date.today()
                        overdue_html = ' <span class="fc-badge missed" style="font-size:0.75rem;">OVERDUE</span>' if is_overdue else ""

                        st.markdown(
                            f"""
                            <div style="margin-bottom:2px;">
                                <strong style="font-size:1.1rem; color:#0F172A;">{t.title}</strong>
                                <span style="margin-left:6px;">{pri_badge}</span>
                                <span style="margin-left:4px;">{stat_badge}</span>
                                {overdue_html}
                            </div>
                            <div style="font-size:0.86rem; color:#64748B;">
                                🏷️ {t.category} • 📅 Due: <strong>{t.due_date.strftime('%b %d, %Y')}</strong>
                            </div>
                            {f'<div style="font-size:0.84rem; color:#475569; margin-top:2px;">{t.description}</div>' if t.description else ''}
                            """,
                            unsafe_allow_html=True
                        )

                    with c_assign:
                        assignee_name = t.assigned_member.full_name if t.assigned_member else "Unassigned"
                        assignee_city = f"({t.assigned_member.city})" if t.assigned_member else ""
                        st.markdown(
                            f"""
                            <div style="background:#F8FAFC; border-radius:10px; padding:0.5rem 0.75rem; font-size:0.84rem; border:1px solid #E2E8F0;">
                                <div><strong>Assignee:</strong> {assignee_name} {assignee_city}</div>
                                {f'<div style="color:#10B981; font-size:0.78rem;">Completed: {t.completed_at.strftime("%b %d")}</div>' if t.completed_at else ''}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    with c_act:
                        if t.status == "Pending":
                            if st.button("Start Task", key=f"start_{t.id}", use_container_width=True):
                                update_task_status(t.id, "In Progress")
                                st.rerun()
                        elif t.status == "In Progress":
                            if st.button("✓ Complete", key=f"comp_{t.id}", type="primary", use_container_width=True):
                                update_task_status(t.id, "Completed")
                                st.success("Task completed!")
                                st.rerun()
                        else:
                            st.caption("✓ Finished")

                    st.markdown("<hr style='margin:0.6rem 0; opacity:0.3;'>", unsafe_allow_html=True)

if __name__ == "__main__":
    render_tasks_page()
