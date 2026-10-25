"""
Data Science & Analytics Processor using Pandas and NumPy.
Aggregates stored SQLite records for check-ins, medication adherence, care tasks,
and multi-dimensional activity patterns.
"""
from datetime import date, datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from database.connection import get_db
from database.models import CheckInRecord, MedicationLog, CareTask, FamilyMember, MedicationReminder

def get_checkin_metrics(family_id: int = 1) -> Dict[str, Any]:
    """Calculate check-in completion rates, weekly trends, and delay distribution using Pandas."""
    with get_db() as db:
        records = (
            db.query(CheckInRecord)
            .join(FamilyMember, CheckInRecord.member_id == FamilyMember.id)
            .filter(FamilyMember.family_id == family_id)
            .all()
        )

    if not records:
        return {
            "total_records": 0,
            "completion_rate": 0.0,
            "checked_in_count": 0,
            "missed_count": 0,
            "awaiting_count": 0,
            "daily_df": pd.DataFrame(),
            "weekday_df": pd.DataFrame(),
            "hourly_df": pd.DataFrame()
        }

    data = []
    for r in records:
        actual_hour = r.actual_checkin_time.hour + (r.actual_checkin_time.minute / 60.0) if r.actual_checkin_time else None
        
        # Calculate delay from scheduled time
        delay_mins = None
        if r.actual_checkin_time:
            try:
                parts = [int(p) for p in r.scheduled_time.split(":")]
                sched_dt = datetime.combine(r.checkin_date, datetime.min.time().replace(hour=parts[0], minute=parts[1]))
                delay_mins = (r.actual_checkin_time - sched_dt).total_seconds() / 60.0
            except Exception:
                delay_mins = 0.0

        data.append({
            "date": r.checkin_date,
            "weekday": r.checkin_date.strftime("%a"),
            "weekday_num": r.checkin_date.weekday(),
            "status": r.status,
            "mood": r.mood,
            "actual_hour": actual_hour,
            "delay_mins": delay_mins,
            "is_checked_in": 1 if r.status == "Checked In" else 0,
            "is_missed": 1 if r.status == "Missed Check-In" else 0
        })

    df = pd.DataFrame(data)
    total = len(df)
    checked_in = int(df["is_checked_in"].sum())
    missed = int(df["is_missed"].sum())
    awaiting = total - (checked_in + missed)
    rate = round((checked_in / total * 100), 1) if total > 0 else 0.0

    # Daily aggregation
    daily_df = (
        df.groupby("date")
        .agg(
            total=("is_checked_in", "count"),
            completed=("is_checked_in", "sum"),
            missed=("is_missed", "sum")
        )
        .reset_index()
        .sort_values("date")
    )

    # Weekday distribution
    weekday_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekday_df = (
        df.groupby("weekday")
        .agg(
            total=("is_checked_in", "count"),
            completed=("is_checked_in", "sum"),
            avg_delay=("delay_mins", "mean")
        )
        .reindex(weekday_order)
        .reset_index()
        .fillna(0)
    )

    return {
        "total_records": total,
        "completion_rate": rate,
        "checked_in_count": checked_in,
        "missed_count": missed,
        "awaiting_count": awaiting,
        "raw_df": df,
        "daily_df": daily_df,
        "weekday_df": weekday_df
    }

