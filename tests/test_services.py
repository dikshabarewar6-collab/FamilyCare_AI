"""
Automated Unit Tests for FamilyCare AI Platform.
Tests database models, member service, check-in logic, medication tracking,
care tasks, analytics processor, and experimental ML activity patterns.
"""
import unittest
import os
import sys
from datetime import datetime, date, timedelta, time

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from database.connection import get_db, init_db
    from database.seed_data import seed_hackathon_demo_data
except (ImportError, ModuleNotFoundError):
    from database import get_db, init_db, seed_hackathon_demo_data
from services.member_service import (
    create_family_member, get_family_members, get_elderly_members,
    update_family_member, delete_family_member
)
from services.checkin_service import (
    get_today_checkin_status, record_checkin, simulate_missed_checkin, get_checkin_history
)
from services.medication_service import (
    create_medication_reminder, record_medication_acknowledgement,
    get_today_medication_status, get_medication_reminders
)
from services.appointment_service import (
    create_appointment, get_upcoming_appointments, update_appointment_status
)
from services.task_service import (
    create_care_task, get_care_tasks, update_task_status, get_pending_tasks_count
)
from analytics.data_processor import (
    get_checkin_metrics, get_medication_metrics, get_task_metrics, get_3d_activity_landscape_data
)
from ml.activity_pattern import run_experimental_ml_analysis

class TestFamilyCareAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize database and seed demo data once before all tests."""
        init_db()
        seed_hackathon_demo_data()

    def test_01_family_members_query(self):
        """Verify members are retrieved correctly from SQLite."""
        members = get_family_members(1)
        self.assertGreaterEqual(len(members), 3, "Expected at least 3 seeded family members.")
        
        elderly = get_elderly_members(1)
        self.assertTrue(any(m.full_name == "Eleanor Vance" for m in elderly), "Eleanor Vance should be marked elderly.")

    def test_02_member_validation_and_creation(self):
        """Test input validation when creating a family member."""
        # Empty name should fail
        with self.assertRaises(ValueError):
            create_family_member({"full_name": "", "relationship_type": "Son", "city": "Boston", "state": "MA"})

        # Valid creation
        new_mem = create_family_member({
            "full_name": "Test Caregiver",
            "relationship_type": "Other Relative",
            "city": "Denver",
            "state": "CO",
            "phone": "+1 555-0100"
        })
        self.assertIsNotNone(new_mem.id)
        self.assertEqual(new_mem.city, "Denver")

        # Cleanup
        delete_family_member(new_mem.id)

    def test_03_checkin_recording_and_status(self):
        """Verify daily 'I'm Okay' check-in workflow."""
        elderly = get_elderly_members(1)[0]
        
        # Record check-in
        rec = record_checkin(elderly.id, mood="Good & Peaceful 😊", notes="Test checkin note")
        self.assertEqual(rec.status, "Checked In")
        self.assertIsNotNone(rec.actual_checkin_time)

        # Status should now report Checked In
        status, cur_rec = get_today_checkin_status(elderly.id)
        self.assertEqual(status, "Checked In")

    def test_04_simulated_missed_checkin(self):
        """Verify hackathon demo simulation of overdue check-in alert."""
        elderly = get_elderly_members(1)[0]
        sim_rec = simulate_missed_checkin(elderly.id)
        self.assertEqual(sim_rec.status, "Missed Check-In")
        self.assertTrue(sim_rec.is_simulated)

        status, _ = get_today_checkin_status(elderly.id)
        self.assertEqual(status, "Missed Check-In")

    def test_05_medication_reminder_acknowledgement(self):
        """Verify medication acknowledgement logging and status tracking."""
        elderly = get_elderly_members(1)[0]
        reminders = get_medication_reminders(elderly.id)
        self.assertGreater(len(reminders), 0)

        rem = reminders[0]
        log = record_medication_acknowledgement(rem.id, status="Taken", note="Test unit test taken")
        self.assertEqual(log.status, "Taken")

        status_list = get_today_medication_status(elderly.id)
        target_status = next((s["status"] for s in status_list if s["reminder"].id == rem.id), None)
        self.assertEqual(target_status, "Taken")

    def test_06_appointment_scheduling(self):
        """Verify doctor appointments can be scheduled and marked completed."""
        elderly = get_elderly_members(1)[0]
        app_dt = datetime.now() + timedelta(days=4)
        
        app = create_appointment({
            "member_id": elderly.id,
            "title": "Dental Cleaning Test",
            "doctor_name": "Dr. Miller",
            "specialty": "Dentistry",
            "clinic_name": "Smile Care",
            "appointment_datetime": app_dt
        })
        self.assertEqual(app.status, "Upcoming")

        updated = update_appointment_status(app.id, "Completed")
        self.assertEqual(updated.status, "Completed")

    def test_07_care_task_lifecycle(self):
        """Verify task creation, progression from Pending to Completed."""
        task = create_care_task({
            "family_id": 1,
            "title": "Pick up winter jacket",
            "category": "Household",
            "due_date": date.today() + timedelta(days=2),
            "priority": "Medium"
        })
        self.assertEqual(task.status, "Pending")

        update_task_status(task.id, "In Progress")
        tasks_in_prog = get_care_tasks(family_id=1, status="In Progress")
        self.assertTrue(any(t.id == task.id for t in tasks_in_prog))

        update_task_status(task.id, "Completed")
        tasks_comp = get_care_tasks(family_id=1, status="Completed")
        self.assertTrue(any(t.id == task.id for t in tasks_comp))

    def test_08_analytics_processor(self):
        """Verify Pandas calculations for check-in rates and medication adherence."""
        c_metrics = get_checkin_metrics(family_id=1)
        self.assertIn("completion_rate", c_metrics)
        self.assertGreater(c_metrics["total_records"], 0)

        m_metrics = get_medication_metrics(family_id=1)
        self.assertIn("adherence_rate", m_metrics)
        self.assertGreater(m_metrics["total_logs"], 0)

        t_metrics = get_task_metrics(family_id=1)
        self.assertIn("completion_rate", t_metrics)

        df_3d = get_3d_activity_landscape_data(family_id=1)
        self.assertFalse(df_3d.empty)
        self.assertIn("actual_hour", df_3d.columns)

    def test_09_experimental_ml_isolation_forest(self):
        """Verify Scikit-Learn IsolationForest activity pattern analysis."""
        ml_res = run_experimental_ml_analysis(family_id=1)
        self.assertEqual(ml_res["status"], "SUCCESS")
        self.assertGreaterEqual(ml_res["sample_size"], 10)
        self.assertIn("anomalies_detected_count", ml_res)
        self.assertIn("rule_based_alerts", ml_res)
        self.assertIn("model_limitations", ml_res)

if __name__ == "__main__":
    unittest.main()
