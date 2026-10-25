"""
Medication Reminders & Adherence Tracking Page.
Track daily medication schedules and distinguish recorded acknowledgements
from verified clinical consumption.
"""

import sys
from pathlib import Path

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

from services.member_service import (
    get_elderly_members,
    get_family_members,
)

from services.medication_service import (
    get_today_medication_status,
    record_medication_acknowledgement,
    create_medication_reminder,
    get_medication_logs,
)


def render_medication_page():
    apply_custom_css()

    render_page_header(
        title="Medication Reminders",
        subtitle=(
            "Manage daily medication schedules, record acknowledgements, "
            "and review family adherence."
        ),
        icon="💊",
    )

    members = (
        get_elderly_members(family_id=1)
        or get_family_members(family_id=1)
    )

    if not members:
        st.info("Please register family members first.")
        return

    member_map = {
        member.id: f"{member.full_name} ({member.city})"
        for member in members
    }

    selected_member_id = st.selectbox(
        "Family Member",
        options=list(member_map.keys()),
        format_func=lambda member_id: member_map[member_id],
    )

    selected_member = next(
        member
        for member in members
        if member.id == selected_member_id
    )

    tab_today, tab_add, tab_logs = st.tabs([
        "📋 Today's Medication Routine",
        "➕ Add Reminder Schedule",
        "📜 Historical Logs",
    ])

    # ---------------------------------------------------------
    # TODAY'S MEDICATION ROUTINE
    # ---------------------------------------------------------
    with tab_today:
        st.markdown(
            f"### Today's Schedule for {selected_member.full_name}"
        )

        items = get_today_medication_status(
            member_id=selected_member_id
        )

        if not items:
            st.info(
                f"No active medication reminders configured for "
                f"{selected_member.full_name}. Add one using the "
                "'Add Reminder Schedule' tab."
            )
        else:
            for item in items:
                reminder = item["reminder"]
                current_status = item["status"]
                logged_at = item.get("logged_at")

                with st.container(border=True):
                    main_col, action_col = st.columns([2, 1.2])

                    with main_col:
                        status_html = render_status_badge(current_status)

                        st.markdown(
                            f"""
                            <div style="margin-bottom:0.25rem;">
                                <strong style="font-size:1.15rem;">
                                    {reminder.medication_name}
                                </strong>
                                <span style="margin-left:8px;">
                                    {status_html}
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        st.write(
                            f"⏰ **{reminder.schedule_time}** · "
                            f"{reminder.frequency}"
                        )

                        st.write(
                            "Dosage note: "
                            f"{reminder.dosage_label or 'As directed by physician'}"
                        )

                        if reminder.instructions:
                            st.caption(
                                f"Instructions: {reminder.instructions}"
                            )

                        if logged_at:
                            st.caption(
                                "Recorded at: "
                                f"{logged_at.strftime('%I:%M %p')}"
                            )

                    with action_col:
                        if current_status != "Taken":
                            if st.button(
                                "✓ Taken",
                                key=f"take_{reminder.id}",
                                type="primary",
                                use_container_width=True,
                            ):
                                record_medication_acknowledgement(
                                    reminder.id,
                                    status="Taken",
                                    note="Acknowledged via app.",
                                )

                                st.success(
                                    f"Recorded {reminder.medication_name} as taken."
                                )
                                st.rerun()

                            if st.button(
                                "Skip",
                                key=f"skip_{reminder.id}",
                                use_container_width=True,
                            ):
                                record_medication_acknowledgement(
                                    reminder.id,
                                    status="Skipped",
                                    note="Skipped by user.",
                                )

                                st.warning(
                                    f"Recorded {reminder.medication_name} as skipped."
                                )
                                st.rerun()
                        else:
                            st.success("✓ Acknowledged for Today")

    # ---------------------------------------------------------
    # ADD MEDICATION REMINDER
    # ---------------------------------------------------------
    with tab_add:
        st.markdown("### Add New Medication Reminder")

        st.caption(
            "Coordinate medication times. FamilyCare AI does not prescribe."
        )

        with st.form("add_med_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                medication_name = st.text_input(
                    "Medication Name *",
                    placeholder="e.g. Lisinopril",
                )

                schedule_time = st.text_input(
                    "Scheduled Time (HH:MM) *",
                    value="08:00",
                )

            with col2:
                frequency = st.selectbox(
                    "Frequency",
                    [
                        "Daily",
                        "Twice Daily (Morning/Evening)",
                        "Weekly",
                        "As Needed",
                    ],
                )

                dosage_label = st.text_input(
                    "Physician's Label / Packaging Note",
                    placeholder="e.g. 1 tablet with water",
                )

            instructions = st.text_area(
                "Physician's Instructions",
                height=80,
            )

            submitted = st.form_submit_button(
                "Add Medication Reminder",
                type="primary",
            )

            if submitted:
                if not medication_name.strip():
                    st.error("Medication name is required.")
                else:
                    from datetime import datetime

                    try:
                        datetime.strptime(schedule_time.strip(), "%H:%M")
                    except ValueError:
                        st.error("Enter the scheduled time in HH:MM format.")
                    else:
                        try:
                            create_medication_reminder({
                                "member_id": selected_member_id,
                                "medication_name": medication_name.strip(),
                                "dosage_label": dosage_label.strip(),
                                "schedule_time": schedule_time.strip(),
                                "frequency": frequency,
                                "instructions": instructions.strip(),
                            })

                            st.success(
                                f"Added reminder for {medication_name.strip()}!"
                            )
                            st.rerun()

                        except Exception as exc:
                            st.error(f"Unable to create reminder: {exc}")

    # ---------------------------------------------------------
    # HISTORICAL MEDICATION LOGS
    # ---------------------------------------------------------
    with tab_logs:
        st.markdown("### 📜 Medication Acknowledgement Log")

        st.caption(
            "Historical log of user-recorded acknowledgements."
        )

        logs = get_medication_logs(limit=40)

        if logs:
            rows = []

            for log in logs:
                # These relationships must be eager-loaded by the service.
                reminder = log.reminder
                member = reminder.member if reminder else None

                rows.append({
                    "Date": (
                        log.log_date.strftime("%Y-%m-%d")
                        if log.log_date else "—"
                    ),
                    "Time": (
                        log.logged_at.strftime("%I:%M %p")
                        if log.logged_at else "—"
                    ),
                    "Member": (
                        member.full_name if member else "Family Member"
                    ),
                    "Medication": (
                        reminder.medication_name if reminder else "Medication"
                    ),
                    "Status": log.status or "—",
                    "Note": log.acknowledgement_note or "—",
                })

            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No medication logs recorded yet.")

    render_disclaimer(
        "FamilyCare AI does NOT provide medical advice, prescription "
        "management, or clinical dosage recommendations. A recorded "
        "acknowledgement indicates that a user interacted with the reminder; "
        "it does NOT constitute clinical verification of medication ingestion "
        "or biological efficacy. Consult your doctor or pharmacist for "
        "medical guidance.",
        title="Medication & Clinical Disclaimer",
    )


if __name__ == "__main__":
    render_medication_page()