def get_medication_metrics(family_id: int = 1) -> Dict[str, Any]:
    """Calculate medication acknowledgement adherence and frequency trends using Pandas."""
    with get_db() as db:
        logs = (
            db.query(MedicationLog)
            .join(FamilyMember, MedicationLog.member_id == FamilyMember.id)
            .filter(FamilyMember.family_id == family_id)
            .all()
        )

    if not logs:
        return {
            "total_logs": 0,
            "adherence_rate": 0.0,
            "taken_count": 0,
            "skipped_count": 0,
            "med_breakdown_df": pd.DataFrame(),
            "trend_df": pd.DataFrame()
        }

    data = []
    for l in logs:
        med_name = l.reminder.medication_name if l.reminder else "Unknown Med"
        data.append({
            "date": l.log_date,
            "medication": med_name,
            "status": l.status,
            "is_taken": 1 if l.status == "Taken" else 0,
            "is_skipped": 1 if l.status == "Skipped" else 0
        })

    df = pd.DataFrame(data)
    total = len(df)
    taken = int(df["is_taken"].sum())
    skipped = int(df["is_skipped"].sum())
    adherence = round((taken / total * 100), 1) if total > 0 else 0.0

    # Group by medication
    med_df = (
        df.groupby("medication")
        .agg(
            total=("status", "count"),
            taken=("is_taken", "sum"),
            skipped=("is_skipped", "sum")
        )
        .reset_index()
    )
    med_df["adherence_pct"] = (med_df["taken"] / med_df["total"] * 100).round(1)

    # Daily trend
    trend_df = (
        df.groupby("date")
        .agg(
            total=("status", "count"),
            taken=("is_taken", "sum")
        )
        .reset_index()
        .sort_values("date")
    )

    return {
        "total_logs": total,
        "adherence_rate": adherence,
        "taken_count": taken,
        "skipped_count": skipped,
        "med_breakdown_df": med_df,
        "trend_df": trend_df,
        "raw_df": df
    }

def get_task_metrics(family_id: int = 1) -> Dict[str, Any]:
    """Calculate care task completion velocity, priority distribution, and overdue count."""
    today = date.today()
    with get_db() as db:
        tasks = db.query(CareTask).filter(CareTask.family_id == family_id).all()

    if not tasks:
        return {
            "total_tasks": 0,
            "completed": 0,
            "pending": 0,
            "overdue": 0,
            "category_df": pd.DataFrame(),
            "priority_df": pd.DataFrame()
        }

    data = []
    for t in tasks:
        is_overdue = 1 if (t.status != "Completed" and t.due_date < today) else 0
        assignee_name = t.assigned_member.full_name if t.assigned_member else "Unassigned"
        data.append({
            "title": t.title,
            "category": t.category,
            "priority": t.priority,
            "status": t.status,
            "is_overdue": is_overdue,
            "assignee": assignee_name,
            "due_date": t.due_date
        })

    df = pd.DataFrame(data)
    total = len(df)
    completed = int((df["status"] == "Completed").sum())
    pending = total - completed
    overdue = int(df["is_overdue"].sum())

    cat_df = df.groupby("category").size().reset_index(name="count")
    pri_df = df.groupby("priority").size().reset_index(name="count")

    return {
        "total_tasks": total,
        "completed": completed,
        "pending": pending,
        "overdue": overdue,
        "completion_rate": round((completed / total * 100), 1) if total > 0 else 0.0,
        "category_df": cat_df,
        "priority_df": pri_df,
        "raw_df": df
    }

def get_3d_activity_landscape_data(family_id: int = 1) -> pd.DataFrame:
    """
    Generate multi-dimensional activity matrix for 3D Plotly exploration:
    X: Day of Week (0 = Monday, 6 = Sunday)
    Y: Check-In Hour of Day (e.g. 8.25 = 8:15 AM)
    Z: Punctuality Index / Consistency Score (Delay from 9:00 AM target)
    """
    metrics = get_checkin_metrics(family_id)
    raw_df = metrics.get("raw_df")
    if raw_df is None or raw_df.empty:
        # Fallback synthetic grid
        days = np.tile(np.arange(7), 4)
        hours = np.random.uniform(8.2, 9.6, len(days))
        delays = np.abs(hours - 9.0) * 60
        return pd.DataFrame({
            "weekday_num": days,
            "weekday": [["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][d] for d in days],
            "actual_hour": hours,
            "delay_mins": delays,
            "status": "Checked In"
        })

    df_valid = raw_df[raw_df["actual_hour"].notna()].copy()
    if df_valid.empty:
        df_valid = pd.DataFrame({
            "weekday_num": [0, 1, 2, 3, 4],
            "weekday": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "actual_hour": [8.8, 9.1, 8.9, 9.2, 8.7],
            "delay_mins": [-12, 6, -6, 12, -18],
            "status": ["Checked In"] * 5
        })
    return df_valid
