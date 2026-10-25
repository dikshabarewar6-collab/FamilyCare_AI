"""
Experimental Activity Pattern Analysis using Scikit-Learn and Rule-Based Baseline.
Detects statistical anomalies in check-in timing and daily routines with transparent explanations.
"""
from typing import Dict, Any, List, Tuple
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from database.connection import get_db
from database.models import CheckInRecord, MedicationLog, FamilyMember

# Features strictly restricted to numerical behavioral patterns:
# 1. checkin_hour: Hour of the day when check-in occurred (float)
# 2. delay_mins: Minutes offset from scheduled 9:00 AM target
# 3. day_of_week: Day of week index (0=Monday, 6=Sunday)
# Identifiers, names, addresses, and sensitive health markers are EXCLUDED.
FEATURE_NAMES = ["checkin_hour", "delay_mins", "day_of_week"]

def extract_activity_features(family_id: int = 1) -> pd.DataFrame:
    """Extract clean numerical features from SQLite records for ML modeling."""
    data = []
    with get_db() as db:
        records = (
            db.query(CheckInRecord)
            .join(FamilyMember, CheckInRecord.member_id == FamilyMember.id)
            .filter(FamilyMember.family_id == family_id)
            .order_by(CheckInRecord.checkin_date.asc())
            .all()
        )

        for r in records:
            if r.actual_checkin_time:
                c_hour = r.actual_checkin_time.hour + (r.actual_checkin_time.minute / 60.0)
                try:
                    parts = [int(p) for p in r.scheduled_time.split(":")]
                    sched_dt = datetime.combine(r.checkin_date, datetime.min.time().replace(hour=parts[0], minute=parts[1]))
                    delay = (r.actual_checkin_time - sched_dt).total_seconds() / 60.0
                except Exception:
                    delay = 0.0
            else:
                # Missed or awaiting
                c_hour = np.nan
                delay = np.nan

            data.append({
                "record_id": r.id,
                "date": r.checkin_date,
                "weekday_name": r.checkin_date.strftime("%a"),
                "day_of_week": r.checkin_date.weekday(),
                "status": r.status,
                "checkin_hour": c_hour,
                "delay_mins": delay,
                "notes": r.notes or ""
            })

    return pd.DataFrame(data)

def run_rule_based_check(df: pd.DataFrame, target_hour: float = 9.0, grace_mins: float = 60.0) -> List[Dict[str, Any]]:
    """
    Transparent Rule-Based Baseline:
    Flags events where check-in delay exceeds the configured grace period (e.g. 60m)
    or where check-in is unrecorded after the morning window.
    """
    flags = []
    if df.empty:
        return flags

    for _, row in df.iterrows():
        if row["status"] == "Missed Check-In":
            flags.append({
                "date": str(row["date"]),
                "type": "Rule: Missed Check-In Window",
                "severity": "Warning",
                "explanation": f"Check-in window and grace period ({grace_mins}m) passed without an 'I'm Okay' signal."
            })
        elif pd.notna(row["delay_mins"]) and row["delay_mins"] > grace_mins:
            flags.append({
                "date": str(row["date"]),
                "type": "Rule: Overdue Check-In",
                "severity": "Notice",
                "explanation": f"Check-in occurred {int(row['delay_mins'])} mins after scheduled window (exceeded {grace_mins}m grace period)."
            })
    return flags

def run_experimental_ml_analysis(family_id: int = 1) -> Dict[str, Any]:
    """
    Run Scikit-learn Isolation Forest on numerical activity features.
    Provides feature transparency, missing value imputation, limitation warnings,
    and clear distinction from verified clinical diagnosis.
    """
    df = extract_activity_features(family_id)

    if df.empty or len(df) < 10:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": "Fewer than 10 records available. The experimental ML model requires at least 10 historical records. Prioritizing rule-based detection.",
            "rule_based_alerts": run_rule_based_check(df)
        }

    # Extract numerical features for Scikit-learn
    X_df = df[FEATURE_NAMES].copy()

    # Handle missing values via median imputation
    median_hour = X_df["checkin_hour"].median() or 9.0
    median_delay = X_df["delay_mins"].median() or 0.0
    X_df["checkin_hour"] = X_df["checkin_hour"].fillna(median_hour + 2.0)  # assume late for missed
    X_df["delay_mins"] = X_df["delay_mins"].fillna(median_delay + 120.0)

    # Fit Isolation Forest
    model = IsolationForest(
        n_estimators=100,
        contamination=0.08,  # expect ~8% statistical anomalies in routine
        random_state=42
    )
    predictions = model.fit_predict(X_df)
    anomaly_scores = model.decision_function(X_df)

    df["anomaly_flag"] = predictions  # -1 = anomaly, 1 = normal
    df["anomaly_score"] = anomaly_scores.round(3)

    # Extract flagged anomalous records
    anomalies = df[df["anomaly_flag"] == -1].copy()
    anomalous_events = []
    for _, row in anomalies.iterrows():
        anomalous_events.append({
            "date": str(row["date"]),
            "weekday": row["weekday_name"],
            "checkin_hour": round(row["checkin_hour"], 2) if pd.notna(row["checkin_hour"]) else "N/A",
            "delay_mins": round(row["delay_mins"], 1) if pd.notna(row["delay_mins"]) else "N/A",
            "score": row["anomaly_score"],
            "status": row["status"],
            "notes": row["notes"]
        })

    rule_alerts = run_rule_based_check(df)

    return {
        "status": "SUCCESS",
        "sample_size": len(df),
        "features_used": FEATURE_NAMES,
        "imputation_strategy": "Median behavioral replacement for missed timestamps",
        "model_type": "Scikit-Learn IsolationForest (n_estimators=100, contamination=0.08)",
        "anomalies_detected_count": len(anomalies),
        "anomalous_events": anomalous_events,
        "rule_based_alerts": rule_alerts,
        "model_limitations": (
            "1. Statistical anomaly flags indicate unusual timing patterns, NOT illness or emergency.\n"
            "2. Small sample sizes (~30 days) may flag benign routine changes (e.g. weekend church, travel).\n"
            "3. Rule-based check-in thresholds remain the primary reliable safety mechanism."
        )
    }
