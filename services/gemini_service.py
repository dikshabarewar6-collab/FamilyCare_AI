"""
Google Gemini AI Service using the official Google Gen AI Python SDK (`google-genai`).
Implements privacy-conscious care synthesis, weekly summaries, schedule optimization,
and caregiver checklist generation.
"""
import os
from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime, date, timedelta
from database.connection import get_db
from database.models import CheckInRecord, MedicationLog, Appointment, CareTask, FamilyMember
from analytics.data_processor import get_checkin_metrics, get_medication_metrics, get_task_metrics
import config

try:
    from google import genai
    from google.genai import errors as genai_errors
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

def get_gemini_api_key(session_key: Optional[str] = None) -> Optional[str]:
    """Retrieve Gemini API key with priority: user session override -> Streamlit secrets -> os.environ -> config.py."""
    if session_key and session_key.strip():
        return session_key.strip()

    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    env_key = os.getenv("GEMINI_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    if config.GEMINI_API_KEY and config.GEMINI_API_KEY.strip():
        return config.GEMINI_API_KEY.strip()

    return None

def build_privacy_conscious_summary(family_id: int = 1, days_back: int = 7) -> Dict[str, Any]:
    """
    Query SQLite and utilize Pandas to construct an aggregated, privacy-conscious data summary.
    Strips precise street addresses, medical IDs, and sensitive PII before sending to Gemini.
    """
    cutoff_date = date.today() - timedelta(days=days_back)

    with get_db() as db:
        members = db.query(FamilyMember).filter(FamilyMember.family_id == family_id).all()
        checkins = (
            db.query(CheckInRecord)
            .join(FamilyMember, CheckInRecord.member_id == FamilyMember.id)
            .filter(FamilyMember.family_id == family_id, CheckInRecord.checkin_date >= cutoff_date)
            .all()
        )
        med_logs = (
            db.query(MedicationLog)
            .join(FamilyMember, MedicationLog.member_id == FamilyMember.id)
            .filter(FamilyMember.family_id == family_id, MedicationLog.log_date >= cutoff_date)
            .all()
        )
        upcoming_apps = (
            db.query(Appointment)
            .join(FamilyMember, Appointment.member_id == FamilyMember.id)
            .filter(FamilyMember.family_id == family_id, Appointment.appointment_datetime >= datetime.now())
            .all()
        )
        pending_tasks = (
            db.query(CareTask)
            .filter(CareTask.family_id == family_id, CareTask.status.in_(["Pending", "In Progress"]))
            .all()
        )

    # Aggregations using Pandas
    c_df = pd.DataFrame([{
        "date": c.checkin_date,
        "status": c.status,
        "mood": c.mood
    } for c in checkins])

    total_checkins = len(c_df)
    completed_checkins = int((c_df["status"] == "Checked In").sum()) if not c_df.empty else 0
    missed_checkins = int((c_df["status"] == "Missed Check-In").sum()) if not c_df.empty else 0
    checkin_rate = round((completed_checkins / total_checkins * 100), 1) if total_checkins > 0 else 0.0

    m_df = pd.DataFrame([{
        "status": l.status,
        "medication": l.reminder.medication_name if l.reminder else "Med"
    } for l in med_logs])

    total_meds = len(m_df)
    taken_meds = int((m_df["status"] == "Taken").sum()) if not m_df.empty else 0
    med_rate = round((taken_meds / total_meds * 100), 1) if total_meds > 0 else 0.0

    # Privacy-conscious members structure
    family_nodes = [
        {"role": m.relationship_type, "city": m.city, "is_elderly": m.is_elderly}
        for m in members
    ]

    apps_summary = [
        {"title": a.title, "specialty": a.specialty, "days_away": (a.appointment_datetime.date() - date.today()).days}
        for a in upcoming_apps
    ]

    tasks_summary = [
        {"title": t.title, "category": t.category, "priority": t.priority}
        for t in pending_tasks
    ]

    return {
        "analysis_period_days": days_back,
        "family_nodes": family_nodes,
        "checkin_completion_rate_pct": checkin_rate,
        "total_scheduled_checkins": total_checkins,
        "completed_checkins": completed_checkins,
        "missed_checkins": missed_checkins,
        "medication_acknowledgement_rate_pct": med_rate,
        "total_medication_logs": total_meds,
        "upcoming_appointments": apps_summary,
        "pending_care_tasks": tasks_summary
    }

def generate_weekly_care_summary(family_id: int = 1, api_key_override: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate an AI-powered Weekly Care Synthesis using the official Google Gen AI SDK.
    Retrieves SQLite records, builds privacy-conscious summary in Pandas, and queries Gemini.
    """
    api_key = get_gemini_api_key(api_key_override)
    if not api_key:
        return {
            "success": False,
            "error_type": "MISSING_KEY",
            "message": "Google Gemini API key not detected. Configure GEMINI_API_KEY in your .env file or enter your key in the AI Care Companion sidebar."
        }

    if not GENAI_AVAILABLE:
        return {
            "success": False,
            "error_type": "SDK_ERROR",
            "message": "google-genai SDK not installed."
        }

    # Prepare privacy-conscious summary
    summary_data = build_privacy_conscious_summary(family_id, days_back=7)

    prompt = f"""
You are the FamilyCare AI Companion, a caring, practical coordinator helping adult children who live in different cities care for their aging parent.

Here is the privacy-conscious care activity data for the past 7 days:
- Family Coordination Nodes: {summary_data['family_nodes']}
- Morning Check-In Completion Rate: {summary_data['checkin_completion_rate_pct']}% ({summary_data['completed_checkins']}/{summary_data['total_scheduled_checkins']} completed, {summary_data['missed_checkins']} missed)
- Medication Acknowledgement Rate: {summary_data['medication_acknowledgement_rate_pct']}% across {summary_data['total_medication_logs']} reminder logs
- Upcoming Medical Appointments: {summary_data['upcoming_appointments']}
- Pending Household & Family Tasks: {summary_data['pending_care_tasks']}

Please provide a structured, compassionate, and actionable "Weekly Family Care Synthesis" with the following sections:
1. 🌟 **Executive Wellness Overview**: A warm 2-sentence summary of how the week went for the parent and family.
2. ☀️ **Morning Check-In & Routine Stability**: Observations on morning consistency and any missed check-in context.
3. 💊 **Medication & Daily Care Routine**: Insights on medication reminder adherence (noting that recorded acknowledgements track routine, not clinical dosage).
4. 🗓️ **Upcoming Schedule & Escort Planning**: Preparation steps for upcoming doctor visits (who should attend or coordinate logistics).
5. 🤝 **Cross-City Coordination Advice**: 2 concrete recommendations on how siblings in different cities can balance tasks to prevent caregiver burnout.

CRITICAL INSTRUCTIONS:
- Clearly label that you are an AI assistant.
- DO NOT provide medical diagnoses, medication changes, or emergency predictions.
- Keep the tone empathetic, organized, and encouraging.
"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        content_text = response.text or "Unable to generate summary."
        return {
            "success": True,
            "content": content_text,
            "model": "gemini-2.5-flash",
            "timestamp": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            "data_summary": summary_data
        }
    except Exception as exc:
        err_msg = str(exc)
        return {
            "success": False,
            "error_type": "API_ERROR",
            "message": f"Gemini API request failed: {err_msg}"
        }

def ask_care_companion(
    user_question: str,
    family_id: int = 1,
    api_key_override: Optional[str] = None
) -> Dict[str, Any]:
    """Interactive Q&A with Gemini Care Companion concerning family coordination and schedules."""
    api_key = get_gemini_api_key(api_key_override)
    if not api_key:
        return {
            "success": False,
            "error_type": "MISSING_KEY",
            "message": "Gemini API key is required to query the AI Care Companion."
        }

    summary_data = build_privacy_conscious_summary(family_id, days_back=7)

    system_instruction = (
        "You are the FamilyCare AI Companion. You help families coordinate elderly parent care when "
        "relatives live in different cities. Provide empathetic, pragmatic advice on scheduling, "
        "caregiver task division, grocery routines, and communication tips. "
        "NEVER offer clinical medical diagnoses, prescription advice, or emergency triage. "
        "Remind users to contact doctors or 911 for medical emergencies."
    )

    full_prompt = f"""
{system_instruction}

Context of the family's current status:
- Check-In Rate: {summary_data['checkin_completion_rate_pct']}%
- Medication Acknowledgement Rate: {summary_data['medication_acknowledgement_rate_pct']}%
- Upcoming Appointments: {summary_data['upcoming_appointments']}
- Pending Tasks: {summary_data['pending_care_tasks']}

User's Question:
"{user_question}"

Please provide a helpful, structured, and warm response:
"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        return {
            "success": True,
            "content": response.text or "No response received.",
            "model": "gemini-2.5-flash"
        }
    except Exception as exc:
        return {
            "success": False,
            "error_type": "API_ERROR",
            "message": f"Error calling Gemini: {str(exc)}"
        }
