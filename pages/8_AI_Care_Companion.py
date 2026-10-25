"""
AI Care Companion Page powered by Google Gemini API.
Privacy-conscious weekly care synthesis, caregiver checklists, and smart cross-city coordination.
"""
import streamlit as st
from components.ui_helpers import (
    apply_custom_css, render_page_header, render_ai_badge, render_disclaimer
)
from services.gemini_service import (
    generate_weekly_care_summary, ask_care_companion, get_gemini_api_key
)

def render_ai_companion_page():
    apply_custom_css()
    render_page_header(
        title="AI Care Companion",
        subtitle="Empathetic, privacy-conscious care intelligence powered by Google Gemini AI.",
        icon="✨",
        badge="Google Gen AI SDK"
    )

    # API Key Configuration Expander
    current_key = get_gemini_api_key(st.session_state.get("user_gemini_key"))
    has_key = bool(current_key)

    with st.expander("🔑 Google Gemini API Key Settings" + (" (Active ✓)" if has_key else " (Key Needed)")):
        st.markdown(
            """
            FamilyCare AI connects to the **Google Gemini API** using the official `google-genai` Python SDK.
            You can load the key via `.env` file (`GEMINI_API_KEY=...`) or enter it below for this session:
            """
        )
        c_k1, c_k2 = st.columns([2.5, 1])
        with c_k1:
            entered_key = st.text_input(
                "Gemini API Key",
                value=st.session_state.get("user_gemini_key", ""),
                type="password",
                placeholder="AIzaSy..."
            )
        with c_k2:
            st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
            if st.button("Save Key", type="primary"):
                st.session_state["user_gemini_key"] = entered_key
                st.success("API key stored for this session!")
                st.rerun()

        st.caption(
            "🔒 Security: Your API key is stored only in session memory or backend environment variables. "
            "It is never exposed to public repositories or non-authorized users."
        )

    # 1. Weekly Care Summary Section
    st.markdown("### 📋 Weekly Care Synthesis")
    st.markdown(
        """
        Aggregate the past 7 days of SQLite check-in regularity, medication adherence logs,
        upcoming doctor visits, and pending household tasks into a comprehensive family report.
        """
    )

    col_btn, col_info = st.columns([1.2, 2])
    with col_btn:
        generate_clicked = st.button("✨ Generate Weekly Care Summary", type="primary", use_container_width=True)

    with col_info:
        st.caption(
            "Privacy Pre-processing: Uses Pandas to strip street addresses and personal identifiers. "
            "Only aggregated percentages and scheduling metrics are passed to Gemini."
        )

    if generate_clicked:
        with st.spinner("Analyzing SQLite records with Pandas & synthesizing summary with Gemini..."):
            result = generate_weekly_care_summary(family_id=1, api_key_override=st.session_state.get("user_gemini_key"))

            if result["success"]:
                st.session_state["cached_weekly_summary"] = result
                st.success("✓ Care summary synthesized successfully!")
            else:
                if result.get("error_type") == "MISSING_KEY":
                    st.warning(
                        "⚠️ **Gemini API Key Required**\n\n"
                        "To generate real-time AI summaries, please provide a Google Gemini API key in the expander above "
                        "or define `GEMINI_API_KEY` in your `.env` file.\n\n"
                        "💡 *All other application features (Check-Ins, Medication Tracking, Appointments, Tasks, "
                        "3D Visualizations, and Analytics) remain 100% operational without an API key!*"
                    )
                else:
                    st.error(f"API Error: {result.get('message')}")

    # Display cached summary if available
    if "cached_weekly_summary" in st.session_state:
        res = st.session_state["cached_weekly_summary"]
        st.markdown(
            f"""
            <div class="fc-ai-bubble">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; border-bottom:1px solid rgba(155, 134, 238, 0.25); padding-bottom:0.5rem;">
                    <div>
                        <strong>Weekly Family Care Synthesis</strong>
                        <div style="font-size:0.75rem; color:#64748B;">Generated: {res.get('timestamp')} • Model: {res.get('model')}</div>
                    </div>
                    {render_ai_badge()}
                </div>
                <div style="font-size:0.95rem; color:#1E293B; line-height:1.65; white-space: pre-wrap;">
{res.get('content')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    # 2. Interactive Care Companion Chat & Quick Prompts
    st.markdown("### 💬 Ask the Care Companion")
    st.caption("Ask questions about family scheduling, caregiver responsibilities, and routine planning.")

    # Quick prompt chips
    st.markdown("**Quick Prompts:**")
    qp1, qp2, qp3 = st.columns(3)
    preset_query = None
    with qp1:
        if st.button("📝 Doctor Visit Prep Checklist", use_container_width=True):
            preset_query = "Generate a comprehensive preparation checklist for Eleanor's upcoming cardiology consultation with Dr. Ramirez."
    with qp2:
        if st.button("🤝 Cross-City Duty Division", use_container_width=True):
            preset_query = "How can Sarah (in NYC) and David (in Seattle) best divide responsibilities for Eleanor in Chicago to prevent caregiver burnout?"
    with qp3:
        if st.button("💡 Check-In Routine Tips", use_container_width=True):
            preset_query = "What are 3 practical tips to help an elderly parent remember their morning check-in without feeling micromanaged?"

    with st.form("ask_companion_form"):
        user_query = st.text_input(
            "Your Question or Prompt",
            value=preset_query or "",
            placeholder="e.g. How can we optimize medicine reminders between morning and evening?"
        )
        ask_submitted = st.form_submit_button("Send to Gemini Care Companion", type="primary")

    if ask_submitted and user_query:
        with st.spinner("Care Companion is thinking..."):
            ans = ask_care_companion(user_query, family_id=1, api_key_override=st.session_state.get("user_gemini_key"))
            if ans["success"]:
                st.markdown(
                    f"""
                    <div class="fc-ai-bubble">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                            <strong>AI Care Companion Response</strong>
                            {render_ai_badge()}
                        </div>
                        <div style="font-size:0.93rem; color:#1E293B; line-height:1.6; white-space: pre-wrap;">
{ans['content']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                if ans.get("error_type") == "MISSING_KEY":
                    st.warning("Please configure your Gemini API Key in the settings expander above to chat with the assistant.")
                else:
                    st.error(f"Error: {ans.get('message')}")

    render_disclaimer(
        "AI Care Companion responses are generated by Google Gemini for organizational and caregiver coordination purposes only. "
        "The AI does NOT provide medical diagnoses, treatment plans, prescriptions, or clinical triage. "
        "Always seek the advice of a qualified physician with any medical questions.",
        title="AI Medical & Ethical Safeguards"
    )

if __name__ == "__main__":
    render_ai_companion_page()
