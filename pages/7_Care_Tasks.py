"""
Family Care Tasks & Household Coordination Page.
Distribute care duties, track prescription refills, grocery orders,
and household safety.
"""

import sys
from pathlib import Path
from datetime import date

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from components.ui_helpers import (
    apply_custom_css,
    render_page_header,
    render_status_badge,
    render_disclaimer,
)

from services.member_service import get_family_members

from services.task_service import (
    create_care_task,
    get_care_tasks,
    update_task_status,
    TASK_CATEGORIES,
    TASK_PRIORITIES,
)


def render_tasks_page():
    """Render the family care tasks page."""

    apply_custom_css()

    render_page_header(
        title="Family Care Tasks",
        subtitle=(
            "Shared to-do list for siblings and caregivers: "
            "grocery delivery, prescription refills, and home maintenance."
        ),
        icon="✅",
    )

    # Load family members
    members = get_family_members(family_id=1) or []

    if not members:
        st.info("Please register family members first.")
        return

    # Tabs
    tab_board, tab_add = st.tabs(
        ["📋 Task Board", "➕ Create New Care Task"]
    )

    # --------------------------------------------------
    # CREATE NEW TASK
    # --------------------------------------------------
    with tab_add:
        st.markdown("### Create Care Task")

        with st.form("add_task_form", clear_on_submit=True):

            col1, col2 = st.columns(2)

            with col1:
                title = st.text_input(
                    "Task Title *",
                    placeholder="e.g. Order blood pressure monitor refills",
                )

                category = st.selectbox(
                    "Category",
                    TASK_CATEGORIES,
                )

                priority = st.selectbox(
                    "Priority Level",
                    TASK_PRIORITIES,
                    index=1 if len(TASK_PRIORITIES) > 1 else 0,
                )

            with col2:
                due_date = st.date_input(
                    "Due Date",
                    value=date.today(),
                )

                # Task assignee options
                member_options = {
                    None: "Unassigned / Open to All"
                }

                for member in members:
                    member_options[member.id] = (
                        f"{member.full_name} ({member.city})"
                    )

                assigned_id = st.selectbox(
                    "Assign To",
                    options=list(member_options.keys()),
                    format_func=lambda value: member_options[value],
                )

            description = st.text_area(
                "Task Description & Details",
                placeholder=(
                    "e.g. Delivery via pharmacy to the family member's address."
                ),
                height=70,
            )

            submitted = st.form_submit_button(
                "Add Task",
                type="primary",
            )

            if submitted:
                if not title.strip():
                    st.error("Task title is required.")

                else:
                    try:
                        create_care_task(
                            {
                                "family_id": 1,
                                "title": title.strip(),
                                "description": description.strip(),
                                "category": category,
                                "due_date": due_date,
                                "priority": priority,
                                "assigned_member_id": assigned_id,
                            }
                        )

                        st.success(
                            f"Task '{title.strip()}' created successfully!"
                        )
                        st.rerun()

                    except Exception as exc:
                        st.error(f"Unable to create task: {exc}")

    # --------------------------------------------------
    # TASK BOARD
    # --------------------------------------------------
    with tab_board:

        filter_col, info_col = st.columns([1, 1])

        with filter_col:
            status_filter = st.selectbox(
                "Filter Status",
                [
                    "All Tasks",
                    "Pending",
                    "In Progress",
                    "Completed",
                ],
            )

        with info_col:
            st.caption(
                "Coordinate household responsibilities across family members."
            )

        selected_status = (
            None
            if status_filter == "All Tasks"
            else status_filter
        )

        try:
            tasks = get_care_tasks(
                family_id=1,
                status=selected_status,
            ) or []

        except Exception as exc:
            st.error(f"Unable to load care tasks: {exc}")
            return

        if not tasks:
            st.info("No care tasks match the selected filter.")

        else:
            for task in tasks:

                with st.container():

                    info_col, assignee_col, action_col = st.columns(
                        [2, 1.4, 1]
                    )

                    # --------------------------------------
                    # TASK DETAILS
                    # --------------------------------------
                    with info_col:

                        priority_badge = render_status_badge(
                            task.priority or "Medium"
                        )

                        status_badge = render_status_badge(
                            task.status or "Pending"
                        )

                        is_overdue = (
                            task.status != "Completed"
                            and task.due_date is not None
                            and task.due_date < date.today()
                        )

                        overdue_html = (
                            '<span style="background:#FEE2E2; '
                            'color:#991B1B; padding:3px 7px; '
                            'border-radius:6px; font-size:0.75rem;">'
                            'OVERDUE</span>'
                            if is_overdue
                            else ""
                        )

                        due_date_text = (
                            task.due_date.strftime("%b %d, %Y")
                            if task.due_date
                            else "Not set"
                        )

                        description_html = ""

                        if task.description:
                            description_html = (
                                '<div style="font-size:0.84rem; '
                                'color:#475569; margin-top:4px;">'
                                f'{task.description}'
                                '</div>'
                            )

                        st.markdown(
                            f"""
                            <div style="margin-bottom:5px;">
                                <strong style="font-size:1.1rem;">
                                    {task.title}
                                </strong>
                                <span style="margin-left:6px;">
                                    {priority_badge}
                                </span>
                                <span style="margin-left:4px;">
                                    {status_badge}
                                </span>
                                {overdue_html}
                            </div>

                            <div style="font-size:0.86rem; color:#64748B;">
                                🏷️ {task.category or "General"}
                                &nbsp;•&nbsp;
                                📅 Due:
                                <strong>{due_date_text}</strong>
                            </div>

                            {description_html}
                            """,
                            unsafe_allow_html=True,
                        )

                    # --------------------------------------
                    # ASSIGNEE DETAILS
                    # --------------------------------------
                    with assignee_col:

                        # This relationship must be eagerly loaded
                        # by get_care_tasks() in task_service.py.
                        assigned_member = task.assigned_member

                        if assigned_member is not None:
                            assignee_name = assigned_member.full_name
                            assignee_city = (
                                f"({assigned_member.city})"
                                if assigned_member.city
                                else ""
                            )
                        else:
                            assignee_name = "Unassigned"
                            assignee_city = ""

                        completed_text = ""

                        if task.completed_at:
                            completed_text = (
                                '<div style="color:#059669; '
                                'font-size:0.78rem; margin-top:4px;">'
                                'Completed: '
                                f'{task.completed_at.strftime("%b %d, %Y")}'
                                '</div>'
                            )

                        st.markdown(
                            f"""
                            <div style="
                                background:#F8FAFC;
                                border-radius:10px;
                                padding:0.6rem;
                                font-size:0.84rem;
                                border:1px solid #E2E8F0;
                            ">
                                <div>
                                    <strong>Assignee:</strong>
                                    {assignee_name}
                                </div>
                                <div>{assignee_city}</div>
                                {completed_text}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    # --------------------------------------
                    # TASK ACTIONS
                    # --------------------------------------
                    with action_col:

                        if task.status == "Pending":

                            if st.button(
                                "Start Task",
                                key=f"start_task_{task.id}",
                                use_container_width=True,
                            ):
                                try:
                                    update_task_status(
                                        task.id,
                                        "In Progress",
                                    )
                                    st.rerun()

                                except Exception as exc:
                                    st.error(
                                        f"Unable to start task: {exc}"
                                    )

                        elif task.status == "In Progress":

                            if st.button(
                                "✓ Complete",
                                key=f"complete_task_{task.id}",
                                type="primary",
                                use_container_width=True,
                            ):
                                try:
                                    update_task_status(
                                        task.id,
                                        "Completed",
                                    )
                                    st.success("Task completed!")
                                    st.rerun()

                                except Exception as exc:
                                    st.error(
                                        f"Unable to complete task: {exc}"
                                    )

                        else:
                            st.caption("✓ Finished")

                    st.markdown(
                        "<hr style='margin:0.6rem 0; opacity:0.3;'>",
                        unsafe_allow_html=True,
                    )

    render_disclaimer(
        "FamilyCare AI supports household and caregiving coordination. "
        "Task assignments and completion statuses are user-recorded "
        "and should be verified when necessary.",
        title="Care Coordination Disclaimer",
    )


if __name__ == "__main__":
    render_tasks_page()